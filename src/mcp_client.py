import asyncio
import importlib.util
import sys
from pathlib import Path
from mcp.client import Client

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MCP_SERVER_FILE = (
    PROJECT_ROOT
    / "mcp"
    / "server.py"
)


def get_mcp_server():

    module_name = "travel_policy_mcp_server"

    spec = importlib.util.spec_from_file_location(
        module_name,
        MCP_SERVER_FILE
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Unable to load MCP server from: {MCP_SERVER_FILE}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    # Register the module before executing it.
    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    if not hasattr(module, "mcp"):
        raise ImportError(
            "MCP server was loaded, but the 'mcp' "
            "server instance was not found."
        )

    return module.mcp


async def call_mcp_tool_async(
    tool_name,
    arguments
):

    mcp_server = get_mcp_server()

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            tool_name,
            arguments
        )

        return result


def call_mcp_tool(
    tool_name,
    arguments
):

    return asyncio.run(
        call_mcp_tool_async(
            tool_name,
            arguments
        )
    )


def check_employee_eligibility_mcp(
    employee_id
):

    return call_mcp_tool(
        "check_employee_eligibility",
        {
            "employee_id": employee_id
        }
    )


def validate_trip_mcp(
    employee_id,
    trip_type,
    amount,
    time
):

    return call_mcp_tool(
        "validate_trip",
        {
            "employee_id": employee_id,
            "trip_type": trip_type,
            "amount": amount,
            "time": time
        }
    )


def calculate_reimbursement_mcp(
    trip_amount,
    policy_limit
):

    return call_mcp_tool(
        "calculate_reimbursement",
        {
            "trip_amount": trip_amount,
            "policy_limit": policy_limit
        }
    )


if __name__ == "__main__":

    print("Testing MCP client...\n")

    print("1. Employee Eligibility:")

    result = check_employee_eligibility_mcp(
        "EMP001"
    )

    print(result)
    print()

    print("2. Trip Validation:")

    result = validate_trip_mcp(
        employee_id="EMP001",
        trip_type="airport",
        amount=1500,
        time="10:00"
    )

    print(result)
    print()

    print("3. Reimbursement Calculation:")

    result = calculate_reimbursement_mcp(
        trip_amount=2500,
        policy_limit=2000
    )

    print(result)
    print()

    print("MCP client test completed successfully!")