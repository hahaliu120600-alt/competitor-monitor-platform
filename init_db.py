import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from models.database import init_database, get_session, Competitor
from datetime import datetime

def init_competitors():
    """初始化竞品数据"""
    session = get_session()
    try:
        # 检查是否已有数据
        existing_count = session.query(Competitor).count()
        if existing_count > 0:
            print(f"数据库已有 {existing_count} 个竞品，跳过初始化")
            return

        # 插入竞品数据
        for comp_data in config.COMPETITORS:
            competitor = Competitor(
                name_en=comp_data['name_en'],
                name_cn=comp_data['name_cn'],
                category=comp_data['category'],
                platforms=comp_data['platforms'],
                official_site=comp_data.get('official_site', ''),
                search_keywords=comp_data['search_keywords'],
                is_active=comp_data.get('is_active', True)
            )
            session.add(competitor)

        session.commit()
        print(f"成功初始化 {len(config.COMPETITORS)} 个竞品数据！")

        # 显示初始化结果
        competitors = session.query(Competitor).all()
        print("\n竞品列表：")
        for comp in competitors:
            status = "✓" if comp.is_active else "✗"
            print(f"  [{status}] {comp.id}. {comp.name_cn} ({comp.name_en}) - {comp.category}")

    except Exception as e:
        session.rollback()
        print(f"初始化竞品数据失败: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    print("开始初始化数据库...")
    init_database()
    print("\n开始初始化竞品数据...")
    init_competitors()
    print("\n数据库初始化完成！")
