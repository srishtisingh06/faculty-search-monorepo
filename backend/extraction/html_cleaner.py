"""
HTML Cleaning Layer
────────────────────
Strips scripts, styles, nav, footer, tracking attributes.
Always BeautifulSoup — never send raw HTML downstream.

This typically cuts HTML size by 60-80%, which matters both for
rule-based extraction speed and for keeping LLM fallback cheap.
"""
import re
from bs4 import BeautifulSoup

NOISE_TAGS = ["script", "style", "svg", "noscript", "iframe", "nav", "footer", "header"]
NOISE_CLASS_PATTERN = re.compile(r"(cookie|advertisement|sidebar|breadcrumb|social-share)", re.I)

# Attributes we strip unless they carry actual faculty data (some sites,
# like IIT Madras, store the whole record in data-* attributes)
KEEP_DATA_ATTRS = {"data-name", "data-mail", "data-phone", "data-designation",
                    "data-resrch", "data-researchareas", "data-office",
                    "data-profile-link", "data-personallink", "data-image"}


def clean_html(raw_html: str) -> BeautifulSoup:
    """Returns a cleaned BeautifulSoup tree, noise removed."""
    soup = BeautifulSoup(raw_html, "lxml")

    for tag in soup(NOISE_TAGS):
        tag.decompose()

    for tag in soup.find_all(class_=NOISE_CLASS_PATTERN):
        tag.decompose()

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr in KEEP_DATA_ATTRS:
                continue
            if attr.startswith(("on", "aria-", "data-track", "data-ga")):
                del tag.attrs[attr]
            elif attr == "style":
                del tag.attrs[attr]

    return soup


def to_plain_text(soup_or_tag) -> str:
    """Collapse whitespace, return readable plain text."""
    text = soup_or_tag.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()
