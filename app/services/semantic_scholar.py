
from __future__ import annotations
import os
import time
import requests

API = "https://api.semanticscholar.org/graph/v1"
API_KEY_ENV = "SEMANTIC_SCHOLAR_API_KEY"

def search(
    query: str,
    limit: int = 20,
    fields: str = "title,authors,year,abstract,url,externalIds,citationCount",
    max_retries: int = 3,
):
    params = {"query": query, "limit": limit, "fields": fields}
    headers = {}
    api_key = os.environ.get(API_KEY_ENV)
    if api_key:
        headers["x-api-key"] = api_key

    for attempt in range(1, max_retries + 1):
        r = requests.get(f"{API}/paper/search", params=params, headers=headers, timeout=30)
        if r.status_code == 429 and attempt < max_retries:
            # Backoff on rate limit; give the service time to recover.
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json().get("data", [])
    return []
