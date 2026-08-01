from app.services.doc_generator.generator import AIDocGeneratorEngine


def test_generate_python_docstrings():
    code = """
def calculate_tax(amount, rate=0.15):
    return amount * rate
"""
    res = AIDocGeneratorEngine.generate_documentation("billing.py", code, "docstring")
    assert "Docstrings for billing.py" in res["doc_title"]
    assert '"""' in res["content"]
    assert "Args:" in res["content"]
    assert "Returns:" in res["content"]


def test_generate_javadocs():
    code = """
public class PaymentGateway {
    public boolean processPayment(double amount, String currency) {
        return true;
    }
}
"""
    res = AIDocGeneratorEngine.generate_documentation("PaymentGateway.java", code, "javadoc")
    assert "JavaDocs for PaymentGateway.java" in res["doc_title"]
    assert "/**" in res["content"]
    assert "@param amount" in res["content"]
    assert "@return boolean" in res["content"]


def test_generate_readme():
    code = "def main(): pass"
    res = AIDocGeneratorEngine.generate_documentation("service.py", code, "readme")
    assert "README Documentation" in res["doc_title"]
    assert "# Service Component Documentation" in res["content"]
    assert "## Overview" in res["content"]


def test_generate_api_documentation():
    code = """
@router.post("/api/v1/users")
def create_user(): pass

@router.get("/api/v1/users/{id}")
def get_user(id: int): pass
"""
    res = AIDocGeneratorEngine.generate_documentation("users_api.py", code, "api_doc")
    assert "API Reference Specifications" in res["content"]
    assert "`POST`" in res["content"]
    assert "`GET`" in res["content"]


def test_generate_missing_comments():
    code = """
def compute(x):
    if x > 10:
        return x * 2
    return x
"""
    res = AIDocGeneratorEngine.generate_documentation("calc.py", code, "missing_comments")
    assert "# Branch condition" in res["content"] or "// Step 1:" in res["content"]


def test_generate_function_descriptions():
    code = "def validate_session(token): pass"
    res = AIDocGeneratorEngine.generate_documentation("auth.py", code, "function_description")
    assert "Functional Specifications" in res["content"]
    assert "## Function: `validate_session()`" in res["content"]


def test_generate_usage_examples():
    code = "def process_order(data): pass"
    res = AIDocGeneratorEngine.generate_documentation("order_service.py", code, "usage_examples")
    assert "Executable Usage Examples" in res["content"]
    assert "from order_service import process_order" in res["content"]
