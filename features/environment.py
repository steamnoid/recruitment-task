from support.api_client import APIClient

BASE_URL = "https://qa-simulator.shared.bvnk.com"

def before_scenario(context, scenario) -> None:
    context.api = APIClient(BASE_URL)
    context.response = None
    context.response_data = None
    context.wallets_before = {}
    context.wallets_after = {}
    context.quote = None