r"""Download an Edureka PDF from a page the current user can access.

The script does not log in, bypass access controls, or guess API endpoints.
Provide cookies exported from the user's own authenticated browser session.
To Run:
python -Wall -m py_compile download_edureka_pdf.py
python download_edureka_pdf.py

To generate edureka-cookies.txt:

- Open Chrome or Edge and sign in to Edureka.
- Open the Edureka classroom page and confirm you can view the presentation.
- Install a trusted cookie-export extension that supports Netscape cookie format, such as Get cookies.txt LOCALLY.
- While on learning.edureka.co, click the extension.
- Export cookies for the current site.
- Save the file as: edureka-cookies.txt


"""

from __future__ import annotations

import argparse
import configparser
import http.cookiejar
import logging
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import (
    Request,
    HTTPCookieProcessor,
    build_opener,
    install_opener,
    urlopen,
)


LOGGER = logging.getLogger("edureka_pdf_downloader")
CONFIG_FILE = Path(__file__).resolve().with_name("edureka_download_config.ini")
DEFAULT_PAGE_URL = (
    "https://learning.edureka.co/classroom/presentation/3103/35187/2575280"
    "?tab=CourseContent"
)
MAX_HTML_BYTES = 10 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class DownloadSettings:
    """Validated settings loaded from the external INI file."""

    page_url: str
    pdf_url: str
    cookie_file: Path
    output_file: Path
    timeout: float


def load_settings(config_file: Path = CONFIG_FILE) -> DownloadSettings:
    """Load download settings and resolve relative paths beside the INI file."""
    if not config_file.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}. "
            "Copy edureka_download_config.ini.example to that path."
        )

    parser = configparser.ConfigParser()
    try:
        parser.read(config_file, encoding="utf-8")
        section = parser["download"]
        timeout = section.getfloat("timeout_seconds", fallback=30.0)
    except (configparser.Error, ValueError, KeyError) as error:
        raise ValueError(f"Invalid configuration file: {config_file}") from error

    def resolve_path(value: str) -> Path:
        path = Path(value).expanduser()
        return path if path.is_absolute() else config_file.parent / path

    if timeout <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    return DownloadSettings(
        page_url=section.get("page_url", fallback=DEFAULT_PAGE_URL).strip(),
        pdf_url=section.get("pdf_url", fallback="").strip(),
        cookie_file=resolve_path(section.get("cookie_file", fallback="edureka-cookies.txt")),
        output_file=resolve_path(section.get("output_file", fallback="edureka_presentation.pdf")),
        timeout=timeout,
    )


class LinkParser(HTMLParser):
    """Collect possible document links from the page HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name.lower() in {"href", "src", "data", "content"} and value:
                self.links.append(value)


def validate_page_url(page_url: str) -> None:
    """Reject malformed or non-HTTPS classroom URLs."""
    parsed = urlparse(page_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("The page URL must be an absolute HTTPS URL")
    if parsed.hostname not in {"learning.edureka.co", "www.edureka.co"}:
        raise ValueError("The page URL must belong to learning.edureka.co")


def validate_pdf_url(pdf_url: str) -> None:
    """Reject malformed or insecure direct PDF URLs."""
    parsed = urlparse(pdf_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("The PDF URL must be an absolute HTTPS URL")


def load_cookies(cookie_file: Path) -> http.cookiejar.MozillaCookieJar:
    """Load Netscape-format browser cookies without exposing their values."""
    if not cookie_file.is_file():
        raise FileNotFoundError(
            f"Cookie file not found: {cookie_file}. Export your authenticated "
            "Edureka browser cookies in Netscape format and save them there, "
            "or update COOKIE_FILE."
        )

    cookies = http.cookiejar.MozillaCookieJar(str(cookie_file))
    try:
        cookies.load(ignore_discard=True, ignore_expires=False)
    except (OSError, http.cookiejar.LoadError) as error:
        raise ValueError("Cookie file is not a valid Netscape cookie export") from error
    return cookies


def fetch_page(page_url: str, timeout: float) -> bytes:
    """Fetch the authenticated classroom page, bounded to a reasonable size."""
    request = Request(
        page_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; EdurekaPdfDownloader/1.0)"},
    )
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get_content_type()
        if content_type != "text/html":
            raise ValueError(f"Expected an HTML classroom page, received {content_type}")
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_HTML_BYTES:
            raise ValueError("Classroom page is unexpectedly large")
        return response.read(MAX_HTML_BYTES + 1)


def candidate_urls(page_url: str, html: bytes) -> Iterable[str]:
    """Yield unique HTTPS PDF references found in HTML and embedded data."""
    decoded = html.decode("utf-8", errors="replace")
    parser = LinkParser()
    parser.feed(decoded)
    references = parser.links + re.findall(
        r"https?://[^\"'\s<>]+?\.pdf(?:\?[^\"'\s<>]*)?", decoded, re.IGNORECASE
    )
    seen: set[str] = set()
    for reference in references:
        pdf_url = urljoin(page_url, reference).replace("\\/", "/")
        parsed = urlparse(pdf_url)
        if (
            pdf_url not in seen
            and parsed.scheme == "https"
            and parsed.netloc
            and ".pdf" in parsed.path.lower()
        ):
            seen.add(pdf_url)
            yield pdf_url


def download_pdf(pdf_url: str, output_path: Path, timeout: float) -> int:
    """Stream a PDF response to disk and return its byte count."""
    request = Request(
        pdf_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; EdurekaPdfDownloader/1.0)"},
    )
    temporary_path = output_path.with_suffix(output_path.suffix + ".part")
    total = 0
    try:
        with urlopen(request, timeout=timeout) as response, temporary_path.open("wb") as target:
            content_type = response.headers.get_content_type()
            first_chunk = response.read(CHUNK_SIZE)
            if not first_chunk.startswith(b"%PDF-"):
                raise ValueError(f"Candidate did not return a PDF (content type: {content_type})")
            target.write(first_chunk)
            total = len(first_chunk)
            while chunk := response.read(CHUNK_SIZE):
                target.write(chunk)
                total += len(chunk)
        temporary_path.replace(output_path)
        return total
    except (OSError, HTTPError, URLError, ValueError):
        temporary_path.unlink(missing_ok=True)
        raise


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="Override the classroom page URL")
    parser.add_argument("--pdf-url", help="Override the direct PDF URL")
    parser.add_argument("-c", "--cookie-file", type=Path, help="Override the Netscape cookie export path")
    parser.add_argument("-o", "--output", type=Path, help="Override the destination PDF path")
    parser.add_argument("--timeout", type=float, help="Override the network timeout in seconds")
    return parser.parse_args()


def main(
    page_url: str | None = None,
    cookie_file: Path | None = None,
    output_path: Path | None = None,
    timeout: float | None = None,
    pdf_url: str | None = None,
) -> int:
    """Run the authenticated PDF discovery and download workflow."""
    try:
        settings = load_settings()
        page_url = page_url if page_url is not None else settings.page_url
        cookie_file = cookie_file if cookie_file is not None else settings.cookie_file
        output_path = output_path if output_path is not None else settings.output_file
        timeout = timeout if timeout is not None else settings.timeout
        pdf_url = pdf_url if pdf_url is not None else settings.pdf_url
        validate_page_url(page_url)
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero")
        if pdf_url:
            validate_pdf_url(pdf_url)
        cookies = load_cookies(cookie_file)
        opener = build_opener(HTTPCookieProcessor(cookies))
        install_opener(opener)
        candidates = [pdf_url] if pdf_url else []
        if not candidates:
            html = fetch_page(page_url, timeout)
            candidates = list(candidate_urls(page_url, html))
        if not candidates:
            raise ValueError(
                "No PDF URL was found in the page HTML. Open the presentation in Edureka "
                "and use its official download control, or inspect the browser Network tab "
                "for a permitted PDF URL."
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        for pdf_url in candidates:
            try:
                size = download_pdf(pdf_url, output_path, timeout)
                LOGGER.info("Downloaded PDF: %s bytes", size)
                print(f"Saved {size:,} bytes to {output_path}")
                return 0
            except (HTTPError, URLError, OSError, ValueError) as error:
                LOGGER.debug("Candidate failed: %s", error)
        raise RuntimeError("PDF references were found, but none returned a valid PDF")
    except (FileNotFoundError, ValueError, HTTPError, URLError, OSError, RuntimeError) as error:
        LOGGER.error("Download failed: %s", error)
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if len(sys.argv) > 1:
        arguments = parse_args()
        sys.exit(
            main(
                arguments.url,
                arguments.cookie_file,
                arguments.output,
                arguments.timeout,
                arguments.pdf_url,
            )
        )
    sys.exit(main())