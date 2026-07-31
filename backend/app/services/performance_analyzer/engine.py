from typing import Any, Dict, List
from app.services.performance_analyzer.rules import PERFORMANCE_RULES


class PerformanceAnalyzerEngine:
    """
    Static Performance Analysis Engine detecting computational bottlenecks,
    N+1 queries, memory leaks, blocking I/O, and expensive regex across codebases.
    """

    @staticmethod
    def analyze_file_performance(file_path: str, code_content: str) -> List[Dict[str, Any]]:
        """
        Scan a source file against Performance Rules and return structured recommendations.
        """
        findings: List[Dict[str, Any]] = []
        if not code_content or len(code_content.strip()) == 0:
            return findings

        lines = code_content.splitlines()

        for rule in PERFORMANCE_RULES:
            match = rule["pattern"].search(code_content)
            if match:
                # Determine line number
                start_char_idx = match.start()
                start_line = code_content[:start_char_idx].count("\n") + 1
                end_line = min(len(lines), start_line + max(1, match.group(0).count("\n")))

                # Extract code snippet
                snippet_lines = lines[max(0, start_line - 1): min(len(lines), end_line + 1)]
                code_snippet = "\n".join(snippet_lines[:8])

                findings.append({
                    "rule_id": rule["id"],
                    "category": rule["category"],
                    "title": rule["title"],
                    "description": rule["description"],
                    "impact_level": rule["impact_level"],
                    "complexity_delta": rule["complexity_delta"],
                    "suggestion_type": rule["suggestion_type"],
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code_snippet": code_snippet,
                    "optimization_suggestion": rule["optimization_suggestion"],
                    "structured_recommendation": rule["structured_recommendation"],
                })

        return findings
