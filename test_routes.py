import requests

# Test the API endpoints to verify they work correctly
BASE_URL = "http://localhost:8000"

def test_api_routes():
    # Test the types endpoint
    try:
        # This requires authentication, so we'll expect a 401 or 403
        # But we want to make sure it doesn't give a 422 error
        headers = {
            "Authorization": "Bearer invalid_token_for_testing",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/memberships/types", headers=headers)
        print(f"GET /memberships/types - Status: {response.status_code}")
        
        if response.status_code == 422:
            print("❌ ERROR: Still getting 422 Unprocessable Entity")
            print(f"Response: {response.text}")
        elif response.status_code in [401, 403]:
            print("✅ SUCCESS: Getting expected auth error (not 422)")
        else:
            print(f"❓ UNEXPECTED: Got status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_api_routes()