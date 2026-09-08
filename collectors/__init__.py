"""数据采集器包"""
from .base_collector import BaseCollector
from .app_update_collector import AppUpdateCollector
from .company_news_collector import CompanyNewsCollector
from .partnership_collector import PartnershipCollector
from .market_data_collector import MarketDataCollector
from .industry_news_collector import IndustryNewsCollector

__all__ = [
    'BaseCollector',
    'AppUpdateCollector',
    'CompanyNewsCollector',
    'PartnershipCollector',
    'MarketDataCollector',
    'IndustryNewsCollector'
]
