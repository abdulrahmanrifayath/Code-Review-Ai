from app.services.performance_analyzer.engine import PerformanceAnalyzerEngine


def test_detect_nested_loops():
    code = """
def process_matrix(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            print(matrix[i][j])
    """
    findings = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code)
    assert len(findings) > 0
    nested = [f for f in findings if f["category"] == "Nested Loops"]
    assert len(nested) == 1
    assert nested[0]["rule_id"] == "PERF-LOOP-001"
    assert nested[0]["suggestion_type"] == "Caching"


def test_detect_repeated_database_queries():
    code = """
def update_users(users, db):
    for user in users:
        result = db.execute(select(User).where(User.id == user.id))
    """
    findings = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code)
    db_findings = [f for f in findings if f["category"] == "Repeated Database Queries"]
    assert len(db_findings) == 1
    assert db_findings[0]["rule_id"] == "PERF-NPLUS1-001"
    assert db_findings[0]["suggestion_type"] == "Indexes"


def test_detect_blocking_operations():
    code = """
async def fetch_data_async(url):
    import time
    time.sleep(5)
    return True
    """
    findings = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code)
    blocking = [f for f in findings if f["category"] == "Blocking Operations"]
    assert len(blocking) == 1
    assert blocking[0]["rule_id"] == "PERF-BLOCK-001"
    assert blocking[0]["suggestion_type"] == "Async"


def test_detect_large_memory_allocations():
    code = """
def read_all_logs(filepath):
    data = open(filepath).read()
    return data
    """
    findings = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code)
    mem = [f for f in findings if f["category"] == "Large Memory Allocations"]
    assert len(mem) == 1
    assert mem[0]["rule_id"] == "PERF-MEM-001"
    assert mem[0]["suggestion_type"] == "Lazy Loading"


def test_detect_repeated_api_calls():
    code = """
def fetch_all(urls):
    for url in urls:
        res = requests.get(url)
    """
    findings = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code)
    api_calls = [f for f in findings if f["category"] == "Repeated API Calls"]
    assert len(api_calls) == 1
    assert api_calls[0]["rule_id"] == "PERF-API-001"
    assert api_calls[0]["suggestion_type"] == "Caching"


def test_detect_expensive_regex():
    code = """
import re

def parse_logs(lines):
    for line in lines:
        pattern = re.compile(r'(a+)+')
        match = pattern.search(line)
    """
    findings = PerformanceAnalyzerEngine.analyze_file_performance("test.py", code)
    regex_findings = [f for f in findings if f["category"] == "Expensive Regex"]
    assert len(regex_findings) == 1
    assert regex_findings[0]["rule_id"] == "PERF-REGEX-001"
