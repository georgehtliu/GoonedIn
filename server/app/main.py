from contextlib import asynccontextmanager
from typing import AsyncIterator, Literal
import base64
import uuid

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

HUGGINGFACE_ENDPOINT = "https://thwanx-beautyrate.hf.space/api/predict"
DEFAULT_FN_INDEX = 0


class BeautyScoreResponse(BaseModel):
  raw: dict


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
  gender: Literal["woman", "man"] = Form("woman")
) -> BeautyScoreResponse:
  if image.content_type not in {"image/jpeg", "image/png"}:
    raise HTTPException(status_code=400, detail="Only JPEG or PNG images are supported.")

  image_bytes = await image.read()
  data_url = f"data:{image.content_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
  payload = {
    "data": [data_url, gender],
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

  return BeautyScoreResponse(raw=response.json())

