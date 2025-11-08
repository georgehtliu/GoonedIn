"""
GoonedIn Backend - Perplexity AI Service
Handles AI-powered features using Perplexity API
"""

import json
import requests
from typing import List, Dict, Optional


class PerplexityService:
    """Service for interacting with Perplexity AI API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, messages: List[Dict], model: str = "llama-3.1-sonar-small-128k-online") -> Optional[str]:
        """Make a request to Perplexity API"""
        if not self.api_key:
            return None
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
            else:
                print(f"Perplexity API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Perplexity API: {str(e)}")
            return None
    
    def generate_conversation_starters(
        self,
        profile1: Dict,
        profile2: Dict
    ) -> List[str]:
        """Generate conversation starters for a match"""
        prompt = f"""Generate 3-5 engaging conversation starters for two professionals who just matched on a networking platform.

Profile 1:
- Name: {profile1.get('name')}
- Job: {profile1.get('job_title')} in {profile1.get('industry')}
- Bio: {profile1.get('bio')}
- Skills: {', '.join(profile1.get('skills', [])[:5])}
- Goals: {', '.join(profile1.get('goals', [])[:3])}

Profile 2:
- Name: {profile2.get('name')}
- Job: {profile2.get('job_title')} in {profile2.get('industry')}
- Bio: {profile2.get('bio')}
- Skills: {', '.join(profile2.get('skills', [])[:5])}
- Goals: {', '.join(profile2.get('goals', [])[:3])}

Return ONLY a JSON array of strings, each string being a conversation starter. Be specific, engaging, and reference their common interests or complementary skills. No additional text, just the JSON array.
Example format: ["Hello! I noticed you're also interested in...", "Hey! Your background in... caught my attention"]
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates professional conversation starters for networking platforms. Always return valid JSON arrays."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages)
        
        if response:
            try:
                # Try to extract JSON from response
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.startswith('```'):
                    response = response[3:]
                if response.endswith('```'):
                    response = response[:-3]
                response = response.strip()
                
                starters = json.loads(response)
                if isinstance(starters, list):
                    return starters[:5]  # Return max 5 starters
            except json.JSONDecodeError:
                # Fallback: return default starters
                pass
        
        # Default fallback starters
        return [
            f"Hi {profile2.get('name')}! I noticed we have similar interests in {profile1.get('industry')}.",
            f"Hey! Your background in {', '.join(profile2.get('skills', [])[:2])} sounds interesting.",
            f"Hello! I'd love to connect and learn more about your experience in {profile2.get('industry')}."
        ]
    
    def generate_compatibility_report(
        self,
        profile1: Dict,
        profile2: Dict,
        compatibility_score: float,
        reasons: List[str]
    ) -> str:
        """Generate a detailed compatibility report"""
        prompt = f"""Generate a detailed, professional compatibility report for two professionals who matched on a networking platform.

Profile 1:
- Name: {profile1.get('name')}
- Age: {profile1.get('age')}
- Job: {profile1.get('job_title')} in {profile1.get('industry')}
- Bio: {profile1.get('bio')}
- Skills: {', '.join(profile1.get('skills', []))}
- Goals: {', '.join(profile1.get('goals', []))}
- Work-life priority: {profile1.get('work_life_priority')}
- Ambition level: {profile1.get('ambition_level')}/10

Profile 2:
- Name: {profile2.get('name')}
- Age: {profile2.get('age')}
- Job: {profile2.get('job_title')} in {profile2.get('industry')}
- Bio: {profile2.get('bio')}
- Skills: {', '.join(profile2.get('skills', []))}
- Goals: {', '.join(profile2.get('goals', []))}
- Work-life priority: {profile2.get('work_life_priority')}
- Ambition level: {profile2.get('ambition_level')}/10

Compatibility Score: {compatibility_score}/100
Key Reasons: {', '.join(reasons)}

Generate a 3-4 paragraph compatibility report that:
1. Highlights their complementary strengths
2. Explains why they're a good match
3. Suggests potential collaboration opportunities
4. Provides insights on how they can benefit each other

Be professional, insightful, and encouraging.
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional networking and career development advisor. Write clear, professional compatibility reports."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages, model="llama-3.1-sonar-large-128k-online")
        
        if response:
            return response.strip()
        
        # Fallback report
        return f"""
Compatibility Report for {profile1.get('name')} and {profile2.get('name')}

These two professionals show strong potential for a valuable networking connection with a compatibility score of {compatibility_score}/100.

{' '.join(reasons)}

Both individuals bring unique strengths to the table. {profile1.get('name')} brings expertise in {profile1.get('industry')}, while {profile2.get('name')} offers complementary skills in {profile2.get('industry')}. Their shared values around {profile1.get('work_life_priority')} work-life balance create a solid foundation for meaningful professional interactions.

Potential collaboration opportunities could arise from their overlapping interests in {', '.join(set(profile1.get('skills', [])) & set(profile2.get('skills', [])) or ['professional development'])}. They may benefit from sharing insights, exploring joint projects, or simply expanding their professional networks within similar domains.

This match presents an opportunity for mutual growth and knowledge exchange in their respective fields.
""".strip()
    
    def generate_sample_profiles(self, count: int = 10) -> List[Dict]:
        """Generate sample profiles using AI"""
        prompt = f"""Generate {count} diverse, realistic professional profiles for a networking platform. Each profile should include:
- name (first name only)
- age (25-55)
- job_title (realistic job title)
- industry (tech, finance, healthcare, marketing, consulting, etc.)
- schedule (flexible, standard, busy, remote)
- ambition_level (1-10)
- stress_level (1-10)
- work_life_priority (work-focused, balanced, life-focused)
- skills (array of 3-5 skills)
- goals (array of 2-3 career goals)
- bio (2-3 sentences)
- looking_for (what they're looking for in connections)

Return ONLY a valid JSON array of objects. No additional text. Make profiles diverse in industries, ages, and career stages.
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates realistic professional profiles. Always return valid JSON arrays."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages)
        
        if response:
            try:
                # Try to extract JSON from response
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.startswith('```'):
                    response = response[3:]
                if response.endswith('```'):
                    response = response[:-3]
                response = response.strip()
                
                profiles = json.loads(response)
                if isinstance(profiles, list):
                    return profiles[:count]
            except json.JSONDecodeError:
                pass
        
        # Fallback: return hardcoded sample profiles
        return self._get_fallback_profiles(count)
    
    def _get_fallback_profiles(self, count: int) -> List[Dict]:
        """Fallback sample profiles if AI generation fails"""
        fallback_profiles = [
            {
                "name": "Alex",
                "age": 28,
                "job_title": "Software Engineer",
                "industry": "Technology",
                "schedule": "flexible",
                "ambition_level": 8,
                "stress_level": 6,
                "work_life_priority": "balanced",
                "skills": ["Python", "React", "AWS", "Docker"],
                "goals": ["Lead a team", "Build scalable products"],
                "bio": "Passionate software engineer with 5 years of experience building web applications. Love solving complex problems and learning new technologies.",
                "looking_for": "Tech professionals to collaborate on projects and share knowledge"
            },
            {
                "name": "Jordan",
                "age": 32,
                "job_title": "Product Manager",
                "industry": "Technology",
                "schedule": "standard",
                "ambition_level": 7,
                "stress_level": 7,
                "work_life_priority": "balanced",
                "skills": ["Product Strategy", "Agile", "Data Analysis", "UX"],
                "goals": ["Launch successful products", "Build strong teams"],
                "bio": "Product manager with a passion for creating user-centric solutions. Enjoy working at the intersection of technology and business.",
                "looking_for": "Product and engineering professionals for mentorship and collaboration"
            },
            {
                "name": "Morgan",
                "age": 35,
                "job_title": "Financial Analyst",
                "industry": "Finance",
                "schedule": "busy",
                "ambition_level": 9,
                "stress_level": 8,
                "work_life_priority": "work-focused",
                "skills": ["Financial Modeling", "Excel", "Data Analysis", "SQL"],
                "goals": ["Become a CFO", "Lead financial strategy"],
                "bio": "Driven financial analyst with expertise in financial modeling and strategic planning. Always looking to grow and take on new challenges.",
                "looking_for": "Finance professionals and executives for career growth and networking"
            }
        ]
        
        # Repeat profiles if needed
        while len(fallback_profiles) < count:
            fallback_profiles.extend(fallback_profiles)
        
        return fallback_profiles[:count]


