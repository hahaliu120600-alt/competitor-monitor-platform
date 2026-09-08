import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector
from models import get_session, MarketData

class MarketDataCollector(BaseCollector):
    """市场数据采集器"""

    def collect(self, competitor, date_range=None):
        """采集竞品的市场数据"""
        try:
            # 注意：市场数据通常来自第三方平台，WebSearch效果有限
            # 这里提供一个框架，实际使用时建议集成SensorTower API或手动录入

            self.logger.info(f"开始采集 {competitor.name_cn} 的市场数据")

            # 尝试搜索公开的市场数据报告
            query = f'{competitor.name_en} app downloads ranking {datetime.now().strftime("%Y-%m")}'
            search_result = self.search_with_claude(query)

            if not search_result:
                self.log_collection_result(competitor.name_cn, 0, "搜索结果为空")
                return []

            market_data = self._parse_market_data(search_result, competitor.id)
            saved_count = self._save_market_data(market_data)

            self.log_collection_result(competitor.name_cn, saved_count)
            return market_data

        except Exception as e:
            self.log_collection_result(competitor.name_cn, 0, str(e))
            return []

    def _parse_market_data(self, text, competitor_id):
        """解析市场数据"""
        import re

        market_data = {
            'competitor_id': competitor_id,
            'date': datetime.now().date(),
            'downloads_7d': None,
            'downloads_30d': None,
            'revenue_30d': None,
            'ranking_ios': None,
            'ranking_android': None,
            'rating_ios': None,
            'rating_android': None,
            'data_source': 'websearch',
            'collected_at': datetime.now()
        }

        # 尝试提取下载量
        download_patterns = [
            r'(\d+(?:,\d+)*)\s*downloads',
            r'下载量[:：]\s*(\d+(?:,\d+)*)',
        ]

        for pattern in download_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                downloads = int(match.group(1).replace(',', ''))
                market_data['downloads_30d'] = downloads
                break

        # 尝试提取排名
        rank_patterns = [
            r'rank(?:ing)?[:：]?\s*#?(\d+)',
            r'排名[:：]\s*第?\s*(\d+)',
        ]

        for pattern in rank_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rank = int(match.group(1))
                market_data['ranking_ios'] = rank
                break

        # 尝试提取评分
        rating_patterns = [
            r'rating[:：]?\s*([\d\.]+)',
            r'评分[:：]\s*([\d\.]+)',
            r'([\d\.]+)\s*stars?',
        ]

        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    market_data['rating_ios'] = rating
                    break

        return [market_data] if any(v is not None for k, v in market_data.items() if k not in ['competitor_id', 'date', 'data_source', 'collected_at']) else []

    def _save_market_data(self, market_data_list):
        """保存市场数据到数据库"""
        if not market_data_list:
            return 0

        session = get_session()
        saved_count = 0

        try:
            for data in market_data_list:
                # 检查当天是否已有数据
                existing = session.query(MarketData).filter_by(
                    competitor_id=data['competitor_id'],
                    date=data['date']
                ).first()

                if existing:
                    # 更新现有数据
                    for key, value in data.items():
                        if value is not None and key not in ['id', 'competitor_id', 'date']:
                            setattr(existing, key, value)
                else:
                    # 创建新数据
                    market_data = MarketData(**data)
                    session.add(market_data)
                    saved_count += 1

            session.commit()
            return saved_count

        except Exception as e:
            session.rollback()
            self.logger.error(f"保存市场数据失败: {e}")
            return 0
        finally:
            session.close()

    def manual_input(self, competitor_id, data_dict):
        """
        手动录入市场数据

        Args:
            competitor_id: 竞品ID
            data_dict: 数据字典，如 {'downloads_30d': 10000, 'rating_ios': 4.5}

        Returns:
            是否成功
        """
        session = get_session()

        try:
            market_data = MarketData(
                competitor_id=competitor_id,
                date=datetime.now().date(),
                data_source='manual',
                collected_at=datetime.now(),
                **data_dict
            )

            session.add(market_data)
            session.commit()
            self.logger.info(f"手动录入市场数据成功: 竞品ID {competitor_id}")
            return True

        except Exception as e:
            session.rollback()
            self.logger.error(f"手动录入市场数据失败: {e}")
            return False
        finally:
            session.close()
