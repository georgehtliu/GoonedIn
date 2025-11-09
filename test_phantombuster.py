#!/usr/bin/env python3
"""
Quick test script for PhantomBuster LinkedIn Search endpoint
Usage: python test_phantombuster.py
"""

import requests
import json

# Configuration
API_URL = "http://localhost:8000/phantombuster/linkedin-search"

# Test payload - searching for 5 Waterloo girls
payload = {
    "query": "Waterloo girls",
    "limit": 5
}

def test_phantombuster():
    print("🧪 Testing PhantomBuster LinkedIn Search Endpoint")
    print(f"📡 Sending request to: {API_URL}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")

    try:
        print("⏳ Launching PhantomBuster agent (this may take 1-3 minutes)...\n")

        response = requests.post(API_URL, json=payload, timeout=300)

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! PhantomBuster search completed\n")
            print(f"📊 Results:")
            print(f"   - Query: {data['query']}")
            print(f"   - Limit: {data['limit']}")
            print(f"   - Profiles Found: {len(data['profiles'])}")
            print(f"   - Container ID: {data['container_id']}")
            if data.get('output_url'):
                print(f"   - Output URL: {data['output_url']}\n")

            print("👥 Profiles:")
            for i, profile in enumerate(data['profiles'], 1):
                print(f"\n   {i}. {profile.get('name', 'Unknown')}")
                print(f"      Headline: {profile.get('headline', 'N/A')}")
                print(f"      Location: {profile.get('location', 'N/A')}")
                print(f"      Profile: {profile.get('profile_url', 'N/A')}")

            print("\n✨ Test completed successfully!")
            return True

        elif response.status_code == 500:
            error = response.json()
            print(f"❌ ERROR: {error.get('detail', 'Unknown error')}\n")

            if "not configured" in error.get('detail', '').lower():
                print("💡 Fix:")
                print("   1. Open server/.env")
                print("   2. Add your PhantomBuster API key:")
                print("      PHANTOMBUSTER_API_KEY=your_key_here")
                print("   3. Add your Agent ID:")
                print("      PHANTOMBUSTER_SEARCH_AGENT_ID=your_agent_id_here")
                print("   4. Restart the server")
                print("\n📖 See PHANTOMBUSTER_SETUP.md for detailed instructions")

            return False

        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot connect to server")
        print("\n💡 Fix:")
        print("   1. Make sure the backend server is running:")
        print("      cd server")
        print("      uvicorn app.main:app --reload")
        print("   2. Check that it's running on http://localhost:8000")
        return False

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request took longer than 5 minutes")
        print("\n💡 This usually means:")
        print("   - PhantomBuster agent is taking too long")
        print("   - Network issues")
        print("   - Agent might be stuck")
        return False

    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_phantombuster()
    exit(0 if success else 1)
