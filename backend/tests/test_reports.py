import json
import pytest
from app.services.reports.report_generator import ProfessionalReportGeneratorEngine


def test_generate_markdown_report():
    content, title, metadata = ProfessionalReportGeneratorEngine.generate_report(
        repository_full_name="acme/service",
        pr_number=5,
        format_type="MARKDOWN"
    )
    assert "Executive Code Review Report - acme/service (PR #5)" in title
    assert "# Executive Code Review Report" in content
    assert "## 1. Executive Summary" in content
    assert "## 2. Quality Score & Health Metrics" in content
    assert "## 3. Security Summary" in content
    assert "## 4. Performance Summary" in content
    assert "## 5. Potential Bug Summary" in content
    assert "## 6. Code Smells" in content
    assert "## 7. AI Generated Tests Summary" in content
    assert "## 8. Documentation Suggestions" in content


def test_generate_html_report():
    content, title, metadata = ProfessionalReportGeneratorEngine.generate_report(
        repository_full_name="acme/service",
        pr_number=5,
        format_type="HTML"
    )
    assert "<!DOCTYPE html>" in content
    assert "<h1>Executive Code Review Report" in content
    assert "1. Executive Summary" in content
    assert "OVERALL SCORE" in content


def test_generate_pdf_report():
    content, title, metadata = ProfessionalReportGeneratorEngine.generate_report(
        repository_full_name="acme/service",
        pr_number=5,
        format_type="PDF"
    )
    assert "<!DOCTYPE html>" in content or "%PDF" in content
    assert metadata["quality_score"]["overall_score"] > 0


def test_generate_json_report():
    content, title, metadata = ProfessionalReportGeneratorEngine.generate_report(
        repository_full_name="acme/service",
        pr_number=5,
        format_type="JSON"
    )
    parsed = json.loads(content)
    assert parsed["repository"] == "acme/service"
    assert parsed["pr_number"] == 5
    assert "executive_summary" in parsed
    assert "quality_score" in parsed
    assert "security_summary" in parsed
    assert "performance_summary" in parsed
    assert "bug_summary" in parsed
    assert "code_smells" in parsed
    assert "generated_tests" in parsed
    assert "documentation_suggestions" in parsed
