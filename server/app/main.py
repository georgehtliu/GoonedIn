import base64
import csv
import uuid
import os
import asyncio
import logging
import re
import io
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Literal
from urllib.parse import quote_plus
from datetime import datetime

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from gender_guesser import detector as gender_detector
import google.generativeai as genai
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

HUGGINGFACE_ENDPOINT = "https://thwanx-beautyrate.hf.space/api/predict"
DEFAULT_FN_INDEX = 0
_gender_detector = gender_detector.Detector(case_sensitive=False)
logger = logging.getLogger(__name__)

PHANTOMBUSTER_BASE_URL = "https://api.phantombuster.com/api/v2"
PHANTOMBUSTER_MAX_WAIT_SECONDS = 180
PHANTOMBUSTER_POLL_INTERVAL_SECONDS = 5
# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")


mongo_client: AsyncIOMotorClient | None = None
mongo_collection = None


def _extract_primary_score(raw: Any) -> Any:
  """Return the first score-like value from the Hugging Face payload."""
  if isinstance(raw, list) and raw:
    first = raw[0]
    if isinstance(first, (int, float, str)):
      return first
    if isinstance(first, (list, tuple)):
      for item in first:
        if isinstance(item, (int, float, str)):
          return item
      # fall back to first element of nested list
      if first:
        return first[0]
    if isinstance(first, dict):
      label = first.get("label")
      if isinstance(label, (int, float, str)):
        return label
      score = first.get("score")
      if isinstance(score, (int, float, str)):
        return score
      confidences = first.get("confidences")
      if isinstance(confidences, list) and confidences:
        top = max(confidences, key=lambda item: item.get("score", 0))
        label = top.get("label")
        if isinstance(label, (int, float, str)):
          return label
        value = top.get("score")
        if isinstance(value, (int, float)):
          return value
      values = first.get("values")
      if isinstance(values, list) and values:
        return values[0]
    return first
  if isinstance(raw, dict):
    data = raw.get("data")
    if isinstance(data, list) and data:
      first = data[0]
      if isinstance(first, (int, float, str)):
        return first
      if isinstance(first, (list, tuple)):
        for item in first:
          if isinstance(item, (int, float, str)):
            return item
        if first:
          return first[0]
      if isinstance(first, dict):
        label = first.get("label")
        if isinstance(label, (int, float, str)):
          return label
        score = first.get("score")
        if isinstance(score, (int, float, str)):
          return score
        confidences = first.get("confidences")
        if isinstance(confidences, list) and confidences:
          top = max(confidences, key=lambda item: item.get("score", 0))
          label = top.get("label")
          if isinstance(label, (int, float, str)):
            return label
          value = top.get("score")
          if isinstance(value, (int, float)):
            return value
        values = first.get("values")
        if isinstance(values, list) and values:
          return values[0]
        nested_data = first.get("data")
        if isinstance(nested_data, list) and nested_data:
          return nested_data[0]
      return first
    # Some Gradio payloads include a "scores" array or nested outputs
    scores = raw.get("scores")
    if isinstance(scores, list) and scores:
      return scores[0]
  return None


def _coerce_to_float(value: Any) -> float | None:
  if isinstance(value, (int, float)):
    return float(value)
  if isinstance(value, str):
    try:
      return float(value)
    except ValueError:
      digit_portion = "".join(ch for ch in value if (ch.isdigit() or ch in ".-"))
      if digit_portion.count(".") > 1 and "." in digit_portion:
        parts = digit_portion.split(".")
        digit_portion = parts[0] + "." + "".join(parts[1:])
      try:
        return float(digit_portion)
      except ValueError:
        return None
  return None


def _find_first_numeric(value: Any) -> float | None:
  """Depth-first search for the first numeric-looking value."""
  score = _coerce_to_float(value)
  if score is not None:
    return score

  if isinstance(value, dict):
    for key in ("score", "value", "label", "confidence", "probability"):
      if key in value:
        score = _coerce_to_float(value[key])
        if score is not None:
          return score
    for nested in value.values():
      score = _find_first_numeric(nested)
      if score is not None:
        return score

  if isinstance(value, (list, tuple, set)):
    for item in value:
      score = _find_first_numeric(item)
      if score is not None:
        return score

  return None


class BeautyScoreResponse(BaseModel):
  raw: dict
  gender: Literal["woman", "man"]
  score: float | None = None


class PhantomProfile(BaseModel):
  profile_url: str | None = None
  name: str | None = None
  headline: str | None = None
  location: str | None = None
  raw: dict[str, Any] | None = None


class PhantomSearchRequest(BaseModel):
  query: str = Field(default="Waterloo girls", min_length=1, max_length=200)
  limit: int = Field(default=50, ge=1, le=50)
  search_url: str | None = None
  category: str | None = None
  search_type: str | None = None
  connection_degrees: list[str] | None = None
  lines_per_launch: int | None = None
  results_per_launch: int | None = None
  results_per_search: int | None = None
  enrich: bool | None = None


def _build_search_argument(request: PhantomSearchRequest, session_cookie: str) -> dict[str, Any]:
  category = request.category or os.getenv("PHANTOMBUSTER_CATEGORY") or "People"
  search_type = request.search_type or os.getenv("PHANTOMBUSTER_SEARCH_TYPE") or "linkedInSearchUrl"
  connection_degrees_env = os.getenv("PHANTOMBUSTER_CONNECTION_DEGREES", "")
  connection_degrees = request.connection_degrees or [d.strip() for d in connection_degrees_env.split(",") if d.strip()]
  lines_per_launch = request.lines_per_launch or int(os.getenv("PHANTOMBUSTER_LINES_PER_LAUNCH", "10"))
  env_results_per_launch = int(os.getenv("PHANTOMBUSTER_RESULTS_PER_LAUNCH", "10"))
  env_results_per_search = int(os.getenv("PHANTOMBUSTER_RESULTS_PER_SEARCH", "10"))
  effective_results_per_launch = request.results_per_launch or env_results_per_launch
  effective_results_per_search = request.results_per_search or env_results_per_search
  enrich_env = os.getenv("PHANTOMBUSTER_ENRICH", "true").lower() == "true"
  enrich = request.enrich if request.enrich is not None else enrich_env
  search_url = request.search_url or os.getenv("PHANTOMBUSTER_LINKEDIN_SEARCH_URL")
  if search_type == "linkedInSearchUrl" and not search_url:
    encoded_query = quote_plus(request.query)
    search_url = f"https://www.linkedin.com/search/results/all/?keywords={encoded_query}&origin=GLOBAL_SEARCH_HEADER"

  identity_id = os.getenv("PHANTOMBUSTER_IDENTITY_ID")
  user_agent = os.getenv("PHANTOMBUSTER_USER_AGENT")

  argument: dict[str, Any] = {
    "category": category,
    "searchType": search_type,
    "sessionCookie": session_cookie,
    "numberOfLinesPerLaunch": lines_per_launch,
    "numberOfResultsPerLaunch": effective_results_per_launch,
    "numberOfResultsPerSearch": effective_results_per_search,
    "enrichLeadsWithAdditionalInformation": enrich,
  }

  if search_url:
    argument["linkedInSearchUrl"] = search_url

  if connection_degrees:
    argument["connectionDegreesToScrape"] = connection_degrees

  if user_agent:
    argument["userAgent"] = user_agent

  if identity_id:
    identity_payload: dict[str, Any] = {
      "identityId": identity_id,
      "sessionCookie": session_cookie
    }
    if user_agent:
      identity_payload["userAgent"] = user_agent
    argument["identities"] = [identity_payload]

  return argument


class PhantomSearchResponse(BaseModel):
  query: str
  limit: int
  profiles: list[PhantomProfile]
  container_id: str
  output_url: str | None = None


class SaveSearchRequest(BaseModel):
  query: str = Field(..., min_length=1, max_length=500)
  result: str = Field(..., min_length=1)


class SaveSearchResponse(BaseModel):
  id: str
  query: str
  result: str
  created_at: datetime


def _infer_gender_from_name(name: str | None) -> Literal["woman", "man"] | None:
  if not name:
    return None

  first_name = name.strip().split()[0]
  if not first_name:
    return None

  guess = _gender_detector.get_gender(first_name)
  if guess in {"male", "mostly_male"}:
    return "man"
  if guess in {"female", "mostly_female"}:
    return "woman"

  return None


def _extract_name_from_row(row: dict[str, Any] | None) -> str | None:
  if not row:
    return None

  for key in (
    "fullName",
    "name",
    "profileFullName",
    "profileName",
    "firstName"
  ):
    value = row.get(key)
    if isinstance(value, str) and value.strip():
      return value

  return None


def _filter_rows_by_gender(rows: list[dict[str, Any]], gender: Literal["woman", "man"] | None) -> list[dict[str, Any]]:
  if gender is None:
    return rows

  filtered: list[dict[str, Any]] = []
  for row in rows:
    inferred = _infer_gender_from_name(_extract_name_from_row(row))
    if inferred == gender:
      filtered.append(row)
  return filtered


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
  global mongo_client, mongo_collection
  mongo_uri = os.getenv("MONGODB_URI") or "mongodb+srv://gooner123:gooner123@cluster0.9xkp2kk.mongodb.net/?appName=Cluster0"
  mongo_db_name = os.getenv("MONGODB_DB", "linkedin_baddie_finder")
  mongo_collection_name = os.getenv("MONGODB_COLLECTION", "search_results")
  mongo_client = AsyncIOMotorClient(mongo_uri)
  mongo_collection = mongo_client[mongo_db_name][mongo_collection_name]
  try:
    await mongo_client.admin.command("ping")
    logger.info("Connected to MongoDB cluster '%s' (database=%s, collection=%s)", mongo_uri, mongo_db_name, mongo_collection_name)
  except Exception as exc:
    logger.error("Failed to connect to MongoDB: %s", exc)
    raise RuntimeError("Unable to connect to MongoDB") from exc
  try:
    yield
  finally:
    if mongo_client:
      mongo_client.close()


app = FastAPI(
  title="LinkedIn Baddie Finder API",
  version="0.1.0",
  lifespan=lifespan
)

app.add_middleware(
  CORSMiddleware,
  allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)


@app.get("/health")
async def read_health() -> dict[str, str]:
  return {"message": "Service is healthy"}


@app.get("/phantombuster/search-cache")
async def phantombuster_search_cache(
  query: str,
  limit: int =50,
  gender: Literal["woman", "man"] | None = None
) -> dict[str, Any]:
  trimmed_query = query.strip()
  if not trimmed_query:
    raise HTTPException(status_code=400, detail="Query must be a non-empty string.")

  if mongo_collection is None:
    raise HTTPException(status_code=500, detail="MongoDB is not configured.")

  cached_document = await mongo_collection.find_one(
    {"query": trimmed_query, "response": {"$exists": True}},
    sort=[("created_at", -1)]
  )
  if cached_document and isinstance(cached_document.get("response"), dict):
    stored_response = dict(cached_document["response"])
    stored_rows = stored_response.get("csv_data") or []
    filtered_rows = _filter_rows_by_gender(list(stored_rows), gender)
    filtered_first_row = filtered_rows[0] if filtered_rows else None

    response_payload = dict(stored_response)
    response_payload["csv_data"] = filtered_rows
    response_payload["csv_row_count"] = len(filtered_rows)
    response_payload["first_row"] = filtered_first_row
    response_payload["filter_gender"] = gender
    response_payload["total_csv_row_count"] = len(stored_rows)
    response_payload["mongo_document_id"] = str(cached_document["_id"])
    response_payload["cached"] = True
    return response_payload

  api_key = os.getenv("PHANTOMBUSTER_API_KEY")
  agent_id = os.getenv("PHANTOMBUSTER_SEARCH_AGENT_ID")
  session_cookie = os.getenv("PHANTOMBUSTER_SESSION_COOKIE")

  if not api_key or not agent_id:
    raise HTTPException(status_code=500, detail="PhantomBuster credentials are not configured.")

  if not session_cookie:
    raise HTTPException(status_code=500, detail="PhantomBuster session cookie is not configured (missing PHANTOMBUSTER_SESSION_COOKIE).")

  trimmed_limit = min(max(limit, 1), 50)
  dynamic_search_url = f"https://www.linkedin.com/search/results/all/?keywords={quote_plus(trimmed_query)}&origin=GLOBAL_SEARCH_HEADER"
  search_request = PhantomSearchRequest(
    query=trimmed_query,
    limit=trimmed_limit,
    search_url=dynamic_search_url,
    results_per_launch=trimmed_limit,
    results_per_search=trimmed_limit
  )

  launch_headers = {
    "X-Phantombuster-Key-1": api_key,
    "Content-Type": "application/json"
  }
  fetch_headers = {
    "X-Phantombuster-Key": api_key,
    "accept": "application/json"
  }

  container_id: str | None = None
  container_status: str | None = None
  fetch_payload: dict[str, Any] = {}

  async with httpx.AsyncClient(timeout=30.0) as client:
    launch_body = {
      "id": agent_id,
      "argument": _build_search_argument(search_request, session_cookie)
    }
    launch_resp = await client.post(f"{PHANTOMBUSTER_BASE_URL}/agents/launch", headers=launch_headers, json=launch_body)
    launch_resp.raise_for_status()
    launch_data = launch_resp.json()
    container_id = str(launch_data.get("containerId") or launch_data.get("data", {}).get("id") or "")
    if not container_id:
      logger.error("PhantomBuster launch response missing containerId: %s", launch_data)
      raise HTTPException(status_code=502, detail="PhantomBuster launch did not return a container identifier.")

    logger.info("Launched PhantomBuster agent %s (container %s) for query '%s'", agent_id, container_id, trimmed_query)

    elapsed = 0
    container_payload: dict[str, Any] | None = None
    while elapsed <= PHANTOMBUSTER_MAX_WAIT_SECONDS:
      container_resp = await client.get(
        f"{PHANTOMBUSTER_BASE_URL}/containers/fetch",
        headers=launch_headers,
        params={"id": container_id}
      )
      container_resp.raise_for_status()
      container_payload = container_resp.json()
      container = container_payload.get("container") or container_payload
      container_status = container.get("status")
      logger.debug("PhantomBuster container %s status=%s", container_id, container_status)

      if container_status in {"finished", "failed", "aborted", "stopped"}:
        break

      await asyncio.sleep(PHANTOMBUSTER_POLL_INTERVAL_SECONDS)
      elapsed += PHANTOMBUSTER_POLL_INTERVAL_SECONDS

    if not container_payload or container_status != "finished":
      logger.error("PhantomBuster container %s ended with status %s", container_id, container_status)
      raise HTTPException(status_code=502, detail=f"PhantomBuster run ended with status: {container_status}")

    fetch_resp = await client.get(
      f"{PHANTOMBUSTER_BASE_URL}/agents/fetch-output",
      headers=fetch_headers,
      params={"id": agent_id}
    )
    fetch_resp.raise_for_status()
    fetch_payload = fetch_resp.json()

    output_value = fetch_payload.get("output")
    if output_value is None and isinstance(fetch_payload.get("container"), dict):
      output_value = fetch_payload["container"].get("output")

    if isinstance(output_value, str):
      output_text = output_value
    else:
      output_text = json.dumps(output_value or "", ensure_ascii=False)

    csv_url: str | None = None
    match = re.search(r"https://\S+?\.csv", output_text)
    if match:
      csv_url = match.group(0).rstrip(")\"'")

    csv_rows: list[dict[str, Any]] = []
    first_row: dict[str, Any] | None = None
    if csv_url:
      csv_response = await client.get(csv_url)
      csv_response.raise_for_status()
      csv_file = io.StringIO(csv_response.text)
      reader = csv.DictReader(csv_file)
      csv_rows = list(reader)
      logger.info("Fetched %d rows from PhantomBuster CSV %s for query '%s'", len(csv_rows), csv_url, trimmed_query)
      print(f"[phantombuster-test] query={trimmed_query} csv_url={csv_url} rows={len(csv_rows)}")
      if csv_rows:
        first_row = csv_rows[0]
        print(f"[phantombuster-test] first_row={first_row}")

  stored_payload: dict[str, Any] = {
    "query": trimmed_query,
    "agent_id": agent_id,
    "container_id": container_id,
    "status": container_status or fetch_payload.get("status"),
    "output": output_text,
    "csv_url": csv_url,
    "csv_row_count": len(csv_rows),
    "csv_data": csv_rows,
    "first_row": first_row
  }

  insert_result = await mongo_collection.insert_one(
    {
      "query": trimmed_query,
      "response": stored_payload,
      "created_at": datetime.utcnow()
    }
  )

  filtered_rows = _filter_rows_by_gender(list(csv_rows), gender)
  filtered_first_row = filtered_rows[0] if filtered_rows else None

  response_payload = dict(stored_payload)
  response_payload["csv_data"] = filtered_rows
  response_payload["csv_row_count"] = len(filtered_rows)
  response_payload["first_row"] = filtered_first_row
  response_payload["filter_gender"] = gender
  response_payload["total_csv_row_count"] = len(csv_rows)
  response_payload["mongo_document_id"] = str(insert_result.inserted_id)
  response_payload["cached"] = False

  return response_payload


@app.post("/beauty-score", response_model=BeautyScoreResponse)
async def get_beauty_score(
  image: UploadFile = File(...),
  name: str | None = Form(None),
  gender: Literal["woman", "man"] | None = Form(None)
) -> BeautyScoreResponse:
  if image.content_type not in {"image/jpeg", "image/png"}:
    raise HTTPException(status_code=400, detail="Only JPEG or PNG images are supported.")

  resolved_gender = gender or _infer_gender_from_name(name)
  if resolved_gender is None:
    raise HTTPException(
      status_code=400,
      detail="Unable to determine gender automatically. Provide a gender or a more specific name."
    )

  image_bytes = await image.read()
  data_url = f"data:{image.content_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
  payload = {
    "data": [data_url, resolved_gender],
    "fn_index": DEFAULT_FN_INDEX,
    "session_hash": uuid.uuid4().hex
  }

  try:
    async with httpx.AsyncClient(timeout=60.0) as client:
      response = await client.post(HUGGINGFACE_ENDPOINT, json=payload)
      response.raise_for_status()
  except httpx.HTTPStatusError as exc:
    raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
  except httpx.HTTPError as exc:
    raise HTTPException(status_code=502, detail=f"Hugging Face request failed: {exc}") from exc

  raw_payload = response.json()
  score_raw = _extract_primary_score(raw_payload)
  score_value = _find_first_numeric(score_raw if score_raw is not None else raw_payload)

  logger.info("Beauty score computed (gender=%s, raw=%s, score=%s)", resolved_gender, score_raw, score_value)
  print(f"[beauty-score] gender={resolved_gender} raw={score_raw!r} score={score_value}")

  return BeautyScoreResponse(raw=raw_payload, gender=resolved_gender, score=score_value)


def _extract_profile_entry(entry: dict[str, Any]) -> PhantomProfile:
  profile_url = entry.get("profileUrl") or entry.get("linkedinUrl") or entry.get("publicProfileUrl") or entry.get("url")
  name = entry.get("fullName") or entry.get("name")
  headline = entry.get("headline") or entry.get("occupation")
  location = entry.get("locationName") or entry.get("location")
  return PhantomProfile(
    profile_url=profile_url,
    name=name,
    headline=headline,
    location=location,
    raw=entry
  )


@app.post("/phantombuster/linkedin-search", response_model=PhantomSearchResponse)
async def phantombuster_linkedin_search(payload: PhantomSearchRequest) -> PhantomSearchResponse:
  api_key = os.getenv("PHANTOMBUSTER_API_KEY")
  agent_id = os.getenv("PHANTOMBUSTER_SEARCH_AGENT_ID")
  session_cookie = os.getenv("PHANTOMBUSTER_SESSION_COOKIE")

  if not api_key or not agent_id:
    raise HTTPException(status_code=500, detail="PhantomBuster credentials are not configured (missing PHANTOMBUSTER_API_KEY or PHANTOMBUSTER_SEARCH_AGENT_ID).")

  if not session_cookie:
    raise HTTPException(status_code=500, detail="PhantomBuster session cookie is not configured (missing PHANTOMBUSTER_SESSION_COOKIE).")

  headers = {
    "X-Phantombuster-Key-1": api_key,
    "Content-Type": "application/json"
  }

  launch_body: dict[str, Any] = {
    "id": agent_id,
    "argument": _build_search_argument(payload, session_cookie)
  }

  # Debug: Log what we're sending to PhantomBuster
  logger.info(f"PhantomBuster launch_body argument: {launch_body['argument']}")

  try:
    async with httpx.AsyncClient(timeout=30.0) as client:
      launch_resp = await client.post(f"{PHANTOMBUSTER_BASE_URL}/agents/launch", headers=headers, json=launch_body)
      launch_resp.raise_for_status()
      launch_data = launch_resp.json()
      container_id = launch_data.get("containerId") or launch_data.get("data", {}).get("id")
      if not container_id:
        logger.error("PhantomBuster launch response missing containerId: %s", launch_data)
        raise HTTPException(status_code=502, detail="PhantomBuster launch did not return a container identifier.")

      logger.info("Launched PhantomBuster agent %s (container %s) for query '%s'", agent_id, container_id, payload.query)

      container_data: dict[str, Any] | None = None
      elapsed = 0
      while elapsed <= PHANTOMBUSTER_MAX_WAIT_SECONDS:
        container_resp = await client.get(
          f"{PHANTOMBUSTER_BASE_URL}/containers/fetch",
          headers=headers,
          params={"id": container_id}
        )
        container_resp.raise_for_status()
        container_data = container_resp.json()
        container = container_data.get("container") or container_data
        status = container.get("status")
        logger.debug("PhantomBuster container %s status=%s", container_id, status)

        if status in {"finished", "failed", "aborted", "stopped"}:
          break

        await asyncio.sleep(PHANTOMBUSTER_POLL_INTERVAL_SECONDS)
        elapsed += PHANTOMBUSTER_POLL_INTERVAL_SECONDS

      if not container_data:
        raise HTTPException(status_code=502, detail="Unable to obtain PhantomBuster container status.")

      container = container_data.get("container") or container_data
      status = container.get("status")

      if status != "finished":
        logger.error("PhantomBuster container %s ended with status %s", container_id, status)
        raise HTTPException(status_code=502, detail=f"PhantomBuster run ended with status: {status}")

      output = container.get("output", {}) if isinstance(container, dict) else {}
      json_url = None
      if isinstance(output, dict):
        json_candidate = output.get("json") or output.get("jsonUrl") or output.get("resultObjectUrl")
        if isinstance(json_candidate, list):
          json_candidate = json_candidate[0] if json_candidate else None
        json_url = json_candidate

      profiles: list[PhantomProfile] = []
      if json_url:
        try:
          result_resp = await client.get(json_url)
          result_resp.raise_for_status()
          result_data = result_resp.json()
          if isinstance(result_data, list):
            for entry in result_data:
              if isinstance(entry, dict):
                profiles.append(_extract_profile_entry(entry))
                if len(profiles) >= payload.limit:
                  break
        except httpx.HTTPError as exc:
          logger.warning("Failed to download PhantomBuster JSON output: %s", exc)
      elif isinstance(output, dict) and output.get("resultObject"):
        result_object = output["resultObject"]
        if isinstance(result_object, list):
          for entry in result_object:
            if isinstance(entry, dict):
              profiles.append(_extract_profile_entry(entry))
              if len(profiles) >= payload.limit:
                break

      return PhantomSearchResponse(
        query=payload.query,
        limit=payload.limit,
        profiles=profiles,
        container_id=str(container_id),
        output_url=json_url
      )

  except httpx.HTTPStatusError as exc:
    logger.error("PhantomBuster API error: %s", exc.response.text)
    raise HTTPException(status_code=exc.response.status_code, detail=f"PhantomBuster API error: {exc.response.text}") from exc
  except httpx.HTTPError as exc:
    logger.error("PhantomBuster network error: %s", exc)
    raise HTTPException(status_code=502, detail=f"PhantomBuster network error: {exc}") from exc
  except asyncio.TimeoutError as exc:
    logger.error("Timed out waiting for PhantomBuster container: %s", exc)
    raise HTTPException(status_code=504, detail="Timed out waiting for PhantomBuster results.") from exc


@app.post("/mongo/save-search", response_model=SaveSearchResponse)
async def save_search_to_mongo(payload: SaveSearchRequest) -> SaveSearchResponse:
  if mongo_collection is None:
    raise HTTPException(status_code=500, detail="MongoDB is not configured.")

  document = {
    "query": payload.query,
    "result": payload.result,
    "created_at": datetime.utcnow()
  }

  insert_result = await mongo_collection.insert_one(document)
  document_id = str(insert_result.inserted_id)

  return SaveSearchResponse(
    id=document_id,
    query=payload.query,
    result=payload.result,
    created_at=document["created_at"]
  )


class FetchContainerRequest(BaseModel):
  container_id: str = Field(min_length=1, max_length=100)
  limit: int = Field(default=10, ge=1, le=1000)


@app.post("/phantombuster/fetch-results", response_model=PhantomSearchResponse)
async def fetch_phantombuster_results(payload: FetchContainerRequest) -> PhantomSearchResponse:
  """Fetch results from a previously launched PhantomBuster container by its ID."""
  api_key = os.getenv("PHANTOMBUSTER_API_KEY")

  if not api_key:
    raise HTTPException(status_code=500, detail="PhantomBuster API key is not configured (missing PHANTOMBUSTER_API_KEY).")

  headers = {
    "X-Phantombuster-Key-1": api_key,
    "Content-Type": "application/json"
  }

  try:
    async with httpx.AsyncClient(timeout=30.0) as client:
      # Fetch container status
      container_resp = await client.get(
        f"{PHANTOMBUSTER_BASE_URL}/containers/fetch",
        headers=headers,
        params={"id": payload.container_id}
      )
      container_resp.raise_for_status()
      container_data = container_resp.json()
      container = container_data.get("container") or container_data
      status = container.get("status")

      logger.info(f"Fetched PhantomBuster container {payload.container_id}, status: {status}")

      # Extract output URL
      output = container.get("output", {}) if isinstance(container, dict) else {}
      json_url = None
      if isinstance(output, dict):
        json_candidate = output.get("json") or output.get("jsonUrl") or output.get("resultObjectUrl")
        if isinstance(json_candidate, list):
          json_candidate = json_candidate[0] if json_candidate else None
        json_url = json_candidate

      # Fetch and parse profiles
      profiles: list[PhantomProfile] = []
      if json_url:
        try:
          result_resp = await client.get(json_url)
          result_resp.raise_for_status()
          result_data = result_resp.json()
          if isinstance(result_data, list):
            for entry in result_data:
              if isinstance(entry, dict):
                profiles.append(_extract_profile_entry(entry))
                if len(profiles) >= payload.limit:
                  break
        except httpx.HTTPError as exc:
          logger.warning("Failed to download PhantomBuster JSON output: %s", exc)
      elif isinstance(output, dict) and output.get("resultObject"):
        result_object = output["resultObject"]
        if isinstance(result_object, list):
          for entry in result_object:
            if isinstance(entry, dict):
              profiles.append(_extract_profile_entry(entry))
              if len(profiles) >= payload.limit:
                break

      return PhantomSearchResponse(
        query="",  # We don't know the original query
        limit=payload.limit,
        profiles=profiles,
        container_id=str(payload.container_id),
        output_url=json_url
      )

  except httpx.HTTPStatusError as exc:
    logger.error("PhantomBuster API error: %s", exc.response.text)
    raise HTTPException(status_code=exc.response.status_code, detail=f"PhantomBuster API error: {exc.response.text}") from exc
  except httpx.HTTPError as exc:
    logger.error("PhantomBuster network error: %s", exc)
    raise HTTPException(status_code=502, detail=f"PhantomBuster network error: {exc}") from exc


# AI Feature Models
class ProfileData(BaseModel):
  name: str
  major: str | None = None
  company: str | None = None
  bio: str | None = None
  location: str | None = None
  interests: list[str] = []
  experience: str | None = None
  age: int | None = None


class AIOverviewRequest(BaseModel):
  profile: ProfileData


class AIOverviewResponse(BaseModel):
  summary: str
  personality_insights: str
  compatibility_notes: str
  conversation_starters: list[str]


class DraftMessageRequest(BaseModel):
  recipient: ProfileData
  tone: Literal["flirty", "polite", "direct", "professional", "casual", "witty"]
  message_type: Literal["cold_dm", "warm_dm", "follow_up"]
  context: str | None = None


class DraftMessageResponse(BaseModel):
  message: str
  tone: str


class SatiricalInsightRequest(BaseModel):
  profile: ProfileData


class SatiricalInsightResponse(BaseModel):
  insights: list[str]


class SocialProfile(BaseModel):
  platform: str
  url: str
  confidence: Literal["high", "medium", "low"]


class FindSocialsRequest(BaseModel):
  name: str
  company: str | None = None
  location: str | None = None


class FindSocialsResponse(BaseModel):
  profiles: list[SocialProfile]


# AI Endpoints
@app.post("/api/ai-overview", response_model=AIOverviewResponse)
async def get_ai_overview(request: AIOverviewRequest) -> AIOverviewResponse:
  """Generate an AI-powered overview of a LinkedIn profile."""
  if not GEMINI_API_KEY:
    raise HTTPException(status_code=503, detail="AI service not configured")

  profile = request.profile

  prompt = f"""Analyze this LinkedIn profile for a dating/networking context:

Name: {profile.name}
Title/Major: {profile.major or 'Not specified'}
Company: {profile.company or 'Not specified'}
Bio: {profile.bio or 'Not specified'}
Location: {profile.location or 'Not specified'}
Interests: {', '.join(profile.interests) if profile.interests else 'Not specified'}
Experience: {profile.experience or 'Not specified'}
Age: {profile.age or 'Not specified'}

Please provide:
1. A compelling 2-3 sentence professional background summary
2. Personality insights and what makes them interesting (2-3 sentences)
3. Compatibility indicators for dating/networking (2-3 sentences)
4. Exactly 3 creative conversation starters

Format your response as:
SUMMARY: [summary here]
PERSONALITY: [personality insights here]
COMPATIBILITY: [compatibility notes here]
STARTERS:
- [starter 1]
- [starter 2]
- [starter 3]

Keep it engaging, dating-app appropriate, and positive."""

  try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    text = response.text

    # Parse response
    lines = text.strip().split('\n')
    summary = ""
    personality = ""
    compatibility = ""
    starters = []

    current_section = None
    for line in lines:
      line = line.strip()
      if line.startswith("SUMMARY:"):
        current_section = "summary"
        summary = line.replace("SUMMARY:", "").strip()
      elif line.startswith("PERSONALITY:"):
        current_section = "personality"
        personality = line.replace("PERSONALITY:", "").strip()
      elif line.startswith("COMPATIBILITY:"):
        current_section = "compatibility"
        compatibility = line.replace("COMPATIBILITY:", "").strip()
      elif line.startswith("STARTERS:"):
        current_section = "starters"
      elif line.startswith("-") and current_section == "starters":
        starters.append(line.lstrip("- ").strip())
      elif current_section and line:
        if current_section == "summary":
          summary += " " + line
        elif current_section == "personality":
          personality += " " + line
        elif current_section == "compatibility":
          compatibility += " " + line

    return AIOverviewResponse(
      summary=summary.strip(),
      personality_insights=personality.strip(),
      compatibility_notes=compatibility.strip(),
      conversation_starters=starters[:3]
    )

  except Exception as exc:
    logger.error(f"AI overview generation failed: {exc}")
    raise HTTPException(status_code=500, detail=f"AI generation failed: {str(exc)}") from exc


@app.post("/api/draft-message", response_model=DraftMessageResponse)
async def draft_message(request: DraftMessageRequest) -> DraftMessageResponse:
  """Generate an AI-drafted message for LinkedIn DMs."""
  if not GEMINI_API_KEY:
    raise HTTPException(status_code=503, detail="AI service not configured")

  recipient = request.recipient

  tone_instructions = {
    "flirty": "Write in a playful, charming, and subtly flirty tone. Be confident but not aggressive.",
    "polite": "Write in a respectful, professional, and courteous tone. Be warm and friendly.",
    "direct": "Write in a straightforward, honest, and confident tone. Get to the point quickly.",
    "professional": "Write in a business-appropriate, respectful, and formal tone.",
    "casual": "Write in a friendly, relaxed, and approachable tone. Be conversational.",
    "witty": "Write with clever humor, wordplay, and engaging wit. Be memorable and fun."
  }

  message_type_instructions = {
    "cold_dm": "This is a first message to someone you haven't matched with or talked to before. Make it engaging and give them a reason to respond.",
    "warm_dm": "This is a message to someone you've matched with or have mutual interest. Be more personal and reference shared interests.",
    "follow_up": "This is a follow-up message to continue a conversation. Build on previous context."
  }

  context_part = f"\nAdditional context: {request.context}" if request.context else ""

  prompt = f"""Draft a LinkedIn direct message with these parameters:

RECIPIENT PROFILE:
Name: {recipient.name}
Title/Major: {recipient.major or 'Not specified'}
Company: {recipient.company or 'Not specified'}
Bio: {recipient.bio or 'Not specified'}
Location: {recipient.location or 'Not specified'}
Interests: {', '.join(recipient.interests) if recipient.interests else 'Not specified'}

TONE: {request.tone.upper()}
{tone_instructions[request.tone]}

MESSAGE TYPE: {request.message_type.upper()}
{message_type_instructions[request.message_type]}{context_part}

Requirements:
- Keep it under 150 words
- Make it personalized based on their profile
- Appropriate for LinkedIn networking with romantic interest
- Include a clear call-to-action or question
- Don't be creepy or overly forward
- Sound natural and authentic

Write ONLY the message, no explanations or meta-commentary."""

  try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    message = response.text.strip()

    # Clean up any markdown formatting or quotes
    message = message.replace('**', '').replace('*', '').strip('"\'')

    return DraftMessageResponse(
      message=message,
      tone=request.tone
    )

  except Exception as exc:
    logger.error(f"Message drafting failed: {exc}")
    raise HTTPException(status_code=500, detail=f"AI generation failed: {str(exc)}") from exc


@app.post("/api/satirical-insights", response_model=SatiricalInsightResponse)
async def get_satirical_insights(request: SatiricalInsightRequest) -> SatiricalInsightResponse:
  """Generate funny, satirical 'probably...' observations about a profile."""
  if not GEMINI_API_KEY:
    raise HTTPException(status_code=503, detail="AI service not configured")

  profile = request.profile

  prompt = f"""Generate 5 funny, satirical "probably..." observations about this LinkedIn profile.
Make them humorous but not mean-spirited. They can be playfully teasing or absurdly random.

Profile:
Name: {profile.name}
Title/Major: {profile.major or 'Not specified'}
Company: {profile.company or 'Not specified'}
Bio: {profile.bio or 'Not specified'}
Interests: {', '.join(profile.interests) if profile.interests else 'Not specified'}

Examples of the style:
- "Probably has 17 different coffee subscriptions"
- "Definitely uses 'synergy' in conversations unironically"
- "Most likely owns a standing desk they never actually stand at"
- "Probably organized their spice rack alphabetically during quarantine"

Generate 5 observations starting with "Probably..." or "Definitely...". Each should be one line.
Make them specific to this person's profile when possible, but keep them lighthearted and fun."""

  try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Parse lines starting with "Probably" or "Definitely"
    insights = []
    for line in text.split('\n'):
      line = line.strip().lstrip('-•* ').strip()
      if line.lower().startswith(('probably', 'definitely', 'likely', 'most likely')):
        insights.append(line)

    # Fallback if parsing failed
    if not insights:
      insights = [line.strip().lstrip('-•* ').strip() for line in text.split('\n') if line.strip()]

    return SatiricalInsightResponse(insights=insights[:5])

  except Exception as exc:
    logger.error(f"Satirical insights generation failed: {exc}")
    raise HTTPException(status_code=500, detail=f"AI generation failed: {str(exc)}") from exc


@app.post("/api/find-socials", response_model=FindSocialsResponse)
async def find_social_profiles(request: FindSocialsRequest) -> FindSocialsResponse:
  """Search for social media profiles based on name and context."""
  # This is a placeholder implementation
  # In a real app, you'd use APIs like:
  # - Clearbit API for professional profiles
  # - Hunter.io for email/social links
  # - Custom web scraping (carefully, respecting robots.txt)

  name = request.name.lower().replace(" ", "")

  # Generate likely profile URLs based on common patterns
  # These are GUESSES - not verified
  potential_profiles = [
    SocialProfile(
      platform="Twitter/X",
      url=f"https://twitter.com/{name}",
      confidence="low"
    ),
    SocialProfile(
      platform="GitHub",
      url=f"https://github.com/{name}",
      confidence="low"
    ),
    SocialProfile(
      platform="Instagram",
      url=f"https://instagram.com/{name}",
      confidence="low"
    )
  ]

  # Note: This is a basic implementation
  # For production, integrate with actual search APIs
  logger.info(f"Generated potential social profiles for {request.name}")

  return FindSocialsResponse(profiles=potential_profiles)

