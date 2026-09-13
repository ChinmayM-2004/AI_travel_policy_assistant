import json
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Employee data file
EMPLOYEE_FILE = PROJECT_ROOT / "data" / "employees" / "employees.json"


def load_employees():
    if not EMPLOYEE_FILE.exists():
        print(f"Error: Employee file not found: {EMPLOYEE_FILE}")
        return []

    try:
        return json.loads(
            EMPLOYEE_FILE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading employee data: {e}")
        return []


def check_employee_eligibility(employee_id):
    employees = load_employees()

    for employee in employees:
        if employee["employee_id"] == employee_id:
            return {
                "status": employee["eligibility_status"],
                "employee_id": employee["employee_id"],
                "country": employee["country"],
                "employee_type": employee["employee_type"],
                "department": employee["department"]
            }

    return {
        "status": "Employee Not Found",
        "employee_id": employee_id,
        "country": None,
        "employee_type": None,
        "department": None
    }


def validate_trip(employee_id, trip_type, amount, time):
    employee = check_employee_eligibility(employee_id)

    if employee["status"] == "Employee Not Found":
        return {
            "status": "Invalid",
            "employee_id": employee_id,
            "reason": "Employee not found."
        }

    if employee["status"] != "Eligible":
        return {
            "status": "Not Eligible",
            "employee_id": employee_id,
            "trip_type": trip_type,
            "amount": amount,
            "time": time,
            "reason": "Employee is not eligible for business travel."
        }

    trip_type_lower = trip_type.lower()

    # -----------------------------------------------------
    # India airport trip
    # -----------------------------------------------------

    if (
        employee["country"] == "India"
        and trip_type_lower == "airport"
    ):
        policy_limit = 2000

        if amount > policy_limit:
            return {
                "status": "Needs Approval",
                "employee_id": employee_id,
                "trip_type": trip_type,
                "amount": amount,
                "time": time,
                "policy_limit": policy_limit,
                "reason": (
                    "The trip exceeds the standard India "
                    "policy limit of INR 2,000."
                )
            }

        return {
            "status": "Approved",
            "employee_id": employee_id,
            "trip_type": trip_type,
            "amount": amount,
            "time": time,
            "policy_limit": policy_limit,
            "reason": (
                "The trip is within the standard India "
                "policy limit."
            )
        }

    # -----------------------------------------------------
    # United States airport / local transportation
    # -----------------------------------------------------

    if (
        employee["country"] == "United States"
        and trip_type_lower == "airport"
    ):
        return {
            "status": "Approved",
            "employee_id": employee_id,
            "trip_type": trip_type,
            "amount": amount,
            "time": time,
            "policy_limit": None,
            "reason": (
                "Reasonable airport transportation expenses "
                "are reimbursable under the US policy when "
                "supported by receipts."
            )
        }

    # -----------------------------------------------------
    # Unsupported trip type
    # -----------------------------------------------------

    return {
        "status": "Needs Policy Review",
        "employee_id": employee_id,
        "trip_type": trip_type,
        "amount": amount,
        "time": time,
        "reason": (
            "No specific trip rule was configured "
            "for this trip type."
        )
    }


def calculate_reimbursement(trip_amount, policy_limit):
    reimbursable_amount = min(
        trip_amount,
        policy_limit
    )

    amount_requiring_review = max(
        trip_amount - policy_limit,
        0
    )

    return {
        "trip_amount": trip_amount,
        "policy_limit": policy_limit,
        "reimbursable_amount": reimbursable_amount,
        "amount_requiring_review": amount_requiring_review
    }


if __name__ == "__main__":

    print(
        check_employee_eligibility(
            "EMP001"
        )
    )

    print(
        validate_trip(
            "EMP001",
            "airport",
            1500,
            "10:00"
        )
    )

    print(
        validate_trip(
            "EMP003",
            "airport",
            50,
            "10:00"
        )
    )

    print(
        calculate_reimbursement(
            2500,
            2000
        )
    )