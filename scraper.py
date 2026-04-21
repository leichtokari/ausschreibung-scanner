import asyncio
import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from ai_model import classify_tender

DOWNLOAD_DIR = "tender_documents"
OUTPUT_EXCEL = "tenders.xlsx"

def download_file(url, site_name):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        path_dir = f"{DOWNLOAD_DIR}/{site_name}/{today}"
        os.makedirs(path_dir, exist_ok=True)

        filename = url.split("/")[-1]
        save_path = f"{path_dir}/{filename}"

        r = requests.get(url)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            return save_path
    except:
        return None
    return None

async def scrape_bayern(page):
    await page.goto("https://www.auftraege.bayern.de")
    await page.wait_for_timeout(3000)
    soup = BeautifulSoup(await page.content(), "html.parser")

    tenders = []
    for item in soup.select(".result-list-item"):
        title = item.select_one(".result-title")
        link = item.select_one("a")
        if not title or not link:
            continue

        tenders.append({
            "site": "Bayern",
            "title": title.get_text(strip=True),
            "link": link["href"],
            "description": ""
        })

    return tenders

async def scrape_munich(page):
    await page.goto("https://vergabe.muenchen.de/NetServer")
    await page.wait_for_timeout(3000)
    soup = BeautifulSoup(await page.content(), "html.parser")

    tenders = []
    for item in soup.select(".nl-list-item"):
        title = item.select_one(".nl-title")
        link = item.select_one("a")
        if not title or not link:
            continue

        tenders.append({
            "site": "Munich",
            "title": title.get_text(strip=True),
            "link": link["href"],
            "description": ""
        })

    return tenders

async def run_scraper():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        bayern = await scrape_bayern(page)
        munich = await scrape_munich(page)

        all_tenders = bayern + munich
        relevant = []

        for t in all_tenders:
            if classify_tender(t["title"]):
                relevant.append(t)

        df = pd.DataFrame(relevant)
        df.to_excel(OUTPUT_EXCEL, index=False)

        await browser.close()
        return df
