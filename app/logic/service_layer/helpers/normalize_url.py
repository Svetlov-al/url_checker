from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path
    return domain.lower()
