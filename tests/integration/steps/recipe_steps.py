# mypy: disable-error-code="untyped-decorator"
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from behave import given, then, when  # type: ignore[import-untyped]
from fastapi.testclient import TestClient

from src.di import override_recipe_repository
from src.domain.entities.recipe import Recipe
from src.domain.ports.recipe_repository import RecipeRepositoryPort
from src.main import app


# Given steps
@given("the application is running")
def step_given_application_running(context: Any) -> None:
    if not hasattr(context, "client"):
        context.client = TestClient(app)


@given("I have a mocked recipe repository")
def step_given_mocked_recipe_repository(context: Any) -> None:
    # Create mock repository
    mock_repo = MagicMock(spec=RecipeRepositoryPort)

    # Setup mock implementations
    async def mock_create(recipe: Recipe) -> Recipe:
        # Auto-increment ID for new recipes
        new_id = len(context.mocked_recipes) + 1
        now = datetime.now(UTC)
        new_recipe = Recipe(
            id=new_id,
            title=recipe.title,
            content=recipe.content,
            summary=recipe.summary,
            creation_date=now,
            last_updated=now,
        )
        context.mocked_recipes[new_id] = new_recipe
        return new_recipe

    async def mock_get_by_id(recipe_id: int) -> Recipe | None:
        return context.mocked_recipes.get(recipe_id)  # type: ignore[no-any-return]

    async def mock_update(recipe: Recipe) -> Recipe | None:
        if recipe.id not in context.mocked_recipes:
            return None
        # Update the existing recipe but preserve creation_date
        existing = context.mocked_recipes[recipe.id]
        updated_recipe = Recipe(
            id=recipe.id,
            title=recipe.title,
            content=recipe.content,
            summary=recipe.summary,
            creation_date=existing.creation_date,
            last_updated=datetime.now(UTC),
        )
        context.mocked_recipes[recipe.id] = updated_recipe
        return updated_recipe

    async def mock_delete(recipe_id: int) -> bool:
        if recipe_id not in context.mocked_recipes:
            return False
        del context.mocked_recipes[recipe_id]
        return True

    async def mock_list_all(skip: int = 0, limit: int = 100) -> list[Recipe]:
        return list(context.mocked_recipes.values())[skip : skip + limit]

    async def mock_search(keyword: str, skip: int = 0, limit: int = 100) -> list[Recipe]:
        keyword_lower = keyword.lower()
        return [
            recipe
            for recipe in context.mocked_recipes.values()
            if (recipe.title and keyword_lower in recipe.title.lower())
            or (recipe.content and keyword_lower in recipe.content.lower())
        ][skip : skip + limit]

    # Configure mock methods
    mock_repo.create = mock_create
    mock_repo.get_by_id = mock_get_by_id
    mock_repo.update = mock_update
    mock_repo.delete = mock_delete
    mock_repo.list_all = mock_list_all
    mock_repo.search = mock_search

    # Override the repository
    override_recipe_repository(mock_repo)

    # Initialize storage for mocked recipes
    if not hasattr(context, "mocked_recipes"):
        context.mocked_recipes = {}


@given('I have a recipe payload with title "{title}", content "{content}", and summary "{summary}"')  # noqa: E501
def step_given_recipe_payload(context: Any, title: str, content: str, summary: str) -> None:
    context.recipe_payload = {
        "title": title,
        "content": content,
        "summary": summary,
    }


# When steps
@when('I POST to "{path}" with the recipe payload')
def step_when_post_recipe(context: Any, path: str) -> None:
    context.response = context.client.post(path, json=context.recipe_payload, follow_redirects=True)


@when('I GET "{path}"')
def step_when_get(context: Any, path: str) -> None:
    context.response = context.client.get(path, follow_redirects=True)


@when('I PUT to "{path}" with title "{title}", content "{content}", and summary "{summary}"')  # noqa: E501
def step_when_put_recipe(context: Any, path: str, title: str, content: str, summary: str) -> None:
    payload = {
        "title": title,
        "content": content,
        "summary": summary,
    }
    context.response = context.client.put(path, json=payload, follow_redirects=True)


@when('I DELETE "{path}"')
def step_when_delete(context: Any, path: str) -> None:
    context.response = context.client.delete(path, follow_redirects=True)


# Then steps
@then("the response status code should be {status_code}")
def step_then_status_code(context: Any, status_code: int) -> None:
    assert context.response.status_code == int(status_code)


@then('the response should contain the recipe with title "{title}"')
def step_then_response_contains_title(context: Any, title: str) -> None:
    data = context.response.json()
    # Handle both single recipe and list of recipes
    if "recipes" in data:
        recipes = data["recipes"]
        titles = [r["title"] for r in recipes]
        assert title in titles, f"Title {title} not found in {titles}"
    else:
        assert data["title"] == title


@then('the response should contain the recipe with summary "{summary}"')
def step_then_response_contains_summary(context: Any, summary: str) -> None:
    data = context.response.json()
    # Handle both single recipe and list of recipes
    if "recipes" in data:
        recipes = data["recipes"]
        summaries = [r["summary"] for r in recipes]
        assert summary in summaries, f"Summary {summary} not found in {summaries}"
    else:
        assert data["summary"] == summary


@then('the response should contain the recipe with content "{content}"')
def step_then_response_contains_content(context: Any, content: str) -> None:
    data = context.response.json()
    # Handle both single recipe and list of recipes
    if "recipes" in data:
        recipes = data["recipes"]
        contents = [r["content"] for r in recipes]
        assert content in contents, f"Content {content} not found in {contents}"
    else:
        assert data["content"] == content


@then("the response should contain a list of recipes")
def step_then_response_contains_list(context: Any) -> None:
    data = context.response.json()
    assert "recipes" in data
    assert isinstance(data["recipes"], list)


@then("the total count should be {count}")
def step_then_total_count(context: Any, count: int) -> None:
    data = context.response.json()
    assert data["total"] == int(count)


@then("the response should contain {count} recipes")
def step_then_recipe_count(context: Any, count: int) -> None:
    data = context.response.json()
    assert len(data["recipes"]) == int(count)


@then("the skip should be {skip}")
def step_then_skip(context: Any, skip: int) -> None:
    data = context.response.json()
    assert data["skip"] == int(skip)


@then("the limit should be {limit}")
def step_then_limit(context: Any, limit: int) -> None:
    data = context.response.json()
    assert data["limit"] == int(limit)


@then('the response should not contain the recipe with title "{title}"')
def step_then_response_not_contains_title(context: Any, title: str) -> None:
    data = context.response.json()
    recipes = data.get("recipes", [])
    for recipe in recipes:
        assert recipe["title"] != title


# Helper steps for setting up test data
@given(
    'a recipe exists with id {recipe_id:d}, title "{title}", content "{content}", and summary "{summary}"'  # noqa: E501
)
def step_given_recipe_exists(
    context: Any, recipe_id: int, title: str, content: str, summary: str
) -> None:  # noqa: E501
    # Create the recipe in the mock repository
    now = datetime.now(UTC)
    recipe = Recipe(
        id=recipe_id,
        title=title,
        content=content,
        summary=summary,
        creation_date=now,
        last_updated=now,
    )
    context.mocked_recipes[recipe_id] = recipe


@given("{count:d} recipes exist")
def step_given_recipes_exist(context: Any, count: int) -> None:
    now = datetime.now(UTC)
    for i in range(1, count + 1):
        recipe = Recipe(
            id=i,
            title=f"Recipe {i}",
            content=f"Content for recipe {i}",
            summary=f"Summary for recipe {i}",
            creation_date=now,
            last_updated=now,
        )
        context.mocked_recipes[i] = recipe


@given('a recipe exists with title "{title}" and content "{content}"')
def step_given_recipe_exists_simple(context: Any, title: str, content: str) -> None:
    # Create the recipe in the mock repository
    now = datetime.now(UTC)
    new_id = len(context.mocked_recipes) + 1
    recipe = Recipe(
        id=new_id,
        title=title,
        content=content,
        summary=f"Summary for {title}",
        creation_date=now,
        last_updated=now,
    )
    context.mocked_recipes[new_id] = recipe


@given("a recipe exists with id {recipe_id:d}")
def step_given_recipe_exists_by_id(context: Any, recipe_id: int) -> None:
    # Create the recipe in the mock repository
    now = datetime.now(UTC)
    recipe = Recipe(
        id=recipe_id,
        title=f"Recipe {recipe_id}",
        content=f"Content for recipe {recipe_id}",
        summary=f"Summary for recipe {recipe_id}",
        creation_date=now,
        last_updated=now,
    )
    context.mocked_recipes[recipe_id] = recipe
