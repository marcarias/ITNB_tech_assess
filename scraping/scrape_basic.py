import os
import json
import asyncio
import re
from crawl4ai import AsyncWebCrawler

# --------------------------------------------------
# Paths and URL configuration
# --------------------------------------------------
BASE_URL = "https://www.itnb.ch/en"
RAW_DIR = "data/raw_basic"
CLEAN_DIR = "data/cleaned_basic"
CHUNK_SIZE = 200   

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

# --------------------------------------------------
# Functions
# --------------------------------------------------
def clean_text(text):
    text = re.sub(r"\n+", "\n", text)
    return text.strip()

def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

# --------------------------------------------------
# Scraper
# --------------------------------------------------
async def main():
    print("\n" + "="*80)
    print(f"Starting scraping from {BASE_URL}...\n")

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=BASE_URL,
            max_pages=10,
            max_depth=1,    # "Crawl and extract textual content exclusively from https://www.itnb.ch/en"
            same_domain_only=True
        )

        pages = result._results
        print(f"Pages scraped: {len(pages)}")

        for i, page in enumerate(pages):
            # Extract content
            content = getattr(page, "markdown", None) or getattr(page, "text", None)
            if not content:
                continue

            # RAW data management (page)
            raw_data = {
                "url": getattr(page, "url", BASE_URL),
                "title": getattr(page, "title", f"Page {i + 1}"),
                "content": content
            }
            raw_path = os.path.join(RAW_DIR, f"page_{i + 1}.json")
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=2)

            # CLEAN data management (chunks)
            for j, chunk in enumerate(chunk_text(clean_text(content))):
                clean_data = {
                    "url": raw_data["url"],
                    "title": raw_data["title"],
                    "content": chunk
                }
                clean_path = os.path.join(CLEAN_DIR, f"page_{i + 1}_chunk_{j + 1}.json")
                with open(clean_path, "w", encoding="utf-8") as f:
                    json.dump(clean_data, f, ensure_ascii=False, indent=2)

            print(f"[OK] Saved page_{i + 1}.json + {j + 1} chunks")

if __name__ == "__main__":
    asyncio.run(main())
