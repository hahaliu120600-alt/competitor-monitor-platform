import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import get_session, Competitor, AppUpdate, CompanyNews, Partnership, MarketData, DailyReport
from sqlalchemy import func

class AnalysisService:
    """数据分析服务"""

    def __init__(self):
        self.session = get_session()

    def get_dashboard_summary(self):
        """获取Dashboard汇总数据"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        summary = {
            'total_competitors': self.session.query(Competitor).filter_by(is_active=True).count(),
            'updates_this_week': self.session.query(AppUpdate).filter(
                AppUpdate.collected_at >= week_ago
            ).count(),
            'news_this_week': self.session.query(CompanyNews).filter(
                CompanyNews.collected_at >= week_ago
            ).count(),
            'partnerships_this_week': self.session.query(Partnership).filter(
                Partnership.collected_at >= week_ago
            ).count(),
            'last_collection_time': self._get_last_collection_time()
        }

        return summary

    def get_recent_activities(self, days=7, limit=20):
        """获取最近的活动动态"""
        cutoff_date = datetime.now() - timedelta(days=days)

        activities = []

        # 获取更新记录
        updates = self.session.query(AppUpdate).filter(
            AppUpdate.collected_at >= cutoff_date
        ).order_by(AppUpdate.collected_at.desc()).limit(limit).all()

        for update in updates:
            competitor = self.session.query(Competitor).get(update.competitor_id)
            # 使用实际发布日期，如果没有则使用采集时间
            actual_date = datetime.combine(update.release_date, datetime.min.time()) if update.release_date else update.collected_at
            activities.append({
                'type': 'update',
                'date': actual_date,
                'competitor': competitor.name_cn,
                'title': f'版本更新 v{update.version}',
                'description': update.highlight,
                'url': update.source_url if update.source_url else None
            })

        # 获取新闻记录
        news = self.session.query(CompanyNews).filter(
            CompanyNews.collected_at >= cutoff_date
        ).order_by(CompanyNews.collected_at.desc()).limit(limit).all()

        for n in news:
            competitor = self.session.query(Competitor).get(n.competitor_id)
            # 使用实际发布日期，如果没有则使用采集时间
            actual_date = datetime.combine(n.publish_date, datetime.min.time()) if n.publish_date else n.collected_at
            activities.append({
                'type': 'news',
                'date': actual_date,
                'competitor': competitor.name_cn,
                'title': n.title,
                'description': n.summary[:150] if n.summary else '',
                'url': n.source_url if n.source_url else None
            })

        # 按时间排序
        activities.sort(key=lambda x: x['date'], reverse=True)

        return activities[:limit]

    def get_competitor_comparison(self):
        """获取竞品对比数据"""
        competitors = self.session.query(Competitor).filter_by(is_active=True).all()

        comparison_data = []

        for comp in competitors:
            # 获取最新版本
            latest_update = self.session.query(AppUpdate).filter_by(
                competitor_id=comp.id
            ).order_by(AppUpdate.release_date.desc()).first()

            # 获取更新频率（最近30天）
            thirty_days_ago = datetime.now() - timedelta(days=30)
            update_count = self.session.query(AppUpdate).filter(
                AppUpdate.competitor_id == comp.id,
                AppUpdate.collected_at >= thirty_days_ago
            ).count()

            # 获取最新市场数据
            latest_market = self.session.query(MarketData).filter_by(
                competitor_id=comp.id
            ).order_by(MarketData.date.desc()).first()

            comparison_data.append({
                'id': comp.id,
                'name': comp.name_cn,
                'name_en': comp.name_en,
                'category': comp.category,
                'latest_version': latest_update.version if latest_update else 'N/A',
                'last_update_date': latest_update.release_date if latest_update else None,
                'updates_30d': update_count,
                'rating': latest_market.rating_ios if latest_market else None,
                'ranking': latest_market.ranking_ios if latest_market else None
            })

        return comparison_data

    def get_trend_data(self, competitor_id, metric='rating', days=30):
        """获取趋势数据"""
        cutoff_date = datetime.now().date() - timedelta(days=days)

        market_data = self.session.query(MarketData).filter(
            MarketData.competitor_id == competitor_id,
            MarketData.date >= cutoff_date
        ).order_by(MarketData.date).all()

        trend_data = {
            'dates': [],
            'values': []
        }

        for data in market_data:
            trend_data['dates'].append(data.date.strftime('%Y-%m-%d'))

            if metric == 'rating':
                value = data.rating_ios or data.rating_android
            elif metric == 'ranking':
                value = data.ranking_ios or data.ranking_android
            elif metric == 'downloads':
                value = data.downloads_30d
            else:
                value = None

            trend_data['values'].append(value)

        return trend_data

    def _get_last_collection_time(self):
        """获取最后一次采集时间"""
        latest_report = self.session.query(DailyReport).order_by(
            DailyReport.report_date.desc()
        ).first()

        if latest_report:
            return latest_report.created_at.strftime('%Y-%m-%d %H:%M')
        return 'N/A'

    def __del__(self):
        if self.session:
            self.session.close()
