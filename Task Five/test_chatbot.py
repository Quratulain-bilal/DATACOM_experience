"""Test suite for the Financial Chatbot."""

from chatbot import simple_chatbot

def run_tests():
    tests = [
        ("What is the total revenue?", "Total Revenue (FY2024):", True),
        ("What is Microsoft's revenue?", "Microsoft's total revenue", True),
        ("What is Tesla's revenue?", "Tesla's total revenue", True),
        ("What is Apple's revenue?", "Apple's total revenue", True),
        ("How has net income changed?", "Net Income Change", True),
        ("How has net income changed for Microsoft?", "Microsoft's net income", True),
        ("What is the profit margin?", "Profit Margins", True),
        ("What is Tesla's profit margin?", "Tesla's profit margin", True),
        ("What are the total assets?", "Total Assets", True),
        ("What is Apple's total assets?", "Apple's total assets", True),
        ("What is the operating cash flow?", "Operating Cash Flow", True),
        ("What is Microsoft's cash flow?", "Microsoft's operating cash flow", True),
        ("Compare all companies", "Company Comparison", True),
        ("help", "I can answer the following", True),
        ("random nonsense xyz", "Sorry, I can only provide", True),
    ]

    passed = 0
    failed = 0

    print("=" * 60)
    print("  CHATBOT TEST RESULTS")
    print("=" * 60)

    for query, expected_substring, should_contain in tests:
        response = simple_chatbot(query)
        if should_contain and expected_substring in response:
            status = "PASS"
            passed += 1
        elif not should_contain and expected_substring not in response:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(f"\n[{status}] Query: \"{query}\"")
        print(f"       Response: {response[:100]}...")

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed}/{passed + failed} tests passed")
    print(f"{'=' * 60}")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
