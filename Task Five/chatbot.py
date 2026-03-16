"""
AI Financial Chatbot Prototype — Rule-Based Logic
BCG x GFC Project | Task 5

A simple rule-based chatbot that responds to predefined financial queries
using analyzed 10-K data from Microsoft, Tesla, and Apple (FY2022-FY2024).
"""

import pandas as pd

# ─── Load Financial Data ───────────────────────────────────────
DATA = {
    "Microsoft": {
        2022: {"revenue": 198.27, "net_income": 72.74, "total_assets": 364.84, "total_liabilities": 198.30, "operating_cf": 89.04},
        2023: {"revenue": 211.92, "net_income": 72.36, "total_assets": 411.98, "total_liabilities": 205.75, "operating_cf": 87.58},
        2024: {"revenue": 245.12, "net_income": 88.14, "total_assets": 512.16, "total_liabilities": 243.69, "operating_cf": 118.55},
    },
    "Tesla": {
        2022: {"revenue": 81.46, "net_income": 12.56, "total_assets": 82.34, "total_liabilities": 36.44, "operating_cf": 14.72},
        2023: {"revenue": 96.77, "net_income": 14.97, "total_assets": 106.62, "total_liabilities": 43.01, "operating_cf": 13.26},
        2024: {"revenue": 97.69, "net_income": 7.09, "total_assets": 122.07, "total_liabilities": 48.26, "operating_cf": 11.53},
    },
    "Apple": {
        2022: {"revenue": 394.33, "net_income": 99.80, "total_assets": 352.76, "total_liabilities": 302.08, "operating_cf": 122.15},
        2023: {"revenue": 383.29, "net_income": 97.00, "total_assets": 352.58, "total_liabilities": 290.44, "operating_cf": 110.54},
        2024: {"revenue": 391.04, "net_income": 93.74, "total_assets": 364.98, "total_liabilities": 308.03, "operating_cf": 118.25},
    },
}


def get_total_revenue(company=None):
    """Query 1: What is the total revenue?"""
    if company and company in DATA:
        rev = DATA[company][2024]["revenue"]
        return f"{company}'s total revenue for FY2024 is ${rev}B."
    else:
        lines = []
        for c in DATA:
            rev = DATA[c][2024]["revenue"]
            lines.append(f"  - {c}: ${rev}B")
        return "Total Revenue (FY2024):\n" + "\n".join(lines)


def get_net_income_change(company=None):
    """Query 2: How has net income changed over the last year?"""
    if company and company in DATA:
        ni_23 = DATA[company][2023]["net_income"]
        ni_24 = DATA[company][2024]["net_income"]
        change = ni_24 - ni_23
        pct = (change / ni_23) * 100
        direction = "increased" if change > 0 else "decreased"
        return (f"{company}'s net income {direction} from ${ni_23}B (FY2023) to ${ni_24}B (FY2024), "
                f"a change of {pct:+.1f}%.")
    else:
        lines = []
        for c in DATA:
            ni_23 = DATA[c][2023]["net_income"]
            ni_24 = DATA[c][2024]["net_income"]
            pct = ((ni_24 - ni_23) / ni_23) * 100
            direction = "increased" if pct > 0 else "decreased"
            lines.append(f"  - {c}: {direction} by {abs(pct):.1f}% (${ni_23}B -> ${ni_24}B)")
        return "Net Income Change (FY2023 to FY2024):\n" + "\n".join(lines)


def get_profit_margin(company=None):
    """Query 3: What is the profit margin?"""
    if company and company in DATA:
        rev = DATA[company][2024]["revenue"]
        ni = DATA[company][2024]["net_income"]
        margin = (ni / rev) * 100
        return f"{company}'s profit margin for FY2024 is {margin:.1f}% (Net Income ${ni}B / Revenue ${rev}B)."
    else:
        lines = []
        for c in DATA:
            rev = DATA[c][2024]["revenue"]
            ni = DATA[c][2024]["net_income"]
            margin = (ni / rev) * 100
            lines.append(f"  - {c}: {margin:.1f}%")
        return "Profit Margins (FY2024):\n" + "\n".join(lines)


def get_total_assets(company=None):
    """Query 4: What are the total assets?"""
    if company and company in DATA:
        assets = DATA[company][2024]["total_assets"]
        return f"{company}'s total assets for FY2024 are ${assets}B."
    else:
        lines = []
        for c in DATA:
            assets = DATA[c][2024]["total_assets"]
            lines.append(f"  - {c}: ${assets}B")
        return "Total Assets (FY2024):\n" + "\n".join(lines)


def get_cash_flow(company=None):
    """Query 5: What is the operating cash flow?"""
    if company and company in DATA:
        ocf = DATA[company][2024]["operating_cf"]
        rev = DATA[company][2024]["revenue"]
        ratio = (ocf / rev) * 100
        return f"{company}'s operating cash flow for FY2024 is ${ocf}B ({ratio:.1f}% of revenue)."
    else:
        lines = []
        for c in DATA:
            ocf = DATA[c][2024]["operating_cf"]
            lines.append(f"  - {c}: ${ocf}B")
        return "Operating Cash Flow (FY2024):\n" + "\n".join(lines)


def compare_companies():
    """Query 6: Compare all three companies."""
    lines = [
        "Company Comparison (FY2024):",
        f"{'Metric':<22} {'Microsoft':>12} {'Tesla':>12} {'Apple':>12}",
        "-" * 60,
    ]
    metrics = [
        ("Revenue ($B)", "revenue"),
        ("Net Income ($B)", "net_income"),
        ("Total Assets ($B)", "total_assets"),
        ("Total Liabilities ($B)", "total_liabilities"),
        ("Operating CF ($B)", "operating_cf"),
    ]
    for label, key in metrics:
        m = DATA["Microsoft"][2024][key]
        t = DATA["Tesla"][2024][key]
        a = DATA["Apple"][2024][key]
        lines.append(f"{label:<22} {m:>12.2f} {t:>12.2f} {a:>12.2f}")

    # Profit margins
    for c in DATA:
        rev = DATA[c][2024]["revenue"]
        ni = DATA[c][2024]["net_income"]
    mm = (DATA["Microsoft"][2024]["net_income"] / DATA["Microsoft"][2024]["revenue"]) * 100
    tm = (DATA["Tesla"][2024]["net_income"] / DATA["Tesla"][2024]["revenue"]) * 100
    am = (DATA["Apple"][2024]["net_income"] / DATA["Apple"][2024]["revenue"]) * 100
    lines.append(f"{'Profit Margin (%)':<22} {mm:>12.1f} {tm:>12.1f} {am:>12.1f}")

    return "\n".join(lines)


def detect_company(user_input):
    """Detect which company the user is asking about."""
    text = user_input.lower()
    if "microsoft" in text or "msft" in text:
        return "Microsoft"
    elif "tesla" in text or "tsla" in text:
        return "Tesla"
    elif "apple" in text or "aapl" in text:
        return "Apple"
    return None


def simple_chatbot(user_query):
    """Main chatbot logic — matches user input to predefined responses."""
    query = user_query.lower().strip()
    company = detect_company(query)

    # Query 1: Total Revenue
    if "revenue" in query:
        return get_total_revenue(company)

    # Query 2: Net Income Change
    elif "net income" in query and ("change" in query or "changed" in query or "growth" in query or "trend" in query):
        return get_net_income_change(company)

    # Query 3: Net Income (without change)
    elif "net income" in query:
        return get_net_income_change(company)

    # Query 4: Profit Margin
    elif "profit margin" in query or "margin" in query:
        return get_profit_margin(company)

    # Query 5: Total Assets
    elif "asset" in query:
        return get_total_assets(company)

    # Query 6: Cash Flow
    elif "cash flow" in query or "operating cash" in query or "ocf" in query:
        return get_cash_flow(company)

    # Query 7: Compare
    elif "compare" in query or "comparison" in query or "vs" in query:
        return compare_companies()

    # Query 8: Help
    elif "help" in query or "what can you" in query or "menu" in query:
        return """I can answer the following financial queries (FY2022-FY2024):

  1. "What is the total revenue?" (or add a company name)
  2. "How has net income changed?"
  3. "What is the profit margin?"
  4. "What are the total assets?"
  5. "What is the operating cash flow?"
  6. "Compare all companies"

Supported companies: Microsoft, Tesla, Apple
Tip: Add a company name to any query for company-specific data.
Example: "What is Microsoft's revenue?" """

    # Default
    else:
        return ("Sorry, I can only provide information on predefined financial queries.\n"
                "Type 'help' to see available queries.")


def run_chatbot():
    """Run the chatbot in interactive command-line mode."""
    print("=" * 60)
    print("  BCG Financial Chatbot — GFC Project")
    print("  Data: Microsoft, Tesla, Apple (FY2022-FY2024)")
    print("  Type 'help' for available queries, 'quit' to exit")
    print("=" * 60)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print("\nChatbot: Goodbye! Thank you for using BCG Financial Chatbot.")
            break
        response = simple_chatbot(user_input)
        print(f"\nChatbot: {response}")


if __name__ == "__main__":
    run_chatbot()
