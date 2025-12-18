# ITNB – AI Engineering Internship Technical Assessment

## Objective
Web Scraping, Ingestion & Chat

This project scrapes content from the ITNB website, ingests it into GroundX,
and enables a chat interface powered by GroundX search and an LLM.

---

## Versioning Approach

The assignment does not explicitly specify whether a versioning or deduplication mechanism is required to prevent re-ingesting content that already exists in the GroundX bucket. For this reason, two ingestion modes are provided:

- **1) Basic Version**. In the basic version, running the pipeline from the project root executes the full workflow: *scrape -> ingest -> chat*. All scraped chunks are ingested into GroundX every time the pipeline is executed, without checking whether the same content has been previously ingested. This version prioritizes simplicity and demonstrates the end-to-end pipeline with minimal control logic.

- **2) Deduplicated Version**. In the deduplicated version, the same pipeline is executed: *scrape -> ingest -> chat*. However, before ingestion, a local version control mechanism is applied using the file `/ingestion/ingested_hashes.json`. Each chunk is hashed and compared against previously ingested hashes. Only new or modified chunks are ingested into GroundX. This approach prevents unnecessary re-ingestion of identical content and avoids saturating the GroundX bucket with duplicate data.

---

## Project Structure
```text
ITNB_tech_assess/
├── chat/                      # Chat interface
│   └── chat.py
├── data/                      # Data storage
│   ├── raw_basic/             # Raw scraped pages (Basic Version)
│   ├── raw_deduplicate/       # Raw scraped pages (Deduplicated Version)
│   ├── cleaned_basic/         # Cleaned & chunked JSON (Basic Version)
│   └── cleaned_deduplicate/   # Cleaned & chunked JSON (Deduplicated Version)
├── ingestion/                 # Scripts to ingest data into GroundX
│   ├── ingest_basic.py
│   ├── ingest_deduplicate.py
│   └── ingested_hashes.json
├── scraping/                  # Web scraping scripts
│   ├── scrape_basic.py
│   └── scrape_deduplicate.py
├── pipeline/                  # Web scraping scripts
│   └── config.py
├── screenshots/               
├── main.py                    # Entry point 
├── requirements.txt
└── .env
```
---

## INSTALL DEPENDENCIES

Navigate to the root directory `ITNB_tech_assess` root directory

### 1. Create and activate a virtual environment (optional, but highly recommended)
**Windows (PowerShell / CMD)**
```bash
python -m venv .venv
.venv\Scripts\activate
```
**Linux / Ubuntu / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Upgrade pip (optional, recommended)
```bash
pip install --upgrade pip
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
---

## ENVIRONMENT VARIABLES
The application requires several API keys to run. 
A template file named `.env.example` is provided in the root directory (`ITNB_tech_assess`)

### 1. Create your own `.env` file by copying the example:
```bash
cp .env.example .env
```

### 2. Open `.env` and fill in your credentials for GroundX and OpenAI.
```bash
GROUNDX_API_KEY – Your API key for GroundX
GROUNDX_BUCKET_ID - The GroundX Bucket ID where data will be ingested
OPENAI_API_KEY – Your OpenAI API key for the LLM
```

---

## USAGE
The following commands can be run ***ONLY*** in the root directory (`ITNB_tech_assess`)

### STEP 1 - SCRAPE THE WEBSITE
This will scrape content from `https://www.itnb.ch/en` and store raw and cleaned data.

**Command (Basic Version)**:
```bash
python scraping/scrape_basic.py
```
or
**Command (Deduplicate Version)**:
```bash
python scraping/scrape_deduplicate.py
```
**Output directories**:
```bash
data/raw_basic/             contains full scraped pages (basic version)
data/raw_deduplicate/       contains full scraped pages (deduplicate version)
data/cleaned_basic/         contains cleaned and chunked JSON files (basic version)
data/cleaned_deduplicate/   contains cleaned and chunked JSON files (deduplicate version)
```

---

### STEP 2 - INGEST DATA INTO GROUNDX
Uploads all cleaned chunks to the configured GroundX bucket and logs success/failure for each item.

**Command (Basic Version)**:
```bash
python ingestion/ingest_basic.py
```
or
**Command (Deduplicate Version)**:
```bash
python ingestion/ingest_deduplicate.py
```
**Expected Output / Log:**

A console output showing `[SUCCESS]` or `[ERROR]` for each file, also `[SKIP]` for the *Deduplicate Version*

A log file ingestion.log will be created with the same messages.

---

### STEP 3 - START THE CHAT INTERFACE
Starts an interactive chat over the ingested content.

**Command**:
```bash
python chat/chat.py
```

**Example interaction**:
```text
> You: What services does ITNB offer?
Answer: ITNB provides consulting, IT solutions, and support for digital transformation projects.

> You: Where is ITNB located?
Answer: ITNB's headquarters are in Switzerland.
```

Type your question and press Enter.
Type 'exit' to quit.

---

### RUN ALL STEPS AT ONCE

If you want to run scraping, ingestion, and start the chat in sequence automatically, you can use `main.py`:

**Command (Basic Version)**:
```bash
python main.py
```
or
**Command (Deduplicate Version)**:
```bash
python main.py --deduplicate
```

---

### NOTES

- The assistant answers strictly using retrieved GroundX context.
- If no relevant content is found, the assistant will say it does not know.
- Scraping depth and page limits can be adjusted in scraping/scrape.py.

---
