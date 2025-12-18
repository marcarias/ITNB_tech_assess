from groundx import Document, GroundX
from dotenv import load_dotenv
import os
import logging

# Mute warnings
logging.getLogger("httpx").setLevel(logging.WARNING)

# --------------------------------------------------
# Load environment variables and paths
# --------------------------------------------------
load_dotenv()

GROUNDX_API_KEY = os.getenv("GROUNDX_API_KEY")
GROUNDX_BUCKET_ID = int(os.getenv("GROUNDX_BUCKET_ID"))

CLEAN_DIR = "data/cleaned_basic"

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
# Ingestion (reporting success or failure for each ingested item)
# --------------------------------------------------
def main():
    logging.info("="*100)
    logging.info("Starting item ingestion to GroundX...\n")

    success = 0
    failure = 0
    failed_items = []

    existing_files = set(os.listdir(CLEAN_DIR))
    
    for file_name in sorted(os.listdir(CLEAN_DIR)):
        file_path = os.path.join(CLEAN_DIR, file_name)

        if not file_name.endswith(".json"):
            continue

        try:
            document = Document(
                bucket_id=GROUNDX_BUCKET_ID,
                file_name=file_name,
                file_path=file_path,
                file_type="json",
            )

            response = client.ingest(documents=[document])

            logging.info(f"[SUCCESS] Ingested: {file_name}")
            success += 1

        except Exception as e:
            logging.error(f"[ERROR] Failed to ingest {file_name}: {e}")
            failed_items.append(file_name)
            failure += 1

    logging.info(f"\nSuccessful items: {success}/{success+failure}")

    if failed_items:
        logging.info("\nReview the following failures:")
        for item in failed_items:
            logging.info(f" - {item}")

if __name__ == "__main__":
    main()