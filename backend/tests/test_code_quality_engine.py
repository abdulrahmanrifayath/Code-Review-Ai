import pytest
from app.services.code_quality_engine.calculator import CodeQualityCalculator


def test_code_quality_calculator_clean_code():
    code = '''
"""
Module docstring for test module.
"""

def clean_function(x: int) -> int:
    """
    Computes square of a number.
    """
    return x * x
'''
    metrics = CodeQualityCalculator.calculate_metrics(
        code_content=code,
        language="Python",
        security_findings_count=0,
        performance_findings_count=0,
        code_smells_count=0
    )

    assert metrics["maintainability_score"] >= 80
    assert metrics["technical_debt_hours"] == 0.0
    assert metrics["complexity_score"] == 1.0
    assert metrics["doc_coverage_percentage"] == 100.0
    assert metrics["architecture_score"] >= 90
    assert metrics["grade"] in ("A+", "A")


def test_code_quality_calculator_complex_code_with_smells():
    code = '''
def complex_function(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                for i in range(10):
                    while a < 100:
                        a += 1
    return a
'''
    metrics = CodeQualityCalculator.calculate_metrics(
        code_content=code,
        language="Python",
        security_findings_count=1,
        performance_findings_count=2,
        code_smells_count=5
    )

    assert metrics["technical_debt_hours"] > 0.0
    assert metrics["complexity_score"] > 1.0
    assert metrics["doc_coverage_percentage"] == 0.0
    assert metrics["overall_quality_score"] < 90
