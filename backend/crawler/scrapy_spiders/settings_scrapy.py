BOT_NAME = "faculty_search"
SPIDER_MODULES = ["crawler.scrapy_spiders"]
NEWSPIDER_MODULE = "crawler.scrapy_spiders"

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = "data/raw/scrapy_cache"

USER_AGENT = (
    "Mozilla/5.0 (compatible; AcademiaBot/1.0; "
    "+https://github.com/yourorg/faculty-search)"
)

FEEDS = {
    "data/raw/scraped_%(name)s.jsonl": {"format": "jsonlines", "overwrite": False}
}

LOG_LEVEL = "INFO"
LOG_FILE = "logs/scrapy.log"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
