import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def test_apify():
    api_key = os.getenv("APIFY_API_KEY")
    actor_id = os.getenv("APIFY_ACTOR_ID")
    
    print(f"Apify API Key: {api_key[:15]}..." if api_key else "Apify API Key: NOT FOUND")
    print(f"Apify Actor ID: {actor_id}")
    
    if not api_key or not actor_id:
        print("ERROR: Missing APIFY_API_KEY or APIFY_ACTOR_ID in .env file.")
        return

    # Use a dummy/test URL
    test_url = "https://www.linkedin.com/in/williamhgates"
    print(f"\nTesting Apify synchronous run for URL: {test_url}")
    print("This may take 1-2 minutes as the Apify actor starts and runs. Please wait...")
    
    actor_id_clean = actor_id.replace("/", "~")
    api_url = f"https://api.apify.com/v2/acts/{actor_id_clean}/run-sync-get-dataset-items"
    params = {"token": api_key}
    payload = {"profileUrls": [test_url]}
    
    try:
        # 180 seconds timeout for full scraper run
        with httpx.Client(timeout=180.0) as client:
            response = client.post(api_url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            
            print("\nSUCCESS: Successfully connected and extracted data from Apify!")
            print(f"Extracted {len(data)} items.")
            if isinstance(data, list) and len(data) > 0:
                print("Sample Data extracted (keys):", list(data[0].keys()))
            else:
                print("Raw Response:", str(data)[:500])
    except httpx.HTTPStatusError as e:
        print(f"\nHTTP ERROR: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")

if __name__ == "__main__":
    test_apify()
