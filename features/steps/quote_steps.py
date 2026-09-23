from datetime import datetime, timezone
from decimal import Decimal
import json
import time
from behave import step, then, when

@when(
    'I create a quote from "{from_currency}" to "{to_currency}" '
    'for "{amount}"'
)
def step_create_quote(
    context,
    from_currency: str,
    to_currency: str,
    amount: str,
) -> None:
    request_body = {
        "from": from_currency,
        "to": to_currency,
        "fromWallet": context.wallets_before[from_currency]["id"],
        "toWallet": context.wallets_before[to_currency]["id"],
        "amountIn": amount,
        "useMaximum": False,
        "useMinimum": False,
        "reference": "behave-conversion-test",
        "payInMethod": "wallet",
        "payOutMethod": "wallet",
    }

    context.response = context.api.request(
        "POST",
        "/api/v1/quote",
        json=request_body,
    )
    context.response.raise_for_status()
    context.response_data = context.response.json()

    if context.response.ok:
        context.created_quote = context.response_data
        
@then("the quote has the requested currencies")
def step_verify_quote_currencies(context) -> None:
    assert context.created_quote["from"] == context.wallets_before[context.created_quote["from"]]["currency"]["code"]
    assert context.created_quote["to"] == context.wallets_before[context.created_quote["to"]]["currency"]["code"]

@then("the quote has a positive exchange rate")
def step_verify_quote_positive_exchange_rate(context) -> None:
    assert Decimal(context.created_quote["price"]) > Decimal("0"), (
        f"Expected a positive exchange rate, but got {context.created_quote['price']}"
    )

@then("the quote has a future acceptance expiry date")
def step_verify_quote_expiry(context) -> None:
    expiry = datetime.fromtimestamp(
        context.created_quote["acceptanceExpiryDate"],
        tz=timezone.utc,
    )
    assert expiry > datetime.now(timezone.utc), (
        f"Expected a future acceptance expiry date, but got {expiry.isoformat()}"
    )

@then('the quote has a "{expected_service_fee}" percent service fee')
def step_verify_quote_service_fee(
    context, 
    expected_service_fee: str
) -> None:
    actual_service_fee = Decimal(
        context.created_quote["fees"]["percentage"]["service"]
    )

    assert actual_service_fee == Decimal(expected_service_fee), (
        f"Expected service fee to be {expected_service_fee}, "
        f"but got {actual_service_fee}"
    )

@when("I accept the created quote")
def step_accept_created_quote(context) -> None:
    context.response = context.api.request(
        "PUT",
        f"/api/v1/quote/accept/{context.created_quote['uuid']}",
    )
    context.response.raise_for_status()
    context.response_data = context.response.json()

    if context.response.ok:
        context.accepted_quote = context.response_data

@step("I wait for the quote payment to complete")
def step_wait_for_payment_to_complete(context) -> None:
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        response = context.api.request(
            "GET",
            f"/api/v1/quote/{context.created_quote['uuid']}",
        )
        response.raise_for_status()
        context.response_data = response.json()
        context.accepted_quote = context.response_data

        if context.accepted_quote["paymentStatus"] == "SUCCESS":
            break

        attempt += 1
        time.sleep(5)

    assert context.accepted_quote["paymentStatus"] == "SUCCESS", (
        f"Expected payment status to be 'SUCCESS', but got {context.accepted_quote['paymentStatus']}"
    )


@when('I wait {seconds:d} seconds for the created quote to expire')
def step_wait_for_quote_to_expire(context, seconds: int) -> None:
    time.sleep(seconds)


@when("I retrieve the created quote")
def step_retrieve_created_quote(context) -> None:
    context.response = context.api.request(
        "GET",
        f'/api/v1/quote/{context.created_quote["uuid"]}',
    )
    context.response_data = context.response.json()

    if context.response.ok:
        context.expired_quote = context.response_data


@then("the created quote is expired")
def step_verify_created_quote_is_expired(context) -> None:
    assert context.expired_quote["quoteStatus"] == "EXPIRED", (
        "Expected quote status to be EXPIRED, but got "
        f'{context.expired_quote["quoteStatus"]}'
    )
    assert context.expired_quote["paymentStatus"] == "EXPIRED", (
        "Expected payment status to be EXPIRED, but got "
        f'{context.expired_quote["paymentStatus"]}'
    )


@when("I try to accept the created quote")
def step_try_to_accept_created_quote(context) -> None:
    context.response = context.api.request(
        "PUT",
        f'/api/v1/quote/accept/{context.created_quote["uuid"]}',
    )
    context.response_data = context.response.json()


@then('the response detail is "{expected_detail}"')
def step_verify_response_detail(context, expected_detail: str) -> None:
    assert context.response_data["detail"] == expected_detail, (
        f'Expected response detail "{expected_detail}", but got '
        f'{context.response_data.get("detail")!r}'
    )

@then("the created quote and the accepted quote match outside lifecycle fields")
def step_verify_quotes_equality(context) -> None:
    fields_that_may_change = {
        "amountDue",
        "quoteStatus",
        "paymentStatus",
        "acceptanceDate",
        "lastUpdated",
    }

    created_quote = {
        key: value
        for key, value in context.created_quote.items()
        if key not in fields_that_may_change
    }
    accepted_quote = {
        key: value
        for key, value in context.accepted_quote.items()
        if key not in fields_that_may_change
    }

    assert created_quote == accepted_quote, (
        "Created and accepted quotes differ outside lifecycle fields.\n"
        f"Created: {json.dumps(created_quote, indent=2)}\n"
        f"Accepted: {json.dumps(accepted_quote, indent=2)}"
    )

@then("the quote is accepted and payment is processing")
def step_verify_accepted_quote(context) -> None:
    assert context.accepted_quote["quoteStatus"] == "ACCEPTED", (
        f"Expected quote status to be 'ACCEPTED', but got {context.accepted_quote['quoteStatus']}"
    )
    assert context.accepted_quote["paymentStatus"] == "PROCESSING", (
        f"Expected payment status to be 'PROCESSING', but got {context.accepted_quote['paymentStatus']}"
    )
    assert context.accepted_quote["acceptanceDate"] is not None

@then("the wallet balances reflect the completed conversion")
def step_verify_wallet_balances(context) -> None:
    source_currency = context.created_quote["from"]
    target_currency = context.created_quote["to"]

    source_before = context.wallets_before[source_currency]["balance_before"]
    source_after = context.wallets_after[source_currency]["balance_after"]
    target_before = context.wallets_before[target_currency]["balance_before"]
    target_after = context.wallets_after[target_currency]["balance_after"]

    amount_due = Decimal(context.created_quote["amountDue"])
    amount_out = Decimal(context.created_quote["amountOut"])
    service_fee = Decimal(
        context.created_quote["fees"]["value"]["service"]
    )
    
    expected_source_after = (
        source_before
        - amount_due
    )
    expected_target_after = target_before + amount_out

    amountOut_decimal_places = len(context.created_quote["amountOut"].partition(".")[2])
    rounding_unit = Decimal("0." + "0" * amountOut_decimal_places)

    assert source_after.quantize(rounding_unit) == (
        expected_source_after.quantize(rounding_unit)
    ), (
        f"Expected {source_currency} balance {expected_source_after}, "
        f"but received {source_after}."
    )

    assert target_after.quantize(rounding_unit) == (
        expected_target_after.quantize(rounding_unit)
    ), (
        f"Expected {target_currency} balance {expected_target_after}, "
        f"but received {target_after}."
    )

@then("the quote value fee is correctly calculated")
def step_verify_service_fee(context) -> None:
    quote_amount_due = Decimal(context.created_quote["amountDue"])
    quote_value_service_fee = Decimal(
        context.created_quote["fees"]["value"]["service"]
    )
    quote_percentage_service_fee = Decimal(
        context.created_quote["fees"]["percentage"]["service"]
    )
    expected_value_service_fee = quote_amount_due * quote_percentage_service_fee / Decimal("100")

    assert expected_value_service_fee == quote_value_service_fee, (
        "Quote service fee is incorrect. "
        f"Expected {expected_value_service_fee}, "
        f"received {quote_value_service_fee}."
    )

@then("the output amount is correctly calculated")
def step_verify_output_amount(context) -> None:
    
    quote_price = Decimal(context.created_quote["price"])
    quote_amount_due = Decimal(context.created_quote["amountDue"])
    quote_amount_out = Decimal(context.created_quote["amountOut"])
    quote_value_service_fee = Decimal(
        context.created_quote["fees"]["value"]["service"]
    )

    expected_amount_out = (quote_amount_due - quote_value_service_fee) * quote_price
    amountOut_decimal_places = len(context.created_quote["amountOut"].partition(".")[2])
    output_rounding_unit = Decimal("0." + "0" * amountOut_decimal_places)

    rounded_quote_amount_out = quote_amount_out.quantize(output_rounding_unit)
    rounded_expected_amount_out = expected_amount_out.quantize(output_rounding_unit)

    assert rounded_quote_amount_out == (
        rounded_expected_amount_out
    ), (
        f"Expected quote amountOut {rounded_expected_amount_out}, "
        f"but received {rounded_quote_amount_out}."
    )

    