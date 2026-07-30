from typing import Any, Dict, List
from app.services.security_analyzer.rules import SECURITY_RULES


class SecurityAnalyzerEngine:
    """
    SAST Security Analyzer Engine detecting SQLi, Hardcoded Credentials, API Keys,
    JWT flaws, Command Injection, Unsafe Files, XSS, CSRF, and Path Traversal.
    """

    @staticmethod
    def scan_file_content(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """
        Scan single file content against SAST security rules.
        """
        findings: List[Dict[str, Any]] = []
        if not code_content:
            return findings

        lines = code_content.splitlines()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//", "/*", "*")):
                continue

            for rule in SECURITY_RULES:
                if rule["pattern"].search(line):
                    findings.append({
                        "rule_id": rule["id"],
                        "category": rule["category"],
                        "cwe_id": rule["cwe_id"],
                        "severity": rule["severity"],
                        "title": rule["title"],
                        "description": rule["description"],
                        "file_path": file_path,
                        "line_number": idx,
                        "code_snippet": stripped[:200],
                        "remediation_suggestion": rule["remediation"],
                    })

        return findings
