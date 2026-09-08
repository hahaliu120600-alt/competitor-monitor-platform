from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, Boolean, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import config

Base = declarative_base()

class Competitor(Base):
    """竞品基础信息表"""
    __tablename__ = 'competitors'

    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False)
    name_cn = Column(String(100), nullable=False)
    category = Column(String(20))  # 国际/国内/本品
    platforms = Column(String(50))  # iOS/Android/Web
    official_site = Column(String(200))
    logo_url = Column(String(200))
    search_keywords = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    updates = relationship('AppUpdate', back_populates='competitor', cascade='all, delete-orphan')
    news = relationship('CompanyNews', back_populates='competitor', cascade='all, delete-orphan')
    partnerships = relationship('Partnership', back_populates='competitor', cascade='all, delete-orphan')
    market_data = relationship('MarketData', back_populates='competitor', cascade='all, delete-orphan')


class AppUpdate(Base):
    """App版本更新记录表"""
    __tablename__ = 'app_updates'

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'), nullable=False)
    version = Column(String(50))
    release_date = Column(Date)
    platform = Column(String(20))  # iOS/Android/Both
    features = Column(Text)  # JSON格式存储功能列表
    highlight = Column(Text)  # 功能亮点分析
    insight = Column(Text)  # 对墨迹天气的启示
    source_url = Column(String(500))
    collected_at = Column(DateTime, default=datetime.now)

    competitor = relationship('Competitor', back_populates='updates')


class CompanyNews(Base):
    """公司动态表"""
    __tablename__ = 'company_news'

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'), nullable=False)
    news_type = Column(String(50))  # funding/acquisition/strategy/personnel
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    publish_date = Column(Date)
    source_url = Column(String(500))
    collected_at = Column(DateTime, default=datetime.now)

    competitor = relationship('Competitor', back_populates='news')


class Partnership(Base):
    """合作动态表"""
    __tablename__ = 'partnerships'

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'), nullable=False)
    partner_name = Column(String(200))
    partnership_type = Column(String(50))  # data_source/channel/brand/tech
    description = Column(Text)
    announce_date = Column(Date)
    source_url = Column(String(500))
    collected_at = Column(DateTime, default=datetime.now)

    competitor = relationship('Competitor', back_populates='partnerships')


class MarketData(Base):
    """市场数据表"""
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('competitors.id'), nullable=False)
    date = Column(Date, nullable=False)
    downloads_7d = Column(Integer)
    downloads_30d = Column(Integer)
    revenue_30d = Column(DECIMAL(10, 2))
    ranking_ios = Column(Integer)
    ranking_android = Column(Integer)
    rating_ios = Column(DECIMAL(3, 2))
    rating_android = Column(DECIMAL(3, 2))
    data_source = Column(String(50))  # websearch/manual/sensortower
    collected_at = Column(DateTime, default=datetime.now)

    competitor = relationship('Competitor', back_populates='market_data')


class DailyReport(Base):
    """每日采集摘要表"""
    __tablename__ = 'daily_reports'

    id = Column(Integer, primary_key=True)
    report_date = Column(Date, nullable=False, unique=True)
    total_updates = Column(Integer, default=0)
    total_news = Column(Integer, default=0)
    total_partnerships = Column(Integer, default=0)
    total_industry_news = Column(Integer, default=0)  # 新增：行业新闻数
    key_insights = Column(Text)  # JSON格式（包含行业新闻）
    status = Column(String(20))  # success/partial/failed
    error_log = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


# 数据库引擎和会话
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_database():
    """初始化数据库"""
    Base.metadata.create_all(engine)
    print("数据库表创建成功！")

def get_session():
    """获取数据库会话"""
    return SessionLocal()
