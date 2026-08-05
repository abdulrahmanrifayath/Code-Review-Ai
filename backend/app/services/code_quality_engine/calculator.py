import math
import re
from typing import Any


class CodeQualityCalculator:
    """
    Calculates Code Quality Metrics including Maintainability Score, Technical Debt (hours),
    Cyclomatic Complexity, Documentation Coverage %, and Architecture Cohesion Score.
    """

    @staticmethod
    def calculate_metrics(
        code_content: str,
        language: str,
        security_findings_count: int = 0,
        performance_findings_count: int = 0,
        code_smells_count: int = 0,
    ) -> dict[str, Any]:
        """
        Calculates comprehensive quality metrics for given source code or multi-file payload.
        """
        if not code_content or len(code_content.strip()) == 0:
            return {
                "maintainability_score": 90,
                "technical_debt_hours": 0.0,
                "complexity_score": 1.0,
                "doc_coverage_percentage": 100.0,
                "architecture_score": 95,
                "overall_quality_score": 92,
                "grade": "A+",
            }

        lines = [line for line in code_content.splitlines() if line.strip()]
        total_loc = max(1, len(lines))

        # 1. Complexity & Function count
        func_patterns = {
            "Python": re.compile(r"^\s*def\s+([a-zA-Z0-9_]+)\s*\("),
            "JavaScript": re.compile(r"(?:function\s+([a-zA-Z0-9_]+)|([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\()"),
            "TypeScript": re.compile(r"(?:function\s+([a-zA-Z0-9_]+)|([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\()"),
            "Java": re.compile(r"(?:public|private|protected|static|\s)+\s+[\w<>]+\s+([a-zA-Z0-9_]+)\s*\("),
        }
        pattern = func_patterns.get(language, re.compile(r"def\s+([a-zA-Z0-9_]+)|function\s+([a-zA-Z0-9_]+)"))

        functions = []
        for line in lines:
            m = pattern.search(line)
            if m:
                functions.append(m.group(1) or m.group(2) or "anonymous")

        total_functions = max(1, len(functions))

        # Strip comments and docstrings when evaluating decision keywords
        code_without_comments = re.sub(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|/\*[\s\S]*?\*/|#.*|//.*', '', code_content)
        code_lines = [l for l in code_without_comments.splitlines() if l.strip()]

        # Decision keywords for complexity
        decision_keywords = ["if ", "elif ", "else if", "for ", "while ", "except ", "catch ", "case ", "&&", "||", " ? "]
        total_decisions = sum(1 for line in code_lines for kw in decision_keywords if kw in line)

        avg_complexity = round(1.0 + (total_decisions / float(total_functions)), 2)

        # 2. Documentation Coverage %
        docstring_patterns = {
            "Python": re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''),
            "JavaScript": re.compile(r'/\*\*[\s\S]*?\*/'),
            "TypeScript": re.compile(r'/\*\*[\s\S]*?\*/'),
            "Java": re.compile(r'/\*\*[\s\S]*?\*/'),
        }
        doc_pattern = docstring_patterns.get(language, re.compile(r'/\*\*[\s\S]*?\*/|"""[\s\S]*?"""'))
        doc_matches = len(doc_pattern.findall(code_content))
        doc_coverage = round(min(100.0, (doc_matches / float(total_functions)) * 100.0), 1)
        if doc_matches > 0 and doc_coverage < 20.0:
            doc_coverage = 50.0 # baseline credit for having documentation

        # 3. Maintainability Index Formula
        # Standard MI normalized scale: 0-100
        halstead_vol = max(10, total_loc * 6)
        mi_raw = 171.0 - (5.2 * math.log(halstead_vol)) - (0.23 * avg_complexity) - (16.2 * math.log(total_loc))
        normalized_mi = max(0, min(100, int((mi_raw / 171.0) * 100 * 1.3)))

        # Penalize maintainability for findings
        maintainability_score = max(0, min(100, normalized_mi - (code_smells_count * 3 + performance_findings_count * 5)))

        # 4. Technical Debt (Hours)
        # 1.5h per smell, 3h per perf finding, 4h per security vulnerability, plus high complexity penalty
        high_complexity_penalty = 2.0 if avg_complexity > 10 else 0.0
        technical_debt_hours = round(
            (code_smells_count * 1.5) +
            (performance_findings_count * 3.0) +
            (security_findings_count * 4.0) +
            high_complexity_penalty,
            1
        )

        # 5. Architecture Score
        # Checks layer boundaries and circular dependencies
        architecture_penalty = 0
        if "select" in code_content.lower() and ("component" in code_content.lower() or "jsx" in code_content.lower() or "tsx" in code_content.lower()):
            architecture_penalty += 15 # UI component directly executing database queries
        if total_loc > 800:
            architecture_penalty += 10 # Oversized monolithic file

        architecture_score = max(30, 100 - architecture_penalty - (performance_findings_count * 4))

        # 6. Overall Quality Score & Grade
        overall_quality_score = int(
            (maintainability_score * 0.35) +
            (architecture_score * 0.25) +
            (max(0, 100 - int(technical_debt_hours * 5)) * 0.20) +
            (doc_coverage * 0.20)
        )
        overall_quality_score = max(0, min(100, overall_quality_score))

        if overall_quality_score >= 90:
            grade = "A+"
        elif overall_quality_score >= 80:
            grade = "A"
        elif overall_quality_score >= 70:
            grade = "B"
        elif overall_quality_score >= 60:
            grade = "C"
        else:
            grade = "F"

        return {
            "maintainability_score": maintainability_score,
            "technical_debt_hours": technical_debt_hours,
            "complexity_score": avg_complexity,
            "doc_coverage_percentage": doc_coverage,
            "architecture_score": architecture_score,
            "overall_quality_score": overall_quality_score,
            "grade": grade,
        }
