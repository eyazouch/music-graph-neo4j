
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint):
    print(f"Testing {endpoint}...")
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"Data type: List, Length: {len(data)}")
                if len(data) > 0:
                    print(f"First item: {data[0]}")
                else:
                    print("Data is empty list []")
            else:
                print(f"Data type: {type(data)}")
                print(f"Data content: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

if __name__ == "__main__":
    test_endpoint("/mongodb/stats")
    test_endpoint("/mongodb/audio/distribution")
    test_endpoint("/mongodb/analytics/evolution")
    test_endpoint("/mongodb/analytics/correlations")
    test_endpoint("/mongodb/audio/mood-clusters")
