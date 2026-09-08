#!/usr/bin/env python3
"""生成示例数据填充网站"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
import json
from models import get_session, AppUpdate, CompanyNews, Partnership, MarketData, DailyReport, Competitor

def generate_sample_data():
    """生成示例数据"""
    session = get_session()

    try:
        print("开始生成示例数据...\n")

        # 1. 生成App更新数据
        print("1. 生成App版本更新数据...")
        competitors = session.query(Competitor).all()

        sample_updates = [
            {
                'competitor_id': 1,
                'version': 'v12.5.0',
                'release_date': date.today() - timedelta(days=2),
                'platform': 'iOS/Android',
                'features': json.dumps([
                    '新增AI驱动的15天精准预报',
                    '优化过敏指数预测算法',
                    '增强型天气雷达可视化',
                    '修复已知问题'
                ], ensure_ascii=False),
                'highlight': '推出增强型过敏体验，提供更精准的过敏指数预报',
                'insight': '从通用天气预报向健康场景深化，值得墨迹天气借鉴',
                'source_url': 'https://weather.com/updates'
            },
            {
                'competitor_id': 2,
                'version': 'v8.3.1',
                'release_date': date.today() - timedelta(days=5),
                'platform': 'iOS/Android',
                'features': json.dumps([
                    '新增MinuteCast分钟级降雨预报',
                    '优化RealFeel温度算法',
                    '支持Apple Watch Ultra 2',
                    '性能优化'
                ], ensure_ascii=False),
                'highlight': 'MinuteCast功能升级，预报准确率提升至95%',
                'insight': '分钟级预报是核心竞争力，墨迹需持续强化',
                'source_url': 'https://accuweather.com/news'
            },
            {
                'competitor_id': 3,
                'version': 'v48.0',
                'release_date': date.today() - timedelta(days=1),
                'platform': 'iOS/Android/Web',
                'features': json.dumps([
                    '冬季天气和海洋预报工具升级',
                    '新增月相显示功能',
                    '实时暴雨和强降雨警报系统',
                    'Harrison Abacus插件支持'
                ], ensure_ascii=False),
                'highlight': '推出实时暴雨警报，社区用户高度评价',
                'insight': '专业气象可视化是差异化优势',
                'source_url': 'https://community.windy.com'
            },
            {
                'competitor_id': 10,
                'version': 'v9.9.40',
                'release_date': date.today() - timedelta(days=3),
                'platform': 'iOS/Android',
                'features': json.dumps([
                    '短时临近预报：采用雷达图像显示技术',
                    '分钟级预报：精准到1分钟',
                    '公里级定位：预报范围缩小到1公里',
                    'AI智能技术：结合机器学习',
                    '全球预报数据可视化'
                ], ensure_ascii=False),
                'highlight': '持续强化"分钟级+公里级"精准预报能力',
                'insight': '对标已停服的彩云天气，承接市场空缺',
                'source_url': 'https://moji.com'
            }
        ]

        for update_data in sample_updates:
            # 检查是否已存在
            existing = session.query(AppUpdate).filter_by(
                competitor_id=update_data['competitor_id'],
                version=update_data['version']
            ).first()

            if not existing:
                update = AppUpdate(**update_data)
                session.add(update)

        session.commit()
        print(f"  ✓ 已添加 {len(sample_updates)} 条版本更新记录")

        # 2. 生成公司动态
        print("2. 生成公司动态数据...")
        sample_news = [
            {
                'competitor_id': 1,
                'news_type': 'strategy',
                'title': 'The Weather Company宣布全球预报准确度领先地位扩大',
                'summary': 'TWC在2026年Q2宣布作为全球最准确的天气预报服务商进一步扩大领先优势，并获评Morning Consult最受信任品牌第6名',
                'publish_date': date.today() - timedelta(days=7),
                'source_url': 'https://weathercompany.com/news'
            },
            {
                'competitor_id': 1,
                'news_type': 'partnership',
                'title': 'The Weather Company与Redfin合作提供房源天气数据',
                'summary': '为房地产平台Redfin的房源提供精准天气数据，帮助购房者了解房屋所在地的气候特征',
                'publish_date': date.today() - timedelta(days=10),
                'source_url': 'https://weathercompany.com/news'
            },
            {
                'competitor_id': 2,
                'news_type': 'funding',
                'title': 'AccuWeather完成新一轮战略融资',
                'summary': 'AccuWeather宣布完成数千万美元融资，将用于AI气象预测技术研发和国际市场拓展',
                'publish_date': date.today() - timedelta(days=15),
                'source_url': 'https://accuweather.com/press'
            }
        ]

        for news_data in sample_news:
            existing = session.query(CompanyNews).filter_by(
                competitor_id=news_data['competitor_id'],
                title=news_data['title']
            ).first()

            if not existing:
                news = CompanyNews(**news_data)
                session.add(news)

        session.commit()
        print(f"  ✓ 已添加 {len(sample_news)} 条公司动态")

        # 3. 生成合作信息
        print("3. 生成合作动态数据...")
        sample_partnerships = [
            {
                'competitor_id': 3,
                'partner_name': 'European Space Agency (ESA)',
                'partnership_type': 'data_source',
                'description': 'Windy与欧洲航天局达成合作，接入Sentinel卫星气象数据，提升全球气象监测能力',
                'announce_date': date.today() - timedelta(days=20),
                'source_url': 'https://windy.com/news'
            }
        ]

        for partner_data in sample_partnerships:
            existing = session.query(Partnership).filter_by(
                competitor_id=partner_data['competitor_id'],
                partner_name=partner_data['partner_name']
            ).first()

            if not existing:
                partnership = Partnership(**partner_data)
                session.add(partnership)

        session.commit()
        print(f"  ✓ 已添加 {len(sample_partnerships)} 条合作动态")

        # 4. 生成市场数据
        print("4. 生成市场数据...")
        sample_market_data = [
            {'competitor_id': 1, 'ranking_ios': 12, 'rating_ios': 4.8, 'downloads_30d': 2500000},
            {'competitor_id': 2, 'ranking_ios': 8, 'rating_ios': 4.6, 'downloads_30d': 3200000},
            {'competitor_id': 3, 'ranking_ios': 25, 'rating_ios': 4.9, 'downloads_30d': 1800000},
            {'competitor_id': 8, 'ranking_ios': 45, 'rating_ios': 4.3, 'downloads_30d': 850000},
            {'competitor_id': 10, 'ranking_ios': 15, 'rating_ios': 4.5, 'downloads_30d': 5600000}
        ]

        for market_data in sample_market_data:
            existing = session.query(MarketData).filter_by(
                competitor_id=market_data['competitor_id'],
                date=date.today()
            ).first()

            if not existing:
                data = MarketData(
                    date=date.today(),
                    data_source='manual',
                    **market_data
                )
                session.add(data)

        session.commit()
        print(f"  ✓ 已添加 {len(sample_market_data)} 条市场数据")

        # 5. 生成ToB行业情报
        print("5. 生成ToB行业情报数据...")
        industry_news = {
            'industry_news': {
                'subway': [
                    {
                        'title': '北京地铁与市气象局签署战略协议',
                        'content': '联合研发轨道交通安全气象预警系统，覆盖全线网27条线路',
                        'category': 'news',
                        'date': (date.today() - timedelta(days=3)).strftime('%Y-%m-%d'),
                        'source': 'https://bjd.com.cn'
                    },
                    {
                        'title': '广州地铁试点"气象+客流"预测模型',
                        'content': '在18号线利用降雨数据优化调度，高峰期运力提升15%',
                        'category': 'news',
                        'date': (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'),
                        'source': 'https://gzmtr.com'
                    },
                    {
                        'title': '华风气象中标成都地铁防灾减灾项目',
                        'content': '华风气象中标成都地铁6条线路的防灾减灾气象服务项目，合同金额1200万元',
                        'category': 'competitor',
                        'date': (date.today() - timedelta(days=8)).strftime('%Y-%m-%d'),
                        'source': ''
                    }
                ],
                'aviation': [
                    {
                        'title': '民航局发布《航空气象服务质量提升指南》',
                        'content': '要求各航空公司在2026年底前完成气象服务系统升级，提升航危天气预警能力',
                        'category': 'policy',
                        'date': (date.today() - timedelta(days=12)).strftime('%Y-%m-%d'),
                        'source': 'http://caac.gov.cn'
                    },
                    {
                        'title': '东航与气象部门合作开展航路气象优化',
                        'content': '通过精准气象数据优化航路规划，预计年节省燃油成本超5000万元',
                        'category': 'news',
                        'date': (date.today() - timedelta(days=6)).strftime('%Y-%m-%d'),
                        'source': ''
                    },
                    {
                        'title': 'WNI推出机场低能见度预警系统',
                        'content': '日本气象新闻公司WNI发布新一代机场低能见度AI预警系统，准确率达92%',
                        'category': 'competitor',
                        'date': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
                        'source': ''
                    }
                ],
                'energy': [
                    {
                        'title': '国家能源局发布风电功率预测双细则考核新标准',
                        'content': '要求各省在2026年Q4前完成预测系统升级，预测准确率需达到90%以上',
                        'category': 'policy',
                        'date': (date.today() - timedelta(days=18)).strftime('%Y-%m-%d'),
                        'source': 'http://nea.gov.cn'
                    },
                    {
                        'title': '国能日新推出基于AI的短期功率预测平台',
                        'content': '据称准确率提升至92%，已在多个省级电网试点应用',
                        'category': 'competitor',
                        'date': (date.today() - timedelta(days=14)).strftime('%Y-%m-%d'),
                        'source': ''
                    },
                    {
                        'title': '远景能源与某省级电网合作开展风光储一体化试点',
                        'content': '联合开展风光储一体化气象服务试点，提升新能源消纳能力',
                        'category': 'competitor',
                        'date': (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
                        'source': ''
                    },
                    {
                        'title': '三峡新能源签约智慧气象服务项目',
                        'content': '与气象服务商签订为期3年的智慧气象服务合同，覆盖全国50个风电场',
                        'category': 'news',
                        'date': (date.today() - timedelta(days=4)).strftime('%Y-%m-%d'),
                        'source': ''
                    }
                ]
            }
        }

        # 创建或更新今日报告
        today_report = session.query(DailyReport).filter_by(report_date=date.today()).first()

        if not today_report:
            today_report = DailyReport(
                report_date=date.today(),
                total_updates=len(sample_updates),
                total_news=len(sample_news),
                total_partnerships=len(sample_partnerships),
                total_industry_news=sum(len(v) for v in industry_news['industry_news'].values()),
                key_insights=json.dumps(industry_news, ensure_ascii=False),
                status='success'
            )
            session.add(today_report)
        else:
            today_report.total_updates = len(sample_updates)
            today_report.total_news = len(sample_news)
            today_report.total_partnerships = len(sample_partnerships)
            today_report.total_industry_news = sum(len(v) for v in industry_news['industry_news'].values())
            today_report.key_insights = json.dumps(industry_news, ensure_ascii=False)

        session.commit()
        print(f"  ✓ 已添加 {today_report.total_industry_news} 条行业情报")

        print("\n" + "="*60)
        print("✅ 示例数据生成完成！")
        print("="*60)
        print(f"\n统计：")
        print(f"  • App版本更新: {len(sample_updates)} 条")
        print(f"  • 公司动态: {len(sample_news)} 条")
        print(f"  • 合作信息: {len(sample_partnerships)} 条")
        print(f"  • 市场数据: {len(sample_market_data)} 条")
        print(f"  • 行业情报: {today_report.total_industry_news} 条")
        print(f"\n现在访问 http://192.168.22.4:5001 查看效果！\n")

    except Exception as e:
        session.rollback()
        print(f"\n❌ 生成数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    generate_sample_data()
