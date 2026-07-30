import os
import re
from typing import Any, Dict, List, Optional


def detect_language_from_filename(filename: str) -> str:
    """
    Detect programming language from file path extension or special filename.
    """
    basename = os.path.basename(filename).lower()
    ext = os.path.splitext(filename)[1].lower()

    if basename in ("dockerfile", "dockerfile.dev", "dockerfile.prod"):
        return "Dockerfile"
    if basename in ("makefile", "gnumakefile"):
        return "Makefile"

    extension_map = {
        ".py": "Python",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".c": "C",
        ".h": "C/C++ Header",
        ".cs": "C#",
        ".php": "PHP",
        ".rb": "Ruby",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".sql": "SQL",
        ".sh": "Shell",
        ".bash": "Shell",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".json": "JSON",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".md": "Markdown",
    }

    return extension_map.get(ext, "Plain Text")


def parse_unified_diff(patch_str: str) -> Dict[str, Any]:
    """
    Parse a unified git diff patch string into structured hunks and line mappings.
    Returns dictionary with hunks, added_lines, deleted_lines, and line stats.
    """
    if not patch_str:
        return {
            "hunks": [],
            "added_lines": [],
            "deleted_lines": [],
            "additions": 0,
            "deletions": 0,
            "total_changes": 0,
        }

    hunks: List[Dict[str, Any]] = []
    added_lines: List[Dict[str, Any]] = []
    deleted_lines: List[Dict[str, Any]] = []

    lines = patch_str.splitlines()
    current_hunk: Optional[Dict[str, Any]] = None

    old_line_num = 0
    new_line_num = 0

    hunk_header_pattern = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@(.*)")

    for line in lines:
        match = hunk_header_pattern.match(line)
        if match:
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) else 1
            new_start = int(match.group(3))
            new_count = int(match.group(4)) if match.group(4) else 1
            heading = match.group(5).strip()

            old_line_num = old_start
            new_line_num = new_start

            current_hunk = {
                "header": line,
                "old_start": old_start,
                "old_count": old_count,
                "new_start": new_start,
                "new_count": new_count,
                "heading": heading,
                "lines": [],
            }
            hunks.append(current_hunk)
            continue

        if current_hunk is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:]
            item = {
                "line_number": new_line_num,
                "type": "add",
                "content": content,
            }
            current_hunk["lines"].append(item)
            added_lines.append(item)
            new_line_num += 1
        elif line.startswith("-") and not line.startswith("---"):
            content = line[1:]
            item = {
                "line_number": old_line_num,
                "type": "delete",
                "content": content,
            }
            current_hunk["lines"].append(item)
            deleted_lines.append(item)
            old_line_num += 1
        elif line.startswith("\\"):
            # e.g., "\ No newline at end of file"
            continue
        else:
            # Context line (starts with ' ' or normal)
            content = line[1:] if line.startswith(" ") else line
            item = {
                "old_line_number": old_line_num,
                "new_line_number": new_line_num,
                "type": "context",
                "content": content,
            }
            current_hunk["lines"].append(item)
            old_line_num += 1
            new_line_num += 1

    return {
        "hunks": hunks,
        "added_lines": added_lines,
        "deleted_lines": deleted_lines,
        "additions": len(added_lines),
        "deletions": len(deleted_lines),
        "total_changes": len(added_lines) + len(deleted_lines),
    }
