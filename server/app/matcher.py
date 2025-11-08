"""
GoonedIn Backend - Matching Engine
Implements compatibility matching algorithm
"""

from typing import List, Tuple, Optional
from models import Profile, Match


class MatchingEngine:
    """Engine for matching profiles based on compatibility"""
    
    def __init__(self):
        self.match_types = {
            'work_life_balance': 'Work-Life Balance Match',
            'ambition': 'Ambition Match',
            'industry': 'Industry Match',
            'skills': 'Skills Match',
            'goals': 'Goals Match',
            'schedule': 'Schedule Match'
        }
    
    def calculate_compatibility_score(
        self,
        profile1: Profile,
        profile2: Profile
    ) -> Tuple[float, List[str], str]:
        """
        Calculate compatibility score between two profiles
        Returns: (score, reasons, match_type)
        """
        score = 0.0
        reasons = []
        max_score = 0.0
        
        # Work-life priority match (high weight)
        if profile1.work_life_priority == profile2.work_life_priority:
            weight = 25.0
            score += weight
            reasons.append(f"Both prioritize {profile1.work_life_priority} work-life balance")
        max_score += 25.0
        
        # Ambition level similarity (high weight)
        ambition_diff = abs(profile1.ambition_level - profile2.ambition_level)
        ambition_score = max(0, 20.0 - (ambition_diff * 5.0))
        score += ambition_score
        if ambition_score > 15:
            reasons.append("Similar ambition levels")
        max_score += 20.0
        
        # Industry match (medium weight)
        if profile1.industry == profile2.industry:
            weight = 15.0
            score += weight
            reasons.append(f"Same industry: {profile1.industry}")
        max_score += 15.0
        
        # Schedule compatibility (medium weight)
        if profile1.schedule == profile2.schedule:
            weight = 15.0
            score += weight
            reasons.append(f"Compatible schedules: {profile1.schedule}")
        max_score += 15.0
        
        # Skills overlap (medium weight)
        common_skills = set(profile1.skills) & set(profile2.skills)
        if common_skills:
            skills_score = min(15.0, len(common_skills) * 3.0)
            score += skills_score
            reasons.append(f"Shared skills: {', '.join(list(common_skills)[:3])}")
        max_score += 15.0
        
        # Goals overlap (low weight)
        common_goals = set(profile1.goals) & set(profile2.goals)
        if common_goals:
            goals_score = min(10.0, len(common_goals) * 2.0)
            score += goals_score
            reasons.append(f"Shared goals: {', '.join(list(common_goals)[:2])}")
        max_score += 10.0
        
        # Normalize score to 0-100
        normalized_score = (score / max_score * 100) if max_score > 0 else 0
        
        # Determine match type
        match_type = self._determine_match_type(profile1, profile2, reasons)
        
        return round(normalized_score, 1), reasons, match_type
    
    def _determine_match_type(
        self,
        profile1: Profile,
        profile2: Profile,
        reasons: List[str]
    ) -> str:
        """Determine the primary match type"""
        if profile1.work_life_priority == profile2.work_life_priority:
            return self.match_types['work_life_balance']
        elif abs(profile1.ambition_level - profile2.ambition_level) <= 1:
            return self.match_types['ambition']
        elif profile1.industry == profile2.industry:
            return self.match_types['industry']
        elif set(profile1.skills) & set(profile2.skills):
            return self.match_types['skills']
        elif set(profile1.goals) & set(profile2.goals):
            return self.match_types['goals']
        elif profile1.schedule == profile2.schedule:
            return self.match_types['schedule']
        else:
            return 'General Match'
    
    def find_matches(
        self,
        profile: Profile,
        all_profiles: List[Profile],
        max_results: int = 20
    ) -> List[Tuple[Profile, float, List[str], str]]:
        """
        Find matches for a profile
        Returns: List of (profile, score, reasons, match_type) tuples
        """
        matches = []
        
        for other_profile in all_profiles:
            # Skip self
            if other_profile.profile_id == profile.profile_id:
                continue
            
            # Skip if already passed
            if other_profile.profile_id in profile.passes:
                continue
            
            # Skip if already liked (unless we want to show mutual likes)
            # if other_profile.profile_id in profile.likes:
            #     continue
            
            # Calculate compatibility
            score, reasons, match_type = self.calculate_compatibility_score(
                profile,
                other_profile
            )
            
            matches.append((other_profile, score, reasons, match_type))
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N matches
        return matches[:max_results]
    
    def create_mutual_match(
        self,
        profile1: Profile,
        profile2: Profile
    ) -> Match:
        """Create a mutual match between two profiles"""
        score, reasons, match_type = self.calculate_compatibility_score(
            profile1,
            profile2
        )
        
        match = Match(
            profile1_id=profile1.profile_id,
            profile2_id=profile2.profile_id,
            compatibility_score=score,
            reasons=reasons,
            match_type=match_type
        )
        
        return match


