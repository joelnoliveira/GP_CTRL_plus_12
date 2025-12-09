import requests
import time
import sys

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("Checking if server is up...")
    try:
        response = requests.get(f"{base_url}/status/alive")
        print(f"Status/Alive: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Server is not running. Please run 'python backend/app/main.py' first.")
        return

    # Test root
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Root failed: {e}")

    # Test datasets (GET)
    try:
        response = requests.get(f"{base_url}/datasets")
        print(f"Datasets: {response.status_code}")
        if response.status_code == 200:
            print(response.json())
    except Exception as e:
        print(f"Datasets failed: {e}")

if __name__ == "__main__":
    test_endpoints()
