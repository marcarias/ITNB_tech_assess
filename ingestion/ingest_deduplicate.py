from groundx import Document, GroundX
from dotenv import load_dotenv
import os
import logging
import json

# Mute warnings
logging.getLogger("httpx").setLevel(logging.WARNING)

# --------------------------------------------------
# Load environment variables and paths
# --------------------------------------------------
load_dotenv()

GROUNDX_API_KEY = os.getenv("GROUNDX_API_KEY")
GROUNDX_BUCKET_ID = int(os.getenv("GROUNDX_BUCKET_ID"))

CLEAN_DIR = "data/cleaned_deduplicate"
HASH_DB = "ingestion/ingested_hashes.json"

if not GROUNDX_API_KEY:
    raise ValueError("GROUNDX_API_KEY not set in environment or .env")


# --------------------------------------------------
# Logging
# --------------------------------------------------
os.makedirs("ingestion", exist_ok=True)
log_file = os.path.join("ingestion", "ingestion_logfile.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file), 
        logging.StreamHandler()         
    ]
)

# --------------------------------------------------
# Client
# --------------------------------------------------
client = GroundX(api_key=GROUNDX_API_KEY)

# --------------------------------------------------
# Functions
# --------------------------------------------------
def load_hashes():
    if not os.path.exists(HASH_DB) or os.path.getsize(HASH_DB) == 0:
        return set()
    try:
        with open(HASH_DB, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except json.JSONDecodeError:
        return set()


def save_hashes(hashes):
    with open(HASH_DB, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, indent=2)


# --------------------------------------------------
# Ingestion (reporting success or failure for each ingested item)
# --------------------------------------------------
def main():
    logging.info("="*100)
    logging.info("Starting item ingestion to GroundX...\n")

    known_hashes = load_hashes()
    success = 0
    failure = 0
    skipped = 0

    failed_items = []
    
    for file_name in sorted(os.listdir(CLEAN_DIR)):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(CLEAN_DIR, file_name)


        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            chunk_hash = data.get("chunk_hash")
            if chunk_hash in known_hashes:
                logging.info(f"[SKIP] Duplicate chunk skipped: {file_name}")
                skipped += 1
                continue

            document = Document(
                bucket_id=GROUNDX_BUCKET_ID,
                file_name=file_name,
                file_path=file_path,
                file_type="json",
            )

            response = client.ingest(documents=[document])

            known_hashes.add(chunk_hash)
            success += 1
            logging.info(f"[SUCCESS] Ingested: {file_name}")

        except Exception as e:
            logging.error(f"[ERROR] Failed to ingest {file_name}: {e}")
            failed_items.append(file_name)
            failure += 1

    save_hashes(known_hashes)

    logging.info("\nSummary:")
    logging.info(f"Ingested : {success}")
    logging.info(f"Skipped  : {skipped}")
    logging.info(f" Failed  : {failure}")
    logging.info(f" Total   : {success + skipped + failure}")

    if failed_items:
        logging.info("\nFailed items:")
        for item in failed_items:
            logging.info(f" - {item}")

if __name__ == "__main__":
    main()