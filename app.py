import os
import sys
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from scheduler import start_scheduler, run_daily_collection, generate_weekly_report
from services import ReportGenerator, AnalysisService
from models import get_session, Competitor

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(config)
CORS(app)

# 创建服务实例
analysis_service = AnalysisService()
report_generator = ReportGenerator()


# ========== 路由定义 ==========

@app.route('/')
def index():
    """首页 - Dashboard"""
    return render_template('index.html')


@app.route('/industry/all')
def industry_all():
    """ToB行业监测页面 - 全部"""
    return render_template('industry.html')


@app.route('/industry/<industry_key>')
def industry_detail_page(industry_key):
    """ToB行业监测页面 - 单个行业"""
    return render_template('industry.html', industry=industry_key)


@app.route('/competitors')
def competitors_page():
    """竞品列表页"""
    return render_template('competitors.html')


@app.route('/competitor/<int:competitor_id>')
def competitor_detail(competitor_id):
    """竞品详情页"""
    return render_template('competitor_detail.html', competitor_id=competitor_id)


@app.route('/trends')
def trends_page():
    """趋势分析页"""
    return render_template('trends.html')


@app.route('/reports')
def reports_page():
    """历史报告页"""
    return render_template('reports.html')


@app.route('/settings')
def settings_page():
    """设置页"""
    return render_template('settings.html')


# ========== API接口 ==========

@app.route('/api/dashboard/summary')
def api_dashboard_summary():
    """获取Dashboard汇总数据"""
    try:
        summary = analysis_service.get_dashboard_summary()
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        logger.error(f"获取Dashboard数据失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/activities/recent')
def api_recent_activities():
    """获取最近活动"""
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 20, type=int)

    try:
        activities = analysis_service.get_recent_activities(days, limit)
        return jsonify({'success': True, 'data': activities})
    except Exception as e:
        logger.error(f"获取最近活动失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/competitors')
def api_competitors_list():
    """获取竞品列表"""
    try:
        comparison_data = analysis_service.get_competitor_comparison()
        return jsonify({'success': True, 'data': comparison_data})
    except Exception as e:
        logger.error(f"获取竞品列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/competitors/<int:competitor_id>')
def api_competitor_detail(competitor_id):
    """获取竞品详情"""
    try:
        session = get_session()
        competitor = session.query(Competitor).get(competitor_id)

        if not competitor:
            return jsonify({'success': False, 'error': '竞品不存在'}), 404

        data = {
            'id': competitor.id,
            'name_cn': competitor.name_cn,
            'name_en': competitor.name_en,
            'category': competitor.category,
            'platforms': competitor.platforms,
            'official_site': competitor.official_site,
            'is_active': competitor.is_active
        }

        session.close()
        return jsonify({'success': True, 'data': data})

    except Exception as e:
        logger.error(f"获取竞品详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/competitors/<int:competitor_id>/updates')
def api_competitor_updates(competitor_id):
    """获取竞品更新历史"""
    try:
        from models import AppUpdate
        session = get_session()

        updates = session.query(AppUpdate).filter_by(
            competitor_id=competitor_id
        ).order_by(AppUpdate.release_date.desc()).limit(20).all()

        data = [{
            'id': u.id,
            'version': u.version,
            'release_date': u.release_date.strftime('%Y-%m-%d') if u.release_date else None,
            'platform': u.platform,
            'highlight': u.highlight,
            'source_url': u.source_url
        } for u in updates]

        session.close()
        return jsonify({'success': True, 'data': data})

    except Exception as e:
        logger.error(f"获取更新历史失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/competitors/<int:competitor_id>/trend')
def api_competitor_trend(competitor_id):
    """获取竞品趋势数据"""
    metric = request.args.get('metric', 'rating')
    days = request.args.get('days', 30, type=int)

    try:
        trend_data = analysis_service.get_trend_data(competitor_id, metric, days)
        return jsonify({'success': True, 'data': trend_data})
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/collection/trigger', methods=['POST'])
def api_trigger_collection():
    """手动触发数据采集"""
    try:
        logger.info("手动触发数据采集...")
        # 在后台线程中运行
        import threading
        thread = threading.Thread(target=run_daily_collection)
        thread.start()

        return jsonify({'success': True, 'message': '数据采集已启动，请稍后查看结果'})
    except Exception as e:
        logger.error(f"触发采集失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    """生成周报"""
    try:
        logger.info("手动生成周报...")
        report_path = report_generator.generate_weekly_report()

        if report_path:
            return jsonify({
                'success': True,
                'message': '周报生成成功',
                'path': report_path
            })
        else:
            return jsonify({'success': False, 'error': '周报生成失败'}), 500

    except Exception as e:
        logger.error(f"生成周报失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports/list')
def api_reports_list():
    """获取报告列表"""
    try:
        import glob
        reports = glob.glob(os.path.join(config.WEEKLY_REPORT_DIR, '*.md'))
        reports.sort(reverse=True)

        data = []
        for report_path in reports[:20]:  # 最多返回20个
            filename = os.path.basename(report_path)
            file_stat = os.stat(report_path)

            data.append({
                'filename': filename,
                'path': report_path,
                'size': file_stat.st_size,
                'created_at': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M')
            })

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        logger.error(f"获取报告列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health')
def api_health():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'running',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/industry/<industry_key>/summary')
def api_industry_summary(industry_key):
    """获取行业摘要"""
    try:
        from models import DailyReport
        import json

        session = get_session()
        latest_report = session.query(DailyReport).order_by(
            DailyReport.report_date.desc()
        ).first()

        if not latest_report or not latest_report.key_insights:
            return jsonify({
                'success': True,
                'data': {
                    'news_count': 0,
                    'policy_count': 0,
                    'competitor_count': 0
                }
            })

        insights = json.loads(latest_report.key_insights)
        industry_news = insights.get('industry_news', {}).get(industry_key, [])

        # 统计各类别数量
        news_count = sum(1 for item in industry_news if item['category'] == 'news')
        policy_count = sum(1 for item in industry_news if item['category'] == 'policy')
        competitor_count = sum(1 for item in industry_news if item['category'] == 'competitor')

        session.close()

        return jsonify({
            'success': True,
            'data': {
                'news_count': news_count,
                'policy_count': policy_count,
                'competitor_count': competitor_count,
                'total': len(industry_news)
            }
        })

    except Exception as e:
        logger.error(f"获取行业摘要失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/industry/<industry_key>/news')
def api_industry_news(industry_key):
    """获取行业新闻列表"""
    try:
        from models import DailyReport
        import json

        session = get_session()
        latest_report = session.query(DailyReport).order_by(
            DailyReport.report_date.desc()
        ).first()

        if not latest_report or not latest_report.key_insights:
            return jsonify({'success': True, 'data': []})

        insights = json.loads(latest_report.key_insights)
        industry_news = insights.get('industry_news', {}).get(industry_key, [])

        session.close()

        return jsonify({'success': True, 'data': industry_news})

    except Exception as e:
        logger.error(f"获取行业新闻失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/industry/collect', methods=['POST'])
def api_industry_collect():
    """手动触发行业情报采集"""
    try:
        logger.info("手动触发行业情报采集...")

        # 在后台线程中运行
        import threading
        from collectors import IndustryNewsCollector

        def collect_task():
            collector = IndustryNewsCollector()
            all_news = collector.collect_all_industries()

            # 合并所有行业新闻
            all_items = []
            for industry_key, news_list in all_news.items():
                all_items.extend(news_list)

            # 保存到数据库
            saved = collector.save_industry_news(all_items)
            logger.info(f"行业情报采集完成，保存 {saved} 条")

        thread = threading.Thread(target=collect_task)
        thread.start()

        return jsonify({
            'success': True,
            'message': '行业情报采集已启动，预计需要1-2分钟完成'
        })

    except Exception as e:
        logger.error(f"触发行业采集失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health')
def api_health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'running',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


# ========== 错误处理 ==========

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': '页面不存在'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


# ========== 主函数 ==========

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("竞品监测平台启动中...")
    logger.info("=" * 60)

    # 启动定时任务调度器
    start_scheduler()

    logger.info(f"\n✓ 服务地址: http://{config.HOST}:{config.PORT}")
    logger.info("✓ 按 Ctrl+C 停止服务\n")

    # 启动Flask应用
    try:
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            use_reloader=False  # 避免调度器重复启动
        )
    except KeyboardInterrupt:
        logger.info("\n正在停止服务...")
        from scheduler import stop_scheduler
        stop_scheduler()
        logger.info("服务已停止")
