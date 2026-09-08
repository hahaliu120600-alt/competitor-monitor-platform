import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector
from models import get_session, CompanyNews

class CompanyNewsCollector(BaseCollector):
    """公司动态采集器"""

    def collect(self, competitor, date_range=None):
        """采集竞品的公司动态"""
        try:
            # 构建搜索查询
            company_name = competitor.name_en if competitor.category == '国际' else competitor.name_cn
            query = f'{company_name} news funding acquisition strategy {datetime.now().strftime("%Y-%m")}'

            self.logger.info(f"开始采集 {competitor.name_cn} 的公司动态: {query}")

            # 使用Claude搜索
            search_result = self.search_with_claude(query)

            if not search_result:
                self.log_collection_result(competitor.name_cn, 0, "搜索结果为空")
                return []

            # 解析新闻信息
            news_items = self._parse_news_info(search_result, competitor.id)

            # 保存到数据库
            saved_count = self._save_news(news_items)

            self.log_collection_result(competitor.name_cn, saved_count)
            return news_items

        except Exception as e:
            self.log_collection_result(competitor.name_cn, 0, str(e))
            return []

    def _parse_news_info(self, text, competitor_id):
        """解析新闻信息"""
        news_items = []

        try:
            # 识别新闻类型关键词
            type_keywords = {
                'funding': ['融资', '投资', 'funding', 'investment', 'raised'],
                'acquisition': ['收购', '并购', 'acquisition', 'acquired', 'merger'],
                'strategy': ['战略', '业务', 'strategy', 'business', 'expansion'],
                'personnel': ['人事', '任命', '离职', 'appointed', 'hired', 'CEO', 'CTO']
            }

            # 按行分析
            lines = text.split('\n')
            current_title = ""
            current_type = "strategy"
            current_summary = ""

            for line in lines:
                line = line.strip()
                if len(line) < 10:
                    continue

                # 识别新闻类型
                for news_type, keywords in type_keywords.items():
                    if any(keyword in line.lower() for keyword in keywords):
                        current_type = news_type
                        break

                # 识别标题行（通常较短且包含关键信息）
                if len(line) < 150 and any(char in line for char in ['：', ':', '-']):
                    if current_title and current_summary:
                        # 保存前一条新闻
                        news_items.append({
                            'competitor_id': competitor_id,
                            'news_type': current_type,
                            'title': current_title,
                            'summary': current_summary,
                            'publish_date': datetime.now().date(),
                            'source_url': '',
                            'collected_at': datetime.now()
                        })

                    current_title = line
                    current_summary = ""
                else:
                    current_summary += line + " "

            # 保存最后一条
            if current_title:
                news_items.append({
                    'competitor_id': competitor_id,
                    'news_type': current_type,
                    'title': current_title,
                    'summary': current_summary.strip()[:500],
                    'publish_date': datetime.now().date(),
                    'source_url': '',
                    'collected_at': datetime.now()
                })

            # 提取URL并关联
            urls = self.extract_urls(text)
            for i, item in enumerate(news_items):
                if i < len(urls):
                    item['source_url'] = urls[i]

        except Exception as e:
            self.logger.error(f"解析新闻信息失败: {e}")

        return news_items[:5]  # 最多返回5条新闻

    def _save_news(self, news_items):
        """保存新闻到数据库"""
        if not news_items:
            return 0

        session = get_session()
        saved_count = 0

        try:
            for news_data in news_items:
                # 检查是否已存在（相同标题）
                existing = session.query(CompanyNews).filter_by(
                    competitor_id=news_data['competitor_id'],
                    title=news_data['title']
                ).first()

                if not existing:
                    news = CompanyNews(**news_data)
                    session.add(news)
                    saved_count += 1

            session.commit()
            return saved_count

        except Exception as e:
            session.rollback()
            self.logger.error(f"保存新闻失败: {e}")
            return 0
        finally:
            session.close()
