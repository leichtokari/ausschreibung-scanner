import requests
from bs4 import BeautifulSoup
import pandas as pd
from ai_model import classify_tender

OUTPUT_EXCEL = "tenders.xlsx"


########################
# 1) Bayern
########################
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


##############################
# 2) NetServer (shared logic)
##############################
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
# 3) DTVP Portal
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


###############################
# 4) eVergabe Online
###############################
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


###############################
# 5) Hessen HAD
###############################
def scrape_had():
    url = "https://www.had.de"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        tenders = []
        for row in soup.select("table tr"):
            cols = row.select("td")
            if len(cols) > 1:
                title = cols[1].get_text(strip=True)
                tenders.append({
                    "site": "HAD Hessen",
                    "title": title,
                    "link": url
                })
        return tenders
    except:
        return []


###############################
# 6) EU TED (API)
###############################
def scrape_ted():
    api_url = "https://ted.europa.eu/api/v2/notices/search?fields=TITLE"
    try:
        r = requests.get(api_url, timeout=12)
        data = r.json()

        tenders = []
        for item in data.get("results", []):
            title = item.get("title", [""])[0]
            tenders.append({
                "site": "TED EU",
                "title": title,
                "link": "https://ted.europa.eu"
            })
        return tenders
    except:
        return []


###############################
# 7) MAIN SCRAPER
###############################
async def run_scraper():
    all_tenders = []

    # Bayern
    all_tenders += scrape_bayern()

    # NetServer group
    netservers = [
        ("https://xvergabe.de/NetServer/PublicationSearchControllerServlet?Max=50&Category=InvitationToTender&Gesetzesgrundlage=VOL&function=SearchPublications&thContext=publications", "xVergabe"),
        ("https://vergabe.muenchen.de/NetServer", "Munich"),
        ("https://vergabe.autobahn.de/NetServer/PublicationSearchControllerServlet?function=SearchPublications&Gesetzesgrundlage=All&Category=InvitationToTender&thContext=publications", "Autobahn"),
        ("https://vergabe.landbw.de/NetServer", "LandBW"),
        ("https://www.vergabe.rlp.de/VMPCenter/company/welcome.do", "RLP")
    ]
    for url, name in netservers:
        all_tenders += scrape_netserver(url, name)

    # DTVP
    all_tenders += scrape_dtvp()

    # eVergabe Online
    all_tenders += scrape_evergabe()

    # Hessen HAD
    all_tenders += scrape_had()

    # TED EU
    all_tenders += scrape_ted()

    # AI Filter
    relevant = [t for t in all_tenders if classify_tender(t["title"])]

    df = pd.DataFrame(relevant)
    df.to_excel(OUTPUT_EXCEL, index=False)

    return df
