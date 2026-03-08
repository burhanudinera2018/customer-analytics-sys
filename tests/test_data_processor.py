"""
Unit tests for DataProcessor - Task 1
"""

import unittest
import tempfile
import csv
import json
import os
from pathlib import Path
from app.modules.data_processor import DataProcessor, Customer

class TestDataProcessor(unittest.TestCase):
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.processor = DataProcessor(self.test_dir)
        
        # Create test customer data
        self.create_test_customers()
        self.create_test_transactions()
    
    def create_test_customers(self):
        """Create test customers CSV"""
        customers_file = Path(self.test_dir) / "customers.csv"
        with open(customers_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['customer_id', 'name', 'email', 'join_date'])
            writer.writerow(['C001', 'John Doe', 'john@test.com', '2024-01-01'])
            writer.writerow(['C002', 'Jane Smith', 'jane@test.com', '2024-01-02'])
    
    def create_test_transactions(self):
        """Create test transactions CSV"""
        transactions_file = Path(self.test_dir) / "transactions.csv"
        with open(transactions_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['transaction_id', 'customer_id', 'amount', 'date', 'category'])
            writer.writerow(['T001', 'C001', '100.50', '2024-01-10', 'electronics'])
            writer.writerow(['T002', 'C001', '50.25', '2024-01-11', 'food'])
            writer.writerow(['T003', 'C002', '200.00', '2024-01-12', 'clothing'])
    
    def test_load_data(self):
        """Test loading customer data"""
        result = self.processor.load_data("customers.csv")
        self.assertTrue(result)
        self.assertEqual(len(self.processor.customers), 2)
    
    def test_process_transactions(self):
        """Test transaction processing"""
        self.processor.load_data("customers.csv")
        result = self.processor.process_transactions("transactions.csv")
        
        self.assertTrue(result)
        self.assertEqual(len(self.processor.transactions), 3)
        
        # Test customer totals updated correctly
        customer = self.processor.customers['C001']
        self.assertEqual(customer.total_spent, 150.75)
        self.assertEqual(customer.transaction_count, 2)
    
    def test_find_matches(self):
        """Test search functionality"""
        self.processor.load_data("customers.csv")
        
        # Test name search
        matches = self.processor.find_matches("john", "name")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['customer_id'], 'C001')
        
        # Test empty search
        matches = self.processor.find_matches("nonexistent")
        self.assertEqual(len(matches), 0)
    
    def test_calculate_metrics(self):
        """Test metrics calculation"""
        self.processor.load_data("customers.csv")
        self.processor.process_transactions("transactions.csv")
        
        metrics = self.processor.calculate_metrics()
        
        self.assertEqual(metrics['total_customers'], 2)
        self.assertEqual(metrics['total_transactions'], 3)
        self.assertEqual(metrics['total_revenue'], 350.75)
        self.assertEqual(metrics['average_transaction_value'], 116.91666666666667)
    
    def test_export_csv(self):
        """Test CSV export - regression test for bug fix"""
        self.processor.load_data("customers.csv")
        result = self.processor.export_data("export_test.csv", "csv")
        
        self.assertTrue(result)
        export_file = Path(self.test_dir) / "export_test.csv"
        self.assertTrue(export_file.exists())
        
        # Verify export content
        with open(export_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
    
    def test_export_json(self):
        """Test JSON export"""
        self.processor.load_data("customers.csv")
        result = self.processor.export_data("export_test.json", "json")
        
        self.assertTrue(result)
        export_file = Path(self.test_dir) / "export_test.json"
        self.assertTrue(export_file.exists())
        
        # Verify JSON is valid
        with open(export_file, 'r') as f:
            data = json.load(f)
            self.assertIn('C001', data)
            self.assertIn('C002', data)

if __name__ == '__main__':
    unittest.main()