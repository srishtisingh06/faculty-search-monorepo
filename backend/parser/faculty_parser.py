"""
Faculty Parser: extracts structured faculty data from raw HTML profile pages.

Input : raw HTML file path + crawl metadata
Output: FacultyProfile dataclass / dict ready for DB insertion
"""
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# ── Regex patterns ─────────────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+91[\s\-]?)?[\(]?[0-9]{2,5}[\)]?[\s\-]?[0-9]{3,5}[\s\-]?[0-9]{3,5}")
SCHOLAR_RE = re.compile(r"scholar\.google\.[a-z.]+/citations\?[^\s\"'<>]+")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[^\s\"'<>]+")
ORCID_RE = re.compile(r"orcid\.org/[0-9\-X]{9,}")

DESIGNATION_KEYWORDS = [
    "Professor", "Associate Professor", "Assistant Professor",
    "Lecturer", "Senior Lecturer", "Reader",
    "Research Scientist", "Visiting Faculty", "Adjunct",
    "Dean", "Head of Department", "HOD",
]

STOP_TAGS = {"script", "style", "noscript", "iframe", "svg", "path"}


# ── Data model ─────────────────────────────────────────────────────────────────
@dataclass
class FacultyProfile:
    faculty_name: str = ""
    designation: str = ""
    department: str = ""
    email: str = ""
    phone: str = ""
    office: str = ""
    research_interests: list[str] = field(default_factory=list)
    research_areas: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    publications: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    google_scholar: str = ""
    linkedin: str = ""
    personal_website: str = ""
    profile_image: str = ""
    profile_url: str = ""
    institute_name: str = ""
    institute_type: str = ""
    raw_html_path: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ── Helpers ────────────────────────────────────────────────────────────────────
def _clean_text(text: str) -> str:
    """Normalise whitespace and strip HTML noise."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _get_text(soup: BeautifulSoup) -> str:
    """Full visible text, excluding script/style."""
    for tag in soup(STOP_TAGS):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def _extract_name(soup: BeautifulSoup) -> str:
    # Priority: h1 → h2 → <title> → meta og:title
    for tag in soup.find_all(["h1", "h2"]):
        text = _clean_text(tag.get_text())
        if 3 <= len(text.split()) <= 8 and not any(
            kw in text.lower() for kw in ("department", "faculty of", "welcome", "home")
        ):
            return text
    title = soup.find("title")
    if title:
        t = _clean_text(title.get_text()).split("|")[0].split("–")[0].strip()
        if 2 <= len(t.split()) <= 6:
            return t
    return ""


def _extract_designation(full_text: str) -> str:
    for desig in DESIGNATION_KEYWORDS:
        pattern = re.compile(
            r"(?:^|\n|\s)(" + re.escape(desig) + r"[^\n,]*)", re.I
        )
        m = pattern.search(full_text)
        if m:
            return _clean_text(m.group(1))
    return ""


def _extract_email(full_text: str) -> str:
    emails = EMAIL_RE.findall(full_text)
    # Filter out noreply, example.com, image extensions
    for e in emails:
        if not re.search(r"\.(png|jpg|gif|svg|css|js)$", e, re.I):
            if "noreply" not in e and "example" not in e:
                return e.lower()
    return ""


def _extract_phone(full_text: str) -> str:
    matches = PHONE_RE.findall(full_text)
    for m in matches:
        cleaned = re.sub(r"\s+", "", m)
        if len(cleaned) >= 7:
            return cleaned
    return ""


def _extract_list_section(soup: BeautifulSoup, keywords: list[str]) -> list[str]:
    """
    Finds a section heading matching any keyword, then collects
    the list items or paragraphs that follow it.
    """
    results: list[str] = []
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    for heading in headings:
        text = heading.get_text(strip=True).lower()
        if any(kw.lower() in text for kw in keywords):
            # Walk siblings until next heading
            sibling = heading.find_next_sibling()
            while sibling and not re.match(r"^h[1-6]$", sibling.name or ""):
                if sibling.name in ("ul", "ol"):
                    for li in sibling.find_all("li"):
                        t = _clean_text(li.get_text())
                        if t:
                            results.append(t)
                elif sibling.name == "p":
                    t = _clean_text(sibling.get_text())
                    if t:
                        results.extend(re.split(r"[;\n]", t))
                sibling = sibling.find_next_sibling()
            break
    return [r.strip() for r in results if r.strip()][:30]


def _extract_education(soup: BeautifulSoup) -> list[str]:
    return _extract_list_section(soup, ["education", "qualification", "academic background", "degree"])


def _extract_publications(soup: BeautifulSoup) -> list[str]:
    return _extract_list_section(soup, ["publications", "journal", "conference", "papers", "books"])[:20]


def _extract_projects(soup: BeautifulSoup) -> list[str]:
    return _extract_list_section(soup, ["projects", "funded projects", "research projects", "grants"])


def _extract_research(soup: BeautifulSoup) -> tuple[list[str], list[str]]:
    interests = _extract_list_section(soup, ["research interest", "areas of interest", "research focus"])
    areas = _extract_list_section(soup, ["research area", "specialization", "expertise"])
    return interests, areas


def _extract_office(full_text: str) -> str:
    m = re.search(r"(?:office|room|cabin|chamber)[:\s]+([A-Z0-9\-/,\s]{3,30})", full_text, re.I)
    return _clean_text(m.group(1)) if m else ""


def _extract_profile_image(soup: BeautifulSoup, base_url: str) -> str:
    for img in soup.find_all("img"):
        src = img.get("src", "") or img.get("data-src", "")
        alt = img.get("alt", "").lower()
        cls = " ".join(img.get("class", [])).lower()
        if any(kw in alt + cls for kw in ("profile", "faculty", "photo", "avatar", "picture")):
            return urljoin(base_url, src)
    return ""


def _extract_links(soup: BeautifulSoup, full_text: str) -> tuple[str, str, str]:
    scholar = ""
    linkedin = ""
    personal = ""

    # From anchor hrefs
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not scholar and "scholar.google" in href:
            scholar = href
        if not linkedin and "linkedin.com/in/" in href:
            linkedin = href

    # Fallback: regex in full text
    if not scholar:
        m = SCHOLAR_RE.search(full_text)
        scholar = "https://" + m.group() if m else ""
    if not linkedin:
        m = LINKEDIN_RE.search(full_text)
        linkedin = "https://" + m.group() if m else ""

    # Personal website: any external link in a bio section
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http") and not any(
            d in href
            for d in ("google", "linkedin", "facebook", "twitter", "youtube", "ac.in", "edu.in")
        ):
            personal = href
            break

    return scholar, linkedin, personal


# ── Main parse function ────────────────────────────────────────────────────────
def parse_profile(
    html: str,
    profile_url: str,
    institute_name: str = "",
    institute_type: str = "",
    department_guess: str = "",
    raw_html_path: str = "",
) -> Optional[FacultyProfile]:
    """
    Parse a single faculty profile HTML.
    Returns FacultyProfile or None if extraction fails.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        full_text = _get_text(BeautifulSoup(html, "lxml"))

        name = _extract_name(soup)
        if not name:
            logger.debug("No name found for %s — skipping", profile_url)
            return None

        interests, areas = _extract_research(soup)
        scholar, linkedin, personal = _extract_links(soup, full_text)

        return FacultyProfile(
            faculty_name=name,
            designation=_extract_designation(full_text),
            department=department_guess,
            email=_extract_email(full_text),
            phone=_extract_phone(full_text),
            office=_extract_office(full_text),
            research_interests=interests,
            research_areas=areas,
            education=_extract_education(soup),
            publications=_extract_publications(soup),
            projects=_extract_projects(soup),
            google_scholar=scholar,
            linkedin=linkedin,
            personal_website=personal,
            profile_image=_extract_profile_image(soup, profile_url),
            profile_url=profile_url,
            institute_name=institute_name,
            institute_type=institute_type,
            raw_html_path=raw_html_path,
        )
    except Exception as exc:
        logger.error("Parse error for %s: %s", profile_url, exc)
        return None


def parse_from_file(meta: dict) -> Optional[dict]:
    """
    Load raw HTML from disk and parse it.
    meta: dict with keys raw_html_path, profile_url, institute_name, etc.
    """
    path = Path(meta.get("raw_html_path", ""))
    if not path.exists():
        logger.warning("HTML file not found: %s", path)
        return None
    html = path.read_text(encoding="utf-8", errors="replace")
    profile = parse_profile(
        html=html,
        profile_url=meta.get("profile_url", ""),
        institute_name=meta.get("institute_name", ""),
        institute_type=meta.get("institute_type", ""),
        department_guess=meta.get("department_guess", ""),
        raw_html_path=str(path),
    )
    return profile.to_dict() if profile else None
