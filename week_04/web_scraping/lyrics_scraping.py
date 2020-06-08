from bs4 import BeautifulSoup as soup
import requests
import os


# select artist for scraping
ARTISTS = ["Barbra Streisand", "Peaches", "Pavement", "Sonic-Youth"]


def lyrics_scraping(artist):
    """goes to lyrics.com, scrapes lyrics for every song by artist and saves each song to .txt file"""
    # create folder for lyrics, if it doesn't exist yet
    try:
        os.makedirs(f"{artist}_lyrics")
    except FileExistsError:
        # directory already exists
        pass

    # get song links and song titles from artist page
    r1 = requests.get(f'https://www.lyrics.com/artist/{artist}/')
    artist_page = soup(r1.text, "html.parser")
    for i in artist_page.find_all(attrs={"class": "tal qx"}):
        link = i.find("a")
        song_title = link.get("href").split("/")[-1]
        address = "https://www.lyrics.com"
        address += link.get("href")
        r2 = requests.get(address)
        song_page = soup(r2.text, "html.parser")
        # find lyrics on page and save to .txt file
        for j in song_page.find_all(attrs={"id": "lyric-body-text"}):
            with open(f"{artist}-lyrics/{song_title}.txt", "w", encoding="utf-8") as f2:
                f2.write(j.text)


def main():
    for artist in ARTISTS:
        lyrics_scraping(artist.lower())


if __name__ == "__main__":
    main()
