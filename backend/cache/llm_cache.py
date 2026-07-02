"""
LLM Result Cache
─────────────────
Avoids paying the (CPU/time) cost of re-running Ollama on HTML that
hasn't changed since the last crawl. Keyed by hash of the cleaned
card text, stored as a simple JSON file (fine at this scale; swap
for SQLite/Redis if you cross ~50k cached entries).
"""
import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CACHE_PATH = Path("cache/llm_cache.json")


class LLMCache:
    def __init__(self, path: Path = DEFAULT_CACHE_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.warning("Cache file corrupted, starting fresh: %s", self.path)
        return {}

    def save(self):
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    @staticmethod
    def key_for(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> dict | None:
        return self._data.get(self.key_for(text))

    def set(self, text: str, result: dict):
        self._data[self.key_for(text)] = result

    def __len__(self):
        return len(self._data)
