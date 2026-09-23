# BVNK API Testing Task

End-to-end API tests for the BVNK QA simulator, written in Python with Behave and Gherkin.

## Prerequisites

- Python 3
- Internet access to `https://qa-simulator.shared.bvnk.com`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Tests

Run the full suite:

```bash
behave
```

Run a single feature:

```bash
behave features/quote.feature
```

Run tests and create reports:

```bash
./run_tests.sh
```

The report command creates:

- `reports/behave.html` - HTML execution report
- `reports/junit/TESTS-*.xml` - JUnit XML reports for CI systems

## Test Coverage

- Account initialization and bearer-token retrieval
- Wallet retrieval and pagination
- Parameterized conversions: ETH to TRX, TRX to USDT, and TRX to ETH
- Quote exchange rate, service fee, output amount, and wallet balance validation
- Quote acceptance and payment completion
- Quote expiry after 20 seconds and rejection of an acceptance attempt with `412 Precondition Failed`

## Project Structure

```text
features/              Gherkin scenarios and Behave steps
support/api_client.py  HTTP client and bearer-token handling
reports/               Generated HTML and JUnit reports
run_tests.sh           Test and report generation command
```