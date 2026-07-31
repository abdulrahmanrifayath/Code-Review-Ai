import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.performance_analyzer.engine import PerformanceAnalyzerEngine
from app.services.code_quality_engine.calculator import CodeQualityCalculator

def run_tests():
    print("--- Running Performance Analyzer Tests ---")
    # Test 1: Nested Loops
    code1 = """
def process_matrix(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            print(matrix[i][j])
    """
    res1 = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code1)
    assert any(f["category"] == "Nested Loops" for f in res1), "Nested Loops detection failed"
    print("PASS: Nested Loops Detection")

    # Test 2: N+1 DB Queries
    code2 = """
def update_users(users, db):
    for user in users:
        result = db.execute(select(User).where(User.id == user.id))
    """
    res2 = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code2)
    assert any(f["category"] == "Repeated Database Queries" for f in res2), "N+1 DB Query detection failed"
    print("PASS: Repeated DB Queries Detection")

    # Test 3: Blocking Operations
    code3 = """
async def fetch_data_async(url):
    import time
    time.sleep(5)
    return True
    """
    res3 = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code3)
    assert any(f["category"] == "Blocking Operations" for f in res3), "Blocking Operations detection failed"
    print("PASS: Blocking Operations Detection")

    # Test 4: Large Memory Allocations
    code4 = """
def read_all_logs(filepath):
    data = open(filepath).read()
    return data
    """
    res4 = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code4)
    assert any(f["category"] == "Large Memory Allocations" for f in res4), "Large Memory Allocations detection failed"
    print("PASS: Large Memory Allocations Detection")

    # Test 5: Repeated API Calls
    code5 = """
def fetch_all(urls):
    for url in urls:
        res = requests.get(url)
    """
    res5 = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code5)
    assert any(f["category"] == "Repeated API Calls" for f in res5), "Repeated API Calls detection failed"
    print("PASS: Repeated API Calls Detection")

    # Test 6: Expensive Regex
    code6 = """
import re
def parse_logs(lines):
    for line in lines:
        pattern = re.compile(r'(a+)+')
        match = pattern.search(line)
    """
    res6 = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code6)
    assert any(f["category"] == "Expensive Regex" for f in res6), "Expensive Regex detection failed"
    print("PASS: Expensive Regex Detection")

    print("\n--- Running Code Quality Engine Tests ---")
    clean_code = '''
"""
Module docstring.
"""
def clean_function(x: int) -> int:
    """Computes square."""
    return x * x
'''
    q_metrics = CodeQualityCalculator.calculate_metrics(
        code_content=clean_code,
        language="Python",
        security_findings_count=0,
        performance_findings_count=0,
        code_smells_count=0
    )
    assert q_metrics["maintainability_score"] >= 80, f"Expected high maintainability, got {q_metrics['maintainability_score']}"
    assert q_metrics["technical_debt_hours"] == 0.0, f"Expected 0 tech debt, got {q_metrics['technical_debt_hours']}"
    assert q_metrics["doc_coverage_percentage"] == 100.0, f"Expected 100% doc coverage, got {q_metrics['doc_coverage_percentage']}"
    print(f"PASS: Clean Code Quality Metrics (Score: {q_metrics['overall_quality_score']}, Grade: {q_metrics['grade']})")

    print("\nAll standalone performance & quality engine tests passed successfully!")

if __name__ == "__main__":
    run_tests()
