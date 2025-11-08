"""
GoonedIn Backend - FastAPI Application
Main application file with all API endpoints
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from typing import List, Dict, Any

from config import Config
from models import Profile, Match, DataStore
from matcher import MatchingEngine
from perplexity_service import PerplexityService
from schemas import (
    ProfileCreate, ProfileResponse, ProfileListResponse, ProfileCreateResponse,
    FindMatchesRequest, MatchResult, FindMatchesResponse,
    LikeRequest, MatchResponse, LikeResponse,
    PassRequest, PassResponse,
    MatchDetailResponse, ProfileMatchesResponse,
    CompatibilityReportResponse,
    GenerateSamplesRequest, GenerateSamplesResponse,
    StatsResponse, HealthResponse, ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="GoonedIn API",
    description="Professional networking and matching platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_store = DataStore(Config.DATA_DIR)
matcher = MatchingEngine()
perplexity = PerplexityService(Config.PERPLEXITY_API_KEY)

# Ensure data directory exists on startup
@app.on_event("startup")
async def startup_event():
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    print("=" * 50)
    print("GoonedIn Backend Starting...")
    print("=" * 50)
    print(f"Data directory: {Config.DATA_DIR}")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"Perplexity API configured: {bool(Config.PERPLEXITY_API_KEY)}")
    print("=" * 50)

# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@app.post('/api/profile/create', response_model=ProfileCreateResponse, status_code=status.HTTP_201_CREATED)
def create_profile(profile_data: ProfileCreate):
    """Create a new profile"""
    try:
        # Create profile
        profile = Profile(
            name=profile_data.name,
            age=profile_data.age,
            job_title=profile_data.job_title,
            industry=profile_data.industry,
            schedule=profile_data.schedule,
            ambition_level=profile_data.ambition_level,
            stress_level=profile_data.stress_level,
            work_life_priority=profile_data.work_life_priority,
            skills=profile_data.skills,
            goals=profile_data.goals,
            bio=profile_data.bio,
            looking_for=profile_data.looking_for
        )
        
        # Save profile
        data_store.save_profile(profile)
        
        return ProfileCreateResponse(
            success=True,
            profile=ProfileResponse(**profile.to_dict()),
            message='Profile created successfully!'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/profiles', response_model=ProfileListResponse)
def get_all_profiles():
    """Get all profiles"""
    try:
        profiles = data_store.get_all_profiles()
        return ProfileListResponse(
            success=True,
            profiles=[ProfileResponse(**p.to_dict()) for p in profiles],
            count=len(profiles)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/profile/{profile_id}', response_model=Dict[str, Any])
def get_profile(profile_id: str):
    """Get a specific profile"""
    try:
        profile = data_store.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail='Profile not found')
        
        return {
            'success': True,
            'profile': profile.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/api/profile/{profile_id}', response_model=Dict[str, Any])
def delete_profile(profile_id: str):
    """Delete a profile"""
    try:
        data_store.delete_profile(profile_id)
        return {
            'success': True,
            'message': 'Profile deleted successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MATCHING ENDPOINTS
# ============================================================================

@app.post('/api/match/find', response_model=FindMatchesResponse)
def find_matches(request: FindMatchesRequest):
    """Find matches for a profile"""
    try:
        profile_id = request.profile_id
        max_results = request.max_results or Config.MAX_MATCHES_PER_REQUEST
        
        # Get the profile
        profile = data_store.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail='Profile not found')
        
        # Get all other profiles
        all_profiles = data_store.get_all_profiles()
        
        # Find matches
        matches = matcher.find_matches(profile, all_profiles, max_results)
        
        # Format response
        match_results = []
        for match_profile, score, reasons, match_type in matches:
            match_results.append(MatchResult(
                profile=ProfileResponse(**match_profile.to_dict()),
                compatibility_score=score,
                reasons=reasons,
                match_type=match_type
            ))
        
        return FindMatchesResponse(
            success=True,
            matches=match_results,
            count=len(match_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/match/like', response_model=LikeResponse)
def like_profile(request: LikeRequest):
    """Like a profile"""
    try:
        liker_id = request.liker_id
        liked_id = request.liked_id
        
        # Get both profiles
        liker = data_store.get_profile(liker_id)
        liked = data_store.get_profile(liked_id)
        
        if not liker or not liked:
            raise HTTPException(status_code=404, detail='One or both profiles not found')
        
        # Add to likes
        if liked_id not in liker.likes:
            liker.likes.append(liked_id)
            data_store.save_profile(liker)
        
        # Check if it's a mutual match
        is_match = liker_id in liked.likes
        
        if is_match:
            # Create mutual match
            match = matcher.create_mutual_match(liker, liked)
            
            # Generate conversation starters
            starters = perplexity.generate_conversation_starters(
                liker.to_dict(),
                liked.to_dict()
            )
            match.conversation_starters = starters
            
            # Save match
            data_store.save_match(match)
            
            # Add to both profiles' matches
            if match.match_id not in liker.matches:
                liker.matches.append(match.match_id)
                data_store.save_profile(liker)
            
            if match.match_id not in liked.matches:
                liked.matches.append(match.match_id)
                data_store.save_profile(liked)
            
            return LikeResponse(
                success=True,
                is_match=True,
                match=MatchResponse(**match.to_dict()),
                message="It's a match! 🎉"
            )
        
        return LikeResponse(
            success=True,
            is_match=False,
            message='Profile liked successfully'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/match/pass', response_model=PassResponse)
def pass_profile(request: PassRequest):
    """Pass on a profile"""
    try:
        passer_id = request.passer_id
        passed_id = request.passed_id
        
        # Get profile
        passer = data_store.get_profile(passer_id)
        if not passer:
            raise HTTPException(status_code=404, detail='Profile not found')
        
        # Add to passes
        if passed_id not in passer.passes:
            passer.passes.append(passed_id)
            data_store.save_profile(passer)
        
        return PassResponse(
            success=True,
            message='Profile passed'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MATCH DETAILS ENDPOINTS
# ============================================================================

@app.get('/api/match/{match_id}', response_model=MatchDetailResponse)
def get_match(match_id: str):
    """Get match details"""
    try:
        match = data_store.get_match(match_id)
        if not match:
            raise HTTPException(status_code=404, detail='Match not found')
        
        # Get both profiles
        profile1 = data_store.get_profile(match.profile1_id)
        profile2 = data_store.get_profile(match.profile2_id)
        
        return MatchDetailResponse(
            success=True,
            match=MatchResponse(**match.to_dict()),
            profile1=ProfileResponse(**profile1.to_dict()) if profile1 else None,
            profile2=ProfileResponse(**profile2.to_dict()) if profile2 else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/matches/{profile_id}', response_model=ProfileMatchesResponse)
def get_profile_matches(profile_id: str):
    """Get all matches for a profile"""
    try:
        profile = data_store.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail='Profile not found')
        
        matches = data_store.get_matches_for_profile(profile_id)
        
        # Get details for each match
        match_details = []
        for match in matches:
            # Determine which profile is the "other" one
            other_profile_id = match.profile2_id if match.profile1_id == profile_id else match.profile1_id
            other_profile = data_store.get_profile(other_profile_id)
            
            match_details.append({
                'match': match.to_dict(),
                'other_profile': other_profile.to_dict() if other_profile else None
            })
        
        return ProfileMatchesResponse(
            success=True,
            matches=match_details,
            count=len(match_details)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/compatibility/{match_id}', response_model=CompatibilityReportResponse)
def get_compatibility_report(match_id: str):
    """Get or generate compatibility report for a match"""
    try:
        match = data_store.get_match(match_id)
        if not match:
            raise HTTPException(status_code=404, detail='Match not found')
        
        # If report already exists, return it
        if match.compatibility_report:
            return CompatibilityReportResponse(
                success=True,
                report=match.compatibility_report
            )
        
        # Generate new report
        profile1 = data_store.get_profile(match.profile1_id)
        profile2 = data_store.get_profile(match.profile2_id)
        
        if not profile1 or not profile2:
            raise HTTPException(status_code=404, detail='One or both profiles not found')
        
        report = perplexity.generate_compatibility_report(
            profile1.to_dict(),
            profile2.to_dict(),
            match.compatibility_score,
            match.reasons
        )
        
        # Save report
        match.compatibility_report = report
        data_store.save_match(match)
        
        return CompatibilityReportResponse(
            success=True,
            report=report
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.post('/api/generate-samples', response_model=GenerateSamplesResponse, status_code=status.HTTP_201_CREATED)
def generate_sample_profiles(request: GenerateSamplesRequest):
    """Generate sample profiles using Perplexity"""
    try:
        count = request.count
        
        # Generate profiles
        sample_data = perplexity.generate_sample_profiles(count)
        
        profiles = []
        for profile_data in sample_data:
            profile = Profile(
                name=profile_data['name'],
                age=profile_data['age'],
                job_title=profile_data['job_title'],
                industry=profile_data['industry'],
                schedule=profile_data['schedule'],
                ambition_level=profile_data['ambition_level'],
                stress_level=profile_data['stress_level'],
                work_life_priority=profile_data['work_life_priority'],
                skills=profile_data['skills'],
                goals=profile_data['goals'],
                bio=profile_data['bio'],
                looking_for=profile_data['looking_for']
            )
            data_store.save_profile(profile)
            profiles.append(ProfileResponse(**profile.to_dict()))
        
        return GenerateSamplesResponse(
            success=True,
            profiles=profiles,
            count=len(profiles),
            message=f'{len(profiles)} sample profiles generated!'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/stats', response_model=StatsResponse)
def get_stats():
    """Get app statistics"""
    try:
        profiles = data_store.get_all_profiles()
        
        # Calculate stats
        total_profiles = len(profiles)
        total_likes = sum(len(p.likes) for p in profiles)
        
        # Get all matches (avoid double counting)
        all_match_ids = set()
        for p in profiles:
            all_match_ids.update(p.matches)
        total_matches = len(all_match_ids)
        
        # Industry breakdown
        industry_counts = {}
        for p in profiles:
            industry_counts[p.industry] = industry_counts.get(p.industry, 0) + 1
        
        # Average compatibility
        all_matches = []
        for match_id in all_match_ids:
            match = data_store.get_match(match_id)
            if match:
                all_matches.append(match)
        
        avg_compatibility = sum(m.compatibility_score for m in all_matches) / len(all_matches) if all_matches else 0
        
        return StatsResponse(
            success=True,
            stats={
                'total_profiles': total_profiles,
                'total_likes': total_likes,
                'total_matches': total_matches,
                'industry_breakdown': industry_counts,
                'average_compatibility': round(avg_compatibility, 1)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/health', response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status='healthy',
        timestamp=datetime.now().isoformat(),
        version='1.0.0',
        message='Server is running'
    )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={'error': 'Endpoint not found'}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={'error': 'Internal server error'}
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=Config.DEBUG
    )
