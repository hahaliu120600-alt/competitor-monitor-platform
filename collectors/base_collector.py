import os
import sys
import logging
from datetime import datetime
from abc import ABC, abstractmethod

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class BaseCollector(ABC):
    """数据采集器基类"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.anthropic_api_key = config.ANTHROPIC_API_KEY

    @abstractmethod
    def collect(self, competitor, date_range=None):
        """
        采集数据的抽象方法

        Args:
            competitor: Competitor对象
            date_range: 日期范围，如 '2026-09-01 to 2026-09-03'

        Returns:
            采集到的数据列表
        """
        pass

    def search_with_claude(self, query):
        """
        使用Claude API进行WebSearch

        Args:
            query: 搜索查询

        Returns:
            搜索结果文本
        """
        if not self.anthropic_api_key:
            self.logger.warning("未配置ANTHROPIC_API_KEY，跳过Claude搜索")
            return None

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.anthropic_api_key)

            message = client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": f"""请搜索并总结：{query}

要求：
1. 提取关键信息（版本号、日期、功能、公司动态等）
2. 返回结构化的文本结果
3. 包含信息来源URL"""
                }]
            )

            # 提取文本内容
            result_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    result_text += block.text

            self.logger.info(f"Claude搜索成功: {query[:50]}...")
            return result_text

        except Exception as e:
            self.logger.error(f"Claude搜索失败: {e}")
            return None

    def parse_date(self, date_str):
        """
        解析日期字符串

        Args:
            date_str: 日期字符串，支持多种格式

        Returns:
            datetime.date对象或None
        """
        if not date_str:
            return None

        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y年%m月%d日',
            '%B %d, %Y',
            '%d %B %Y',
            '%m/%d/%Y'
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue

        self.logger.warning(f"无法解析日期: {date_str}")
        return None

    def extract_urls(self, text):
        """
        从文本中提取URL

        Args:
            text: 文本内容

        Returns:
            URL列表
        """
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls[:5]  # 最多返回5个URL

    def log_collection_result(self, competitor_name, data_count, error=None):
        """记录采集结果"""
        if error:
            self.logger.error(f"{competitor_name} 采集失败: {error}")
        else:
            self.logger.info(f"{competitor_name} 采集成功，获得 {data_count} 条数据")
