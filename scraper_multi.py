import requests
from bs4 import BeautifulSoup
import pandas as pd
from ai_model import classify_tender

OUTPUT_EXCEL = "tenders.xlsx"


#############################################################
#  UTILITIES
#############################################################

def fetch(url, timeout=12):
    """Fetch page safely."""
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return r.text
    except:
        pass
    return ""


def extract_description_from_link(url):
    """Try to load a detail page and extract some description text."""
    html = fetch(url)
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Common text containers
    selectors = [
        "p", "div", ".description", ".content", ".detail", ".body"
    ]

    for sel in selectors:
        blocks = soup.select(sel)
        if blocks:
            text = " ".join(b.get_text(" ", strip=True) for b in blocks)
            return text[:1500]  # Limit length for safety

    return ""


#############################################################
# 1) Bayern
#############################################################
def scrape_bayern():
    url = "https://www.auftraege.bayern.de"
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    for item in soup.select(".result-list-item"):
        title = item.select_one(".result-title")
        link = item.select_one("a")

        if not title or not link:
            continue

        link_url = link.get("href")
        desc = extract_description_from_link(link_url)

        tenders.append({
            "site": "Bayern",
            "title": title.get_text(strip=True),
            "description": desc,
            "link": link_url
        })

    return tenders


#############################################################
# 2) NetServer cluster (xVergabe, Munich, Autobahn, RLP, BW)
#############################################################
def scrape_netserver(url, site_name):
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    # NetServer sites use either .nl-list-item OR .result-list-item
    for item in soup.select(".nl-list-item, .result-list-item"):
        title = item.select_one(".nl-title, .result-title")
        link = item.select_one("a")

        if not title or not link:
            continue

        link_url = link.get("href")
        # NetServer links might be relative
        if link_url.startswith("/"):
            base = url.split("/NetServer")[0]
            link_url = base + link_url

        desc = extract_description_from_link(link_url)

        tenders.append({
            "site": site_name,
            "title": title.get_text(strip=True),
            "description": desc,
            "link": link_url
        })

    return tenders


#############################################################
# 3) DTVP
#############################################################
def scrape_dtvp():
    url = "https://www.dtvp.de/Center/public/projectsearch"
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    for item in soup.select(".project-result"):
        title = item.select_one(".project-title")
        link = item.select_one("a")

        if not title or not link:
            continue

        link_url = link.get("href")
        desc = extract_description_from_link(link_url)

        tenders.append({
            "site": "DTVP",
            "title": title.get_text(strip=True),
            "description": desc,
            "link": link_url
        })

    return tenders


#############################################################
# 4) eVergabe Online
#############################################################
def scrape_evergabe():
    url = "https://www.evergabe-online.de/oeffentliche-ausschreibungen"
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    for item in soup.select(".search-result-item"):
        title = item.select_one(".title")
        link = item.select_one("a")

        if not title or not link:
            continue

        link_url = link.get("href")
        desc = extract_description_from_link(link_url)

        tenders.append({
            "site": "eVergabe",
            "title": title.get_text(strip=True),
            "description": desc,
            "link": link_url
        })

    return tenders


#############################################################
# 5) HAD Hessen
#############################################################
def scrape_had():
    url = "https://www.had.de"
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    for row in soup.select("table tr"):
        cols = row.select("td")
        if len(cols) < 2:
            continue

        title = cols[1].get_text(strip=True)
        desc = extract_description_from_link(url)

        tenders.append({
            "site": "HAD Hessen",
            "title": title,
            "description": desc,
            "link": url
        })

    return tenders


#############################################################
# 6) TED EU API
#############################################################
def scrape_ted():
    api_url = "https://ted.europa.eu/api/v2/notices/search?fields=TITLE,DESCRIPTION"
    try:
        r = requests.get(api_url, timeout=12)
        data = r.json()
    except:
        return []

    tenders = []

    for item in data.get("results", []):
        title = item.get("title", [""])[0]
        desc = item.get("description", [""])[0] if "description" in item else ""

        tenders.append({
            "site": "TED EU",
            "title": title,
            "description": desc,
            "link": "https://ted.europa.eu"
        })

    return tenders


#############################################################
# 7) MAIN RUNNER — scans all sites + AI filter
#############################################################
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

    # eVergabe
    all_tenders += scrape_evergabe()

    # Hessen HAD
    all_tenders += scrape_had()

    # EU TED
    all_tenders += scrape_ted()

    #################################################
    # AI FILTER (title + description)
    #################################################
    relevant = []
    for t in all_tenders:
        if classify_tender(t["title"], t["description"]):
            relevant.append(t)

    df = pd.DataFrame(relevant)
    df.to_excel(OUTPUT_EXCEL, index=False)

    return df

