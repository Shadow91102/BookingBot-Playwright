from playwright.sync_api import sync_playwright
from datetime import datetime
import uuid
import pytz
import argparse
import json

def get_field_by_label(card, label):
    """Find the value for a given label inside the card."""
    return card.locator(
        f":scope >> xpath=.//m-text[normalize-space(text())='{label}']/following-sibling::m-text[1]"
    ).inner_text()

def getMatchedLoadType(cards):
    count = cards.count()
    matched_index = None
    for i in range(count):
        card = cards.nth(i)

        name = card.locator("m-stack > m-group > m-stack > m-group > m-text").inner_text()
        operation = get_field_by_label(card, "Operation")
        equipment_type = get_field_by_label(card, "Equipment Type")
        transportation_mode = get_field_by_label(card, "Transportation Mode")

        if (
                name.strip() == inputs["name"] and
                operation.strip() == inputs["operation"] and
                equipment_type.strip() == inputs["equipment_type"] and
                transportation_mode.strip() == inputs["transportation_mode"]
            ):
            matched_index = i
            break
    return matched_index

def getMatchedWarehouse(cards):
    search_fragments = [part.strip().lower() for part in inputs["warehouse_address"].split(",")]

    matched_index = None
    for i in range(cards.count()):
        card_text = cards.nth(i).inner_text().lower()
        if all(fragment in card_text for fragment in search_fragments):
            matched_index = i
            break
    return matched_index

def load_inputs_from_json(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Add generated reference number
    data["reference_number"] = f"REF-{uuid.uuid4().hex[:8]}"
    return data

def main():
    global inputs

    parser = argparse.ArgumentParser(description="Book an appointment via JSON config")
    parser.add_argument("--config", type=str, required=True, help="Path to input JSON file")
    args = parser.parse_args()

    inputs = load_inputs_from_json(args.config)
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Set headless=True for production
        page = browser.new_page()

        try:
            # --- LOGIN ---
            page.goto("https://schedule.staging.opendock.com/login")
            page.get_by_role("textbox", name="Enter your email address").fill(inputs["email"])
            page.get_by_role("textbox", name="Enter your password").fill(inputs["password"])

            page.wait_for_selector('[data-testid="login-btn"]:not([aria-disabled="true"])', timeout=5000)
            page.click('[data-testid="login-btn"]')
            page.wait_for_load_state("networkidle")

            # Check for login error
            if page.locator("text=Invalid credentials").is_visible():
                print("❌ Login failed: Invalid email or password.")
                return

            # --- WAREHOUSE SEARCH ---
            page.goto("https://schedule.staging.opendock.com/book")
            page.wait_for_load_state("networkidle")

            page.wait_for_selector('input[id="warehouse-search"]').fill(inputs["warehouse_address"])
            page.wait_for_selector('m-card.clickable', timeout=5000)

            cards = page.locator('m-card.clickable')
            matched_index = getMatchedWarehouse(cards)

            if matched_index is not None:
                cards.nth(matched_index).click(timeout=5000)
                page.wait_for_load_state("networkidle")
            else:
                print(f"❌ No warehouse match found for address: {inputs['warehouse_address']}")
                return

            # --- LOAD TYPE SELECTION ---
            page.get_by_test_id("book-warehouse-btn").click()
            page.wait_for_selector("m-card.clickable")
            cards = page.locator("m-card.clickable")
            matched_index = getMatchedLoadType(cards)

            if matched_index is not None:
                cards.nth(matched_index).click(timeout=5000)
                page.wait_for_load_state("networkidle")
            else:
                print(f"❌ No matching load type card for name: {inputs['name']}, operation: {inputs['operation']}, equipment: {inputs['equipment_type']}")
                return

            # --- DATE/TIME SELECTION ---
            try:
                naive_datetime = datetime.strptime(f"{inputs["date_str"]} {inputs["time_str"]}", "%Y-%m-%d %I:%M %p")
                user_timezone = pytz.timezone(inputs["timezone_str"])
                localized_datetime = user_timezone.localize(naive_datetime)
                iso_datetime_id = localized_datetime.isoformat(timespec='milliseconds')
                # page.get_by_test_id(iso_datetime_id).click() 
                # Click on date slot
                date_slot = page.get_by_test_id(iso_datetime_id)
                if date_slot:
                    date_slot.click()
                else:
                    print(f"❌ Time slot not available: {inputs['date_str']} {inputs['time_str']} ({inputs['timezone_str']})")
                    return
            except Exception as e:
                print(f"❌ Error parsing or selecting datetime: {e}")
                return

            # --- APPOINTMENT DETAILS ---
            page.get_by_role("textbox", name="Reference Number").fill(inputs["reference_number"])
            page.get_by_placeholder("Email subscribers").fill(inputs["email_subscribers"])
            page.get_by_role("textbox", name="Appointment notes").fill(inputs["appointment_notes"])
            page.locator('input[id="custom-field-pc/pallet-count"]').fill(str(inputs["pallet_count"]))

            # Click create and wait
            page.get_by_role("textbox", name="Appointmen11111t notes")
            page.get_by_test_id("create-appointment-btn").click(timeout=5000)
            page.wait_for_load_state("networkidle")

            # --- CONFIRMATION ---
            # Extract confirmation number
            confirmation_number = page.locator("m-text:has-text('Confirmation number') + m-text").text_content()
            print("Confirmation number:", confirmation_number)

        except Exception as e:
            print(f"❌ Script crashed: {e}")

        finally:
            browser.close()



if __name__ == "__main__":
    main()