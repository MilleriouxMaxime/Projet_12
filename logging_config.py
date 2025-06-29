import os

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

load_dotenv()


def init_sentry():
    """Initialize Sentry SDK with appropriate configuration."""
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            SqlalchemyIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # By default the SDK will try to use the SENTRY_RELEASE
        # environment variable, or infer a git commit
        # SHA as release, however you may want to set
        # something more human-readable.
        release="epicevents@1.0.0",
    )


def log_employee_change(action, employee_data):
    with sentry_sdk.push_scope() as scope:
        scope.set_extra("employee_number", employee_data.get("employee_number"))
        scope.set_extra("department", employee_data.get("department"))
        scope.set_extra("action", action)
        sentry_sdk.capture_message(
            f"Employee {action}: {employee_data.get('full_name', 'Unknown')}",
            level="info",
        )


def log_contract_signature(contract_data):
    """Log contract signature."""
    sentry_sdk.capture_message(
        f"Contract signed: Contract ID {contract_data.get('id')}",
        level="info",
        extras={
            "contract_id": contract_data.get("id"),
            "client_id": contract_data.get("client_id"),
            "total_amount": contract_data.get("total_amount"),
        },
    )


def log_exception(exception, context=None):
    """Log unexpected exceptions."""
    sentry_sdk.capture_exception(exception, extras=context or {})
