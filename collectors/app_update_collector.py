import os
import sys
import json
import re
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector
from models import get_session, AppUpdate

class AppUpdateCollector(BaseCollector):
    """App更新信息采集器"""

    def collect(self, competitor, date_range=None):
        """
        采集竞品的App更新信息

        Args:
            competitor: Competitor对象
            date_range: 日期范围字符串，如 '2026-09'

        Returns:
            采集到的更新记录列表
        """
        try:
            # 构建搜索查询
            if date_range:
                query = f"{competitor.search_keywords} {date_range}"
            else:
                # 默认搜索最近一个月
                current_month = datetime.now().strftime('%Y-%m')
                query = f"{competitor.search_keywords} {current_month}"

            self.logger.info(f"开始采集 {competitor.name_cn} 的更新信息: {query}")

            # 使用Claude搜索
            search_result = self.search_with_claude(query)

            if not search_result:
                self.log_collection_result(competitor.name_cn, 0, "搜索结果为空")
                return []

            # 解析搜索结果
            updates = self._parse_update_info(search_result, competitor.id)

            # 保存到数据库
            saved_count = self._save_updates(updates)

            self.log_collection_result(competitor.name_cn, saved_count)
            return updates

        except Exception as e:
            self.log_collection_result(competitor.name_cn, 0, str(e))
            return []

    def _parse_update_info(self, text, competitor_id):
        """
        解析更新信息文本

        Args:
            text: 搜索结果文本
            competitor_id: 竞品ID

        Returns:
            更新记录列表
        """
        updates = []

        try:
            # 尝试提取版本号
            version_patterns = [
                r'[vV]ersion\s+(\d+\.[\d\.]+)',
                r'[vV](\d+\.[\d\.]+)',
                r'版本\s*[:：]?\s*(\d+\.[\d\.]+)'
            ]

            versions = []
            for pattern in version_patterns:
                versions.extend(re.findall(pattern, text))

            # 提取日期
            date_patterns = [
                r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                r'(\d{4}年\d{1,2}月\d{1,2}日)'
            ]

            dates = []
            for pattern in date_patterns:
                dates.extend(re.findall(pattern, text))

            # 提取功能关键词
            feature_keywords = ['新增', '优化', '修复', 'new', 'feature', 'update', 'fix', 'improve']
            features = []

            lines = text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in feature_keywords):
                    if len(line.strip()) > 10 and len(line.strip()) < 200:
                        features.append(line.strip())

            # 提取URL
            urls = self.extract_urls(text)

            # 如果找到版本信息，创建更新记录
            if versions:
                version = versions[0]
                release_date = self.parse_date(dates[0]) if dates else date.today()

                update = {
                    'competitor_id': competitor_id,
                    'version': version,
                    'release_date': release_date,
                    'platform': 'Both',  # 默认双端
                    'features': json.dumps(features[:10], ensure_ascii=False),
                    'highlight': self._generate_highlight(features),
                    'insight': '',  # 后续可用AI生成
                    'source_url': urls[0] if urls else '',
                    'collected_at': datetime.now()
                }
                updates.append(update)
            else:
                # 即使没找到明确版本号，如果有更新信息也记录
                if features:
                    update = {
                        'competitor_id': competitor_id,
                        'version': '未知',
                        'release_date': date.today(),
                        'platform': 'Both',
                        'features': json.dumps(features[:10], ensure_ascii=False),
                        'highlight': self._generate_highlight(features),
                        'insight': '',
                        'source_url': urls[0] if urls else '',
                        'collected_at': datetime.now()
                    }
                    updates.append(update)

        except Exception as e:
            self.logger.error(f"解析更新信息失败: {e}")

        return updates

    def _generate_highlight(self, features):
        """生成功能亮点摘要"""
        if not features:
            return "暂无详细信息"

        # 取前3个功能作为亮点
        highlights = features[:3]
        return '; '.join(highlights)

    def _save_updates(self, updates):
        """
        保存更新记录到数据库

        Args:
            updates: 更新记录列表

        Returns:
            保存成功的记录数
        """
        if not updates:
            return 0

        session = get_session()
        saved_count = 0

        try:
            for update_data in updates:
                # 检查是否已存在（相同竞品、版本、日期）
                existing = session.query(AppUpdate).filter_by(
                    competitor_id=update_data['competitor_id'],
                    version=update_data['version'],
                    release_date=update_data['release_date']
                ).first()

                if existing:
                    # 更新现有记录
                    existing.features = update_data['features']
                    existing.highlight = update_data['highlight']
                    existing.source_url = update_data['source_url']
                    existing.collected_at = datetime.now()
                    self.logger.info(f"更新已存在的记录: {update_data['version']}")
                else:
                    # 创建新记录
                    app_update = AppUpdate(**update_data)
                    session.add(app_update)
                    saved_count += 1

            session.commit()
            return saved_count

        except Exception as e:
            session.rollback()
            self.logger.error(f"保存更新记录失败: {e}")
            return 0
        finally:
            session.close()
