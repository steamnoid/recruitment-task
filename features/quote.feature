Feature: Quote creation

    Scenario Outline: Create a conversion quote
        Given I initialize a new API account
        And I identify the "<from_currency>" wallet "before" the operation
        And I identify the "<to_currency>" wallet "before" the operation
        And I record the "<from_currency>" wallet balance "before" the operation
        And I record the "<to_currency>" wallet balance "before" the operation
        When I create a quote from "<from_currency>" to "<to_currency>" for "<amount>"
        Then the response status code is 201
        And the quote has the requested currencies
        And the quote has a positive exchange rate
        And the quote has a future acceptance expiry date
        And the quote has a "<service_fee>" percent service fee
        And the quote value fee is correctly calculated
        When I accept the created quote
        Then the response status code is 200
        And the quote is accepted and payment is processing
        When I wait for the quote payment to complete
        Then the created quote and the accepted quote match outside lifecycle fields
        And I identify the "<from_currency>" wallet "after" the operation
        And I identify the "<to_currency>" wallet "after" the operation
        And I record the "<from_currency>" wallet balance "after" the operation
        And I record the "<to_currency>" wallet balance "after" the operation
        And the wallet balances reflect the completed conversion
        And the output amount is correctly calculated

        Examples:
            | from_currency | to_currency | amount | service_fee |
            | ETH           | TRX         | 1      | 0.01        |
            | TRX           | USDT        | 420    | 0.01        |
            | TRX           | ETH         | 987    | 0.01        |

    Scenario: An expired quote cannot be accepted
        Given I initialize a new API account
        And I identify the "TRX" wallet "before" the operation
        And I identify the "USDT" wallet "before" the operation
        When I create a quote from "TRX" to "USDT" for "100"
        Then the response status code is 201
        When I wait 21 seconds for the created quote to expire
        And I retrieve the created quote
        Then the response status code is 200
        And the created quote is expired
        When I try to accept the created quote
        Then the response status code is 412
        And the response detail is "Precondition Failed"