import asyncio

from mcp.server import MCPServer
from mcp.client import Client

from mcp.server import MCPServer

from server import mcp


async def main():
    print("Testing MCP tool invocation...\n")

    async with Client(mcp) as client:

        # Test employee eligibility
        result = await client.call_tool(
            "check_employee_eligibility",
            {
                "employee_id": "EMP001"
            }
        )

        print("1. Employee Eligibility:")
        print(result)

        # Test trip validation
        result = await client.call_tool(
            "validate_trip",
            {
                "employee_id": "EMP001",
                "trip_type": "airport",
                "amount": 1500,
                "time": "10:00"
            }
        )

        print("\n2. Trip Validation:")
        print(result)

        # Test reimbursement calculation
        result = await client.call_tool(
            "calculate_reimbursement",
            {
                "trip_amount": 2500,
                "policy_limit": 2000
            }
        )

        print("\n3. Reimbursement Calculation:")
        print(result)

        print("\nMCP tool invocation successful!")


if __name__ == "__main__":
    asyncio.run(main())
