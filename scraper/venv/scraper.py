from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.sampleTree
songs = db.songs

def scrape_and_save_song(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse the song data here
    title = soup.find("h1").text.strip()
    artist = soup.find("h2").text.strip()

    song_data = {
        "title": title,
        "artist": artist,
        # Add more parsed data here, like samples and sampled_by
    }

    # Save to MongoDB
    songs.insert_one(song_data)
    return song_data
