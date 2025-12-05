"""
Test 1.2: WebDriver Initialization Test
"""
import sys
from crawler import KTourCrawler

def test_webdriver_init():
    print("=== Test 1.2: WebDriver Initialization ===\n")

    try:
        print("Step 1: Creating KTourCrawler instance...")
        crawler = KTourCrawler(headless=True)
        print("[OK] KTourCrawler instance created")

        print("\nStep 2: Setting up WebDriver...")
        crawler.setup_driver()
        print("[OK] WebDriver initialized successfully")

        print("\nStep 3: Checking driver status...")
        if crawler.driver:
            print(f"[OK] Driver is active: {type(crawler.driver)}")
        else:
            print("[FAIL] Driver is None")
            return False

        print("\nStep 4: Cleaning up...")
        crawler.close()
        print("[OK] WebDriver closed successfully")

        print("\n=== Test 1.2 PASSED ===")
        return True

    except Exception as e:
        print(f"\n[FAIL] Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n=== Test 1.2 FAILED ===")
        return False

if __name__ == "__main__":
    success = test_webdriver_init()
    sys.exit(0 if success else 1)
