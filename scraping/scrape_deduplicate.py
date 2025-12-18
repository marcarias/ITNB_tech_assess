import os
import json
import asyncio
import re
import hashlib
from crawl4ai import AsyncWebCrawler

# --------------------------------------------------
# Paths and URL configuration
# --------------------------------------------------
BASE_URL = "https://www.itnb.ch/en"
RAW_DIR = "data/raw_deduplicate"
CLEAN_DIR = "data/cleaned_deduplicate"
CHUNK_SIZE = 200   

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

# --------------------------------------------------
# Functions
# --------------------------------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"\n+", "\n", text)
    return text.strip()

def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())

def chunk_text(text: str, chunk_size=CHUNK_SIZE):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield i, " ".join(words[i:i + chunk_size])

def make_page_id(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()

def make_chunk_hash(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

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

        existing_page_ids = set()
        for f in os.listdir(RAW_DIR):
            if not f.endswith(".json"):
                continue
            with open(os.path.join(RAW_DIR, f), "r", encoding="utf-8") as jf:
                existing_page_ids.add(json.load(jf).get("page_id"))

        raw_index = len(existing_page_ids)

        for page in pages:
            # Extract content
            content = getattr(page, "markdown", None) or getattr(page, "text", None)
            if not content:
                continue

            # RAW data management (page)
            url = getattr(page, "url", BASE_URL)
            title = f"Page {raw_index+1}"
            page_id = make_page_id(url)

            if page_id not in existing_page_ids:
                raw_data = {
                    "page_id": page_id,
                    "url": url,
                    "title": title,
                    "content": content
                }

                raw_path = os.path.join(RAW_DIR, f"page_{raw_index + 1}.json")
                with open(raw_path, "w", encoding="utf-8") as f:
                    json.dump(raw_data, f, ensure_ascii=False, indent=2)

                existing_page_ids.add(page_id)
                raw_index += 1
                print(f"[RAW] New page saved: {url}")
            else:
                print(f"[RAW] Skipped existing page: {url}")


            # CLEAN data management (chunks)
            cleaned = clean_text(content)

            for chunk_index, chunk in chunk_text(cleaned):
                chunk_hash = make_chunk_hash(chunk)
                clean_path = os.path.join(CLEAN_DIR, f"{chunk_hash}.json")

                if os.path.exists(clean_path):
                    print(f"[CLEAN] Skipping existing chunk: {chunk_hash}")
                    continue  

                clean_data = {
                    "page_id": page_id,
                    "url": url,
                    "title": title,
                    "chunk_index": chunk_index//CHUNK_SIZE,
                    "chunk_hash": chunk_hash,
                    "content": chunk
                }

                with open(clean_path, "w", encoding="utf-8") as f:
                    json.dump(clean_data, f, ensure_ascii=False, indent=2)

                print(f"[CLEAN] New chunk saved: {chunk_hash}")

if __name__ == "__main__":
    asyncio.run(main())
