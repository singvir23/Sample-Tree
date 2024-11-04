import os
import time
import random
import sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Load environment variables from .env file
load_dotenv(dotenv_path='/Users/viraajsingh/Desktop/Sample-Tree/backend/.env')

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'whosampled_db')  # Default to 'whosampled_db' if not set

if not MONGO_URI:
    print("Error: MONGO_URI not found in environment variables.")
    sys.exit(1)

# Initialize MongoDB Client
def init_mongo():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # 5 seconds timeout
        # Attempt to retrieve server info to trigger connection
        client.server_info()
        print("MongoDB connection established.")
        return client
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

# Introduce random delays to mimic human behavior
def random_delay(min_delay=2, max_delay=5):
    delay = random.uniform(min_delay, max_delay)
    print(f"Sleeping for {delay:.2f} seconds to mimic human behavior.")
    time.sleep(delay)

# Scroll the page to load dynamic content
def scroll_page(page, delay=2):
    current_height = page.evaluate("document.body.scrollHeight")
    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        print("Scrolling to bottom of the page...")
        time.sleep(delay)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == current_height:
            print("Reached the bottom of the page.")
            break
        current_height = new_height

# Fetch and save page content with debugging
def fetch_page(url, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"longitude": -122.4194, "latitude": 37.7749},
            permissions=["geolocation"]
        )
        page = context.new_page()

        # Setup network logging (optional but useful for debugging)
        def log_request(request):
            print(f"Request: {request.method} {request.url}")

        def log_response(response):
            print(f"Response: {response.status} {response.url}")

        page.on("request", log_request)
        page.on("response", log_response)

        try:
            print(f"Navigating to {url}")
            page.goto(url, timeout=60000)  # 60 seconds timeout
            print("Page navigation completed.")

            # Take a screenshot after navigation
            page.screenshot(path="screenshot_after_navigation.png")
            print("Screenshot after navigation saved as 'screenshot_after_navigation.png'.")

            # Handle potential pop-ups or modals
            try:
                consent_button = page.query_selector("button.cookie-consent-accept")
                if consent_button:
                    consent_button.click()
                    print("Cookie consent accepted.")
                    random_delay()
                    # Take a screenshot after handling consent
                    page.screenshot(path="screenshot_after_consent.png")
                    print("Screenshot after cookie consent saved as 'screenshot_after_consent.png'.")
            except PlaywrightTimeoutError:
                print("No cookie consent banner found.")

            try:
                modal_close = page.query_selector("button.close-modal")
                if modal_close:
                    modal_close.click()
                    print("Modal closed.")
                    random_delay()
                    # Take a screenshot after closing modal
                    page.screenshot(path="screenshot_after_modal_close.png")
                    print("Screenshot after closing modal saved as 'screenshot_after_modal_close.png'.")
            except PlaywrightTimeoutError:
                print("No modal found to close.")

            # Wait for the main content to load
            try:
                # Adjust the selector based on actual HTML structure
                # Using a more precise selector as per your description
                print("Waiting for the 'div.divided-layout' section to load...")
                page.wait_for_selector("div.divided-layout", timeout=60000)  # Wait up to 60 seconds
                print("'div.divided-layout' section loaded.")
                # Take a screenshot after main content loaded
                page.screenshot(path="screenshot_after_content_load.png")
                print("Screenshot after content load saved as 'screenshot_after_content_load.png'.")
            except PlaywrightTimeoutError:
                print("'div.divided-layout' section did not load within the timeout period.")
                # Take a screenshot of the current state
                page.screenshot(path="screenshot_timeout.png")
                print("Screenshot after timeout saved as 'screenshot_timeout.png'.")
                # Save the HTML content for further inspection
                html_content = page.content()
                with open("debug_song_page_timeout.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("HTML content saved to 'debug_song_page_timeout.html' for inspection.")
                browser.close()
                return None

            # Scroll the page to load all dynamic content
            scroll_page(page)

            # Optional random delay
            random_delay()

            # Get the HTML content and save it for inspection
            html_content = page.content()
            with open("debug_song_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("HTML content saved to 'debug_song_page.html' for inspection.")

            # Optionally, take a final screenshot after scrolling
            page.screenshot(path="screenshot_after_scrolling.png")
            print("Screenshot after scrolling saved as 'screenshot_after_scrolling.png'.")

            browser.close()
            return html_content

        except PlaywrightTimeoutError:
            print("Page load timed out.")
            browser.close()
            return None

# Check if CAPTCHA is present
def is_captcha_present(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Example: Check for reCAPTCHA or other CAPTCHA indicators
    # Adjust the selectors based on actual CAPTCHA implementation
    captcha_div = soup.find("div", class_="g-recaptcha")
    if captcha_div:
        print("CAPTCHA detected on the page.")
        return True
    # Add other CAPTCHA checks if necessary
    return False

# Parse the song page to extract samples and sampled_by
def parse_song_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {
        "samples": [],
        "sampled_by": []
    }

    # Extract the song title and artist from the header
    head_title = soup.find("h1", class_="headTitle")
    if head_title:
        search_query = head_title.text.strip().replace("Search Results for “", "").replace("”", "")
        data["search_query"] = search_query
        print(f"Search Query: {search_query}")
    else:
        data["search_query"] = "Unknown Title"
        print("Search query title not found.")

    # Function to extract songs from a given section
    def extract_songs(section_header_text):
        songs = []
        # Find the section with the specified header
        section_header = soup.find("h3", class_="section-header-title", string=lambda text: text and section_header_text in text)
        if section_header:
            print(f"Found section: {section_header_text}")
            # The table containing the songs is a sibling of the header
            parent_section = section_header.find_parent("section")
            if parent_section:
                table = parent_section.find("table", class_="table tdata")
                if table:
                    tbody = table.find("tbody")
                    if tbody:
                        rows = tbody.find_all("tr")
                        print(f"Found {len(rows)} entries in section: {section_header_text}")
                        for row in rows:
                            # Extract track name
                            track_td = row.find("td", class_="tdata__td2")
                            track_name = track_td.find("a", class_="trackName playIcon").text.strip() if track_td else "Unknown Track"

                            # Extract artist(s)
                            artist_td = row.find_all("td", class_="tdata__td3")[0] if row.find_all("td", class_="tdata__td3") else None
                            artists = [a.text.strip() for a in artist_td.find_all("a")] if artist_td else ["Unknown Artist"]

                            # Extract release year
                            year_td = row.find_all("td", class_="tdata__td3")[1] if len(row.find_all("td", class_="tdata__td3")) > 1 else None
                            release_year = year_td.text.strip() if year_td else "Unknown Year"

                            # Extract additional info (e.g., genre)
                            info_td = row.find_all("td", class_="tdata__td3")[2] if len(row.find_all("td", class_="tdata__td3")) > 2 else None
                            additional_info = info_td.text.strip() if info_td else ""

                            # Extract URL
                            sample_url = "https://www.whosampled.com" + row.find("a", href=True)['href'] if row.find("a", href=True) else ""

                            song_entry = {
                                "track_name": track_name,
                                "artists": artists,
                                "release_year": release_year,
                                "additional_info": additional_info,
                                "url": sample_url
                            }
                            songs.append(song_entry)
                            print(f"Extracted Song: {song_entry}")
        else:
            print(f"Section header '{section_header_text}' not found.")
        return songs

    # Extract "Contains Samples" section
    data["samples"] = extract_songs("contains samples of")

    # Extract "Sampled in" section
    data["sampled_by"] = extract_songs("Sampled in")
    
    return data

# Insert data into MongoDB
def insert_into_mongo(client, song_data, original_song):
    db = client[DB_NAME]
    songs_collection = db['Song']
    
    # Prepare the document
    document = {
        "original_song": original_song,
        "search_query": song_data.get("search_query", ""),
        "samples": song_data.get("samples", []),
        "sampled_by": song_data.get("sampled_by", [])
    }
    
    try:
        # Use upsert to avoid duplicate entries based on original_song and search_query
        result = songs_collection.update_one(
            {"original_song": original_song, "search_query": document["search_query"]},
            {"$set": document},
            upsert=True
        )
        if result.upserted_id:
            print(f"Inserted new entry with id: {result.upserted_id}")
        else:
            print(f"Updated existing entry for: {original_song}")
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")

# Main scraping function
def scrape_song(artist, song_title):
    client = init_mongo()
    
    try:
        # Construct the song URL based on the artist and song title
        # Assuming the URL structure is /Artist/Song/
        artist_formatted = artist.strip().replace(" ", "-")
        song_formatted = song_title.strip().replace(" ", "-")
        song_url = f"https://www.whosampled.com/{artist_formatted}/{song_formatted}/"
        print(f"Constructed Song URL: {song_url}")
        
        # Fetch the song page
        print("Fetching the song page...")
        song_page = fetch_page(song_url, headless=False)  # Temporarily set headless=False for debugging
        if not song_page:
            print("Failed to retrieve the song page.")
            return None

        # Check for CAPTCHA
        if is_captcha_present(song_page):
            print("CAPTCHA detected on the song page. Manual intervention required.")
            return None

        # Parse the song data
        print("Parsing the song data...")
        song_data = parse_song_data(song_page)
        print("Parsed Data:", song_data)

        # Insert the data into MongoDB
        insert_into_mongo(client, song_data, original_song=f"{artist} - {song_title}")
        
        return song_data
    finally:
        # Ensure the MongoDB client is closed
        client.close()

# Example usage
if __name__ == "__main__":
    artist = "Drake"
    song_title = "Sticky"
    scraped_data = scrape_song(artist, song_title)
    if scraped_data:
        print("Scraping completed successfully.")
    else:
        print("Scraping failed or was incomplete.")
