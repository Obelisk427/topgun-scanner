import requests
from bs4 import BeautifulSoup
import os
import sys

# --- CONFIGURATION ---
URL = "https://playtopgunsports.com/UpcomingTournaments.aspx"  # Replace with the actual Top Gun page URL
TOURNAMENT_NAME = "APPOMATTOX INAUGURAL (4)"  # Replace with your ACTUAL upcoming tournament!

# This tells Python to look in GitHub's hidden secrets vault for your webhook
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_notification():
    """Sends a message to Discord when the schedule goes live."""
    if not DISCORD_WEBHOOK_URL:
        print("Error: Discord Webhook URL is missing from the environment variables!")
        return

    data = {
        "content": f"🚨 The schedule for '{TOURNAMENT_NAME}' has just been posted! Check it here: {URL}"
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print("Discord notification sent.")
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

def check_for_bracket():
    """Searches for the specific tournament and checks buttons for 'Schedule'."""
    print(f"Checking for '{TOURNAMENT_NAME}' schedule...")
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        tournament_element = soup.find(string=lambda text: text and TOURNAMENT_NAME.lower() in text.lower())

        if tournament_element:
            row = tournament_element.find_parent('tr')
            if row:
                schedule_found = False
                for element in row.find_all(['a', 'button', 'input']):
                    element_text = element.get_text(strip=True).lower()
                    element_value = element.get('value', '').lower()
                    
                    if 'schedule' in element_text or 'schedule' in element_value:
                        schedule_found = True
                        break
                
                if schedule_found:
                    print("Schedule button found! Sending Discord alert...")
                    send_discord_notification()
                    sys.exit(0)
                else:
                    print("Tournament found, but couldn't detect a 'Schedule' button.")
            else:
                print("Found the tournament name, but couldn't read the table layout.")
        else:
            print(f"Could not find '{TOURNAMENT_NAME}' on the page.")

    except Exception as e:
        print(f"Error fetching or parsing the page: {e}")

if __name__ == "__main__":
    check_for_bracket()