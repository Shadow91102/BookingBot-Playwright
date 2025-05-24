from playwright.sync_api import sync_playwright, expect
from datetime import datetime, timedelta
import uuid

# Input variables with example values
inputs = {
    "email": "jonathan@vooma.ai",
    "password": "nepcur-8sewsi-zuwxoV",
    "warehouse_address": "3004 Wayland Ave, Elgin, IL",
    "appointment_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),  # e.g., "2025-05-23"
    "appointment_time": "10:00 AM",
    "load_type": "Standard Load",  # Adjust based on actual card title
    "reference_number": f"REF-{uuid.uuid4().hex[:8]}",  # Generate unique reference
    "email_subscribers": "user1@example.com,user2@example.com",
    "appointment_notes": "Urgent delivery",
    "pallet_count": 10
}

def schedule_appointment():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Set headless=True for production
        page = browser.new_page()

        try:
            # Step 0: Login
            page.goto("https://schedule.staging.opendock.com/login")
            page.get_by_role("textbox", name="Enter your email address").fill(inputs["email"])
            page.get_by_role("textbox", name="Enter your password").fill(inputs["password"])

            # Wait for the Sign in button to be enabled
            page.wait_for_selector('[data-testid="login-btn"]:not([aria-disabled="true"])', timeout=5000)
            page.click('[data-testid="login-btn"]')
            page.wait_for_load_state("networkidle")
            # Step 1: Search for warehouse
            page.goto("https://schedule.staging.opendock.com/book")
            page.wait_for_selector('input[id="warehouse-search"]').fill(inputs["warehouse_address"])
            page.wait_for_selector('m-card.clickable', timeout=5000)  # Wait for card grid
            # expect(page.get_by_test_id("warehouse-search-results").locator("m-card")).to_contain_text("3004 Wayland Ave Elgin, IL 60124").click()
            # page.get_by_test_id("warehouse-search-results").locator("m-card")
            # Try clicking card by warehouse name

            cards = page.locator('m-card.clickable')  # Wait for card grid

            matched_card = None
            search_fragments = [part.strip().lower() for part in inputs["warehouse_address"].split(",")]
            # search_fragments = inputs["warehouse_address"]
            for i in range(cards.count()):
                card = cards.nth(i)
                text = card.inner_text().lower()

                print(text)

                if all(fragment in text for fragment in search_fragments):
                    matched_card = card
                    break

            if matched_card:
                print("Matched card found.")
                # Example: highlight it
                page.evaluate("card => card.style.border = '2px solid green'", matched_card)
            else:
                print("No matching card found.")

            page.wait_for_load_state("networkidle")

            # Step 2: Select load type
            page.click('button:has-text("Book appointment")')  # Click Book Preditment button
            page.wait_for_selector('div.M-Card')  # Wait for load type cards
            page.click(f'div.M-Card:has-text("{inputs["load_type"]}")')  # Select card by title
            page.wait_for_load_state("networkidle")

            # Step 3: Select date and time
            page.wait_for_selector('div[class*="date-time-selector"]')  # Adjust selector
            page.click(f'text="{inputs["appointment_date"]}"')  # Select date
            page.click(f'text="{inputs["appointment_time"]}"')  # Select time
            page.click('button:has-text("Booking confrm")')  # Click confirm button
            page.wait_for_load_state("networkidle")

            # Step 4: Enter details and confirm
            page.fill('input[name="reference_number"]', inputs["reference_number"])
            page.fill('input[name="email_subscribers"]', inputs["email_subscribers"])
            page.fill('textarea[name="appointment_notes"]', inputs["appointment_notes"])
            page.fill('input[name="pallet_count"]', str(inputs["pallet_count"]))
            page.click('button:has-text("Confirm booking")')
            page.wait_for_load_state("networkidle")

            # Extract confirmation number
            confirmation_number = page.locator('div[class*="confirmation-number"]').inner_text()  # Adjust selector
            print(f"Confirmation Number: {confirmation_number}")

        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            browser.close()

if __name__ == "__main__":
    schedule_appointment()