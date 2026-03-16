#!/usr/bin/env python3
"""
Data Processing Script for Customer Analytics (Refactored)
This script processes customer transaction data and generates reports.

Changes from original:
- Fixed bug in export_customer_data where 'format' parameter shadowed built-in
- Fixed crash when customer data contains non-dict values
- Added input validation in load_data and process_transactions
- Replaced inefficient category breakdown loop with dictionary-based aggregation
- Added defensive checks before accessing customer dict keys
"""

import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes customer transaction data and generates analytics reports."""

    def __init__(self, input_file: str):
        """Initialize the data processor with input file path."""
        self.input_file = input_file
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.reports: Dict[str, Any] = {}

    def load_data(self) -> bool:
        """Load customer data from a CSV file.

        Expected CSV columns: customer_id, name, email, join_date
        Populates self.customers dict keyed by customer_id.

        Returns:
            True if data loaded successfully, False otherwise.
        """
        try:
            with open(self.input_file, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    customer_id = row.get("customer_id")
                    if not customer_id:
                        logger.warning(f"Skipping row with missing customer_id: {row}")
                        continue
                    self.customers[customer_id] = {
                        "name": row.get("name", ""),
                        "email": row.get("email", ""),
                        "join_date": row.get("join_date", ""),
                        "total_spent": 0.0,
                        "transaction_count": 0,
                    }
            logger.info(f"Loaded {len(self.customers)} customers")
            return True
        except FileNotFoundError:
            logger.error(f"Input file {self.input_file} not found")
            return False
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def process_transactions(self, transaction_file: str) -> bool:
        """Process transaction data and update customer records.

        Args:
            transaction_file: Path to transactions CSV file.

        Returns:
            True if transactions processed successfully, False otherwise.
        """
        try:
            with open(transaction_file, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        amount = float(row["amount"])
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping invalid transaction row: {row} ({e})")
                        continue

                    transaction = {
                        "transaction_id": row.get("transaction_id", ""),
                        "customer_id": row.get("customer_id", ""),
                        "amount": amount,
                        "date": row.get("date", ""),
                        "category": row.get("category", "Unknown"),
                    }
                    self.transactions.append(transaction)

                    # Update customer totals using dict lookup (O(1))
                    customer_id = row.get("customer_id", "")
                    customer = self.customers.get(customer_id)
                    if customer is not None:
                        customer["total_spent"] += amount
                        customer["transaction_count"] += 1
                    else:
                        logger.warning(
                            f"Transaction for unknown customer: {customer_id}"
                        )

            logger.info(f"Processed {len(self.transactions)} transactions")
            return True
        except FileNotFoundError:
            logger.error(f"Transaction file {transaction_file} not found")
            return False
        except Exception as e:
            logger.error(f"Error processing transactions: {e}")
            return False

    def calculate_customer_metrics(self) -> Dict[str, Any]:
        """Calculate various customer metrics and statistics.

        Returns:
            Dictionary containing total_customers, total_transactions,
            total_revenue, average_transaction_value, top_customers,
            and category_breakdown.
        """
        if not self.customers:
            logger.error("No customer data available")
            return {}

        total_revenue = sum(
            cust["total_spent"]
            for cust in self.customers.values()
            if isinstance(cust, dict)
        )
        total_transactions = len(self.transactions)

        metrics = {
            "total_customers": len(self.customers),
            "total_transactions": total_transactions,
            "total_revenue": total_revenue,
            "average_transaction_value": (
                total_revenue / total_transactions if total_transactions > 0 else 0.0
            ),
            "top_customers": [],
            "category_breakdown": {},
        }

        # Find top 10 customers by total spent (sorted)
        customer_list = [
            (cid, data)
            for cid, data in self.customers.items()
            if isinstance(data, dict)
        ]
        customer_list.sort(key=lambda x: x[1]["total_spent"], reverse=True)
        metrics["top_customers"] = customer_list[:10]

        # Category breakdown using dict.get for cleaner accumulation
        category_counts: Dict[str, int] = {}
        for transaction in self.transactions:
            category = transaction.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        metrics["category_breakdown"] = category_counts

        return metrics

    def find_matches(
        self, search_term: str, field: str = "name"
    ) -> List[Dict[str, Any]]:
        """Find customers matching the search term in the specified field.

        Args:
            search_term: String to search for (case-insensitive).
            field: Customer field to search in (default: 'name').

        Returns:
            List of matching customer dicts with customer_id included.
        """
        matches = []
        search_term_lower = search_term.lower()

        for customer_id, customer_data in self.customers.items():
            if not isinstance(customer_data, dict):
                continue
            if field in customer_data:
                field_value = str(customer_data[field]).lower()
                if search_term_lower in field_value:
                    matches.append({"customer_id": customer_id, **customer_data})

        return matches

    def generate_report(self, report_type: str, output_file: str) -> bool:
        """Generate various types of reports and save to JSON file.

        Args:
            report_type: One of 'customer_summary', 'metrics', 'transactions'.
            output_file: Path to output JSON file.

        Returns:
            True if report generated successfully, False otherwise.
        """
        try:
            if report_type == "customer_summary":
                report_data = {
                    "generated_at": datetime.now().isoformat(),
                    "customers": list(self.customers.values()),
                }
            elif report_type == "metrics":
                report_data = {
                    "generated_at": datetime.now().isoformat(),
                    "metrics": self.calculate_customer_metrics(),
                }
            elif report_type == "transactions":
                report_data = {
                    "generated_at": datetime.now().isoformat(),
                    "transactions": self.transactions,
                }
            else:
                logger.error(f"Unknown report type: {report_type}")
                return False

            with open(output_file, "w") as file:
                json.dump(report_data, file, indent=2, default=str)

            logger.info(f"Generated {report_type} report: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False

    def export_customer_data(self, output_file: str, output_format: str = "csv") -> bool:
        """Export customer data in specified format.

        Args:
            output_file: Path to output file.
            output_format: 'csv' or 'json' (renamed from 'format' to avoid
                          shadowing the built-in).

        Returns:
            True if export succeeded, False otherwise.
        """
        try:
            if output_format == "csv":
                with open(output_file, "w", newline="") as file:
                    if self.customers:
                        # Validate that customer values are dicts before accessing keys
                        sample = next(iter(self.customers.values()))
                        if not isinstance(sample, dict):
                            logger.error("Customer data is corrupted (non-dict value)")
                            return False
                        fieldnames = ["customer_id"] + list(sample.keys())
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()

                        for customer_id, data in self.customers.items():
                            if isinstance(data, dict):
                                row = {"customer_id": customer_id, **data}
                                writer.writerow(row)
                            else:
                                logger.warning(
                                    f"Skipping non-dict customer entry: {customer_id}"
                                )
            elif output_format == "json":
                # Validate all values are serializable dicts
                clean_customers = {
                    cid: data
                    for cid, data in self.customers.items()
                    if isinstance(data, dict)
                }
                with open(output_file, "w") as file:
                    json.dump(clean_customers, file, indent=2, default=str)
            else:
                logger.error(f"Unsupported format: {output_format}")
                return False

            logger.info(f"Exported customer data to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False


def main():
    """Main function to run the data processing pipeline."""
    processor = DataProcessor("customers.csv")

    if not processor.load_data():
        logger.error("Failed to load customer data")
        return

    if not processor.process_transactions("transactions.csv"):
        logger.error("Failed to process transactions")
        return

    # Generate reports
    processor.generate_report("customer_summary", "customer_summary.json")
    processor.generate_report("metrics", "metrics.json")
    processor.generate_report("transactions", "transactions.json")

    # Export data
    processor.export_customer_data("customers_export.csv", "csv")
    processor.export_customer_data("customers_export.json", "json")

    logger.info("Data processing completed successfully")


if __name__ == "__main__":
    main()
