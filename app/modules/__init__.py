"""
Modules package for customer analytics system
"""

from app.modules.data_processor import DataProcessor
from app.modules.kudos_system import KudosSystem
from app.modules.order_bot import OrderBot
from app.modules.ai_assistant import AIAssistant

__all__ = ['DataProcessor', 'KudosSystem', 'OrderBot', 'AIAssistant']