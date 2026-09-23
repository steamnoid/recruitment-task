from behave import step, then
from decimal import Decimal

@then("the response contains {expected_count:d} wallets")
def step_verify_wallet_count(context, expected_count: int) -> None:
    assert isinstance(context.response_data, list), (
        "Expected the response body to be a list of wallets"
    )
    assert len(context.response_data) == expected_count, (
        f"Expected {expected_count} wallets, "
        f"but found {len(context.response_data)}"
    )

@then("every wallet has an ID, currency and balance")
def step_verify_wallet_fields(context) -> None:
    for wallet in context.response_data:
        assert "id" in wallet, "Wallet is missing 'id'"
        assert "currency" in wallet, "Wallet is missing 'currency'"
        assert "balance" in wallet, "Wallet is missing 'balance'"

@step('I identify the "{currency}" wallet "{when}" the operation')
def step_identify_wallet(context, currency: str, when: str) -> None:
    response = context.api.request("GET", "/api/wallet")
    response.raise_for_status()

    wallets = response.json()
    matching_wallet = next(
        (wallet for wallet in wallets if wallet["currency"]["code"] == currency),
        None,
    )

    assert matching_wallet is not None, (
        f"No wallet found with currency '{currency}'"
    )

    if when == "before":
        context.wallets_before[currency] = matching_wallet
    elif when == "after":
        context.wallets_after[currency] = matching_wallet

@step('I record the "{currency}" wallet balance "{when}" the operation')
def step_record_wallet_balance(context, currency: str, when: str) -> None:
    if when == "before":
        context.wallets_before[currency]["balance_before"] = Decimal(context.wallets_before[currency]["balance"])
    elif when == "after":
        context.wallets_after[currency]["balance_after"] = Decimal(context.wallets_after[currency]["balance"])