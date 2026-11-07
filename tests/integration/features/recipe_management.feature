Feature: Recipe Management API
    As a user
    I want to manage my recipes through a REST API
    So that I can create, read, update, delete, and search recipes

    Background:
        Given the application is running
        And I have a mocked recipe repository

    Scenario: Create a new recipe
        Given I have a recipe payload with title "Spaghetti Bolognese", content "Ingredients...", and summary "Classic Italian dish"
        When I POST to "/api/v1/recipes/" with the recipe payload
        Then the response status code should be 201
        And the response should contain the recipe with title "Spaghetti Bolognese"
        And the response should contain the recipe with summary "Classic Italian dish"

    Scenario: Get a recipe by ID
        Given a recipe exists with id 1, title "Spaghetti Bolognese", content "Ingredients...", and summary "Classic Italian dish"
        When I GET "/api/v1/recipes/1"
        Then the response status code should be 200
        And the response should contain the recipe with title "Spaghetti Bolognese"

    Scenario: Get a non-existent recipe
        When I GET "/api/v1/recipes/999"
        Then the response status code should be 404

    Scenario: Update a recipe
        Given a recipe exists with id 1, title "Old Title", content "Old content", and summary "Old summary"
        When I PUT to "/api/v1/recipes/1" with title "New Title", content "New content", and summary "New summary"
        Then the response status code should be 200
        And the response should contain the recipe with title "New Title"
        And the response should contain the recipe with content "New content"

    Scenario: Delete a recipe
        Given a recipe exists with id 1
        When I DELETE "/api/v1/recipes/1"
        Then the response status code should be 204

    Scenario: Delete a non-existent recipe
        When I DELETE "/api/v1/recipes/999"
        Then the response status code should be 404

    Scenario: List all recipes
        Given 3 recipes exist
        When I GET "/api/v1/recipes/"
        Then the response status code should be 200
        And the response should contain a list of recipes
        And the total count should be 3

    Scenario: List recipes with pagination
        Given 15 recipes exist
        When I GET "/api/v1/recipes/?skip=0&limit=10"
        Then the response status code should be 200
        And the response should contain 10 recipes
        And the skip should be 0
        And the limit should be 10

    Scenario: Search recipes by keyword
        Given a recipe exists with title "Pasta Carbonara" and content "Pasta with eggs..."
        And a recipe exists with title "Beef Stew" and content "Beef with vegetables..."
        When I GET "/api/v1/recipes/search?keyword=pasta"
        Then the response status code should be 200
        And the response should contain the recipe with title "Pasta Carbonara"
        And the response should not contain the recipe with title "Beef Stew"