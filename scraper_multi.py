import requests
from bs4 import BeautifulSoup
import pandas as pd
from ai_model import classify_tender

OUTPUT_EXCEL = "tenders.xlsx"

###############
# 1) Bayern
###############
def scrape_bayern():
    url = "https://www.auftraege.bayern.de"
    try:
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
                "link": link.get("href")
            })
        return tenders
    except:
        return []

######################
# 2) NetServer family
######################
def scrape_netserver(url, site_name):
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")

        tenders = []
        for item in soup.select(".nl-list-item, .result-list-item"):
            title = item.select_one(".nl-title, .result-title")
            link = item.select_one("a")
            if not title or not link:
                continue

            tenders.append({
                "site": site_name,
                "title": title.get_text(strip=True),
                "link": link.get("href")
            })
        return tenders
    except:
        return []

###########################
# 3) DTvP – Deutsches Vergabeportal
###########################
def scrape_dtvp():
    url = "https://www.dtvp.de/Center/public/projectsearch"
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")

        tenders = []
        for item in soup.select(".project-result"):
            title = item.select_one(".project-title")
            link = item.select_one("a")
            if not title or not link:
                continue
            tenders.append({
                "site": "DTVP",
                "title": title.get_text(strip=True),
                "link": link.get("href")
            })
        return tenders
    except:
        return []

###################
# 4) eVergabe Online
###################
def scrape_evergabe():
    url = "https://www.evergabe-online.de/oeffentliche-ausschreibungen"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        tenders = []
        for item in soup.select(".search-result-item"):
            title = item.select_one(".title")
            link = item.select_one("a")
            if not title or not link:
                continue
            tenders.append({
                "site": "eVergabe",
                "title": title.get_text(strip=True),
                "link": link.get("href")
            })
        return tenders
    except:
        return []

##################
# 5) Hessen HAD
##################
def scrape_had():
    url = "https://www.had.de"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        tenders = []
        for item in soup.select("table tr"):
            cols = item.select("td")
            if len(cols) > 1:
                title = cols[1].get_text(strip=True)
                tenders.append({
                    "site": "HAD Hessen",
                    "title": title,
    
