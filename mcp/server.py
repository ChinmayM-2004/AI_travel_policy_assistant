import sys
from pathlib import Path

from mcp.server import MCPServer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.tools import (
    check_employee_eligibility as check_employee_eligibility_tool,
    validate_trip as validate_trip_tool,
    calculate_reimbursement as calculate_reimbursement_tool,
)


mcp = MCPServer(
    "AI Travel Policy Assistant",
    description="MCP server for employee travel policy tools."
)


@mcp.tool()
def check_employee_eligibility(employee_id: str) -> dict:
    """Check whether an employee is eligible for business travel."""
    return check_employee_eligibility_tool(employee_id)


@mcp.tool()
def validate_trip(
    employee_id: str,
    trip_type: str,
    amount: float,
    time: str
) -> dict:
    """Validate an employee trip against the configured travel policy."""
    return validate_trip_tool(
        employee_id,
        trip_type,
        amount,
        time
    )


@mcp.tool()
def calculate_reimbursement(
    trip_amount: float,
    policy_limit: float
) -> dict:
    """Calculate the reimbursable amount and amount requiring review."""
    return calculate_reimbursement_tool(
        trip_amount,
        policy_limit
    )


async def test_mcp_server():

    print("AI Travel Policy MCP Server")

    print("Available tools:")

    tools = await mcp.list_tools()

    for tool in tools:
        print(f"- {tool.name}")

    print("\nMCP server initialized successfully.")


if __name__ == "__main__":

    import asyncio

    asyncio.run(test_mcp_server())