"""
GoonedIn Backend - Flask Application
Main application file with all API endpoints
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

from config import Config
from models import Profile, Match, DataStore
from matcher import MatchingEngine
from perplexity_service import PerplexityService

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for frontend

# Initialize services
data_store = DataStore(Config.DATA_DIR)
matcher = MatchingEngine()
perplexity = PerplexityService(Config.PERPLEXITY_API_KEY)

# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@app.route('/api/profile/create', methods=['POST'])
def create_profile():
    """Create a new profile"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'age', 'job_title', 'industry', 'schedule',
                          'ambition_level', 'stress_level', 'work_life_priority',
                          'skills', 'goals', 'bio', 'looking_for']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create profile
        profile = Profile(
            name=data['name'],
            age=int(data['age']),
            job_title=data['job_title'],
            industry=data['industry'],
            schedule=data['schedule'],
            ambition_level=int(data['ambition_level']),
            stress_level=int(data['stress_level']),
            work_life_priority=data['work_life_priority'],
            skills=data['skills'],
            goals=data['goals'],
            bio=data['bio'],
            looking_for=data['looking_for']
        )
        
        # Save profile
        data_store.save_profile(profile)
        
        return jsonify({
            'success': True,
            'profile': profile.to_dict(),
            'message': 'Profile created successfully!'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profiles', methods=['GET'])
def get_all_profiles():
    """Get all profiles"""
    try:
        profiles = data_store.get_all_profiles()
        return jsonify({
            'success': True,
            'profiles': [p.to_dict() for p in profiles],
            'count': len(profiles)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    """Get a specific profile"""
    try:
        profile = data_store.get_profile(profile_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify({
            'success': True,
            'profile': profile.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete a profile"""
    try:
        data_store.delete_profile(profile_id)
        return jsonify({
            'success': True,
            'message': 'Profile deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# MATCHING ENDPOINTS
# ============================================================================

@app.route('/api/match/find', methods=['POST'])
def find_matches():
    """Find matches for a profile"""
    try:
        data = request.json
        profile_id = data.get('profile_id')
        max_results = data.get('max_results', Config.MAX_MATCHES_PER_REQUEST)
        
        if not profile_id:
            return jsonify({'error': 'profile_id is required'}), 400
        
        # Get the profile
        profile = data_store.get_profile(profile_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Get all other profiles
        all_profiles = data_store.get_all_profiles()
        
        # Find matches
        matches = matcher.find_matches(profile, all_profiles, max_results)
        
        # Format response
        match_results = []
        for match_profile, score, reasons, match_type in matches:
            match_results.append({
                'profile': match_profile.to_dict(),
                'compatibility_score': score,
                'reasons': reasons,
                'match_type': match_type
            })
        
        return jsonify({
            'success': True,
            'matches': match_results,
            'count': len(match_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/match/like', methods=['POST'])
def like_profile():
    """Like a profile"""
    try:
        data = request.json
        liker_id = data.get('liker_id')
        liked_id = data.get('liked_id')
        
        if not liker_id or not liked_id:
            return jsonify({'error': 'Both liker_id and liked_id are required'}), 400
        
        # Get both profiles
        liker = data_store.get_profile(liker_id)
        liked = data_store.get_profile(liked_id)
        
        if not liker or not liked:
            return jsonify({'error': 'One or both profiles not found'}), 404
        
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
            
            return jsonify({
                'success': True,
                'is_match': True,
                'match': match.to_dict(),
                'message': "It's a match! 🎉"
            }), 200
        
        return jsonify({
            'success': True,
            'is_match': False,
            'message': 'Profile liked successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/match/pass', methods=['POST'])
def pass_profile():
    """Pass on a profile"""
    try:
        data = request.json
        passer_id = data.get('passer_id')
        passed_id = data.get('passed_id')
        
        if not passer_id or not passed_id:
            return jsonify({'error': 'Both passer_id and passed_id are required'}), 400
        
        # Get profile
        passer = data_store.get_profile(passer_id)
        if not passer:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Add to passes
        if passed_id not in passer.passes:
            passer.passes.append(passed_id)
            data_store.save_profile(passer)
        
        return jsonify({
            'success': True,
            'message': 'Profile passed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# MATCH DETAILS ENDPOINTS
# ============================================================================

@app.route('/api/match/<match_id>', methods=['GET'])
def get_match(match_id):
    """Get match details"""
    try:
        match = data_store.get_match(match_id)
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        
        # Get both profiles
        profile1 = data_store.get_profile(match.profile1_id)
        profile2 = data_store.get_profile(match.profile2_id)
        
        return jsonify({
            'success': True,
            'match': match.to_dict(),
            'profile1': profile1.to_dict() if profile1 else None,
            'profile2': profile2.to_dict() if profile2 else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/matches/<profile_id>', methods=['GET'])
def get_profile_matches(profile_id):
    """Get all matches for a profile"""
    try:
        profile = data_store.get_profile(profile_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
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
        
        return jsonify({
            'success': True,
            'matches': match_details,
            'count': len(match_details)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compatibility/<match_id>', methods=['GET'])
def get_compatibility_report(match_id):
    """Get or generate compatibility report for a match"""
    try:
        match = data_store.get_match(match_id)
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        
        # If report already exists, return it
        if match.compatibility_report:
            return jsonify({
                'success': True,
                'report': match.compatibility_report
            }), 200
        
        # Generate new report
        profile1 = data_store.get_profile(match.profile1_id)
        profile2 = data_store.get_profile(match.profile2_id)
        
        if not profile1 or not profile2:
            return jsonify({'error': 'One or both profiles not found'}), 404
        
        report = perplexity.generate_compatibility_report(
            profile1.to_dict(),
            profile2.to_dict(),
            match.compatibility_score,
            match.reasons
        )
        
        # Save report
        match.compatibility_report = report
        data_store.save_match(match)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/generate-samples', methods=['POST'])
def generate_sample_profiles():
    """Generate sample profiles using Perplexity"""
    try:
        data = request.json
        count = data.get('count', 10)
        
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
            profiles.append(profile.to_dict())
        
        return jsonify({
            'success': True,
            'profiles': profiles,
            'count': len(profiles),
            'message': f'{len(profiles)} sample profiles generated!'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
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
        
        return jsonify({
            'success': True,
            'stats': {
                'total_profiles': total_profiles,
                'total_likes': total_likes,
                'total_matches': total_matches,
                'industry_breakdown': industry_counts,
                'average_compatibility': round(avg_compatibility, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    print("=" * 50)
    print("GoonedIn Backend Starting...")
    print("=" * 50)
    print(f"Data directory: {Config.DATA_DIR}")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"Perplexity API configured: {bool(Config.PERPLEXITY_API_KEY)}")
    print("=" * 50)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
