"""
Refactored Data Processor - Task 1
Fixed bugs and optimized performance
"""

import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Customer:
    """Customer data class"""
    customer_id: str
    name: str
    email: str
    join_date: str
    total_spent: float = 0.0
    transaction_count: int = 0

@dataclass
class Transaction:
    """Transaction data class"""
    transaction_id: str
    customer_id: str
    amount: float
    date: str
    category: str

class DataProcessor:
    """Optimized data processor with bug fixes"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.customers: Dict[str, Customer] = {}
        self.transactions: List[Transaction] = []
        self.reports: Dict[str, Any] = {}
        
    def load_data(self, customer_file: str = "customers.csv") -> bool:
        """Load customer data with error handling"""
        try:
            file_path = self.data_dir / customer_file
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Fixed: Handle missing keys properly
                    customer = Customer(
                        customer_id=row.get('customer_id', ''),
                        name=row.get('name', ''),
                        email=row.get('email', ''),
                        join_date=row.get('join_date', ''),
                        total_spent=0.0,
                        transaction_count=0
                    )
                    self.customers[customer.customer_id] = customer
            
            logger.info(f"Loaded {len(self.customers)} customers")
            return True
            
        except FileNotFoundError:
            logger.error(f"Customer file {customer_file} not found")
            return False
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def process_transactions(self, transaction_file: str = "transactions.csv") -> bool:
        """Process transactions with optimized dictionary lookup (fixed O(n²) issue)"""
        try:
            file_path = self.data_dir / transaction_file
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Create transaction object
                    transaction = Transaction(
                        transaction_id=row['transaction_id'],
                        customer_id=row['customer_id'],
                        amount=float(row['amount']),
                        date=row['date'],
                        category=row['category']
                    )
                    self.transactions.append(transaction)
                    
                    # Optimized: O(1) dictionary lookup instead of nested loops
                    if transaction.customer_id in self.customers:
                        customer = self.customers[transaction.customer_id]
                        customer.total_spent += transaction.amount
                        customer.transaction_count += 1
                    else:
                        logger.warning(f"Transaction for unknown customer: {transaction.customer_id}")
            
            logger.info(f"Processed {len(self.transactions)} transactions")
            return True
            
        except FileNotFoundError:
            logger.error(f"Transaction file {transaction_file} not found")
            return False
        except Exception as e:
            logger.error(f"Error processing transactions: {e}")
            return False
    
    def find_matches(self, search_term: str, field: str = "name") -> List[Dict]:
        """Optimized search with list comprehension"""
        search_term_lower = search_term.lower()
        
        matches = [
            {
                "customer_id": c.customer_id,
                "name": c.name,
                "email": c.email,
                "total_spent": c.total_spent,
                "transaction_count": c.transaction_count
            }
            for c in self.customers.values()
            if search_term_lower in getattr(c, field, '').lower()
        ]
        
        return matches
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate customer metrics efficiently"""
        if not self.customers:
            return {}
        
        # Use list comprehensions for better performance
        total_revenue = sum(c.total_spent for c in self.customers.values())
        total_transactions = sum(c.transaction_count for c in self.customers.values())
        
        # Top customers - sort once
        top_customers = sorted(
            [asdict(c) for c in self.customers.values()],
            key=lambda x: x['total_spent'],
            reverse=True
        )[:10]
        
        # Category breakdown using dictionary comprehension
        category_breakdown = {}
        for t in self.transactions:
            category_breakdown[t.category] = category_breakdown.get(t.category, 0) + 1
        
        return {
            "total_customers": len(self.customers),
            "total_transactions": total_transactions,
            "total_revenue": total_revenue,
            "average_transaction_value": total_revenue / total_transactions if total_transactions > 0 else 0,
            "top_customers": top_customers,
            "category_breakdown": category_breakdown
        }
    
    def export_data(self, output_file: str, format: str = "csv") -> bool:
        """Fixed: Handle dictionary export correctly (bug fix)"""
        try:
            output_path = self.data_dir / output_file
            
            if format == "csv":
                with open(output_path, 'w', newline='') as f:
                    # Fixed: Convert Customer objects to dict properly
                    fieldnames = ['customer_id', 'name', 'email', 'join_date', 
                                 'total_spent', 'transaction_count']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for customer in self.customers.values():
                        writer.writerow(asdict(customer))
                        
            elif format == "json":
                with open(output_path, 'w') as f:
                    # Fixed: Proper JSON serialization
                    data = {
                        cid: asdict(customer)
                        for cid, customer in self.customers.items()
                    }
                    json.dump(data, f, indent=2)
            
            logger.info(f"Exported data to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False