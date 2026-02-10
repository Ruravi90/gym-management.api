import requests

# Test CORS functionality
BASE_URL = "http://localhost:8000"

def test_cors():
    try:
        # Test a simple endpoint to check if CORS is working
        headers = {
            "Origin": "http://localhost:4200",  # Typical Angular dev server origin
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Requested-With, Content-Type",
        }
        
        # Test the statistics endpoint mentioned in the error
        response = requests.options(f"{BASE_URL}/memberships/statistics", headers=headers)
        print(f"OPTIONS /memberships/statistics - Status: {response.status_code}")
        
        # Check if CORS headers are present
        cors_headers = [header for header in response.headers.keys() if 'cors' in header.lower() or 'allow' in header.lower()]
        print(f"CORS-related headers: {cors_headers}")
        
        for header in cors_headers:
            print(f"  {header}: {response.headers[header]}")
        
        # Also test a simple GET request
        response_get = requests.get(f"{BASE_URL}/health")
        print(f"GET /health - Status: {response_get.status_code}")
        
        # Check for CORS headers in GET response
        cors_headers_get = [header for header in response_get.headers.keys() if 'access-control' in header.lower()]
        print(f"CORS headers in GET response: {cors_headers_get}")
        
        for header in cors_headers_get:
            print(f"  {header}: {response_get.headers[header]}")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_cors()