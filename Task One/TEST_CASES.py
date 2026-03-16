#!/usr/bin/env python3
"""
Unit tests for process_data_final.py
These tests verify the bug fix and correct behaviour of the DataProcessor class.
"""

import unittest
import os
import tempfile
import json
import csv

from process_data_final import DataProcessor


class TestDataProcessorLoadData(unittest.TestCase):
    """Tests for the load_data method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.customer_file = os.path.join(self.temp_dir, "customers.csv")
        with open(self.customer_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["customer_id", "name", "email", "join_date"])
            writer.writerow(["C001", "John Smith", "john@test.com", "2023-01-15"])
            writer.writerow(["C002", "Jane Doe", "jane@test.com", "2023-02-20"])

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_load_data_success(self):
        processor = DataProcessor(self.customer_file)
        result = processor.load_data()
        self.assertTrue(result)
        self.assertEqual(len(processor.customers), 2)

    def test_load_data_file_not_found(self):
        processor = DataProcessor("nonexistent.csv")
        result = processor.load_data()
        self.assertFalse(result)

    def test_load_data_customer_structure(self):
        processor = DataProcessor(self.customer_file)
        processor.load_data()
        customer = processor.customers["C001"]
        self.assertIsInstance(customer, dict)
        self.assertEqual(customer["name"], "John Smith")
        self.assertEqual(customer["total_spent"], 0.0)
        self.assertEqual(customer["transaction_count"], 0)


class TestProcessTransactions(unittest.TestCase):
    """Tests for the process_transactions method."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.customer_file = os.path.join(self.temp_dir, "customers.csv")
        self.transaction_file = os.path.join(self.temp_dir, "transactions.csv")

        with open(self.customer_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["customer_id", "name", "email", "join_date"])
            writer.writerow(["C001", "John Smith", "john@test.com", "2023-01-15"])

        with open(self.transaction_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["transaction_id", "customer_id", "amount", "date", "category"])
            writer.writerow(["T001", "C001", "150.50", "2024-01-10", "electronics"])
            writer.writerow(["T002", "C001", "50.00", "2024-01-12", "food"])

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_process_transactions_updates_totals(self):
        processor = DataProcessor(self.customer_file)
        processor.load_data()
        processor.process_transactions(self.transaction_file)
        self.assertAlmostEqual(processor.customers["C001"]["total_spent"], 200.50)
        self.assertEqual(processor.customers["C001"]["transaction_count"], 2)

    def test_process_transactions_unknown_customer(self):
        """Transactions for unknown customers should not crash."""
        with open(self.transaction_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["transaction_id", "customer_id", "amount", "date", "category"])
            writer.writerow(["T099", "UNKNOWN", "100.00", "2024-01-01", "food"])

        processor = DataProcessor(self.customer_file)
        processor.load_data()
        result = processor.process_transactions(self.transaction_file)
        self.assertTrue(result)


class TestExportCustomerDataBug(unittest.TestCase):
    """Tests targeting the original bug in export_customer_data.

    Original bug: The function parameter was named 'format' (shadowing the
    built-in), and would crash with "'dict' object has no attribute 'keys'"
    when customer data contained corrupted (non-dict) entries.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.output_csv = os.path.join(self.temp_dir, "export.csv")
        self.output_json = os.path.join(self.temp_dir, "export.json")

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_export_json_with_corrupted_customer_data(self):
        """Reproduce the original bug: non-dict customer value causes crash."""
        processor = DataProcessor("dummy.csv")
        processor.customers = {
            "C001": {"name": "John", "email": "j@t.com", "join_date": "2023-01-01",
                     "total_spent": 100.0, "transaction_count": 2},
            "C002": "corrupted_data",  # Bug trigger
        }
        result = processor.export_customer_data(self.output_json, "json")
        self.assertTrue(result)

        with open(self.output_json, "r") as f:
            data = json.load(f)
        self.assertIn("C001", data)
        self.assertNotIn("C002", data)

    def test_export_csv_with_corrupted_customer_data(self):
        """CSV export should skip corrupted entries."""
        processor = DataProcessor("dummy.csv")
        processor.customers = {
            "C001": {"name": "John", "email": "j@t.com", "join_date": "2023-01-01",
                     "total_spent": 100.0, "transaction_count": 2},
            "C002": "corrupted_data",
        }
        result = processor.export_customer_data(self.output_csv, "csv")
        self.assertTrue(result)

    def test_export_csv_normal_data(self):
        processor = DataProcessor("dummy.csv")
        processor.customers = {
            "C001": {"name": "John", "email": "j@t.com", "join_date": "2023-01-01",
                     "total_spent": 100.0, "transaction_count": 2},
        }
        result = processor.export_customer_data(self.output_csv, "csv")
        self.assertTrue(result)

        with open(self.output_csv, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["customer_id"], "C001")

    def test_export_json_normal_data(self):
        processor = DataProcessor("dummy.csv")
        processor.customers = {
            "C001": {"name": "John", "email": "j@t.com", "join_date": "2023-01-01",
                     "total_spent": 100.0, "transaction_count": 2},
        }
        result = processor.export_customer_data(self.output_json, "json")
        self.assertTrue(result)

    def test_export_unsupported_format(self):
        processor = DataProcessor("dummy.csv")
        processor.customers = {"C001": {"name": "John"}}
        result = processor.export_customer_data(self.output_json, "xml")
        self.assertFalse(result)


class TestCalculateMetrics(unittest.TestCase):
    """Tests for calculate_customer_metrics."""

    def test_metrics_with_no_data(self):
        processor = DataProcessor("dummy.csv")
        result = processor.calculate_customer_metrics()
        self.assertEqual(result, {})

    def test_metrics_calculation(self):
        processor = DataProcessor("dummy.csv")
        processor.customers = {
            "C001": {"name": "John", "total_spent": 200.0, "transaction_count": 2},
            "C002": {"name": "Jane", "total_spent": 100.0, "transaction_count": 1},
        }
        processor.transactions = [
            {"transaction_id": "T1", "customer_id": "C001", "amount": 100, "category": "food"},
            {"transaction_id": "T2", "customer_id": "C001", "amount": 100, "category": "food"},
            {"transaction_id": "T3", "customer_id": "C002", "amount": 100, "category": "clothing"},
        ]
        metrics = processor.calculate_customer_metrics()
        self.assertEqual(metrics["total_customers"], 2)
        self.assertEqual(metrics["total_transactions"], 3)
        self.assertEqual(metrics["total_revenue"], 300.0)
        self.assertEqual(metrics["average_transaction_value"], 100.0)
        self.assertEqual(metrics["category_breakdown"]["food"], 2)
        self.assertEqual(metrics["category_breakdown"]["clothing"], 1)


class TestFindMatches(unittest.TestCase):
    """Tests for find_matches."""

    def test_find_by_name(self):
        processor = DataProcessor("dummy.csv")
        processor.customers = {
            "C001": {"name": "John Smith", "email": "john@test.com"},
            "C002": {"name": "Jane Doe", "email": "jane@test.com"},
        }
        matches = processor.find_matches("john")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["customer_id"], "C001")

    def test_find_no_match(self):
        processor = DataProcessor("dummy.csv")
        processor.customers = {
            "C001": {"name": "John Smith", "email": "john@test.com"},
        }
        matches = processor.find_matches("alice")
        self.assertEqual(len(matches), 0)


if __name__ == "__main__":
    unittest.main()
