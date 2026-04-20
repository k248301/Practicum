import requests
import time
import sys

def test_endpoint():
    url = "http://localhost:8081/fetch-news"
    print(f"Testing {url}...")
    
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        duration = time.time() - start_time
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Article Count: {data.get('count')}")
            if data.get('count') > 0:
                print("Successfully fetched articles.")
            else:
                print("Fetched 0 articles (might be valid if no news).")
        else:
            print(f"Error: {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"Request failed: {e}")
        # Dont exit 1 here, maybe server isn't up yet, let user know
        sys.exit(1)

if __name__ == "__main__":
    # Wait for server to start if running in parallel, but here we run it manually
    print("Test script running...")
    test_endpoint()
