from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.sampleTree
songs = db.songs

def scrape_song(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse song info (adapt based on WhoSampled structure)
    title = soup.find("h1").text.strip()
    artist = soup.find("h2").text.strip()
    # Fetch samples and sampled_by data...

    # Save to MongoDB
    song_data = {
        "title": title,
        "artist": artist,
        # Add more song data...
    }
    songs.insert_one(song_data)

# Example usage
scrape_song("https://www.whosampled.com/SomeSong/")
