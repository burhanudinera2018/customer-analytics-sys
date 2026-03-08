"""
Data Summary Module - Menyediakan ringkasan data untuk AI
"""

from typing import Dict, Any

class DataSummary:
    """Menyediakan ringkasan data dalam format yang mudah dibaca AI"""
    
    @staticmethod
    def get_summary(processor) -> str:
        """Dapatkan ringkasan data"""
        if not processor:
            return "No data available"
        
        metrics = processor.calculate_metrics()
        
        summary = []
        summary.append("CURRENT DATA SUMMARY")
        summary.append("="*50)
        
        # Basic metrics
        summary.append(f"Total Customers: {metrics.get('total_customers', 0)}")
        summary.append(f"Total Transactions: {metrics.get('total_transactions', 0)}")
        summary.append(f"Total Revenue: ${metrics.get('total_revenue', 0):,.2f}")
        summary.append(f"Average Transaction: ${metrics.get('average_transaction_value', 0):,.2f}")
        
        # Category breakdown
        categories = metrics.get('category_breakdown', {})
        if categories:
            summary.append("\nCategory Breakdown:")
            for cat, count in categories.items():
                summary.append(f"  - {cat}: {count} transactions")
        
        # Top customers
        top_customers = metrics.get('top_customers', [])
        if top_customers:
            summary.append("\nTop Customers:")
            for i, cust in enumerate(top_customers[:5], 1):
                name = cust.get('name', 'Unknown')
                spent = cust.get('total_spent', 0)
                summary.append(f"  {i}. {name}: ${spent:,.2f}")
        
        summary.append("="*50)
        summary.append("Answer questions based ONLY on this data.")
        
        return "\n".join(summary)
    
    @staticmethod
    def get_quick_stats(processor) -> Dict[str, Any]:
        """Dapatkan statistik cepat"""
        if not processor:
            return {}
        
        metrics = processor.calculate_metrics()
        return {
            "total_customers": metrics.get('total_customers', 0),
            "total_revenue": metrics.get('total_revenue', 0),
            "total_transactions": metrics.get('total_transactions', 0),
            "avg_transaction": metrics.get('average_transaction_value', 0),
        }