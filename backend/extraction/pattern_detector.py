import re
from collections import defaultdict
from bs4 import BeautifulSoup, Tag

SIGNAL_RE = re.compile(r"professor|faculty|lecturer|dr\.|@|phone|department", re.I)
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]


def _signature(tag: Tag) -> tuple:
    return (tag.name, tuple(sorted(tag.get("class", []))))

def detect_repeating_blocks(soup: BeautifulSoup, min_repeats: int = 3) -> list[Tag]:
    """
    Returns the best-scoring group of repeating sibling elements,
    i.e. the elements most likely to be individual faculty cards.
    Returns [] if nothing qualifies.
    """
    candidates: dict[tuple, list[Tag]] = defaultdict(list)

    # PRIORITY 1: Table rows — very strong signal if a table has many <tr> with <td>
    for table in soup.find_all("table"):
        rows = [r for r in table.find_all("tr") if r.find_all("td")]
        if len(rows) >= min_repeats:
            candidates[("tr", ("__table_row__",))] = rows

    # PRIORITY 2: generic div/ul/section card groups
    for parent in soup.find_all(["div", "ul", "ol", "section"]):
        children = [c for c in parent.find_all(recursive=False) if isinstance(c, Tag)]
        if len(children) < min_repeats:
            continue

        groups: dict[tuple, list[Tag]] = defaultdict(list)
        for child in children:
            groups[_signature(child)].append(child)

        for sig, group in groups.items():
            if len(group) >= min_repeats:
                if len(group) > len(candidates.get(sig, [])):
                    candidates[sig] = group

    if not candidates:
        return []

    scored = []
    for sig, group in candidates.items():
        sample = group[0]
        sample_text = sample.get_text(" ", strip=True)

        is_table_row = sig[0] == "tr"
        has_heading = bool(sample.find(HEADING_TAGS))
        has_signal = bool(SIGNAL_RE.search(sample_text))
        has_data_attrs = bool(sample.get("data-name") or sample.get("data-mail"))
        reasonable_size = 10 < len(sample_text) < 2000

        score = (
            (len(group) >= 5) * 1
            + has_heading * 2
            + has_signal * 2
            + has_data_attrs * 3
            + is_table_row * 3
            + reasonable_size * 1
        )
        scored.append((score, group))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_group = scored[0]

    if best_score < 2:
        return []

    return best_group