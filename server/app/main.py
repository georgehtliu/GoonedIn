import base64
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator, Literal

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gender_guesser import detector as gender_detector

HUGGINGFACE_ENDPOINT = "https://thwanx-beautyrate.hf.space/api/predict"
DEFAULT_FN_INDEX = 0
_gender_detector = gender_detector.Detector(case_sensitive=False)


class BeautyScoreResponse(BaseModel):
  raw: dict
  gender: Literal["woman", "man"]


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
  allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
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

  return BeautyScoreResponse(raw=response.json(), gender=resolved_gender)

