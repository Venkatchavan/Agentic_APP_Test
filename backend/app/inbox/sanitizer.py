"""
Email HTML sanitiser — strips dangerous content before AI processing.
Treats all imported content as untrusted input per security rules.
"""

import re

from app.common.security import sanitize_html


def sanitize_email_body(raw_html: str) -> str:
    """
    Full sanitisation pipeline for email bodies:
    1. Strip dangerous HTML tags/attrs
    2. Remove tracking pixels
    3. Collapse excessive whitespace
    4. Truncate to safe length for model context
    """
    cleaned = sanitize_html(raw_html)
    cleaned = _remove_tracking_pixels(cleaned)
    cleaned = _collapse_whitespace(cleaned)
    cleaned = _truncate_for_model(cleaned)
    return cleaned


def _remove_tracking_pixels(html: str) -> str:
    """Remove 1x1 tracking images."""
    return re.sub(
        r'<img[^>]*(width\s*=\s*["\']?1|height\s*=\s*["\']?1)[^>]*>',
        "",
        html,
        flags=re.IGNORECASE,
    )


def _collapse_whitespace(text: str) -> str:
    """Collapse multiple whitespace/newlines."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _truncate_for_model(text: str, max_chars: int = 15000) -> str:
    """Truncate to stay within model context budget."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated for processing ...]"


def extract_plain_text(html_or_text: str) -> str:
    """Extract plain text from HTML, stripping all tags."""
    from bs4 import BeautifulSoup

    if "<" in html_or_text and ">" in html_or_text:
        soup = BeautifulSoup(html_or_text, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    return html_or_text
