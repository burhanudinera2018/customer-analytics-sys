#!/usr/bin/env python3
"""
Test pengiriman context ke AI Assistant
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.data_processor import DataProcessor
from app.modules.ai_assistant import AIAssistant

def test_context():
    """Test AI Assistant dengan data real"""
    
    print("="*60)
    print("🔍 TESTING AI ASSISTANT WITH REAL DATA")
    print("="*60)
    
    # Load data
    processor = DataProcessor("data")
    processor.load_data("customers.csv")
    processor.process_transactions("transactions.csv")
    
    # Get metrics
    metrics = processor.calculate_metrics()
    
    # Prepare context
    context = {
        "total_customers": metrics.get('total_customers', 0),
        "total_transactions": metrics.get('total_transactions', 0),
        "total_revenue": metrics.get('total_revenue', 0),
        "average_transaction_value": metrics.get('average_transaction_value', 0),
        "category_breakdown": metrics.get('category_breakdown', {}),
        "top_customers": metrics.get('top_customers', [])
    }
    
    print("\n📊 Context Data:")
    for key, value in context.items():
        print(f"   {key}: {value}")
    
    # Initialize AI
    ai = AIAssistant()
    
    # Test queries
    test_queries = [
        "How many customers do we have?",
        "What's the total revenue?",
        "Show category breakdown",
        "Who are top customers?",
        "What are the insights from our data?"
    ]
    
    print("\n" + "="*60)
    print("🤖 AI RESPONSES:")
    print("="*60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        response = ai.ask(query, context)
        print(f"💬 Response: {response}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_context()