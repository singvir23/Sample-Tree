import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import json

def get_random_headers():
    """
    Generates random headers for each request (not used in Selenium).
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

def fetch_page(url):
    """
    Fetches a webpage using Selenium with a headless Chrome browser.
    """
    options = Options()
    options.headless = False  # Set to True to run without opening a browser window for debugging
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the ChromeDriver without `executable_path`
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        # Wait for the search results to load (waits for `.trackDetails` elements to appear)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "trackDetails"))
        )

        # Scroll down to trigger any lazy-loaded content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for any lazy-loaded content to load

        # Get the page content after waiting and scrolling
        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        print(f"Failed to load page with Selenium. Error: {e}")
        driver.quit()
        return None


def get_song_url(artist, song_title):
    """
    Constructs the search URL on WhoSampled and finds the exact song URL.
    """
    query = urllib.parse.quote(f"{artist} {song_title}")
    search_url = f"https://www.whosampled.com/search/?q={query}"
    
    # Fetch the search page
    print("Fetching search page...")
    search_page = fetch_page(search_url)
    if not search_page:
        print("Failed to retrieve the search page.")
        return None

    # Debug: Print the HTML content of the search page
    print("Search Page HTML:\n", search_page[:2000])  # Print the first 2000 characters for readability

    # Parse the rendered HTML with BeautifulSoup
    soup = BeautifulSoup(search_page, 'html.parser')

    # Find the first result matching both artist and song title
    results = soup.find_all("div", class_="trackDetails")
    print(f"Found {len(results)} potential results in search.")
    
    for result in results:
        title_element = result.find("a", class_="trackName")
        artist_element = result.find("span", class_="trackArtist")
        
        if title_element and artist_element:
            title = title_element.text.strip().lower()
            artist_name = artist_element.text.strip().lower()
            
            # Debug: Print each title and artist found
            print(f"Found title: {title}, artist: {artist_name}")

            # Check if both title and artist match
            if song_title.lower() == title and artist.lower() in artist_name:
                # Get the song URL
                song_url = "https://www.whosampled.com" + title_element['href']
                print("Match found! Song URL:", song_url)
                return song_url

    print("No matching song found.")
    return None

def parse_song_data(html_content):
    """
    Parses song data from HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find("h1").text.strip() if soup.find("h1") else "Unknown Title"
    artist = soup.find("h2").text.strip() if soup.find("h2") else "Unknown Artist"
    samples = []
    sampled_by = []

    # Extract samples and sampled_by data here based on WhoSampled HTML structure
    samples_section = soup.find_all("section", {"class": "sampled-songs"})
    if samples_section:
        samples = [a.text.strip() for a in samples_section[0].find_all("a", {"class": "trackName"})]

    sampled_by_section = soup.find_all("section", {"class": "sampled-by"})
    if sampled_by_section:
        sampled_by = [a.text.strip() for a in sampled_by_section[0].find_all("a", {"class": "trackName"})]

    return {"title": title, "artist": artist, "samples": samples, "sampled_by": sampled_by}

def scrape_song(artist, song_title):
    """
    Scrapes WhoSampled for a specific song by artist and title.
    """
    # Construct the search URL with the artist and song title
    song_url = get_song_url(artist, song_title)
    if not song_url:
        print("No matching song found for:", artist, "-", song_title)
        return None
    
    # Fetch the song page
    print("Fetching song page...")
    time.sleep(random.uniform(1, 3))  # Random delay to avoid rate-limiting
    song_page = fetch_page(song_url)
    if not song_page:
        print("Failed to retrieve the song page.")
        return None

    # Parse and return song data
    song_data = parse_song_data(song_page)
    print("Scraped data:", json.dumps(song_data, indent=2))
    return song_data

# Example usage
if __name__ == "__main__":
    artist = "Drake"
    song_title = "Sticky"
    scrape_song(artist, song_title)
