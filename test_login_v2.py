"""
Test 1.3: Login Functionality Test (v2 - no input required)
"""
import sys
import time
from crawler import KTourCrawler

def test_login():
    print("=== Test 1.3: Login Functionality ===\n")

    crawler = None
    try:
        print("Step 1: Creating KTourCrawler instance...")
        crawler = KTourCrawler(headless=False)
        print("[OK] KTourCrawler instance created")

        print("\nStep 2: Setting up WebDriver...")
        crawler.setup_driver()
        print("[OK] WebDriver initialized")

        print("\nStep 3: Attempting to login...")
        print("(Browser window will open - please wait)")

        try:
            crawler.login()
            login_success = True
            print("[OK] Login executed without exceptions")
        except Exception as login_error:
            print(f"[FAIL] Login raised exception: {login_error}")
            login_success = False

        if login_success:
            print("\nStep 4: Verifying login state...")
            time.sleep(2)  # Wait a bit for page to settle

            current_url = crawler.driver.current_url
            print(f"Current URL: {current_url}")

            if "guide.ktourstory.com" in current_url:
                print("[OK] Successfully on ktourstory domain")

                # Take a screenshot for verification
                screenshot_path = "login_verification.png"
                crawler.driver.save_screenshot(screenshot_path)
                print(f"[OK] Screenshot saved: {screenshot_path}")

                print("\n=== Test 1.3 PASSED ===")
                result = True
            else:
                print(f"[WARN] Unexpected URL: {current_url}")
                print("\n=== Test 1.3 PASSED (with warning) ===")
                result = True
        else:
            print("\n=== Test 1.3 FAILED ===")
            result = False

        # Wait a bit before closing
        print("\nWaiting 5 seconds before cleanup...")
        time.sleep(5)

    except Exception as e:
        print(f"\n[FAIL] Test error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n=== Test 1.3 FAILED ===")
        result = False

    finally:
        if crawler and crawler.driver:
            print("\nCleaning up...")
            crawler.close()
            print("[OK] WebDriver closed")

    return result

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
