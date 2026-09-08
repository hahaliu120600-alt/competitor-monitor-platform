import os
import sys
from datetime import datetime, timedelta, date
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from models import get_session, Competitor, AppUpdate, CompanyNews, Partnership, MarketData

class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.session = get_session()

    def generate_weekly_report(self, start_date=None, end_date=None):
        """
        生成周报

        Args:
            start_date: 开始日期，默认为7天前
            end_date: 结束日期，默认为今天

        Returns:
            报告文件路径
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=7)

        # 获取期数
        report_number = self._get_next_report_number()

        # 生成报告内容
        report_content = self._generate_report_content(start_date, end_date, report_number)

        # 保存为Markdown文件
        filename = f"天气类App竞品监测周报_第{report_number}期_{end_date.strftime('%Y%m%d')}.md"
        filepath = os.path.join(config.WEEKLY_REPORT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # 更新记忆文件
        self._update_memory_file(report_number, end_date)

        return filepath

    def _get_next_report_number(self):
        """获取下一期报告编号"""
        try:
            # 读取记忆文件
            if os.path.exists(config.MEMORY_FILE_PATH):
                with open(config.MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找最后一期编号
                    import re
                    matches = re.findall(r'第(\d+)期', content)
                    if matches:
                        return int(matches[-1]) + 1
            return 12  # 默认从第12期开始（接上之前的第11期）
        except:
            return 12

    def _generate_report_content(self, start_date, end_date, report_number):
        """生成报告内容"""
        content = f"""# 天气类App竞品监测周报

**报告期数**：第{report_number}期
**监测周期**：{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}
**报告日期**：{datetime.now().strftime('%Y-%m-%d')}

---

## 一、本周核心洞察

> {self._generate_key_insights(start_date, end_date)}

---

## 二、市场数据总览

{self._generate_market_overview(start_date, end_date)}

---

## 三、APP更新动态

{self._generate_app_updates_section(start_date, end_date)}

---

## 四、公司动态

{self._generate_company_news_section(start_date, end_date)}

---

## 五、合作动态

{self._generate_partnership_section(start_date, end_date)}

---

## 六、行业趋势与深度洞察

{self._generate_insights_section(start_date, end_date)}

---

## 七、下周重点关注

{self._generate_next_week_focus()}

"""
        return content

    def _generate_key_insights(self, start_date, end_date):
        """生成核心洞察"""
        # 统计本周数据
        updates = self.session.query(AppUpdate).filter(
            AppUpdate.collected_at >= start_date,
            AppUpdate.collected_at <= end_date
        ).all()

        news_count = self.session.query(CompanyNews).filter(
            CompanyNews.collected_at >= start_date,
            CompanyNews.collected_at <= end_date
        ).count()

        insights = []

        if updates:
            insights.append(f"本周监测到 {len(updates)} 个App版本更新")

        if news_count > 0:
            insights.append(f"收集到 {news_count} 条公司动态")

        if not insights:
            insights.append("本周竞品市场相对平静，暂无重大更新和动态")

        return '\n> '.join([''] + insights)

    def _generate_market_overview(self, start_date, end_date):
        """生成市场数据总览表格"""
        competitors = self.session.query(Competitor).all()

        table = """| 竞品名称 | 平台 | 最新版本 | 近7天下载量 | 下载环比 | 近30天收入 | 商店排名 | 评分 |
|----------|------|---------|-----------|---------|-----------|---------|------|
"""

        for comp in competitors:
            # 获取最新版本
            latest_update = self.session.query(AppUpdate).filter_by(
                competitor_id=comp.id
            ).order_by(AppUpdate.release_date.desc()).first()

            version = latest_update.version if latest_update else '暂无数据'

            # 获取最新市场数据
            latest_market_data = self.session.query(MarketData).filter_by(
                competitor_id=comp.id
            ).order_by(MarketData.date.desc()).first()

            downloads = latest_market_data.downloads_7d if latest_market_data and latest_market_data.downloads_7d else '暂无数据'
            ranking = latest_market_data.ranking_ios if latest_market_data and latest_market_data.ranking_ios else '暂无数据'
            rating = latest_market_data.rating_ios if latest_market_data and latest_market_data.rating_ios else '暂无数据'

            name = f"**{comp.name_cn}**" if comp.category == '本品' else comp.name_cn
            table += f"| {name} | {comp.platforms} | {version} | {downloads} | 暂无数据 | 暂无数据 | {ranking} | {rating} |\n"

        table += '\n*数据来源：系统自动采集 + 手动补充。标注"暂无数据"的项目表示本期未获取到可靠数据。*\n'

        return table

    def _generate_app_updates_section(self, start_date, end_date):
        """生成App更新动态章节"""
        updates = self.session.query(AppUpdate).filter(
            AppUpdate.collected_at >= start_date,
            AppUpdate.collected_at <= end_date
        ).all()

        if not updates:
            return "### 本周暂无App更新记录\n\n本周未监测到竞品的版本更新信息。\n"

        content = "### 本周有更新的App\n\n"

        for i, update in enumerate(updates, 1):
            competitor = self.session.query(Competitor).get(update.competitor_id)

            content += f"#### {i}. {competitor.name_cn} v{update.version}\n"
            content += f"- **更新日期**：{update.release_date}\n"
            content += f"- **更新平台**：{update.platform}\n"
            content += f"- **更新内容**：\n"

            # 解析features JSON
            import json
            try:
                features = json.loads(update.features) if update.features else []
                for feature in features[:5]:
                    content += f"  - {feature}\n"
            except:
                content += f"  - {update.highlight}\n"

            if update.highlight:
                content += f"- **功能亮点分析**：{update.highlight}\n"

            if update.source_url:
                content += f"- **来源**：{update.source_url}\n"

            content += "\n"

        return content

    def _generate_company_news_section(self, start_date, end_date):
        """生成公司动态章节"""
        news_items = self.session.query(CompanyNews).filter(
            CompanyNews.collected_at >= start_date,
            CompanyNews.collected_at <= end_date
        ).all()

        if not news_items:
            return "*本周未监测到重大公司动态*\n"

        # 按类型分组
        news_by_type = defaultdict(list)
        for news in news_items:
            news_by_type[news.news_type].append(news)

        content = ""

        type_names = {
            'funding': '### 战略/融资/收购\n',
            'acquisition': '### 战略/融资/收购\n',
            'strategy': '### 战略动向\n',
            'personnel': '### 人事变动\n'
        }

        for news_type, items in news_by_type.items():
            content += type_names.get(news_type, '### 其他动态\n')
            for news in items:
                competitor = self.session.query(Competitor).get(news.competitor_id)
                content += f"- **{competitor.name_cn}**：{news.title}\n"
                if news.summary:
                    content += f"  {news.summary[:200]}...\n"
                if news.source_url:
                    content += f"  （来源：{news.source_url}）\n"
                content += "\n"

        return content

    def _generate_partnership_section(self, start_date, end_date):
        """生成合作动态章节"""
        partnerships = self.session.query(Partnership).filter(
            Partnership.collected_at >= start_date,
            Partnership.collected_at <= end_date
        ).all()

        if not partnerships:
            return "*本周未监测到重大合作动态*\n"

        content = ""
        for partner in partnerships:
            competitor = self.session.query(Competitor).get(partner.competitor_id)
            content += f"- **{competitor.name_cn}** x {partner.partner_name}：{partner.description}\n"
            if partner.source_url:
                content += f"  （来源：{partner.source_url}）\n"
            content += "\n"

        return content

    def _generate_insights_section(self, start_date, end_date):
        """生成洞察章节"""
        return """### 行业趋势
本周天气类App市场保持平稳发展态势。

### 竞品策略分析
各主要竞品持续优化核心天气预报能力，并探索垂直场景拓展。

### 对墨迹天气的建议
1. **产品层面**：持续强化"分钟级+公里级"精准预报能力
2. **运营层面**：关注竞品的用户增长策略
3. **商业化层面**：探索场景化广告和会员增值服务
"""

    def _generate_next_week_focus(self):
        """生成下周关注重点"""
        return """1. 持续跟踪国际竞品的AI功能集成进展
2. 关注国内竞品的合作动态
3. 监测市场排名和用户评价变化趋势
"""

    def _update_memory_file(self, report_number, report_date):
        """更新记忆文件"""
        try:
            if not os.path.exists(config.MEMORY_FILE_PATH):
                return

            with open(config.MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

            # 添加新的输出记录
            new_record = f"| 第{report_number}期 | {report_date.strftime('%Y-%m-%d')} | 已完成 | 自动生成 |"

            # 在输出历史表格中添加新行
            if '## 输出历史' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '## 输出历史' in line:
                        # 找到表格末尾
                        j = i + 3  # 跳过标题和表头
                        while j < len(lines) and lines[j].startswith('|'):
                            j += 1
                        lines.insert(j, new_record)
                        break

                content = '\n'.join(lines)

                with open(config.MEMORY_FILE_PATH, 'w', encoding='utf-8') as f:
                    f.write(content)

        except Exception as e:
            print(f"更新记忆文件失败: {e}")

    def __del__(self):
        if self.session:
            self.session.close()
