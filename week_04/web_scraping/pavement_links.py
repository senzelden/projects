from bs4 import BeautifulSoup

with open("pavement.txt", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html")
    for node in soup.findAll(attrs={"class": "tal qx"}):
        link = node.find("a")
        address = "https://www.lyrics.com"
        address += link.get("href")
        print(address)