import argparse
import asyncio

from pipeline.config import PipelineConfig

from scraping.scrape_basic import main as scrape_basic
from scraping.scrape_deduplicate import main as scrape_deduplicate

from ingestion.ingest_basic import main as ingest_basic
from ingestion.ingest_deduplicate import main as ingest_deduplicate

from chat.chat import main as chat_main


async def run_pipeline(config: PipelineConfig):
    # Scraping
    if config.deduplicate:
        print("Scraping (deduplicate)")
        await scrape_deduplicate()
    else:
        print("Scraping (basic)")
        await scrape_basic()

    # Ingestion
    if config.deduplicate:
        print("Ingestion (deduplicate)")
        ingest_deduplicate()
    else:
        print("Ingestion (basic)")
        ingest_basic()

    # Chat
    chat_main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deduplicate",
        action="store_true",
        help="Run scraping + ingestion with deduplication"
    )
    args = parser.parse_args()

    config = PipelineConfig(deduplicate=args.deduplicate)
    asyncio.run(run_pipeline(config))

