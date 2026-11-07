# mypy: disable-error-code="untyped-decorator"
from behave import given, then, when  # type: ignore[import-untyped]
from fastapi.testclient import TestClient

from src.main import app


# Given steps
@given("the API is running")
def step_given_api_running(context: object) -> None:
    if not hasattr(context, "client"):
        context.client = TestClient(app)  # type: ignore[attr-defined]


# When steps
@when("I request the health endpoint")
def step_when_request_health(context: object) -> None:
    context.response = context.client.get("/health", follow_redirects=True)  # type: ignore[attr-defined]


@when("I request the items list endpoint")
def step_when_request_items_list(context: object) -> None:
    context.response = context.client.get("/api/v1/items/", follow_redirects=True)  # type: ignore[attr-defined]


@when('I create an item with name "{name}"')
def step_when_create_item(context: object, name: str) -> None:
    context.response = context.client.post(  # type: ignore[attr-defined]
        "/api/v1/items/",
        json={"name": name},
        follow_redirects=True,
    )


# Then steps
@then("the response status should be {status_code:d}")
def step_then_response_status(context: object, status_code: int) -> None:
    assert context.response.status_code == status_code  # type: ignore[attr-defined]


@then('the response should contain "{key}" with value "{value}"')
def step_then_response_contains(context: object, key: str, value: str) -> None:
    assert context.response.json()[key] == value  # type: ignore[attr-defined]


@then("the response should be an empty list")
def step_then_response_empty_list(context: object) -> None:
    assert context.response.json() == []  # type: ignore[attr-defined]


@then("the response should be a list")
def step_then_response_is_list(context: object) -> None:
    assert isinstance(context.response.json(), list)  # type: ignore[attr-defined]


@then("the response should contain 2 items")
def step_then_response_contains_2_items(context: object) -> None:
    assert len(context.response.json()) == 2  # type: ignore[attr-defined]


@then('the response should contain "{key}"')
def step_then_response_contains_key(context: object, key: str) -> None:
    assert key in context.response.json()  # type: ignore[attr-defined]
