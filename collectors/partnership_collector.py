import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector
from models import get_session, Partnership

class PartnershipCollector(BaseCollector):
    """合作动态采集器"""

    def collect(self, competitor, date_range=None):
        """采集竞品的合作动态"""
        try:
            company_name = competitor.name_en if competitor.category == '国际' else competitor.name_cn
            query = f'{company_name} partnership collaboration 合作 {datetime.now().strftime("%Y-%m")}'

            self.logger.info(f"开始采集 {competitor.name_cn} 的合作动态: {query}")

            search_result = self.search_with_claude(query)

            if not search_result:
                self.log_collection_result(competitor.name_cn, 0, "搜索结果为空")
                return []

            partnerships = self._parse_partnership_info(search_result, competitor.id)
            saved_count = self._save_partnerships(partnerships)

            self.log_collection_result(competitor.name_cn, saved_count)
            return partnerships

        except Exception as e:
            self.log_collection_result(competitor.name_cn, 0, str(e))
            return []

    def _parse_partnership_info(self, text, competitor_id):
        """解析合作信息"""
        partnerships = []

        type_keywords = {
            'data_source': ['数据', 'data', '气象局', 'weather data'],
            'channel': ['渠道', '预装', 'channel', 'preinstall', '车载'],
            'brand': ['品牌', '联名', 'brand', 'co-brand'],
            'tech': ['技术', 'AI', 'technology', 'cloud']
        }

        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 20]

        for line in lines:
            if 'partnership' in line.lower() or '合作' in line or 'collaboration' in line.lower():
                # 识别合作类型
                partner_type = 'channel'
                for ptype, keywords in type_keywords.items():
                    if any(kw in line.lower() for kw in keywords):
                        partner_type = ptype
                        break

                partnerships.append({
                    'competitor_id': competitor_id,
                    'partner_name': '待提取',
                    'partnership_type': partner_type,
                    'description': line[:500],
                    'announce_date': datetime.now().date(),
                    'source_url': '',
                    'collected_at': datetime.now()
                })

        urls = self.extract_urls(text)
        for i, item in enumerate(partnerships):
            if i < len(urls):
                item['source_url'] = urls[i]

        return partnerships[:3]

    def _save_partnerships(self, partnerships):
        """保存合作信息到数据库"""
        if not partnerships:
            return 0

        session = get_session()
        saved_count = 0

        try:
            for partner_data in partnerships:
                existing = session.query(Partnership).filter_by(
                    competitor_id=partner_data['competitor_id'],
                    description=partner_data['description']
                ).first()

                if not existing:
                    partnership = Partnership(**partner_data)
                    session.add(partnership)
                    saved_count += 1

            session.commit()
            return saved_count

        except Exception as e:
            session.rollback()
            self.logger.error(f"保存合作信息失败: {e}")
            return 0
        finally:
            session.close()
