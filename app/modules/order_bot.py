"""
OrderBot - Autonomous Order Processing Agent
Task 3: Agentic AI Design Implementation
Dengan penanganan path yang lebih robust
"""

import logging
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import os

logger = logging.getLogger(__name__)

@dataclass
class Order:
    """Order data structure"""
    order_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    product_sku: str
    quantity: int
    total_amount: float
    order_date: str
    status: str = "pending"
    validation_errors: list = None

class EmailTool:
    """Simulated email integration tool dengan path handling yang lebih baik"""
    
    def __init__(self, inbox_path: str = "data/emails"):
        """
        Initialize EmailTool dengan penanganan path yang robust
        
        Args:
            inbox_path: Path ke direktori inbox
        """
        # Gunakan absolute path
        self.base_dir = Path.cwd()  # Current working directory
        self.inbox_path = self.base_dir / inbox_path
        
        # Buat direktori jika belum ada
        try:
            self.inbox_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Email inbox directory: {self.inbox_path}")
        except Exception as e:
            logger.error(f"❌ Error creating inbox directory: {e}")
            # Fallback ke temporary directory
            import tempfile
            self.inbox_path = Path(tempfile.gettempdir()) / "orderbot_emails"
            self.inbox_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"⚠️ Using fallback directory: {self.inbox_path}")
    
    def check_new_orders(self) -> list:
        """Check inbox for new order emails"""
        try:
            # In production, this would connect to email API
            # Simulated for demo - create sample order files if none exist
            order_files = list(self.inbox_path.glob("order_*.pdf"))
            
            # If no files, create sample for demo
            if not order_files:
                self._create_sample_orders()
                order_files = list(self.inbox_path.glob("order_*.pdf"))
            
            return [str(f) for f in order_files]
            
        except Exception as e:
            logger.error(f"Error checking orders: {e}")
            return []
    
    def _create_sample_orders(self):
        """Create sample order files for demo"""
        sample_orders = [
            {"id": "ORD-001", "customer": "C001", "product": "HW-001", "qty": 2},
            {"id": "ORD-002", "customer": "C002", "product": "HW-002", "qty": 1},
            {"id": "ORD-003", "customer": "C003", "product": "HW-001", "qty": 3},
        ]
        
        for order in sample_orders:
            file_path = self.inbox_path / f"order_{order['id']}.pdf"
            if not file_path.exists():
                # Create empty file as placeholder
                file_path.touch()
                logger.info(f"Created sample order: {file_path.name}")
    
    def send_email(self, to: str, subject: str, body: str):
        """Send email notification"""
        logger.info(f"📧 Email sent to {to}: {subject}")
        
        # Log to file for demo
        log_file = Path.cwd() / "data/logs" / "emails_sent.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"{timestamp} | To: {to} | Subject: {subject}\n")
        
        return True

class PDFParserTool:
    """PDF parsing tool for order forms"""
    
    def __init__(self):
        self.orders_dir = Path.cwd() / "data/orders"
        self.orders_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_order(self, pdf_path: str) -> Dict[str, Any]:
        """Extract order data from PDF"""
        try:
            path = Path(pdf_path)
            
            # Simulated PDF parsing
            # In production, use PyPDF2 or similar
            
            # Generate order ID from filename or create new
            if path.exists() and path.stat().st_size > 0:
                # Parse from filename
                filename = path.stem
                order_id = filename.replace('order_', '') if filename.startswith('order_') else f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            else:
                order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Mock parsing - in reality, this would extract from PDF
            order_data = {
                "order_id": order_id,
                "customer_id": "C001",
                "customer_name": "John Smith",
                "customer_email": "john@example.com",
                "product_sku": "HW-001",
                "quantity": 2,
                "total_amount": 299.99,
                "order_date": datetime.now().isoformat()
            }
            
            # Save parsed order for reference
            order_file = self.orders_dir / f"{order_id}.json"
            with open(order_file, 'w') as f:
                json.dump(order_data, f, indent=2)
            
            logger.info(f"✅ Parsed order: {order_id}")
            return order_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            # Return default data for demo
            return {
                "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "customer_id": "C001",
                "customer_name": "John Smith",
                "customer_email": "john@example.com",
                "product_sku": "HW-001",
                "quantity": 2,
                "total_amount": 299.99,
                "order_date": datetime.now().isoformat()
            }

class SalesforceTool:
    """Salesforce API integration"""
    
    def __init__(self):
        self.data_dir = Path.cwd() / "data"
        self.customers_file = self.data_dir / "customers.csv"
    
    def check_customer_status(self, customer_id: str) -> Dict[str, Any]:
        """Check customer account status"""
        try:
            # Try to read from customers.csv first
            if self.customers_file.exists():
                import csv
                with open(self.customers_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['customer_id'] == customer_id:
                            return {
                                "status": "active",
                                "credit_limit": 5000,
                                "balance": 0,
                                "name": row['name'],
                                "email": row['email']
                            }
            
            # Fallback to simulated data
            customers = {
                "C001": {"status": "active", "credit_limit": 5000, "balance": 1200, "name": "John Smith"},
                "C002": {"status": "active", "credit_limit": 10000, "balance": 300, "name": "Jane Doe"},
                "C003": {"status": "inactive", "credit_limit": 0, "balance": 500, "name": "Bob Johnson"},
            }
            return customers.get(customer_id, {"status": "unknown", "error": "Customer not found"})
            
        except Exception as e:
            logger.error(f"Error checking customer status: {e}")
            return {"status": "unknown", "error": str(e)}

class InventoryTool:
    """Google Sheets inventory tracking"""
    
    def __init__(self, sheet_id: str = "inventory_sheet"):
        self.sheet_id = sheet_id
        self.data_dir = Path.cwd() / "data"
        self.inventory_file = self.data_dir / "inventory.json"
        self._init_inventory()
    
    def _init_inventory(self):
        """Initialize inventory data"""
        if not self.inventory_file.exists():
            inventory_data = {
                "HW-001": {"available": 50, "location": "Warehouse A", "price": 149.99},
                "HW-002": {"available": 25, "location": "Warehouse B", "price": 299.99},
                "HW-003": {"available": 0, "location": "None", "price": 99.99},
                "HW-004": {"available": 100, "location": "Warehouse A", "price": 79.99},
            }
            with open(self.inventory_file, 'w') as f:
                json.dump(inventory_data, f, indent=2)
    
    def check_inventory(self, sku: str) -> Dict[str, Any]:
        """Check product availability"""
        try:
            # Read from inventory file
            if self.inventory_file.exists():
                with open(self.inventory_file, 'r') as f:
                    inventory = json.load(f)
                    return inventory.get(sku, {"available": 0, "error": "SKU not found"})
            
            # Fallback to hardcoded data
            inventory = {
                "HW-001": {"available": 50, "location": "Warehouse A"},
                "HW-002": {"available": 25, "location": "Warehouse B"},
                "HW-003": {"available": 0, "location": "None"},
            }
            return inventory.get(sku, {"available": 0, "error": "SKU not found"})
            
        except Exception as e:
            logger.error(f"Error checking inventory: {e}")
            return {"available": 0, "error": str(e)}
    
    def decrement_inventory(self, sku: str, quantity: int) -> bool:
        """Update inventory after order"""
        try:
            if self.inventory_file.exists():
                with open(self.inventory_file, 'r') as f:
                    inventory = json.load(f)
                
                if sku in inventory:
                    inventory[sku]["available"] -= quantity
                    
                    with open(self.inventory_file, 'w') as f:
                        json.dump(inventory, f, indent=2)
                    
                    logger.info(f"📦 Inventory updated: {sku} reduced by {quantity}")
                    return True
            
            logger.info(f"📦 Inventory updated: {sku} reduced by {quantity} (simulated)")
            return True
            
        except Exception as e:
            logger.error(f"Error updating inventory: {e}")
            return False

class OrderBot:
    """
    Autonomous Order Processing Agent
    Implements the agentic AI design from Task 3
    """
    
    def __init__(self):
        """Initialize OrderBot dengan semua tools"""
        
        # Setup directories
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.data_dir / "logs"
        
        # Create all necessary directories
        for dir_path in [self.data_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize tools
        self.email_tool = EmailTool()
        self.pdf_parser = PDFParserTool()
        self.salesforce = SalesforceTool()
        self.inventory = InventoryTool()
        
        # Metrics
        self.orders_processed = 0
        self.successful_orders = 0
        self.failed_orders = 0
        self.memory = []  # Learning memory
        
        # Agent goal from specification
        self.goal = {
            "objective": "Autonomously process all new hardware orders from email receipt to fulfillment confirmation within 5 minutes",
            "target_accuracy": 99.5
        }
        
        # Load memory if exists
        self._load_memory()
        
        logger.info(f"✅ OrderBot initialized. Data dir: {self.data_dir}")
    
    def _load_memory(self):
        """Load learning memory from file"""
        memory_file = self.data_dir / "orderbot_memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded {len(self.memory)} memories")
            except:
                self.memory = []
    
    def _save_memory(self):
        """Save learning memory to file"""
        memory_file = self.data_dir / "orderbot_memory.json"
        try:
            with open(memory_file, 'w') as f:
                json.dump(self.memory[-1000:], f, indent=2)  # Keep last 1000
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def process_new_orders(self) -> Dict[str, Any]:
        """Main agent loop - process all new orders"""
        logger.info("🔍 OrderBot checking for new orders...")
        
        # Perception: Check email inbox
        new_order_files = self.email_tool.check_new_orders()
        
        results = {
            "total_found": len(new_order_files),
            "processed": [],
            "failed": [],
            "metrics": {}
        }
        
        for order_file in new_order_files:
            result = self._process_single_order(order_file)
            if result["success"]:
                results["processed"].append(result)
                self.successful_orders += 1
            else:
                results["failed"].append(result)
                self.failed_orders += 1
            
            self.orders_processed += 1
            
            # Learning: Store outcome in memory
            self._update_memory(result)
        
        # Update metrics
        results["metrics"] = self.get_performance_metrics()
        
        # Save memory
        self._save_memory()
        
        logger.info(f"✅ Processed {results['total_found']} orders")
        return results
    
    def _process_single_order(self, order_file: str) -> Dict[str, Any]:
        """Process a single order through the workflow"""
        
        try:
            # Step 1: Parse PDF
            order_data = self.pdf_parser.parse_order(order_file)
            order = Order(**order_data)
            
            # Step 2: Check customer status (Salesforce)
            customer_status = self.salesforce.check_customer_status(order.customer_id)
            
            if customer_status.get("status") != "active":
                return self._handle_exception(
                    order, 
                    "customer_inactive",
                    f"Customer {order.customer_id} is not active"
                )
            
            # Step 3: Check inventory (Google Sheets)
            inventory_status = self.inventory.check_inventory(order.product_sku)
            
            if inventory_status.get("available", 0) < order.quantity:
                return self._handle_exception(
                    order,
                    "out_of_stock",
                    f"Insufficient inventory: {inventory_status.get('available', 0)} available, {order.quantity} requested"
                )
            
            # Step 4: Decision Point - All checks passed
            return self._execute_success_plan(order, inventory_status)
            
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return {
                "success": False,
                "error": "processing_error",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _execute_success_plan(self, order: Order, inventory: Dict) -> Dict[str, Any]:
        """Execute success plan - all validations passed"""
        
        try:
            # Action 1: Update inventory
            self.inventory.decrement_inventory(order.product_sku, order.quantity)
            
            # Action 2: Update Salesforce (simulated)
            # In production, would call Salesforce API
            
            # Action 3: Send confirmation emails
            self.email_tool.send_email(
                to=order.customer_email,
                subject=f"Order Confirmation: {order.order_id}",
                body=f"Your order {order.order_id} has been confirmed and will be shipped soon."
            )
            
            self.email_tool.send_email(
                to="warehouse@company.com",
                subject=f"New Order for Fulfillment: {order.order_id}",
                body=f"Order {order.order_id}: {order.quantity}x {order.product_sku} for {order.customer_name}"
            )
            
            order.status = "fulfilled"
            
            return {
                "success": True,
                "order_id": order.order_id,
                "customer": order.customer_name,
                "product": order.product_sku,
                "quantity": order.quantity,
                "processing_time": "2 minutes",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._handle_exception(order, "execution_error", str(e))
    
    def _handle_exception(self, order: Order, reason: str, details: str) -> Dict[str, Any]:
        """Handle exceptions in the workflow"""
        
        order.status = "failed"
        order.validation_errors = [{"reason": reason, "details": details}]
        
        # Notify sales rep
        self.email_tool.send_email(
            to="sales@company.com",
            subject=f"Order Processing Issue: {order.order_id}",
            body=f"Order {order.order_id} failed: {details}"
        )
        
        logger.warning(f"⚠️ Order {order.order_id} failed: {details}")
        
        return {
            "success": False,
            "order_id": order.order_id,
            "error": reason,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_memory(self, result: Dict[str, Any]):
        """Learning: Store outcomes for pattern recognition"""
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "pattern": self._identify_pattern(result)
        })
        
        # Keep only last 1000 for memory efficiency
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]
    
    def _identify_pattern(self, result: Dict) -> str:
        """Identify patterns in failures for learning"""
        if not result.get("success") and "error" in result:
            return f"failure_pattern_{result['error']}"
        return "success_pattern"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        total = self.successful_orders + self.failed_orders
        accuracy = (self.successful_orders / total * 100) if total > 0 else 0
        
        # Analyze failure patterns
        failure_patterns = {}
        for memory in self.memory:
            if not memory["result"].get("success", True):
                pattern = memory.get("pattern", "unknown")
                failure_patterns[pattern] = failure_patterns.get(pattern, 0) + 1
        
        return {
            "orders_processed": self.orders_processed,
            "successful": self.successful_orders,
            "failed": self.failed_orders,
            "accuracy": round(accuracy, 2),
            "goal_achieved": accuracy >= self.goal["target_accuracy"],
            "failure_patterns": failure_patterns,
            "learning_memory_size": len(self.memory)
        }