"""
GoonedIn Backend - Pydantic Schemas
Request and response models for FastAPI
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# Profile Schemas
class ProfileCreate(BaseModel):
    name: str
    age: int
    job_title: str
    industry: str
    schedule: str
    ambition_level: int = Field(ge=1, le=10)
    stress_level: int = Field(ge=1, le=10)
    work_life_priority: str
    skills: List[str]
    goals: List[str]
    bio: str
    looking_for: str


class ProfileResponse(BaseModel):
    profile_id: str
    name: str
    age: int
    job_title: str
    industry: str
    schedule: str
    ambition_level: int
    stress_level: int
    work_life_priority: str
    skills: List[str]
    goals: List[str]
    bio: str
    looking_for: str
    likes: List[str]
    passes: List[str]
    matches: List[str]
    created_at: str


class ProfileListResponse(BaseModel):
    success: bool
    profiles: List[ProfileResponse]
    count: int


class ProfileCreateResponse(BaseModel):
    success: bool
    profile: ProfileResponse
    message: str


# Match Schemas
class FindMatchesRequest(BaseModel):
    profile_id: str
    max_results: Optional[int] = 20


class MatchResult(BaseModel):
    profile: ProfileResponse
    compatibility_score: float
    reasons: List[str]
    match_type: str


class FindMatchesResponse(BaseModel):
    success: bool
    matches: List[MatchResult]
    count: int


class LikeRequest(BaseModel):
    liker_id: str
    liked_id: str


class MatchResponse(BaseModel):
    match_id: str
    profile1_id: str
    profile2_id: str
    compatibility_score: Optional[float]
    reasons: List[str]
    match_type: Optional[str]
    compatibility_report: Optional[str]
    conversation_starters: List[str]
    created_at: str


class LikeResponse(BaseModel):
    success: bool
    is_match: bool
    match: Optional[MatchResponse] = None
    message: str


class PassRequest(BaseModel):
    passer_id: str
    passed_id: str


class PassResponse(BaseModel):
    success: bool
    message: str


class MatchDetailResponse(BaseModel):
    success: bool
    match: MatchResponse
    profile1: Optional[ProfileResponse]
    profile2: Optional[ProfileResponse]


class ProfileMatchesResponse(BaseModel):
    success: bool
    matches: List[Dict[str, Any]]
    count: int


class CompatibilityReportResponse(BaseModel):
    success: bool
    report: str


class GenerateSamplesRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=50)


class GenerateSamplesResponse(BaseModel):
    success: bool
    profiles: List[ProfileResponse]
    count: int
    message: str


class StatsResponse(BaseModel):
    success: bool
    stats: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str

