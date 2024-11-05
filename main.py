import requests
from bs4 import BeautifulSoup
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

"""get song list from billboard"""
header = {"User-Agent": os.getenv("USER_AGENT")}
date = input("Where in time would you like to travel to? Enter the date in this format YYYY-MM-DD\n")
web_contents = requests.get(url=f"https://www.billboard.com/charts/hot-100/{date}", headers=header).text
soup = BeautifulSoup(web_contents, "html.parser")
song_items = soup.select("li > h3#title-of-a-story")
song_list = [i.getText().strip() for i in song_items]

"""construct a Spotify object that uses an auth_manager to automatically renew credentials"""
scope = "playlist-modify-private"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri="http://example.com",
        show_dialog=True,
        cache_path="token.txt"
    )
)

"""get song uri for songs in song list form Spotify, skip the unavailable ones"""
list_of_song_uri = []
year = date.split("-")[0]
for song in song_list:
    response = sp.search(q=f"track:{song} year:{year}", type="track", market="CA", limit=1, offset=0)
    try:
        song_uri = response["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f"Spotify does not have '{song}'. Skipped. ")
    else:
        list_of_song_uri.append(song_uri)

"""creating new playlist on Spotify"""
user_id = sp.current_user()["id"]
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"Top Hits {date}",
    description=f"The top 100 popular songs on {date} according to Billboard",
    public=False
)["id"]

"parsing the list of songs to the newly constructed playlist"
sp.playlist_add_items(playlist_id=playlist, items=list_of_song_uri)
