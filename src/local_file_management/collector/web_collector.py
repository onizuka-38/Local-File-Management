import time

import requests
from bs4 import BeautifulSoup


def collect_web_text(url: str, timeout: int = 10, max_retries: int = 2) -> str:
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return " ".join(soup.get_text(separator=" ").split())
        except requests.RequestException as exc:
            last_error = exc
            if attempt == max_retries:
                break
            time.sleep(0.5 * (attempt + 1))

    if last_error is not None:
        raise last_error
    return ""
