import os
from dotenv import load_dotenv
from groundx import GroundX
from openai import OpenAI
from colorama import init, Fore, Style
import json
import re
import logging

# Mute warnings
logging.getLogger("httpx").setLevel(logging.WARNING)
init(autoreset=True)

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

GROUNDX_API_KEY = os.getenv("GROUNDX_API_KEY")
GROUNDX_BUCKET_ID = int(os.getenv("GROUNDX_BUCKET_ID"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL_NAME")

if not all([GROUNDX_API_KEY, OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL]):
    raise ValueError("Missing required environment variables")

# --------------------------------------------------
# Client
# --------------------------------------------------
gx_client = GroundX(api_key=GROUNDX_API_KEY)

llm_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

# --------------------------------------------------
# Functions
# --------------------------------------------------
def retrieve_context(question):
    return gx_client.search.content(
        id=GROUNDX_BUCKET_ID,
        query=question,
    )

def get_top_matching_chunk(search_response, max_chars=200):
    results = getattr(search_response.search, "results", [])
    if results:
        raw_text = results[0].text
        if raw_text and raw_text.strip():
            return raw_text[:max_chars]

    aggregated = getattr(search_response.search, "text", None)
    if aggregated and aggregated.strip():
        return aggregated[:max_chars]

    return None


def generate_answer(question, search_response):
    llm_text = search_response.search.text

    instruction = (
        "You are an assistant answering questions strictly using the provided context. "
        "Be precise, concise, and direct. Avoid unnecessary explanations. "
        "If the answer is not present, say you do not know."
    )

    completion = llm_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": f"{instruction}\n===\n{llm_text}\n==="},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content.strip()

# --------------------------------------------------
# Chat client
# --------------------------------------------------
def main():
    print("\n" + "="*80)
    print("ITNB Chat")
    print("Type 'exit' to quit\n")

    while True:
        print(" "*50)
        print("="*100)
        question = input(Fore.CYAN + "You: " + Fore.WHITE)
        if question.lower() in ("exit", "quit"):
            break

        try:
            search_response = retrieve_context(question)

            if not search_response or not getattr(search_response.search, "text", None):
                print("\nNo relevant content found.\n")
                continue

            # Retrieve top-matching chunk
            chunk = get_top_matching_chunk(search_response)

            # Extract title and URL of top-matching chunk
            title = "Unknown title"
            url = "Unknown URL"
            results = getattr(search_response.search, "results", [])
            if results:
                raw_text = results[0].text
                title_match = re.search(r'"title"\s*:\s*"([^"]+)"', raw_text or "")
                url_match = re.search(r'"url"\s*:\s*"([^"]+)"', raw_text or "")
                if title_match:
                    title = title_match.group(1)
                if url_match:
                    url = url_match.group(1)

            # Display top-matching chunk
            print(Fore.MAGENTA + "\nTop-matching chunk:")
            print(Fore.WHITE + (chunk if chunk else "No content retrieved.") + "\n")

            # Display source
            print(Fore.YELLOW + "Source:" + Fore.WHITE + f" {title} — {url}\n")

            # Show LLMresponse
            answer = generate_answer(question, search_response)
            print(Fore.GREEN + "Answer:")
            print(Fore.WHITE + f"{answer}\n")

        except Exception as e:
            print(Fore.RED + "[ERROR] " + str(e))

if __name__ == "__main__":
    main()
