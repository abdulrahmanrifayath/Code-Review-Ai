from typing import Any, Dict, List
from app.services.performance_analyzer.engine import PerformanceAnalyzerEngine
from app.services.static_analysis.linter_runners import LinterRunnerManager
from app.services.static_analysis.tree_sitter_analyzer import TreeSitterAnalyzer


class StaticAnalysisEngine:
    """
    Unified Engine coordinating Tree-sitter AST analysis, Performance Analyzer, and linter runners
    across Python, Java, JavaScript, and TypeScript.
    """

    @staticmethod
    async def analyze_code(file_path: str, code_content: str, language: str) -> Dict[str, Any]:
        """
        Execute static analysis pipeline for a single source file.
        Returns dictionary containing security_findings, performance_findings, and code_smells.
        """
        security_findings: List[Dict[str, Any]] = []
        performance_findings: List[Dict[str, Any]] = []
        code_smells: List[Dict[str, Any]] = []

        if not code_content:
            return {
                "security_findings": security_findings,
                "performance_findings": performance_findings,
                "code_smells": code_smells,
            }

        # Performance Analyzer Scan
        perf_res = PerformanceAnalyzerEngine.analyze_file_performance(file_path, code_content)
        performance_findings.extend(perf_res)

        # 1. AST Analysis (Complexity, Unused Code, Dead Code, Duplication)
        complexity_results = TreeSitterAnalyzer.calculate_cyclomatic_complexity(code_content, language)
        for comp in complexity_results:
            if comp["is_high_complexity"]:
                code_smells.append({
                    "smell_type": "high_cyclomatic_complexity",
                    "description": f"Function '{comp['function_name']}' has high cyclomatic complexity ({comp['complexity']}).",
                    "severity": "WARNING",
                    "file_path": file_path,
                    "start_line": comp["start_line"],
                    "end_line": comp["end_line"],
                    "refactoring_tip": "Consider decomposing function into smaller helper methods.",
                })

        unused_findings = TreeSitterAnalyzer.detect_unused_code(code_content, language)
        for u in unused_findings:
            code_smells.append({
                "smell_type": u["smell_type"],
                "description": u["description"],
                "severity": u["severity"],
                "file_path": file_path,
                "start_line": u["line_number"],
                "end_line": u["line_number"],
                "refactoring_tip": f"Remove unused import or variable '{u.get('symbol')}'",
            })

        dead_code_findings = TreeSitterAnalyzer.detect_dead_code(code_content)
        for d in dead_code_findings:
            code_smells.append({
                "smell_type": d["smell_type"],
                "description": d["description"],
                "severity": d["severity"],
                "file_path": file_path,
                "start_line": d["line_number"],
                "end_line": d["line_number"],
                "refactoring_tip": "Remove unreachable dead code statements.",
            })

        dup_findings = TreeSitterAnalyzer.detect_duplicate_code(code_content)
        for dup in dup_findings:
            code_smells.append({
                "smell_type": dup["smell_type"],
                "description": dup["description"],
                "severity": dup["severity"],
                "file_path": file_path,
                "start_line": dup["line_number"],
                "end_line": dup["line_number"] + 3,
                "refactoring_tip": "Extract duplicate logic into a shared utility function.",
            })

        # 2. Linter & SAST Runners
        if language == "Python":
            pylint_res = await LinterRunnerManager.run_pylint(file_path, code_content)
            for p in pylint_res:
                code_smells.append({
                    "smell_type": f"pylint_{p['rule_id']}",
                    "description": p["message"],
                    "severity": "WARNING" if p["type"] == "warning" else "INFO",
                    "file_path": file_path,
                    "start_line": p["line"],
                    "end_line": p["line"],
                    "refactoring_tip": "Address linting rule violations.",
                })

            bandit_res = await LinterRunnerManager.run_bandit(file_path, code_content)
            for b in bandit_res:
                security_findings.append({
                    "rule_id": b["rule_id"],
                    "title": b["title"],
                    "description": f"SAST Vulnerability: {b['title']} on line {b['line']}",
                    "severity": b["severity"],
                    "cwe_id": b["cwe_id"],
                    "file_path": file_path,
                    "start_line": b["line"],
                    "end_line": b["line"],
                    "code_snippet": b.get("code"),
                    "remediation_suggestion": "Sanitize inputs and avoid unsafe functions.",
                })

        elif language in ("JavaScript", "TypeScript"):
            eslint_res = await LinterRunnerManager.run_eslint(file_path, code_content)
            for es in eslint_res:
                code_smells.append({
                    "smell_type": f"eslint_{es['rule_id']}",
                    "description": es["message"],
                    "severity": es["severity"],
                    "file_path": file_path,
                    "start_line": es["line"],
                    "end_line": es["line"],
                    "refactoring_tip": "Follow ESLint code style guidelines.",
                })

        return {
            "security_findings": security_findings,
            "performance_findings": performance_findings,
            "code_smells": code_smells,
        }
