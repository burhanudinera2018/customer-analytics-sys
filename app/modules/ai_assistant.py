"""
AI Assistant Module - WITH REAL DATA CONTEXT
Mengirim data aktual ke model untuk mencegah halusinasi
"""

import logging
import json
from typing import Dict, Any, Optional
import requests
import os
import time
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AIAssistant:
    """AI Assistant dengan context data real"""
    
    def __init__(self, model: str = None, host: str = None, timeout: int = 60):
        self.model = model or os.getenv('OLLAMA_MODEL', 'qwen2:0.5b')
        
        raw_host = host or os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
        if not raw_host.startswith(('http://', 'https://')):
            raw_host = f"http://{raw_host}"
        self.host = raw_host.rstrip('/')
        
        self.timeout = timeout
        self.generate_url = f"{self.host}/api/generate"
        
        logger.info("="*60)
        logger.info("🤖 AI ASSISTANT - WITH REAL DATA CONTEXT")
        logger.info("="*60)
        logger.info(f"✅ Model: {self.model}")
        logger.info(f"✅ Host: {self.host}")
        logger.info("="*60)
    
    def ask(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Kirim pertanyaan dengan context data real
        """
        try:
            # Pastikan context selalu ada
            if context is None:
                context = {}
            
            # Format data real dengan jelas
            data_context = self._format_data_context(context)
            
            # Build prompt yang memaksa model menggunakan data
            full_prompt = self._build_factual_prompt(prompt, data_context)
            
            logger.info(f"📤 Sending prompt with context")
            
            response = requests.post(
                self.generate_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 200,
                        "temperature": 0.1,  # Sangat rendah untuk mengurangi kreativitas
                        "top_k": 10,
                        "top_p": 0.3,
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                
                # Validasi jawaban mengandung data
                if self._contains_data(answer, context):
                    return answer
                else:
                    # Jika jawaban tidak mengandung data, beri respons berbasis data
                    return self._generate_data_based_response(prompt, context)
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error: {e}")
            return self._generate_data_based_response(prompt, context if context else {})
    
    def _format_data_context(self, context: Dict) -> str:
        """Format context data dengan jelas"""
        lines = []
        lines.append("="*40)
        lines.append("DATA AKTUAL SAAT INI:")
        lines.append("="*40)
        
        if 'total_customers' in context:
            lines.append(f"📊 Total Customers: {context['total_customers']}")
        
        if 'total_transactions' in context:
            lines.append(f"💰 Total Transactions: {context['total_transactions']}")
        
        if 'total_revenue' in context:
            lines.append(f"💵 Total Revenue: ${context['total_revenue']:,.2f}")
        
        if 'average_transaction_value' in context:
            lines.append(f"📈 Avg Transaction: ${context['average_transaction_value']:,.2f}")
        
        if 'category_breakdown' in context and context['category_breakdown']:
            lines.append("\n📦 Category Breakdown:")
            for cat, count in context['category_breakdown'].items():
                lines.append(f"   • {cat}: {count} transactions")
        
        if 'top_customers' in context and context['top_customers']:
            lines.append("\n🏆 Top Customers:")
            for i, cust in enumerate(context['top_customers'][:5], 1):
                if isinstance(cust, dict):
                    name = cust.get('name', 'Unknown')
                    spent = cust.get('total_spent', 0)
                    lines.append(f"   {i}. {name}: ${spent:,.2f}")
        
        lines.append("="*40)
        lines.append("JAWAB BERDASARKAN DATA DI ATAS SAJA!")
        lines.append("Jangan menambahkan informasi lain.")
        lines.append("="*40)
        
        return "\n".join(lines)
    
    def _build_factual_prompt(self, prompt: str, data_context: str) -> str:
        """Build prompt yang memaksa jawaban faktual"""
        return f"""{data_context}

PERTANYAAN: {prompt}

INSTRUKSI PENTING:
1. Jawab HANYA berdasarkan data di atas
2. Jika data tidak tersedia, katakan "Data tidak tersedia"
3. Jangan membuat data fiktif
4. Jawab singkat dan faktual

JAWABAN:"""
    
    def _contains_data(self, answer: str, context: Dict) -> bool:
        """Cek apakah jawaban mengandung data real"""
        answer_lower = answer.lower()
        
        # Cek apakah jawaban menyebutkan angka-angka dari context
        data_mentions = 0
        
        if 'total_customers' in context:
            if str(context['total_customers']) in answer:
                data_mentions += 1
        
        if 'total_revenue' in context:
            revenue_str = f"${context['total_revenue']:,.0f}"
            if revenue_str in answer or f"{context['total_revenue']:.0f}" in answer:
                data_mentions += 1
        
        return data_mentions > 0
    
    def _generate_data_based_response(self, prompt: str, context: Dict) -> str:
        """Generate response berbasis data secara manual"""
        prompt_lower = prompt.lower()
        
        # Template respons berdasarkan data
        if 'customer' in prompt_lower or 'pelanggan' in prompt_lower:
            if 'total_customers' in context:
                return f"📊 Total customers saat ini: **{context['total_customers']}**"
        
        if 'revenue' in prompt_lower or 'pendapatan' in prompt_lower or 'total' in prompt_lower:
            if 'total_revenue' in context:
                return f"💰 Total revenue: **${context['total_revenue']:,.2f}**"
        
        if 'transaction' in prompt_lower or 'transaksi' in prompt_lower:
            if 'total_transactions' in context:
                avg = context.get('average_transaction_value', 0)
                return f"📊 Total transaksi: **{context['total_transactions']}** (Avg: ${avg:,.2f})"
        
        if 'category' in prompt_lower or 'kategori' in prompt_lower:
            if 'category_breakdown' in context and context['category_breakdown']:
                cats = context['category_breakdown']
                response = "📦 **Category Breakdown:**\n"
                for cat, count in cats.items():
                    response += f"• {cat}: {count} transactions\n"
                return response
        
        if 'top' in prompt_lower or 'terbaik' in prompt_lower or 'performer' in prompt_lower:
            if 'top_customers' in context and context['top_customers']:
                response = "🏆 **Top Customers:**\n"
                for i, cust in enumerate(context['top_customers'][:5], 1):
                    name = cust.get('name', 'Unknown')
                    spent = cust.get('total_spent', 0)
                    response += f"{i}. {name}: ${spent:,.2f}\n"
                return response
        
        # Default response
        return (
            "📊 **Data yang tersedia:**\n"
            f"• Customers: {context.get('total_customers', 'N/A')}\n"
            f"• Transactions: {context.get('total_transactions', 'N/A')}\n"
            f"• Revenue: ${context.get('total_revenue', 0):,.2f}\n\n"
            "Apa yang ingin Anda ketahui lebih lanjut?"
        )


# Test langsung
if __name__ == "__main__":
    ai = AIAssistant()
    
    # Sample data
    test_context = {
        "total_customers": 5,
        "total_transactions": 10,
        "total_revenue": 1282.24,
        "average_transaction_value": 128.22,
        "category_breakdown": {
            "electronics": 3,
            "clothing": 3,
            "food": 2,
            "books": 2
        },
        "top_customers": [
            {"name": "John Smith", "total_spent": 376.00},
            {"name": "Jane Doe", "total_spent": 290.50},
            {"name": "Bob Johnson", "total_spent": 225.75}
        ]
    }
    
    # Test queries
    test_queries = [
        "How many customers do we have?",
        "What's the total revenue?",
        "Show category breakdown",
        "Who are top customers?",
        "What are the insights?"
    ]
    
    print("\n🔍 TESTING AI ASSISTANT WITH REAL DATA")
    print("="*60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        response = ai.ask(query, test_context)
        print(f"💬 Response: {response}")
    
    print("\n" + "="*60)