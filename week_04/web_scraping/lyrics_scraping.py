from bs4 import BeautifulSoup as soup
import requests
import os


ARTIST = "Barbra-Streisand"
try:
    os.makedirs(f"{ARTIST}_lyrics")
except FileExistsError:
    # directory already exists
    pass

r1 = requests.get(f'https://www.lyrics.com/artist/{ARTIST}/')
artist_page = soup(r1.text, "html.parser")
for node in artist_page.find_all(attrs={"class": "tal qx"}):
    link = node.find("a")
    song_title = link.get("href").split("/")[-1]
    address = "https://www.lyrics.com"
    address += link.get("href")
    r2 = requests.get(address)
    song_page = soup(r2.text, "html.parser")
    for node in song_page.find_all(attrs={"id": "lyric-body-text"}):
        with open(f"{ARTIST}_lyrics/{song_title}.txt", "w", encoding="utf-8") as f2:
            f2.write(node.text)