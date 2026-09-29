import json
from pathlib import Path

from app.graph import graph

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def initial_state(customer_query: str) -> dict:
    return {
        "customer_query": customer_query,
        "category": "",
        "priority": "",
        "issue_summary": "",
        "generated_response": "",
        "review_feedback": "",
        "approved": False,
        "final_response": "",
        "iteration_count": 0,
    }


def save_output(result: dict) -> None:
    (OUTPUT_DIR / "final_response.txt").write_text(
        result["final_response"], encoding="utf-8"
    )

    serializable = {
        "customer_query": result["customer_query"],
        "category": result["category"],
        "priority": result["priority"],
        "issue_summary": result["issue_summary"],
        "generated_response": result["generated_response"],
        "review_feedback": result["review_feedback"],
        "approved": result["approved"],
        "final_response": result["final_response"],
        "iteration_count": result["iteration_count"],
    }
    (OUTPUT_DIR / "execution_result.json").write_text(
        json.dumps(serializable, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def print_section(title: str):
    print("\n" + "=" * 55)
    print(title)
    print("=" * 55)


def main():
    print("=" * 55)
    print("       AI CUSTOMER SUPPORT AGENT")
    print("=" * 55)
    customer_query = input("Enter customer query: ").strip()

    if not customer_query:
        print("Customer query cannot be empty.")
        return

    try:
        result = graph.invoke(initial_state(customer_query))

        print_section("UNDERSTANDING CUSTOMER QUERY")
        print(result["issue_summary"])

        print_section("CLASSIFICATION")
        print(f"Category: {result['category']}")
        print(f"Priority: {result['priority']}")

        print_section("GENERATED RESPONSE")
        print(result["generated_response"])

        print_section("REVIEW")
        print(f"Approved: {result['approved']}")
        print(f"Feedback: {result['review_feedback'] or 'None'}")
        print(f"Fix cycles used: {result['iteration_count']}")

        print_section("FINAL RESPONSE")
        print(result["final_response"])

        save_output(result)
        print("\nSaved:")
        print("- output/final_response.txt")
        print("- output/execution_result.json")

    except Exception as exc:
        print(f"\nApplication error: {exc}")
        raise


if __name__ == "__main__":
    main()
