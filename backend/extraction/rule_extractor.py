"""
Rule-Based Extraction Layer
─────────────────────────────
Cheap, fast, deterministic. Tries multiple strategies in order.
Returns None if nothing matched well — that's the signal for the
pipeline to escalate to the LLM fallback.

These strategies are generalized from what you already hand-wrote
for IIT Bombay (CSS classes), IIT Madras (data-* attributes),
IIT Delhi (heading walking), and IIT Kanpur (h5 + sibling text).
"""
import re
from bs4 import BeautifulSoup, Tag

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")
SCHOLAR_RE = re.compile(r"scholar\.google\.[a-z.]+/citations\?[^\s\"'<>]+")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[^\s\"'<>]+")
ORCID_RE = re.compile(r"orcid\.org/[0-9\-X]{9,}")

DESIGNATION_KEYWORDS = [
    "Professor", "Associate Professor", "Assistant Professor",
    "Lecturer", "Reader", "Head of Department", "HOD", "Dean",
]


def _find_link(text: str, pattern: re.Pattern, prefix: str = "https://") -> str:
    m = pattern.search(text)
    if not m:
        return ""
    val = m.group()
    return val if val.startswith("http") else prefix + val


def _strategy_data_attributes(card: Tag) -> dict | None:
    """Strategy A — sites that embed everything in data-* attrs (IIT Madras style)."""
    if not card.get("data-name"):
        return None

    email = (card.get("data-mail", "") or "").replace("[at]", "@").replace("[dot]", ".")
    research = card.get("data-resrch", "") or card.get("data-researchareas", "")

    return {
        "name": card.get("data-name", "").strip(),
        "designation": card.get("data-designation", "").strip(),
        "email": email.strip(),
        "phone": card.get("data-phone", "").strip(),
        "research_areas": [r.strip() for r in research.split(",") if r.strip()],
        "profile_url": card.get("data-profile-link", "") or card.get("data-personallink", ""),
    }


def _strategy_heading_proximity(card: Tag) -> dict | None:
    """Strategy B — generic: a heading tag is the name, email/phone found nearby in text."""
    heading = card.find(["h1", "h2", "h3", "h4", "h5", "h6"])
    if not heading:
        return None

    name = heading.get_text(strip=True)
    if not name or len(name.split()) > 6:
        return None

    full_text = card.get_text(" ", strip=True)

    designation = ""
    for kw in DESIGNATION_KEYWORDS:
        if kw.lower() in full_text.lower():
            designation = kw
            break

    email_match = EMAIL_RE.search(full_text)
    phone_match = PHONE_RE.search(full_text)

    link = card.find("a", href=True)
    profile_url = link["href"] if link else ""

    return {
        "name": name,
        "designation": designation,
        "email": email_match.group() if email_match else "",
        "phone": phone_match.group() if phone_match else "",
        "research_areas": [],
        "profile_url": profile_url,
    }

def _strategy_table_row(card: Tag) -> dict | None:
    """Strategy — plain <tr> table rows (NIT Trichy style: S# | Staff# | Name | Gender | Designation | Dept)."""
    if card.name != "tr":
        return None
    cells = card.find_all("td")
    if len(cells) < 3:
        return None

    cell_texts = [c.get_text(strip=True) for c in cells]

    # Find the cell that looks like a person's name (has a link, or 2-5 capitalized words)
    name = ""
    profile_url = ""
    designation = ""

    for i, cell in enumerate(cells):
        text = cell_texts[i]
        link = cell.find("a", href=True)
        if link and len(text.split()) <= 6 and len(text) > 4:
            name = text
            profile_url = link["href"]
            break

    if not name:
        # Fallback: look for a cell that looks like "Dr.X.Y.NAME" or all-caps name
        for text in cell_texts:
            if re.match(r"^(Dr\.|Prof\.)?[A-Z][A-Za-z.\s]{4,40}$", text) and len(text.split()) <= 6:
                name = text
                break

    if not name:
        return None

    for text in cell_texts:
        if any(kw in text for kw in DESIGNATION_KEYWORDS):
            designation = text
            break

    return {
        "name": name.replace("Dr.", "Dr. ").strip(),
        "designation": designation,
        "email": "",
        "phone": "",
        "research_areas": [],
        "profile_url": profile_url,
    }




def _strategy_definition_list(card: Tag) -> dict | None:
    """Strategy C — dt/dd pairs, common in older static sites."""
    dts = card.find_all("dt")
    if not dts:
        return None
    pairs = {}
    for dt in dts:
        dd = dt.find_next_sibling("dd")
        if dd:
            pairs[dt.get_text(strip=True).lower()] = dd.get_text(strip=True)

    name = pairs.get("name", "")
    if not name:
        return None

    return {
        "name": name,
        "designation": pairs.get("designation", "") or pairs.get("title", ""),
        "email": pairs.get("email", ""),
        "phone": pairs.get("phone", ""),
        "research_areas": [r.strip() for r in pairs.get("research", "").split(",") if r.strip()],
        "profile_url": "",
    }


STRATEGIES = [_strategy_data_attributes, _strategy_table_row, _strategy_definition_list, _strategy_heading_proximity]

def rule_extract(card_html: str) -> dict | None:
    """
    Try each strategy in order. Returns the first successful extraction,
    enriched with scholar/linkedin/orcid links found anywhere in the card.
    Returns None if no strategy produced a plausible name.
    """
    soup = BeautifulSoup(card_html, "lxml")
    # lxml wraps fragments in <html><body> — skip past those to the real card
    card = soup.body.find() if soup.body and soup.body.find() else soup

    full_text = card.get_text(" ", strip=True)
    full_html = str(card)

    for strategy in STRATEGIES:
        result = strategy(card)
        if result and result.get("name") and 2 <= len(result["name"].split()) <= 6:
            result["scholar_url"] = _find_link(full_html, SCHOLAR_RE)
            result["linkedin_url"] = _find_link(full_html, LINKEDIN_RE)
            result["orcid_url"] = _find_link(full_html, ORCID_RE)
            return result

    return None
