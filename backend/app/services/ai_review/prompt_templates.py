from typing import Any

SYSTEM_PROMPT = """You are a Principal Software Architect and Lead Security Engineer performing an automated code review on a GitHub Pull Request.

Your job is to thoroughly analyze code changes across 6 dimensions:
1. BUGS & RELIABILITY: Null references, race conditions, edge cases, error handling flaws.
2. NAMING & CONVENTIONS: Non-idiomatic, vague, or misleading variable/function names.
3. ARCHITECTURE & MODULARITY: Layer separation, component coupling, abstraction boundaries.
4. MAINTAINABILITY: Code readability, complexity, DRY violations, documentation.
5. SOLID PRINCIPLES:
   - S: Single Responsibility Principle
   - O: Open/Closed Principle
   - L: Liskov Substitution Principle
   - I: Interface Segregation Principle
   - D: Dependency Inversion Principle
6. LINE-BY-LINE REVIEW COMMENTS: Specific inline comments with executable suggested fixes.

You MUST respond with a SINGLE valid JSON object matching the schema below. Do not wrap in markdown or add conversational text outside the JSON object.

JSON Output Schema:
{
  "summary": "Executive summary of the pull request quality and changes.",
  "score": 90, // Integer overall quality score (0 to 100)
  "recommendation": "APPROVE" | "REQUEST_CHANGES" | "COMMENT",
  "findings": [
    {
      "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO",
      "category": "BUG" | "SECURITY" | "PERFORMANCE" | "NAMING" | "ARCHITECTURE" | "MAINTAINABILITY" | "SOLID_PRINCIPLE",
      "explanation": "Detailed root cause analysis and technical explanation.",
      "suggested_fix": "Optional executable code diff snippet or remediation tip.",
      "confidence_score": 0.95, // Float between 0.0 and 1.0
      "file_path": "path/to/file.ext",
      "line_number": 42
    }
  ],
  "inline_comments": [
    {
      "path": "path/to/file.ext",
      "line": 42,
      "body": "Detailed review comment for this specific line.",
      "suggestion": "Optional drop-in replacement code snippet."
    }
  ]
}
"""


def build_user_prompt(context: dict[str, Any]) -> str:
    """
    Format user prompt incorporating PR metadata, diff patches, and static analysis findings.
    """
    repo = context.get("repository", {})
    pr = context.get("pull_request", {})
    files = context.get("changed_files", [])
    static = context.get("static_analysis", {})

    prompt_parts = [
        f"### REPOSITORY: {repo.get('full_name')} (Language: {repo.get('language')})",
        f"### PULL REQUEST #{pr.get('number')}: {pr.get('title')}",
        f"Author: {pr.get('author')} | Branch: {pr.get('head_branch')} -> {pr.get('base_branch')}",
        f"Stats: +{pr.get('additions')} / -{pr.get('deletions')}",
        f"Description:\n{pr.get('body') or 'No description provided.'}\n",
        "### PRE-DETECTED STATIC ANALYSIS FINDINGS:",
    ]

    sec_findings = static.get("security_findings", [])
    smells = static.get("code_smells", [])

    if not sec_findings and not smells:
        prompt_parts.append("No static analysis findings reported.\n")
    else:
        for sf in sec_findings:
            prompt_parts.append(f"- [SECURITY {sf.get('severity')}] {sf.get('title')} at {sf.get('file_path')}:{sf.get('start_line')}")
        for cs in smells:
            prompt_parts.append(f"- [CODE SMELL] {cs.get('description')} at {cs.get('file_path')}:{cs.get('start_line')}")
        prompt_parts.append("")

    prompt_parts.append("### CHANGED FILES & DIFF PATCHES:")

    for f in files:
        prompt_parts.append(f"\n--- FILE: {f.get('filename')} (Status: {f.get('status')}, Language: {f.get('language')}) ---")
        patch = f.get("patch")
        if patch:
            prompt_parts.append(patch)
        else:
            prompt_parts.append("(No diff patch content available)")

    prompt_parts.append("\nAnalyze the pull request according to the instructions and return the structured JSON output.")
    return "\n".join(prompt_parts)
