import pytest
from app.services.test_generator.generator import AITestGeneratorEngine


def test_generate_pytest_comprehensive_suite():
    code = """
def process_user_registration(user_data):
    if not user_data or "email" not in user_data:
        raise ValueError("Invalid user payload")
    return {"status": "created", "id": 101, "email": user_data["email"]}
"""
    res = AITestGeneratorEngine.generate_test_suite(
        target_file="user_service.py",
        code_content=code,
        test_framework="pytest",
        test_category="comprehensive"
    )

    assert res["test_name"] == "test_user_service.py"
    assert "import pytest" in res["generated_code"]
    assert "test_process_user_registration_positive_success" in res["generated_code"]
    assert "test_process_user_registration_negative_invalid_input" in res["generated_code"]
    assert "test_process_user_registration_boundary_values" in res["generated_code"]
    assert "test_process_user_registration_with_mock_dependency" in res["generated_code"]
    assert "Workflow & Architecture" in res["workflow_explanation"]


def test_generate_junit_suite():
    code = """
public class OrderService {
    public boolean processOrder(String orderId) {
        if (orderId == null) throw new IllegalArgumentException("Order ID required");
        return true;
    }
}
"""
    res = AITestGeneratorEngine.generate_test_suite(
        target_file="OrderService.java",
        code_content=code,
        test_framework="junit",
        test_category="comprehensive"
    )

    assert res["test_name"] == "OrderserviceTest.java" or res["test_name"] == "OrderServiceTest.java"
    assert "import org.junit.jupiter.api.Test;" in res["generated_code"]
    assert "@ParameterizedTest" in res["generated_code"]
    assert "assertThrows" in res["generated_code"]
    assert "JUnit 5" in res["workflow_explanation"]


def test_generate_jest_suite():
    code = """
async function fetchUserProfile(userId) {
    if (!userId) throw new Error("User ID required");
    return { id: userId, name: "Alice" };
}
"""
    res = AITestGeneratorEngine.generate_test_suite(
        target_file="userService.ts",
        code_content=code,
        test_framework="jest",
        test_category="comprehensive"
    )

    assert res["test_name"] == "userService.test.ts"
    assert "describe(" in res["generated_code"]
    assert "expect(" in res["generated_code"]
    assert "jest.fn()" in res["generated_code"]
    assert "Vitest" in res["workflow_explanation"]
