import base64
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Literal
import logging

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gender_guesser import detector as gender_detector

HUGGINGFACE_ENDPOINT = "https://thwanx-beautyrate.hf.space/api/predict"
DEFAULT_FN_INDEX = 0
_gender_detector = gender_detector.Detector(case_sensitive=False)
logger = logging.getLogger(__name__)


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


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
  # Add startup/shutdown hooks here (e.g., DB connections, clients)
  yield


app = FastAPI(
  title="LinkedIn Baddie Finder API",
  version="0.1.0",
  lifespan=lifespan
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5176",
    "http://localhost:5176"
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)


@app.get("/health")
async def read_health() -> dict[str, str]:
  return {"message": "Service is healthy"}


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

