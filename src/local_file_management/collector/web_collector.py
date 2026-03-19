import requests
from bs4 import BeautifulSoup


def collect_web_text(url: str, timeout: int = 10) -> str:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return " ".join(soup.get_text(separator=" ").split())
