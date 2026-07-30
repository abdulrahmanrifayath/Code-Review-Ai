import asyncio
import json
import os
import re
import shutil
import tempfile
from typing import Any, Dict, List, Optional
from app.core.logging import logger


class LinterRunnerManager:
    """
    Manager for executing CLI static linters (ESLint, Pylint, Flake8, Bandit, Checkstyle, PMD)
    with rule-based fallbacks.
    """

    @staticmethod
    async def run_pylint(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Run Pylint on Python code."""
        findings: List[Dict[str, Any]] = []
        if not shutil.which("pylint"):
            return LinterRunnerManager._python_fallback_rules(file_path, code_content)

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
            tmp.write(code_content)
            tmp_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                "pylint", "--output-format=json", tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if stdout:
                data = json.loads(stdout.decode())
                for item in data:
                    findings.append({
                        "tool": "pylint",
                        "rule_id": item.get("symbol", "pylint-rule"),
                        "message": item.get("message", ""),
                        "line": item.get("line", 1),
                        "column": item.get("column", 0),
                        "type": item.get("type", "warning"),
                    })
        except Exception as exc:
            logger.warning("Pylint execution failed: %s", str(exc))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return findings

    @staticmethod
    async def run_bandit(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Run Bandit Python SAST security scanner."""
        findings: List[Dict[str, Any]] = []
        if not shutil.which("bandit"):
            return LinterRunnerManager._bandit_fallback_security_rules(file_path, code_content)

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
            tmp.write(code_content)
            tmp_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                "bandit", "-f", "json", tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if stdout:
                data = json.loads(stdout.decode())
                for item in data.get("results", []):
                    findings.append({
                        "tool": "bandit",
                        "rule_id": item.get("test_id", "B000"),
                        "title": item.get("issue_text", "Security Vulnerability"),
                        "severity": item.get("issue_severity", "HIGH").upper(),
                        "cwe_id": f"CWE-{item.get('issue_cwe', {}).get('id', '200')}",
                        "line": item.get("line_number", 1),
                        "code": item.get("code", ""),
                    })
        except Exception as exc:
            logger.warning("Bandit execution failed: %s", str(exc))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return findings

    @staticmethod
    async def run_eslint(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Run ESLint on JavaScript/TypeScript code."""
        findings: List[Dict[str, Any]] = []
        if not shutil.which("eslint"):
            return LinterRunnerManager._js_ts_fallback_rules(file_path, code_content)

        ext = os.path.splitext(file_path)[1] or ".ts"
        with tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False) as tmp:
            tmp.write(code_content)
            tmp_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                "eslint", "-f", "json", tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if stdout:
                data = json.loads(stdout.decode())
                for file_res in data:
                    for msg in file_res.get("messages", []):
                        findings.append({
                            "tool": "eslint",
                            "rule_id": msg.get("ruleId", "eslint-rule"),
                            "message": msg.get("message", ""),
                            "line": msg.get("line", 1),
                            "column": msg.get("column", 0),
                            "severity": "ERROR" if msg.get("severity") == 2 else "WARNING",
                        })
        except Exception as exc:
            logger.warning("ESLint execution failed: %s", str(exc))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return findings

    @staticmethod
    def _python_fallback_rules(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Rule-based Python quality checker when CLI binary is missing."""
        results = []
        lines = code_content.splitlines()
        for idx, line in enumerate(lines, start=1):
            if "except Exception:" in line or "except:" in line:
                results.append({
                    "tool": "pylint",
                    "rule_id": "W0703",
                    "message": "Catching too general exception 'Exception'.",
                    "line": idx,
                    "column": 0,
                    "type": "warning",
                })
            if "print(" in line and not file_path.startswith("test"):
                results.append({
                    "tool": "pylint",
                    "rule_id": "T201",
                    "message": "print statement found. Consider using logging instead.",
                    "line": idx,
                    "column": 0,
                    "type": "warning",
                })
        return results

    @staticmethod
    def _bandit_fallback_security_rules(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Rule-based Python security scanner fallback."""
        results = []
        lines = code_content.splitlines()
        sec_patterns = [
            (re.compile(r"exec\s*\("), "B102", "Use of exec detected (code execution vulnerability)", "CRITICAL", "CWE-95"),
            (re.compile(r"eval\s*\("), "B307", "Use of eval detected (dynamic code injection)", "CRITICAL", "CWE-95"),
            (re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE), "B105", "Possible hardcoded password credential detected", "HIGH", "CWE-259"),
            (re.compile(r"api_key\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE), "B106", "Possible hardcoded API key credential detected", "HIGH", "CWE-798"),
        ]

        for idx, line in enumerate(lines, start=1):
            for pat, rule_id, title, sev, cwe in sec_patterns:
                if pat.search(line):
                    results.append({
                        "tool": "bandit",
                        "rule_id": rule_id,
                        "title": title,
                        "severity": sev,
                        "cwe_id": cwe,
                        "line": idx,
                        "code": line.strip(),
                    })

        return results

    @staticmethod
    def _js_ts_fallback_rules(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """Rule-based JS/TS quality checker fallback."""
        results = []
        lines = code_content.splitlines()
        for idx, line in enumerate(lines, start=1):
            if "console.log(" in line:
                results.append({
                    "tool": "eslint",
                    "rule_id": "no-console",
                    "message": "Unexpected console statement.",
                    "line": idx,
                    "column": 0,
                    "severity": "WARNING",
                })
            if "eval(" in line:
                results.append({
                    "tool": "eslint",
                    "rule_id": "no-eval",
                    "message": "eval() can be harmful.",
                    "line": idx,
                    "column": 0,
                    "severity": "ERROR",
                })
            if " == null" in line or " == true" in line:
                results.append({
                    "tool": "eslint",
                    "rule_id": "eqeqeq",
                    "message": "Expected '===' and instead saw '=='.",
                    "line": idx,
                    "column": 0,
                    "severity": "WARNING",
                })
        return results
