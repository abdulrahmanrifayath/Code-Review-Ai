import html
import re


def sanitize_filename(filename: str, default_name: str = "download") -> str:
    """
    Sanitizes user-provided or dynamic filenames to prevent path traversal attacks
    and unsafe file system operations.
    Removes Directory Traversal sequences (.., /, \\) and non-alphanumeric symbols.
    """
    if not filename:
        return default_name

    # Remove directory path separators and null bytes
    clean = filename.replace("\\", "_").replace("/", "_").replace("\x00", "")

    # Remove path traversal '..'
    clean = re.sub(r"\.\.+", "", clean)

    # Restrict to safe characters: alphanumeric, underscores, hyphens, and periods
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean)

    # Remove leading periods or hyphens
    clean = clean.lstrip(".-_")

    return clean or default_name


def sanitize_header_value(header_val: str) -> str:
    """
    Sanitizes HTTP header string values to prevent HTTP Header Injection / CRLF Injection.
    """
    if not header_val:
        return ""
    # Strip carriage returns and line feeds
    return re.sub(r"[\r\n]", "", str(header_val)).strip()


def sanitize_html_text(text: str) -> str:
    """
    Escapes HTML markup tags to prevent Cross-Site Scripting (XSS).
    """
    if not text:
        return ""
    return html.escape(str(text))
