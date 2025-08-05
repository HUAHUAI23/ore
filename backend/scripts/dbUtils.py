#!/usr/bin/env python3
"""
开发工具脚本
提供数据库管理和开发辅助功能 (同步版本)
"""

import sys

import click
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from backend.models.base import (
    create_all_tables_sync,
    drop_all_tables_sync,
    reset_database_sync,
    print_table_info,
    get_table_names,
    get_all_models,
)
from backend.core.config import settings


# ============================================
# 同步数据库引擎 (仅用于开发脚本)
# ============================================
def create_sync_engine():
    """创建同步数据库引擎，仅用于开发脚本"""
    # 将异步 URL 转换为同步 URL
    sync_url = settings.database_url

    # 如果是 asyncpg URL，转换为 psycopg2 URL
    if "postgresql+asyncpg://" in sync_url:
        sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
    elif "postgresql://" not in sync_url:
        # 如果既不是 asyncpg 也不是标准 postgresql URL，添加协议
        sync_url = f"postgresql://{sync_url}"
    return create_engine(
        sync_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=settings.database_echo,
    )


# 创建同步引擎实例
sync_engine = create_sync_engine()


# ============================================
# 数据库操作函数 (同步版本)
# ============================================
def drop_tables():
    """删除所有表"""
    try:
        click.echo("🗑️  开始删除所有数据库表...")
        drop_all_tables_sync(sync_engine)
        click.echo("✅ 所有表已成功删除")
        return True
    except SQLAlchemyError as e:
        click.echo(f"❌ 删除表时发生错误: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"❌ 删除表时发生未知错误: {e}", err=True)
        return False


def create_tables():
    """创建所有表"""
    try:
        click.echo("🏗️  开始创建所有数据库表...")
        create_all_tables_sync(sync_engine)
        click.echo("✅ 所有表已成功创建")
        return True
    except SQLAlchemyError as e:
        click.echo(f"❌ 创建表时发生错误: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"❌ 创建表时发生未知错误: {e}", err=True)
        return False


def reset_database():
    """重置数据库（删除后重建）"""
    try:
        click.echo("🔄 开始重置数据库...")
        reset_database_sync(sync_engine)
        click.echo("✅ 数据库重置完成")
        return True
    except SQLAlchemyError as e:
        click.echo(f"❌ 重置数据库时发生错误: {e}", err=True)
        return False
    except Exception as e:
        click.echo(f"❌ 重置数据库时发生未知错误: {e}", err=True)
        return False


def test_connection():
    """测试数据库连接"""
    try:
        click.echo("🔌 正在测试数据库连接...")
        with sync_engine.begin() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        click.echo("✅ 数据库连接正常")
        return True
    except Exception as e:
        click.echo(f"❌ 数据库连接失败: {e}", err=True)
        return False


# ============================================
# Click 命令定义
# ============================================
@click.group()
def cli():
    """Ore 项目开发工具 🛠️"""
    click.echo(f"🚀 {settings.app_name} 开发工具")
    click.echo(
        f"📊 数据库: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'Local'}"
    )


@cli.command()
@click.option("--confirm", is_flag=True, help="跳过确认提示")
def drop_tables_cmd(confirm):
    """删除所有数据库表 ⚠️"""
    if not confirm:
        click.echo("⚠️  警告: 此操作将删除所有数据库表和数据!")
        if not click.confirm("你确定要继续吗?"):
            click.echo("🚫 操作已取消")
            return

    success = drop_tables()
    if success:
        click.echo("🎉 表删除操作完成")
    else:
        sys.exit(1)


@cli.command()
def create_tables_cmd():
    """创建所有数据库表 🏗️"""
    success = create_tables()
    if success:
        click.echo("🎉 表创建操作完成")
        # 显示创建的表信息
        tables = get_table_names()
        click.echo(f"📋 已创建 {len(tables)} 个表: {', '.join(tables)}")
    else:
        sys.exit(1)


@cli.command()
@click.option("--confirm", is_flag=True, help="跳过确认提示")
def reset_db(confirm):
    """重置数据库（删除后重建所有表） 🔄"""
    if not confirm:
        click.echo("⚠️  警告: 此操作将删除所有数据库表和数据，然后重新创建!")
        if not click.confirm("你确定要继续吗?"):
            click.echo("🚫 操作已取消")
            return

    success = reset_database()
    if success:
        click.echo("🎉 数据库重置完成")
        # 显示重置后的表信息
        tables = get_table_names()
        click.echo(f"📋 重建了 {len(tables)} 个表: {', '.join(tables)}")
    else:
        sys.exit(1)


@cli.command()
def show_tables():
    """显示所有表信息 📋"""
    click.echo("📊 数据库表信息:")
    try:
        print_table_info()

        tables = get_table_names()
        models = get_all_models()

        click.echo(f"\n📈 统计信息:")
        click.echo(f"  🗂️  表数量: {len(tables)}")
        click.echo(f"  📄 模型数量: {len(models)}")
        click.echo(f"  📋 表名列表: {', '.join(tables)}")

    except Exception as e:
        click.echo(f"❌ 获取表信息时发生错误: {e}", err=True)


@cli.command()
def check_connection():
    """检查数据库连接 🔌"""
    success = test_connection()
    if not success:
        sys.exit(1)


@cli.command()
def show_config():
    """显示数据库配置信息 ⚙️"""
    click.echo("⚙️  数据库配置信息:")
    click.echo(f"  🌐 数据库类型: PostgreSQL")
    click.echo(f"  🔗 连接池大小: {settings.database_pool_size}")
    click.echo(f"📊 最大溢出: {settings.database_max_overflow}")
    click.echo(f"  📝 SQL回显: {settings.database_echo}")

    # 隐藏敏感信息的数据库URL
    db_url = settings.database_url
    if "@" in db_url:
        parts = db_url.split("@")
        masked_url = f"{parts[0].split('//')[0]}//*****@{parts[1]}"
    else:
        masked_url = db_url
    click.echo(f"  📍 数据库地址: {masked_url}")


# ============================================
# 便捷命令组合
# ============================================
@cli.command()
@click.option("--confirm", is_flag=True, help="跳过确认提示")
def quick_reset(confirm):
    """快速重置: 检查连接 → 重置数据库 → 显示表信息 ⚡"""
    if not confirm:
        click.echo("⚡ 快速重置将执行以下操作:")
        click.echo("  1️⃣  检查数据库连接")
        click.echo("  2️⃣  删除所有表")
        click.echo("  3️⃣  重新创建所有表")
        click.echo("  4️⃣  显示表信息")
        if not click.confirm("\n确定要继续吗?"):
            click.echo("🚫 操作已取消")
            return

    click.echo("⚡ 开始快速重置...")

    # 1. 检查连接
    if not test_connection():
        sys.exit(1)

    # 2. 重置数据库
    if not reset_database():
        sys.exit(1)

    # 3. 显示表信息
    try:
        tables = get_table_names()
        click.echo(f"\n🎉 快速重置完成! 重建了 {len(tables)} 个表")
        print_table_info()
    except Exception as e:
        click.echo(f"⚠️  重置完成，但显示表信息时出错: {e}")


# TODO: 初始化开发环境 换成 alembic upgrade head
# @cli.command()
# def init_dev():
#     """初始化开发环境: 检查连接 → 创建表 🚀"""
#     click.echo("🚀 初始化开发环境...")

#     # 1. 检查连接
#     if not test_connection():
#         sys.exit(1)

#     # 2. 创建表
#     if not create_tables():
#         sys.exit(1)

#     # 3. 显示结果
#     try:
#         tables = get_table_names()
#         click.echo(f"\n🎉 开发环境初始化完成! 创建了 {len(tables)} 个表")
#         print_table_info()
#     except Exception as e:
#         click.echo(f"⚠️  初始化完成，但显示表信息时出错: {e}")


if __name__ == "__main__":
    cli()
