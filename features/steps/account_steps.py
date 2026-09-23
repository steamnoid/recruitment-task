from behave import given, then, when

@given("I initialize a new API account")
def step_initialize_api_account(context) -> None:
    context.response = context.api.initialise_account()
    context.response_data = context.response.json()

@then("the response status code is {expected_status:d}")
def step_verify_response_status(context, expected_status: int) -> None:
    assert context.response is not None, "No API response was received"
    assert context.response.status_code == expected_status, (
        f"Expected status {expected_status}, "
        f"but received {context.response.status_code}: {context.response.text}"
    )

@then("the response contains an authentication token")
def step_verify_authenticated_token(context) -> None:
    assert context.api.token, "The initialization response did not contain a token"

@when('I request "{path}" with authentication')
def step_request_authenticated_endpoint(context, path: str) -> None:
    context.response = context.api.request("GET", path)
    context.response_data = context.response.json()