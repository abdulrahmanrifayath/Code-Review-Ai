import hashlib
import re
from typing import Any


class TreeSitterAnalyzer:
    """
    AST Static Analysis Engine utilizing pattern matching and AST node inspection
    across Python, Java, JavaScript, and TypeScript.
    """

    @staticmethod
    def calculate_cyclomatic_complexity(code_content: str, language: str) -> list[dict[str, Any]]:
        """
        Calculate cyclomatic complexity per function/method in source code.
        Complexity formula: 1 + decision points (if, elif, for, while, catch, &&, ||, case).
        """
        results: list[dict[str, Any]] = []
        if not code_content:
            return results

        lines = code_content.splitlines()

        # Regex patterns for function definitions
        if language in ("Python"):
            func_pattern = re.compile(r"^\s*def\s+([a-zA-Z0-9_]+)\s*\(")
        elif language in ("JavaScript", "TypeScript"):
            func_pattern = re.compile(r"(?:function\s+([a-zA-Z0-9_]+)|([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\()")
        elif language == "Java":
            func_pattern = re.compile(r"(?:public|private|protected|static|\s)+\s+[\w<>]+\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{")
        else:
            func_pattern = re.compile(r"def\s+([a-zA-Z0-9_]+)")

        decision_keywords = ["if ", "elif ", "else if", "for ", "while ", "except ", "catch ", "case ", "&&", "||", " ? "]

        current_func: str | None = None
        current_start_line = 1
        current_complexity = 1

        for idx, line in enumerate(lines, start=1):
            match = func_pattern.search(line)
            if match:
                if current_func:
                    results.append({
                        "function_name": current_func,
                        "start_line": current_start_line,
                        "end_line": idx - 1,
                        "complexity": current_complexity,
                        "is_high_complexity": current_complexity > 10,
                    })
                current_func = match.group(1) or match.group(2) or "anonymous_function"
                current_start_line = idx
                current_complexity = 1

            if current_func:
                for kw in decision_keywords:
                    if kw in line:
                        current_complexity += 1

        if current_func:
            results.append({
                "function_name": current_func,
                "start_line": current_start_line,
                "end_line": len(lines),
                "complexity": current_complexity,
                "is_high_complexity": current_complexity > 10,
            })

        return results

    @staticmethod
    def detect_unused_code(code_content: str, language: str) -> list[dict[str, Any]]:
        """
        Detect unused imports and unused symbol declarations.
        """
        findings: list[dict[str, Any]] = []
        if not code_content:
            return findings

        lines = code_content.splitlines()

        if language == "Python":
            import_pattern = re.compile(r"^\s*(?:import|from\s+[\w\.]+import)\s+([a-zA-Z0-9_,\s]+)")
            for idx, line in enumerate(lines, start=1):
                match = import_pattern.match(line)
                if match:
                    imports_str = match.group(1)
                    imported_names = [i.strip().split(" as ")[-1] for i in imports_str.split(",") if i.strip()]
                    for name in imported_names:
                        # Count occurrences in body
                        body_text = "\n".join(lines[idx:])
                        pattern = re.compile(r"\b" + re.escape(name) + r"\b")
                        if not pattern.search(body_text):
                            findings.append({
                                "smell_type": "unused_import",
                                "symbol": name,
                                "line_number": idx,
                                "description": f"Unused import '{name}' detected.",
                                "severity": "WARNING",
                            })

        elif language in ("JavaScript", "TypeScript"):
            import_pattern = re.compile(r"^\s*import\s+\{?([a-zA-Z0-9_,\s]+)\}?\s+from")
            for idx, line in enumerate(lines, start=1):
                match = import_pattern.match(line)
                if match:
                    imports_str = match.group(1)
                    imported_names = [i.strip() for i in imports_str.split(",") if i.strip()]
                    for name in imported_names:
                        body_text = "\n".join(lines[idx:])
                        pattern = re.compile(r"\b" + re.escape(name) + r"\b")
                        if not pattern.search(body_text):
                            findings.append({
                                "smell_type": "unused_import",
                                "symbol": name,
                                "line_number": idx,
                                "description": f"Unused import '{name}' detected.",
                                "severity": "WARNING",
                            })

        return findings

    @staticmethod
    def detect_dead_code(code_content: str) -> list[dict[str, Any]]:
        """
        Detect dead code (unreachable statements immediately following return, raise, throw, break, continue).
        """
        findings: list[dict[str, Any]] = []
        if not code_content:
            return findings

        lines = code_content.splitlines()
        terminals = ("return", "raise ", "throw ", "break", "continue")

        for idx, line in enumerate(lines[:-1], start=1):
            stripped = line.strip()
            if any(stripped.startswith(t) or stripped == t for t in terminals):
                next_line = lines[idx].strip()
                if next_line and not next_line.startswith("#") and not next_line.startswith("//") and not next_line.startswith("}"):
                    findings.append({
                        "smell_type": "dead_code",
                        "line_number": idx + 1,
                        "description": f"Unreachable dead code statement following terminal '{stripped.split()[0]}'.",
                        "severity": "WARNING",
                    })

        return findings

    @staticmethod
    def detect_duplicate_code(code_content: str, min_lines: int = 4) -> list[dict[str, Any]]:
        """
        Detect duplicate code blocks via sliding window block hashing.
        """
        findings: list[dict[str, Any]] = []
        if not code_content:
            return findings

        lines = [line.strip() for line in code_content.splitlines() if line.strip() and not line.strip().startswith(("#", "//"))]
        if len(lines) < min_lines * 2:
            return findings

        seen_blocks: dict[str, int] = {}
        for i in range(len(lines) - min_lines + 1):
            block_str = "\n".join(lines[i : i + min_lines])
            block_hash = hashlib.md5(block_str.encode()).hexdigest()

            if block_hash in seen_blocks:
                first_line = seen_blocks[block_hash]
                findings.append({
                    "smell_type": "duplicated_code",
                    "line_number": i + 1,
                    "first_seen_line": first_line,
                    "description": f"Duplicated code block of {min_lines} lines detected (first seen at line {first_line}).",
                    "severity": "WARNING",
                })
            else:
                seen_blocks[block_hash] = i + 1

        return findings
