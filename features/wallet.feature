Feature: Wallet retrieval

    Scenario Outline: Retrieve initialized account wallets
        Given I initialize a new API account
        When I request "<path>" with authentication
        Then the response status code is <status>
        And the response contains <wallet_count> wallets
        And every wallet has an ID, currency and balance

        Examples:
            | path                              | status | wallet_count |
            | /api/wallet                       | 200    | 3            |
            | /api/wallet?offset=0&max_count=2  | 200    | 2            |   