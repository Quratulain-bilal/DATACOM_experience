#!/usr/bin/env python3
"""
Data Processing Script for Customer Analytics
This script processes customer transaction data and generates reports.
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
        self.customers = {}
        self.transactions = []
        self.reports = {}

    def load_data(self) -> bool:
        """Load customer and transaction data from CSV files."""
        try:
            # Load customer data
            with open(self.input_file, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    customer_id = row["customer_id"]
                    self.customers[customer_id] = {
                        "name": row["name"],
                        "email": row["email"],
                        "join_date": row["join_date"],
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
        """Process transaction data and update customer records."""
        try:
            with open(transaction_file, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    transaction = {
                        "transaction_id": row["transaction_id"],
                        "customer_id": row["customer_id"],
                        "amount": float(row["amount"]),
                        "date": row["date"],
                        "category": row["category"],
                    }
                    self.transactions.append(transaction)

                    # Update customer totals
                    customer_id = row["customer_id"]
                    if customer_id in self.customers:
                        self.customers[customer_id]["total_spent"] += float(
                            row["amount"]
                        )
                        self.customers[customer_id]["transaction_count"] += 1
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
        """Calculate various customer metrics and statistics."""
        if not self.customers:
            logger.error("No customer data available")
            return {}

        metrics = {
            "total_customers": len(self.customers),
            "total_transactions": len(self.transactions),
            "total_revenue": sum(
                cust["total_spent"] for cust in self.customers.values()
            ),
            "average_transaction_value": 0.0,
            "top_customers": [],
            "category_breakdown": {},
        }

        # Calculate average transaction value
        if metrics["total_transactions"] > 0:
            metrics["average_transaction_value"] = (
                metrics["total_revenue"] / metrics["total_transactions"]
            )

        # Find top customers by total spent
        customer_list = [(cid, data) for cid, data in self.customers.items()]
        customer_list.sort(key=lambda x: x[1]["total_spent"], reverse=True)
        metrics["top_customers"] = customer_list[:10]

        # Calculate category breakdown
        for transaction in self.transactions:
            category = transaction["category"]
            if category not in metrics["category_breakdown"]:
                metrics["category_breakdown"][category] = 0
            metrics["category_breakdown"][category] += 1

        return metrics

    def find_matches(
        self, search_term: str, field: str = "name"
    ) -> List[Dict[str, Any]]:
        """Find customers matching the search term in the specified field."""
        matches = []
        search_term_lower = search_term.lower()

        for customer_id, customer_data in self.customers.items():
            if field in customer_data:
                field_value = str(customer_data[field]).lower()
                if search_term_lower in field_value:
                    matches.append({"customer_id": customer_id, **customer_data})

        return matches

    def generate_report(self, report_type: str, output_file: str) -> bool:
        """Generate various types of reports and save to file."""
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

            # Save report to file
            with open(output_file, "w") as file:
                json.dump(report_data, file, indent=2)

            logger.info(f"Generated {report_type} report: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False

    def export_customer_data(self, output_file: str, format: str = "csv") -> bool:
        """Export customer data in specified format."""
        try:
            if format == "csv":
                with open(output_file, "w", newline="") as file:
                    if self.customers:
                        fieldnames = ["customer_id"] + list(
                            next(iter(self.customers.values())).keys()
                        )
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()

                        for customer_id, data in self.customers.items():
                            row = {"customer_id": customer_id, **data}
                            writer.writerow(row)
            elif format == "json":
                with open(output_file, "w") as file:
                    json.dump(self.customers, file, indent=2)
            else:
                logger.error(f"Unsupported format: {format}")
                return False

            logger.info(f"Exported customer data to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False


def main():
    """Main function to run the data processing pipeline."""
    # Initialize processor
    processor = DataProcessor("customers.csv")

    # Load data
    if not processor.load_data():
        logger.error("Failed to load customer data")
        return

    # Process transactions
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
