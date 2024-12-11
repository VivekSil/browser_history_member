import re
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from functools import reduce


def is_educational_domain(domain: str) -> bool:
    """
    Checks if a domain is educational based on TLD and common patterns.
    """
    edu_patterns = [
        # United States
        r"\.edu$",
        # International academic domains
        r"\.edu\.[a-z]{2}$",  # .edu.au, .edu.uk, etc.
        r"\.ac\.[a-z]{2}$",  # .ac.uk, .ac.jp, etc.
        r"\.edu\.",  # Catch other .edu variants
        # Country-specific academic domains
        r"\.ac\.jp$",  # Japan
        r"\.ac\.uk$",  # United Kingdom
        r"\.ac\.nz$",  # New Zealand
        r"\.ac\.za$",  # South Africa
        r"\.edu\.au$",  # Australia
        r"\.edu\.cn$",  # China
        r"\.edu\.hk$",  # Hong Kong
        r"\.edu\.sg$",  # Singapore
        r"\.edu\.my$",  # Malaysia
        r"\.edu\.in$",  # India
        r"\.edu\.br$",  # Brazil
        r"\.edu\.mx$",  # Mexico
        r"\.edu\.ar$",  # Argentina
        r"\.edu\.es$",  # Spain
        r"\.edu\.pl$",  # Poland
        r"\.edu\.ru$",  # Russia
        r"\.edu\.tr$",  # Turkey
        r"\.ac\.ir$",  # Iran
        r"\.ac\.kr$",  # South Korea
        r"\.ac\.th$",  # Thailand
        r"\.ac\.id$",  # Indonesia
        # European academic domains
        r"\.uni-[^.]+\.de$",  # German universities
        r"\.univ-[^.]+\.fr$",  # French universities
        r"\.uni-[^.]+\.at$",  # Austrian universities
        r"\.uni-[^.]+\.ch$",  # Swiss universities
        r"\.universitet\.dk$",  # Danish universities
        r"\.universiteit\.nl$",  # Dutch universities
        # Common university URL patterns
        r"university\.",
        r"\.uni\.",
        r"\.college\.",
        r"\.institute\.",
        r"\.school\.",
    ]

    return any(re.search(pattern, domain.lower()) for pattern in edu_patterns)


def is_research_repository(domain: str) -> bool:
    cs_research_domains = {
        "arxiv.org": "general_preprints",  # cs.* categories
        "ieee.org": "professional_society",  # IEEE Xplore
        "acm.org": "professional_society",  # ACM Digital Library
        "neurips.cc": "machine_learning",  # NeurIPS
        "icml.cc": "machine_learning",  # ICML
        "iclr.cc": "deep_learning",  # ICLR
        "aaai.org": "artificial_intelligence",  # AAAI
        "ijcai.org": "artificial_intelligence",  # IJCAI
        "usenix.org": "systems",  # USENIX
        "aclweb.org": "computational_linguistics",  # ACL
        "openreview.net": "peer_review",  # Many ML conferences
        "dl.acm.org": "computing",  # ACM Digital Library
        "computer.org": "ieee_cs",  # IEEE Computer Society
        "researchgate.net": "research_network",
        "scholar.google.com": "scholar_search",
        "semantic.scholar.org": "ai_search",
        "dblp.org": "cs_bibliography",
    }

    domain_lower = domain.lower()
    return domain_lower in cs_research_domains


def is_github_repo(url: str) -> bool:
    try:
        parsed = urlparse(url)

        if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            return False

        path_parts = [p for p in parsed.path.split("/") if p]

        # A GitHub repo URL must have at least owner/repo (2 parts)
        if len(path_parts) < 2:
            return False

        non_repo_paths = {
            "marketplace",
            "sponsors",
            "settings",
            "notifications",
            "explore",
            "topics",
            "collections",
            "events",
            "features",
            "security",
            "enterprise",
            "pricing",
            "search",
        }

        if path_parts[0].lower() in non_repo_paths:
            return False

        return True
    except Exception:
        return False


def classify_url(url: str):
    url_lower = url.lower()

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    query = parse_qs(parsed.query)

    if domain.startswith("www."):
        domain = domain[4:]

    educational_platforms = {
        "coursera.org": "online_course",
        "udemy.com": "online_course",
        "edx.org": "online_course",
        "khanacademy.org": "online_course",
        "udacity.com": "online_course",
        "skillshare.com": "online_course",
        "pluralsight.com": "online_course",
        "linkedin.com/learning": "online_course",
        "codecademy.com": "online_course",
        "brilliant.org": "online_course",
        "duolingo.com": "online_course",
        "canvas.net": "lms",
        "blackboard.com": "lms",
        "moodle.org": "lms",
        "youtube.com": "video_platform",
        "youtu.be": "video_platform",
        "teachertube.com": "video_platform",
    }

    tutorial_patterns = [
        r"/tutorial",
        r"/learn",
        r"/course",
        r"/lesson",
        r"/documentation",
        r"/workshop",
        r"/training",
        r"/lecture",
        r"/class",
        r"/syllabus",
        r"/curriculum",
        r"/mooc",
        r"/resources",
        r"/study",
        r"/teach",
        r"/explained",
        r"/introduction",
        r"/basics",
        r"/degree",
        r"/assignment",
        r"/practice",
        r"/exercise",
        r"/problem",
        r"/solution",
        r"/example",
        r"/demo",
        r"/showcase",
        r"/walkthrough",
        r"/step-by-step",
        r"/crash-course",
    ]

    educational_keywords = [
        "tutorial",
        "learn",
        "course",
        "lesson",
        "lecture",
        "educational",
        "teaching",
        "explained",
        "introduction",
        "guide",
        "how to",
        "basics",
        "fundamentals",
        "principles",
        "crash course",
        "for beginners",
        "101",
        "masterclass",
        "workshop",
        "training",
        "education",
        "walkthrough",
        "step by step",
        "introduction to",
        "getting started",
        "complete guide",
        "deep dive",
        "explanation",
        "understand",
        "concept",
        "theory",
        "practice",
        "example",
        "demonstration",
        "review",
    ]

    def is_educational_video(url_lower, query):
        if "youtube.com" in domain or "youtu.be" in domain:
            if "/playlist" in url_lower and "learning" in url_lower:
                return True

            if "/c/" in url_lower or "/channel/" in url_lower:
                educational_channels = [
                    "crash course",
                    "khan academy",
                    "mit",
                    "stanford",
                    "harvard",
                    "ted-ed",
                    "vsauce",
                    "3blue1brown",
                    "codecademy",
                    "freecodecamp",
                    "coursera",
                ]
                return any(channel in url_lower for channel in educational_channels)

            video_title = " ".join(query.get("title", []) + query.get("v", []))
            return any(
                keyword in video_title.lower() for keyword in educational_keywords
            )

        return False

    if domain in educational_platforms.keys():
        platform_type = next(
            (v for k, v in educational_platforms.items() if k in domain), None
        )
        if platform_type == "video_platform" and is_educational_video(url_lower, query):
            return "educational_video"
        else:
            return platform_type

    if any(re.search(pattern, url_lower) for pattern in tutorial_patterns):
        return "tutorial"

    if is_educational_domain(domain) or is_research_repository(domain):
        return "academic"

    if re.search(r"/research/", url_lower) or domain == "":
        return "research"

    if is_github_repo(url_lower):
        return "github_repo"

    return "general"


def create_headers() -> Dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }


def clean_title(title: str) -> str:
    return " ".join(re.sub(r"[\n\r\t]", "", title).split()).strip()


def fetch_webpage(url: str, headers: Dict[str, str]) -> Optional[str]:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def parse_html(html: Optional[str]) -> Optional[BeautifulSoup]:
    return BeautifulSoup(html, "html.parser") if html else None


def extract_title(soup: Optional[BeautifulSoup]) -> Optional[str]:
    if not soup:
        return None

    # From tag
    if soup.title and soup.title.string:
        return clean_title(soup.title.string)

    # From OG
    og_title = soup.find("meta", {"property": "og:title"})
    if og_title and og_title.get("content"):
        return clean_title(og_title["content"])

    # from twitter
    twitter_title = soup.find("meta", {"name": "twitter:title"})
    if twitter_title and twitter_title.get("content"):
        return clean_title(twitter_title["content"])

    h1 = soup.find("h1")
    if h1 and h1.string:
        return clean_title(h1.string)

    return None


def get_webpage_title(url: str) -> Dict[str, Optional[str]]:
    pipeline = [
        lambda url_parsed: fetch_webpage(url, create_headers()),
        parse_html,
        extract_title,
    ]

    title = reduce(lambda x, f: f(x) if x is not None else None, pipeline, url)

    return title
