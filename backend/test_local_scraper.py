import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from app.services.scraper import scraper_service

async def main():
    test_url = "https://www.linkedin.com/in/williamhgates"
    print(f"Testing optimized local scraper on: {test_url}")
    print("This runs entirely locally on your machine for free using Playwright.")
    print("It will try Googlebot headers first, then fall back to Mobile headers if needed.")
    print("Please wait...\n")
    
    result = await scraper_service.scrape(test_url)
    
    if "Error scraping" in result:
        print("\nFAILED: Local scraper hit the LinkedIn Auth Wall.")
        print(f"Details: {result}")
    else:
        print("\nSUCCESS: Successfully scraped the profile locally for free!")
        print(f"Scraped length: {len(result)} characters.")
        print("\nPreview of scraped data:")
        print("-" * 50)
        clean_preview = result[:1000].encode('ascii', errors='ignore').decode('ascii')
        print(clean_preview + "...")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
