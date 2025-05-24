
# 📦 Opendock Appointment Booking Automation

This script automates the process of booking an appointment on the Opendock scheduling platform using [Playwright](https://playwright.dev/). It logs in, searches for a warehouse, selects load type, sets appointment date/time, and submits booking details — all using parameters from a JSON config file.

---

## 🚀 Features

- Automates login, search, load selection, and booking steps
- Timezone-aware ISO datetime formatting
- Easily configurable through a JSON file
- Playwright-based browser automation

---

## 📁 Project Structure

```
.
├── booking_bot.py # Final production-ready script
├── schedule_appointment.py # Main working script with logic
├── inputs.json # JSON config file with appointment inputs
├── requirements.txt # Python dependencies
└── README.md # You're reading it :)
```

---

## 🔧 Setup

### 1. Clone the repo

```bash
git clone https://github.com/Shadow91102/BookingBot-Playwright.git
cd BookingBot-Playwright
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

## 📝 Configuration

Edit the `inputs.json` file:

```json
{
  "email": "jonathan@vooma.ai",
  "password": "nepcur-8sewsi-zuwxoV",
  "warehouse_address": "3004 Wayland Ave, Elgin, IL",
  "name": "FTL Packaged Goods",
  "operation": "Drop",
  "equipment_type": "Dry Van",
  "transportation_mode": "FTL",
  "date_str": "2025-05-26",
  "time_str": "11:30 AM",
  "timezone_str": "America/Chicago",
  "email_subscribers": "user1@example.com,user2@example.com",
  "appointment_notes": "Urgent delivery",
  "pallet_count": 10
}
```

The script will automatically generate a unique `reference_number` during execution.

---

## ▶️ Run the Script

```bash
python main.py --config inputs.json
```

This will launch a browser, perform the booking steps, and print the confirmation number if successful.

---

## 🧪 Testing

To run in non-headless mode for debugging:

```python
browser = p.chromium.launch(headless=False)
```

---

## ✅ Output

On success, you’ll see something like:

```
Confirmation number: #1234567890
```

If there's a mismatch or error (e.g., warehouse not found), the script will notify you in the console.

---

## 🛠️ Dependencies

- [Playwright (Python)](https://playwright.dev/python/)
- `pytz`
- `uuid`

Install them via:

```bash
pip install -r requirements.txt
```

---

## 📄 License

MIT — feel free to use and adapt this script for your needs.
