import os
import sys
import logging
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from models import get_session, Competitor, DailyReport
from collectors import (
    AppUpdateCollector,
    CompanyNewsCollector,
    PartnershipCollector,
    MarketDataCollector,
    IndustryNewsCollector
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建采集器实例
app_update_collector = AppUpdateCollector()
company_news_collector = CompanyNewsCollector()
partnership_collector = PartnershipCollector()
market_data_collector = MarketDataCollector()
industry_news_collector = IndustryNewsCollector()


def run_daily_collection():
    """执行每日数据采集"""
    logger.info("=" * 60)
    logger.info(f"开始每日数据采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    session = get_session()
    total_updates = 0
    total_news = 0
    total_partnerships = 0
    total_industry_news = 0
    errors = []

    try:
        # 获取所有活跃竞品
        competitors = session.query(Competitor).filter_by(is_active=True).all()
        logger.info(f"共有 {len(competitors)} 个活跃竞品需要监测")

        for competitor in competitors:
            logger.info(f"\n--- 开始采集: {competitor.name_cn} ({competitor.name_en}) ---")

            try:
                # 1. 采集App更新信息
                logger.info(f"[1/3] 采集App更新...")
                updates = app_update_collector.collect(competitor)
                total_updates += len(updates)

                # 2. 采集公司动态
                logger.info(f"[2/3] 采集公司动态...")
                news = company_news_collector.collect(competitor)
                total_news += len(news)

                # 3. 采集合作动态（降低频率，避免过多请求）
                # 仅在周一、周三、周五采集
                if datetime.now().weekday() in [0, 2, 4]:
                    logger.info(f"[3/3] 采集合作动态...")
                    partnerships = partnership_collector.collect(competitor)
                    total_partnerships += len(partnerships)
                else:
                    logger.info(f"[3/3] 跳过合作动态采集（非采集日）")

                logger.info(f"✓ {competitor.name_cn} 采集完成")

            except Exception as e:
                error_msg = f"{competitor.name_cn} 采集失败: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        # 采集ToB行业情报（每天执行）
        logger.info("\n--- 开始采集ToB行业情报 ---")
        try:
            all_industry_news = industry_news_collector.collect_all_industries()

            # 合并所有行业新闻
            all_items = []
            for industry_key, news_list in all_industry_news.items():
                all_items.extend(news_list)

            # 保存到数据库
            saved = industry_news_collector.save_industry_news(all_items)
            total_industry_news = saved
            logger.info(f"✓ ToB行业情报采集完成，保存 {saved} 条")
        except Exception as e:
            error_msg = f"ToB行业情报采集失败: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

        # 创建每日报告
        daily_report = DailyReport(
            report_date=date.today(),
            total_updates=total_updates,
            total_news=total_news,
            total_partnerships=total_partnerships,
            total_industry_news=total_industry_news,
            key_insights="",  # 后续可添加AI生成的洞察
            status='success' if not errors else 'partial',
            error_log='\n'.join(errors) if errors else None
        )

        session.add(daily_report)
        session.commit()

        logger.info("=" * 60)
        logger.info("每日数据采集完成！")
        logger.info(f"  App更新: {total_updates} 条")
        logger.info(f"  公司动态: {total_news} 条")
        logger.info(f"  合作信息: {total_partnerships} 条")
        logger.info(f"  行业情报: {total_industry_news} 条")
        if errors:
            logger.warning(f"  错误数: {len(errors)}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"每日采集任务失败: {e}")
    finally:
        session.close()


def generate_weekly_report():
    """生成周报"""
    logger.info("=" * 60)
    logger.info(f"开始生成周报 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        from services.report_generator import ReportGenerator

        generator = ReportGenerator()
        report_path = generator.generate_weekly_report()

        if report_path:
            logger.info(f"✓ 周报生成成功: {report_path}")
        else:
            logger.error("周报生成失败")

    except Exception as e:
        logger.error(f"周报生成失败: {e}")

    logger.info("=" * 60)


def backup_database():
    """备份数据库"""
    logger.info(f"开始备份数据库 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        import shutil

        backup_filename = f"competitors_backup_{datetime.now().strftime('%Y%m%d')}.db"
        backup_path = os.path.join(config.BACKUP_DIR, backup_filename)

        shutil.copy2(config.DATABASE_PATH, backup_path)

        logger.info(f"✓ 数据库备份成功: {backup_path}")

        # 清理30天前的备份
        import glob
        backups = glob.glob(os.path.join(config.BACKUP_DIR, '*.db'))
        for backup in backups:
            file_date = datetime.fromtimestamp(os.path.getmtime(backup))
            if (datetime.now() - file_date).days > 30:
                os.remove(backup)
                logger.info(f"清理旧备份: {backup}")

    except Exception as e:
        logger.error(f"数据库备份失败: {e}")


# 创建调度器
scheduler = BackgroundScheduler(timezone=config.TIMEZONE)


def start_scheduler():
    """启动调度器"""
    logger.info("正在启动定时任务调度器...")

    # 每日数据采集（凌晨2点）
    scheduler.add_job(
        func=run_daily_collection,
        trigger=CronTrigger(**config.DAILY_COLLECTION_TIME),
        id='daily_collection',
        name='每日数据采集',
        replace_existing=True
    )
    logger.info(f"✓ 已添加任务：每日数据采集 (每天 {config.DAILY_COLLECTION_TIME['hour']}:{config.DAILY_COLLECTION_TIME['minute']:02d})")

    # 每周生成周报（周五17点）
    scheduler.add_job(
        func=generate_weekly_report,
        trigger=CronTrigger(**config.WEEKLY_REPORT_TIME),
        id='weekly_report',
        name='生成周报',
        replace_existing=True
    )
    logger.info(f"✓ 已添加任务：生成周报 (每周五 {config.WEEKLY_REPORT_TIME['hour']}:{config.WEEKLY_REPORT_TIME['minute']:02d})")

    # 每周备份数据库（周日凌晨3点）
    scheduler.add_job(
        func=backup_database,
        trigger=CronTrigger(**config.BACKUP_TIME),
        id='weekly_backup',
        name='数据库备份',
        replace_existing=True
    )
    logger.info(f"✓ 已添加任务：数据库备份 (每周日 {config.BACKUP_TIME['hour']}:{config.BACKUP_TIME['minute']:02d})")

    # 启动调度器
    scheduler.start()
    logger.info("✓ 定时任务调度器已启动")

    # 打印所有任务
    logger.info("\n当前调度任务列表:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} (ID: {job.id}), 下次执行: {job.next_run_time}")


def stop_scheduler():
    """停止调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已停止")


if __name__ == '__main__':
    # 测试运行
    print("测试运行数据采集...")
    run_daily_collection()
