"""
Test 1.3: Login Functionality Test
"""
import sys
from crawler import KTourCrawler

def test_login():
    print("=== Test 1.3: Login Functionality ===\n")

    crawler = None
    try:
        print("Step 1: Creating KTourCrawler instance...")
        crawler = KTourCrawler(headless=False)  # headless=False to see the browser
        print("[OK] KTourCrawler instance created")

        print("\nStep 2: Setting up WebDriver...")
        crawler.setup_driver()
        print("[OK] WebDriver initialized")

        print("\nStep 3: Attempting to login...")
        print("(This will open a browser window - please wait)")
        login_result = crawler.login()

        if login_result:
            print("[OK] Login successful!")
            print("\nStep 4: Verifying login state...")
            # Check if we're on the expected page after login
            current_url = crawler.driver.current_url
            print(f"Current URL: {current_url}")

            if "guide.ktourstory.com" in current_url:
                print("[OK] Successfully logged in and navigated to ktourstory")
                print("\n=== Test 1.3 PASSED ===")
                result = True
            else:
                print(f"[WARN] Logged in but unexpected URL: {current_url}")
                print("\n=== Test 1.3 PASSED (with warning) ===")
                result = True
        else:
            print("[FAIL] Login failed")
            print("\n=== Test 1.3 FAILED ===")
            result = False

    except Exception as e:
        print(f"\n[FAIL] Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n=== Test 1.3 FAILED ===")
        result = False

    finally:
        if crawler and crawler.driver:
            print("\nCleaning up...")
            input("Press Enter to close the browser and finish test...")
            crawler.close()
            print("[OK] WebDriver closed")

    return result

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
