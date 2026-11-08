# mypy: disable-error-code="untyped-decorator"
from typing import Any

from behave import given, then, when  # type: ignore[import-untyped]
from fastapi.testclient import TestClient

from src.main import app


# Given steps
@given("the API is running")
def step_given_api_running(context: Any) -> None:
    if not hasattr(context, "client"):
        context.client = TestClient(app)


# When steps
@when("I request the health endpoint")
def step_when_request_health(context: Any) -> None:
    context.response = context.client.get("/health", follow_redirects=True)


# Then steps
@then("the response status should be {status_code:d}")
def step_then_response_status(context: Any, status_code: int) -> None:
    assert context.response.status_code == status_code


@then('the response should contain "{key}" with value "{value}"')
def step_then_response_contains(context: Any, key: str, value: str) -> None:
    assert context.response.json()[key] == value


@then("the response should be an empty list")
def step_then_response_empty_list(context: Any) -> None:
    assert context.response.json() == []


@then("the response should be a list")
def step_then_response_is_list(context: Any) -> None:
    assert isinstance(context.response.json(), list)


@then("the response should contain 2 items")
def step_then_response_contains_2_items(context: Any) -> None:
    assert len(context.response.json()) == 2


@then('the response should contain "{key}"')
def step_then_response_contains_key(context: Any, key: str) -> None:
    assert key in context.response.json()
