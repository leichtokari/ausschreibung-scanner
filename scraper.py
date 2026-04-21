import requests
from bs4 import BeautifulSoup
import pandas as pd
from ai_model import classify_tender

OUTPUT_EXCEL = "tenders.xlsx"


def scrape_bayern():
    url = "https://www.auftraege.bayern.de"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    tenders = []

    for item in soup.select(".result-list-item"):
        title = item.select_one(".result-title")
        link = item.select_one("a")

        if not title or not link:
            continue

        tenders.append({
            "site": "Bayern",
            "title": title.get_text(strip=True),
            "link": link.get("href"),
            "description": ""
        })

    return tenders


def scrape_munich():
    url = "https://vergabe.muenchen.de/NetServer"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    tenders = []

    for item in soup.select(".nl-list-item"):
        title = item.select_one(".nl-title")
        link = item.select_one("a")

        if not title or not link:
            continue

        tenders.append({
            "site": "Munich",
            "title": title.get_text(strip=True),
            "link": link.get("href"),
            "description": ""
        })

    return tenders



async def run_scraper():
    # Scraping both sites
    bayern = scrape_bayern()
    munich = scrape_munich()

    all_tenders = bayern + munich
    relevant = []

    for t in all_tenders:
        if classify_tender(t["title"]):
            relevant.append(t)

    df = pd.DataFrame(relevant)
    df.to_excel(OUTPUT_EXCEL, index=False)

    return df
