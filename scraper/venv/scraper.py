import time
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests_html import HTMLSession
import urllib.parse
import json

def get_random_headers():
    """
    Generates random headers for each request.
    """
    ua = UserAgent()  # Automatically generates random user agents
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",  # Sets Google as the referer
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    return headers

def fetch_page(url):
    """
    Fetches a webpage using randomized headers and JavaScript rendering.
    """
    headers = get_random_headers()
    session = HTMLSession()
    
    try:
        # Fetch the page and render JavaScript
        response = session.get(url, headers=headers)
        response.html.render(timeout=20)  # Render JavaScript
        
        response.encoding = 'utf-8'  # Ensure UTF-8 encoding
        return response.html.html  # Return fully rendered HTML content
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_song_url(artist, song_title):
    """
    Constructs the search URL on WhoSampled and finds the exact song URL.
    """
    # Construct search URL with encoded query
    query = urllib.parse.quote(f"{artist} {song_title}")
    search_url = f"https://www.whosampled.com/search/?q={query}"
    
    # Fetch the search page
    print("Fetching search page...")
    search_page = fetch_page(search_url)
    if not search_page:
        print("Failed to retrieve the search page.")
        return None

    # Parse the rendered HTML with BeautifulSoup
    soup = BeautifulSoup(search_page, 'html.parser')
    
    # Debugging: Print HTML content to verify structure
    # print(soup.prettify())

    # Find the first result matching both artist and song title
    results = soup.find_all("div", class_="trackDetails")
    for result in results:
        title_element = result.find("a", class_="trackName")
        artist_element = result.find("span", class_="trackArtist")
        
        if title_element and artist_element:
            title = title_element.text.strip().lower()
            artist_name = artist_element.text.strip().lower()
            
            # Check if both title and artist match
            if song_title.lower() == title and artist.lower() in artist_name:
                # Get the song URL
                return "https://www.whosampled.com" + title_element['href']
    
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
