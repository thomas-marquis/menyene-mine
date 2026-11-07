Feature: Health Check
    As a system administrator
    I want to verify the API is running
    So that I can ensure the service is healthy

    Scenario: Health endpoint returns OK
        Given the API is running
        When I request the health endpoint
        Then the response status should be 200
        And the response should contain "status" with value "ok"
