"""
GoonedIn Backend - Data Models
Defines Profile, Match, and DataStore classes
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class Profile:
    """User profile model"""
    
    def __init__(
        self,
        name: str,
        age: int,
        job_title: str,
        industry: str,
        schedule: str,
        ambition_level: int,
        stress_level: int,
        work_life_priority: str,
        skills: List[str],
        goals: List[str],
        bio: str,
        looking_for: str,
        profile_id: Optional[str] = None,
        likes: Optional[List[str]] = None,
        passes: Optional[List[str]] = None,
        matches: Optional[List[str]] = None,
        created_at: Optional[str] = None
    ):
        self.profile_id = profile_id or str(uuid.uuid4())
        self.name = name
        self.age = age
        self.job_title = job_title
        self.industry = industry
        self.schedule = schedule
        self.ambition_level = ambition_level
        self.stress_level = stress_level
        self.work_life_priority = work_life_priority
        self.skills = skills or []
        self.goals = goals or []
        self.bio = bio
        self.looking_for = looking_for
        self.likes = likes or []
        self.passes = passes or []
        self.matches = matches or []
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary"""
        return {
            'profile_id': self.profile_id,
            'name': self.name,
            'age': self.age,
            'job_title': self.job_title,
            'industry': self.industry,
            'schedule': self.schedule,
            'ambition_level': self.ambition_level,
            'stress_level': self.stress_level,
            'work_life_priority': self.work_life_priority,
            'skills': self.skills,
            'goals': self.goals,
            'bio': self.bio,
            'looking_for': self.looking_for,
            'likes': self.likes,
            'passes': self.passes,
            'matches': self.matches,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Profile':
        """Create profile from dictionary"""
        return cls(
            profile_id=data.get('profile_id'),
            name=data['name'],
            age=data['age'],
            job_title=data['job_title'],
            industry=data['industry'],
            schedule=data['schedule'],
            ambition_level=data['ambition_level'],
            stress_level=data['stress_level'],
            work_life_priority=data['work_life_priority'],
            skills=data.get('skills', []),
            goals=data.get('goals', []),
            bio=data['bio'],
            looking_for=data['looking_for'],
            likes=data.get('likes', []),
            passes=data.get('passes', []),
            matches=data.get('matches', []),
            created_at=data.get('created_at')
        )


class Match:
    """Match model for mutual matches"""
    
    def __init__(
        self,
        profile1_id: str,
        profile2_id: str,
        match_id: Optional[str] = None,
        compatibility_score: Optional[float] = None,
        reasons: Optional[List[str]] = None,
        match_type: Optional[str] = None,
        compatibility_report: Optional[str] = None,
        conversation_starters: Optional[List[str]] = None,
        created_at: Optional[str] = None
    ):
        self.match_id = match_id or str(uuid.uuid4())
        self.profile1_id = profile1_id
        self.profile2_id = profile2_id
        self.compatibility_score = compatibility_score
        self.reasons = reasons or []
        self.match_type = match_type
        self.compatibility_report = compatibility_report
        self.conversation_starters = conversation_starters or []
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert match to dictionary"""
        return {
            'match_id': self.match_id,
            'profile1_id': self.profile1_id,
            'profile2_id': self.profile2_id,
            'compatibility_score': self.compatibility_score,
            'reasons': self.reasons,
            'match_type': self.match_type,
            'compatibility_report': self.compatibility_report,
            'conversation_starters': self.conversation_starters,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Match':
        """Create match from dictionary"""
        return cls(
            match_id=data.get('match_id'),
            profile1_id=data['profile1_id'],
            profile2_id=data['profile2_id'],
            compatibility_score=data.get('compatibility_score'),
            reasons=data.get('reasons', []),
            match_type=data.get('match_type'),
            compatibility_report=data.get('compatibility_report'),
            conversation_starters=data.get('conversation_starters', []),
            created_at=data.get('created_at')
        )


class DataStore:
    """Simple file-based data store"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.profiles_dir = os.path.join(data_dir, 'profiles')
        self.matches_dir = os.path.join(data_dir, 'matches')
        
        # Create directories if they don't exist
        os.makedirs(self.profiles_dir, exist_ok=True)
        os.makedirs(self.matches_dir, exist_ok=True)
    
    def _get_profile_path(self, profile_id: str) -> str:
        """Get file path for a profile"""
        return os.path.join(self.profiles_dir, f'{profile_id}.json')
    
    def _get_match_path(self, match_id: str) -> str:
        """Get file path for a match"""
        return os.path.join(self.matches_dir, f'{match_id}.json')
    
    def save_profile(self, profile: Profile):
        """Save a profile to disk"""
        file_path = self._get_profile_path(profile.profile_id)
        with open(file_path, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
    
    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Get a profile by ID"""
        file_path = self._get_profile_path(profile_id)
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            return Profile.from_dict(data)
    
    def get_all_profiles(self) -> List[Profile]:
        """Get all profiles"""
        profiles = []
        if not os.path.exists(self.profiles_dir):
            return profiles
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                profile_id = filename[:-5]  # Remove .json extension
                profile = self.get_profile(profile_id)
                if profile:
                    profiles.append(profile)
        
        return profiles
    
    def delete_profile(self, profile_id: str):
        """Delete a profile"""
        file_path = self._get_profile_path(profile_id)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def save_match(self, match: Match):
        """Save a match to disk"""
        file_path = self._get_match_path(match.match_id)
        with open(file_path, 'w') as f:
            json.dump(match.to_dict(), f, indent=2)
    
    def get_match(self, match_id: str) -> Optional[Match]:
        """Get a match by ID"""
        file_path = self._get_match_path(match_id)
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            return Match.from_dict(data)
    
    def get_matches_for_profile(self, profile_id: str) -> List[Match]:
        """Get all matches for a profile"""
        matches = []
        if not os.path.exists(self.matches_dir):
            return matches
        
        for filename in os.listdir(self.matches_dir):
            if filename.endswith('.json'):
                match_id = filename[:-5]  # Remove .json extension
                match = self.get_match(match_id)
                if match and (match.profile1_id == profile_id or match.profile2_id == profile_id):
                    matches.append(match)
        
        return matches


