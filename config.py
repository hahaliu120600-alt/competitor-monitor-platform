import os
from datetime import datetime

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 数据库配置
DATABASE_PATH = os.path.join(DATA_DIR, 'competitors.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask配置
SECRET_KEY = os.urandom(24)
DEBUG = True
HOST = '0.0.0.0'
PORT = 5001  # 改为5001端口（避免与AirPlay冲突）

# 定时任务配置
TIMEZONE = 'Asia/Shanghai'

# 数据采集配置
DAILY_COLLECTION_TIME = {'hour': 2, 'minute': 0}  # 每天凌晨2点
WEEKLY_REPORT_TIME = {'day_of_week': 'fri', 'hour': 17, 'minute': 0}  # 每周五17点
BACKUP_TIME = {'day_of_week': 'sun', 'hour': 3, 'minute': 0}  # 每周日凌晨3点

# Claude API配置
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
CLAUDE_MODEL = 'claude-opus-4-8'

# ToB行业监测配置
TOB_INDUSTRIES = {
    'subway': {
        'name': '地铁行业',
        'keywords': ['地铁', '轨道交通', '气象', '防汛', '防灾减灾', '智能调度'],
        'competitors': ['华风气象', '华云气象'],
        'focus': '各省一线城市地铁与气象结合需求'
    },
    'aviation': {
        'name': '航空行业',
        'keywords': ['航空', '航班延误', '航路气象', '航危天气', '航空气象服务'],
        'competitors': ['WNI（日本气象新闻）'],
        'focus': '各航空公司与气象相关的新闻和服务'
    },
    'energy': {
        'name': '能源行业',
        'keywords': ['风电', '光伏', '电网', '双细则', '功率预测', '新能源'],
        'competitors': ['国能日新', '东润环能', '金风科技', '远景能源', 'Meteologica'],
        'focus': '能源与气象相关的政策、技术动态'
    }
}

# 竞品配置
COMPETITORS = [
    {
        'name_en': 'The Weather Channel',
        'name_cn': 'The Weather Channel',
        'category': '国际',
        'platforms': 'iOS/Android/Web',
        'official_site': 'https://weather.com',
        'search_keywords': '"The Weather Channel" app update'
    },
    {
        'name_en': 'AccuWeather',
        'name_cn': 'AccuWeather',
        'category': '国际',
        'platforms': 'iOS/Android/Web',
        'official_site': 'https://accuweather.com',
        'search_keywords': '"AccuWeather" app update news'
    },
    {
        'name_en': 'Windy.com',
        'name_cn': 'Windy',
        'category': '国际',
        'platforms': 'iOS/Android/Web',
        'official_site': 'https://windy.com',
        'search_keywords': '"Windy" weather app news'
    },
    {
        'name_en': 'Weather & Radar',
        'name_cn': 'Weather & Radar',
        'category': '国际',
        'platforms': 'iOS/Android',
        'official_site': 'https://weatherandradar.com',
        'search_keywords': '"Weather & Radar" app update'
    },
    {
        'name_en': 'Clime',
        'name_cn': 'Clime',
        'category': '国际',
        'platforms': 'iOS/Android',
        'official_site': 'https://climeweather.com',
        'search_keywords': '"Clime" weather app news'
    },
    {
        'name_en': 'Weathernews',
        'name_cn': 'ウェザーニュース',
        'category': '国际',
        'platforms': 'iOS/Android',
        'official_site': 'https://weathernews.jp',
        'search_keywords': '"Weathernews" ウェザーニュース update'
    },
    {
        'name_en': 'WeatherLive',
        'name_cn': 'WeatherLive',
        'category': '国际',
        'platforms': 'iOS/Android',
        'official_site': '',
        'search_keywords': '"WeatherLive" weather app'
    },
    {
        'name_en': 'Tianqitong',
        'name_cn': '天气通',
        'category': '国内',
        'platforms': 'iOS/Android',
        'official_site': '',
        'search_keywords': '"天气通" App 更新'
    },
    {
        'name_en': 'Caiyun',
        'name_cn': '彩云天气',
        'category': '国内',
        'platforms': 'iOS/Android',
        'official_site': '',
        'search_keywords': '"彩云天气" 新功能 动态',
        'is_active': False  # 已停服
    },
    {
        'name_en': 'MojiWeather',
        'name_cn': '墨迹天气',
        'category': '本品',
        'platforms': 'iOS/Android',
        'official_site': 'https://moji.com',
        'search_keywords': '"墨迹天气" 更新 新闻'
    }
]

# 周报配置
WEEKLY_REPORT_DIR = '/Users/xiaoxiao.liu/竞品监测周报/'
MEMORY_FILE_PATH = '/Users/xiaoxiao.liu/.claude/projects/-Users-xiaoxiao-liu/memory/weekly_competitor_report.md'

# 日志配置
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
