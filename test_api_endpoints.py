import requests
import json

# Test the new membership types API endpoints
BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    # First, try to get an authentication token (you'll need valid credentials)
    # For this test, we'll assume you have a valid token or the endpoints are public for testing
    
    print("Testing new membership system API endpoints...")
    
    # Test getting membership types (this requires authentication)
    try:
        # This would normally require a valid JWT token
        headers = {
            "Authorization": "Bearer YOUR_VALID_TOKEN_HERE",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/memberships/types", headers=headers)
        print(f"GET /memberships/types - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data)} membership types")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {e}")
        print("Note: This test requires a valid authentication token")

    # Test the API documentation endpoint
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"API Documentation - Status: {response.status_code}")
    except Exception as e:
        print(f"Error accessing docs: {e}")

if __name__ == "__main__":
    test_api_endpoints()