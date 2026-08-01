import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.security_sanitizer import (
    sanitize_filename,
    sanitize_header_value,
    sanitize_html_text,
)


class TestSecuritySanitizer(unittest.TestCase):
    def test_sanitize_filename_directory_traversal(self):
        # Prevent path traversal attacks like ../../etc/passwd
        raw = "../../../etc/passwd"
        clean = sanitize_filename(raw, "default.txt")
        self.assertNotIn("..", clean)
        self.assertNotIn("/", clean)
        self.assertNotIn("\\", clean)

    def test_sanitize_filename_null_byte_and_special_chars(self):
        raw = "report\x00_2026<script>.pdf"
        clean = sanitize_filename(raw, "report.pdf")
        self.assertNotIn("\x00", clean)
        self.assertNotIn("<", clean)
        self.assertNotIn(">", clean)

    def test_sanitize_header_value_crlf_injection(self):
        raw = "attachment; filename=\"test.pdf\"\r\nX-Injected-Header: malicious"
        clean = sanitize_header_value(raw)
        self.assertNotIn("\r", clean)
        self.assertNotIn("\n", clean)

    def test_sanitize_html_text_xss_prevention(self):
        raw = "<script>alert('XSS')</script>"
        clean = sanitize_html_text(raw)
        self.assertNotIn("<script>", clean)
        self.assertIn("&lt;script&gt;", clean)


if __name__ == "__main__":
    unittest.main()
