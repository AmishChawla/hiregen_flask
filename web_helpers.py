"""Presentation helpers. No database or external-service dependencies."""
import re
from urllib.parse import urlsplit, urlunsplit


def absolute_website_url(value):
    """Normalize a public HTTP(S) website; reject unsafe schemes and credentials."""
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    if re.search(r'[\s\\\x00-\x1f\x7f]', value):
        return None
    if value.startswith('//'):
        value = 'https:' + value
    elif '://' not in value:
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', value):
            return None
        value = 'https://' + value
    try:
        parts = urlsplit(value)
        if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
            return None
        parts.port  # Validate an optional port.
        if not re.fullmatch(r'[a-zA-Z0-9.-]+', parts.hostname):
            return None
        return urlunsplit(parts)
    except ValueError:
        return None


def public_hiregen_url(value):
    """Validate API-provided sitemap links before including them in public XML."""
    normalized = absolute_website_url(value)
    if not normalized:
        return None
    parts = urlsplit(normalized)
    host = parts.hostname.lower()
    if parts.port not in (None, 443) or not (host == 'hiregen.com' or host.endswith('.hiregen.com')):
        return None
    if not all(re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?', label) for label in host.split('.')):
        return None
    # A nested scheme is malformed, even if embedded in the path.
    if '://' in parts.path:
        return None
    return urlunsplit(('https', parts.netloc.lower(), parts.path or '/', parts.query, ''))


def is_public_job(job):
    return (isinstance(job, dict) and job.get('status') == 'published'
            and str(job.get('job_opening_status', '')).lower() == 'active')


def sitemap_entries(entries):
    result = []
    seen = set()
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        location = public_hiregen_url(entry.get('url'))
        if location and location not in seen:
            seen.add(location)
            result.append(dict(entry, url=location))
    return result
