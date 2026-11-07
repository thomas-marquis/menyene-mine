Feature: Items API
    As a user of the API
    I want to manage items
    So that I can create and retrieve items

    Background:
        Given the API is running

    Scenario: Create a new item
        When I create an item with name "Test Item"
        Then the response status should be 201
        And the response should contain "name" with value "Test Item"
        And the response should contain "id"

    Scenario: List items returns items
        When I request the items list endpoint
        Then the response status should be 200
        And the response should be a list
