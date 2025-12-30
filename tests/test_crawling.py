"""
Test 2.1: Crawling Functionality Test (2025-12-04 to 2025-12-05)
"""
import sys
import time
from datetime import datetime
from crawler import KTourCrawler
from data_saver import DataSaver

def test_crawling():
    print("=== Test 2.1: Crawling Functionality (2 days) ===\n")

    crawler = None
    try:
        # Test parameters
        start_date = "2025-12-04"
        end_date = "2025-12-05"

        print(f"Test period: {start_date} to {end_date}")
        print()

        print("Step 1: Creating KTourCrawler instance...")
        crawler = KTourCrawler(headless=False)
        print("[OK] KTourCrawler instance created")

        print("\nStep 2: Setting up WebDriver...")
        crawler.setup_driver()
        print("[OK] WebDriver initialized")

        print("\nStep 3: Logging in...")
        try:
            crawler.login()
            print("[OK] Login completed")
        except Exception as e:
            print(f"[FAIL] Login failed: {e}")
            return False

        print("\nStep 4: Starting crawling process...")
        print(f"Crawling date range: {start_date} ~ {end_date}")

        try:
            crawler.crawl_date_range(start_date, end_date)
            print("[OK] Crawling completed without exceptions")
        except Exception as crawl_error:
            print(f"[FAIL] Crawling failed: {crawl_error}")
            import traceback
            traceback.print_exc()
            return False

        print("\nStep 5: Checking collected data...")
        reservations = crawler.get_reservations()
        count = len(reservations)

        print(f"Total reservations collected: {count}")

        if count > 0:
            print("[OK] Data collected successfully")

            # Show sample data
            print("\nSample data (first 3 reservations):")
            for i, res in enumerate(reservations[:3], 1):
                print(f"\n  Reservation {i}:")
                print(f"    Date: {res.get('date', 'N/A')}")
                print(f"    Team: {res.get('team', 'N/A')}")
                print(f"    Customer: {res.get('customer_name', 'N/A')}")
                print(f"    Reservation #: {res.get('reservation_number', 'N/A')}")
                print(f"    Channel: {res.get('channel', 'N/A')}")
        elif count == 0:
            print("[WARN] No data collected (this might be normal if no reservations exist)")

        # Save data for verification
        print("\nStep 6: Saving collected data...")
        saver = DataSaver(output_dir='output')

        if count > 0:
            # Save in all formats
            csv_file = saver.save_to_csv(reservations, filename='test_crawl_2days')
            excel_file = saver.save_to_excel(reservations, filename='test_crawl_2days')
            json_file = saver.save_to_json(reservations, filename='test_crawl_2days')

            print(f"[OK] CSV saved: {csv_file}")
            print(f"[OK] Excel saved: {excel_file}")
            print(f"[OK] JSON saved: {json_file}")

            # Show summary statistics
            print("\nSummary Statistics:")
            summary = saver.get_summary_statistics(reservations)
            for key, value in summary.items():
                print(f"  {key}: {value}")
        else:
            print("[SKIP] No data to save")

        print("\n=== Test 2.1 PASSED ===")
        result = True

        # Wait before closing
        print("\nWaiting 5 seconds before cleanup...")
        time.sleep(5)

    except Exception as e:
        print(f"\n[FAIL] Test error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n=== Test 2.1 FAILED ===")
        result = False

    finally:
        if crawler and crawler.driver:
            print("\nCleaning up...")
            crawler.close()
            print("[OK] WebDriver closed")

    return result

if __name__ == "__main__":
    success = test_crawling()
    sys.exit(0 if success else 1)
