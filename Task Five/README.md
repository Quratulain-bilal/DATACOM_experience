# BCG Financial Chatbot — GFC Project (Task 5)

## Overview
A rule-based AI financial chatbot prototype that responds to predefined financial queries using analyzed 10-K data from Microsoft, Tesla, and Apple (FY2022–FY2024).

## How It Works
The chatbot uses **if-else rule-based logic** to match user queries to predefined responses. It:
1. Detects which company the user is asking about (Microsoft, Tesla, or Apple)
2. Identifies the financial metric being queried (revenue, net income, margins, etc.)
3. Returns a data-driven response using extracted 10-K financial data

## Predefined Queries
| # | Query | Example |
|---|-------|---------|
| 1 | Total Revenue | "What is the total revenue?" or "What is Microsoft's revenue?" |
| 2 | Net Income Change | "How has net income changed?" or "Tesla net income trend" |
| 3 | Profit Margin | "What is the profit margin?" or "Apple's margin" |
| 4 | Total Assets | "What are the total assets?" |
| 5 | Operating Cash Flow | "What is the operating cash flow?" |
| 6 | Company Comparison | "Compare all companies" |

## How to Run
```bash
# Interactive chatbot
python chatbot.py

# Run tests
python test_chatbot.py
```

## Limitations
- Only responds to predefined query patterns (rule-based, not NLP)
- Limited to 3 companies: Microsoft, Tesla, Apple
- Data covers FY2022–FY2024 only (static, not real-time)
- Cannot handle complex multi-part questions
- No learning or memory between sessions
- No natural language understanding beyond keyword matching

## Files
- `chatbot.py` — Main chatbot script with rule-based logic
- `test_chatbot.py` — Test suite (15 tests)
- `README.md` — This documentation
