Feature: Account initialization

    Scenario: Initialize a new account successfully
        Given I initialize a new API account
        Then the response status code is 200
        And the response contains an authentication token