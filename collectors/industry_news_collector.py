import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector
from models import get_session

class IndustryNewsCollector(BaseCollector):
    """ToB行业新闻采集器"""

    def __init__(self):
        super().__init__()
        import config
        self.industries = config.TOB_INDUSTRIES

    def collect(self, competitor=None, date_range=None):
        """
        实现BaseCollector的抽象方法（兼容接口）

        Args:
            competitor: 未使用（行业采集不需要）
            date_range: 日期范围

        Returns:
            空列表（实际使用collect_all_industries）
        """
        # 行业采集使用专门的方法
        return []

    def collect_industry(self, industry_key, days=7):
        """
        采集特定行业的新闻

        Args:
            industry_key: 行业标识 (subway/aviation/energy)
            days: 采集最近N天的新闻

        Returns:
            新闻列表
        """
        if industry_key not in self.industries:
            self.logger.error(f"未知行业: {industry_key}")
            return []

        industry = self.industries[industry_key]

        self.logger.info(f"开始采集 {industry['name']} 行业情报")

        try:
            # 构建搜索查询
            keywords = ' OR '.join([f'"{kw}"' for kw in industry['keywords'][:3]])
            query = f"气象 {keywords} {datetime.now().strftime('%Y-%m')}"

            self.logger.info(f"搜索查询: {query}")

            # 使用Claude搜索
            search_result = self.search_with_claude(query)

            if not search_result:
                self.log_collection_result(industry['name'], 0, "搜索结果为空")
                return []

            # 解析新闻
            news_items = self._parse_industry_news(search_result, industry_key)

            self.log_collection_result(industry['name'], len(news_items))
            return news_items

        except Exception as e:
            self.log_collection_result(industry['name'], 0, str(e))
            return []

    def collect_all_industries(self):
        """采集所有行业的新闻"""
        all_news = {}

        for industry_key in self.industries.keys():
            all_news[industry_key] = self.collect_industry(industry_key)

        return all_news

    def _parse_industry_news(self, text, industry_key):
        """解析行业新闻"""
        news_items = []
        industry = self.industries[industry_key]

        try:
            lines = text.split('\n')
            current_item = {
                'industry': industry_key,
                'industry_name': industry['name'],
                'title': '',
                'content': '',
                'date': datetime.now().date(),
                'source': '',
                'category': 'news',  # news/policy/competitor
                'collected_at': datetime.now()
            }

            for line in lines:
                line = line.strip()
                if len(line) < 10:
                    continue

                # 识别类别
                if any(word in line for word in ['政策', '通知', '标准', 'policy']):
                    current_item['category'] = 'policy'
                elif any(comp in line for comp in industry['competitors']):
                    current_item['category'] = 'competitor'

                # 提取标题（通常较短且包含关键词）
                if len(line) < 100 and any(kw in line for kw in industry['keywords']):
                    if current_item['title'] and current_item['content']:
                        # 保存前一条
                        news_items.append(current_item.copy())
                        current_item = {
                            'industry': industry_key,
                            'industry_name': industry['name'],
                            'title': '',
                            'content': '',
                            'date': datetime.now().date(),
                            'source': '',
                            'category': 'news',
                            'collected_at': datetime.now()
                        }
                    current_item['title'] = line
                else:
                    current_item['content'] += line + ' '

            # 保存最后一条
            if current_item['title']:
                news_items.append(current_item)

            # 提取URL
            urls = self.extract_urls(text)
            for i, item in enumerate(news_items):
                if i < len(urls):
                    item['source'] = urls[i]

        except Exception as e:
            self.logger.error(f"解析行业新闻失败: {e}")

        return news_items[:10]  # 最多返回10条

    def save_industry_news(self, news_items):
        """保存行业新闻到数据库（使用JSON存储）"""
        if not news_items:
            return 0

        import json
        from models import get_session, DailyReport

        session = get_session()
        saved_count = 0

        try:
            # 将行业新闻追加到今日报告
            today = datetime.now().date()
            report = session.query(DailyReport).filter_by(report_date=today).first()

            if not report:
                report = DailyReport(
                    report_date=today,
                    total_updates=0,
                    total_news=0,
                    total_partnerships=0,
                    key_insights='',
                    status='success'
                )
                session.add(report)

            # 读取现有insights
            try:
                insights = json.loads(report.key_insights) if report.key_insights else {}
            except:
                insights = {}

            # 添加行业新闻
            if 'industry_news' not in insights:
                insights['industry_news'] = {}

            for item in news_items:
                industry = item['industry']
                if industry not in insights['industry_news']:
                    insights['industry_news'][industry] = []

                insights['industry_news'][industry].append({
                    'title': item['title'],
                    'content': item['content'][:200],
                    'category': item['category'],
                    'date': item['date'].strftime('%Y-%m-%d'),
                    'source': item.get('source', '')
                })
                saved_count += 1

            report.key_insights = json.dumps(insights, ensure_ascii=False)
            session.commit()

            return saved_count

        except Exception as e:
            session.rollback()
            self.logger.error(f"保存行业新闻失败: {e}")
            return 0
        finally:
            session.close()
