#!/usr/bin/env python3
"""
命令行启动脚本
提供灵活的服务器启动选项
"""
import click
import uvicorn
import sys
import os


from backend.core.config import settings


@click.command()
@click.option("--host", default="0.0.0.0", help="绑定的主机地址")
@click.option("--port", default=8000, type=int, help="绑定的端口号")
@click.option("--reload", is_flag=True, help="启用自动重载（开发模式）")
@click.option("--workers", default=1, type=int, help="工作进程数（生产模式）")
@click.option(
    "--log-level",
    type=click.Choice(["critical", "error", "warning", "info", "debug"]),
    default="info",
    help="日志级别",
)
@click.option(
    "--env",
    default="production",
    type=click.Choice(["development", "production", "testing"]),
    help="运行环境",
)
def start_server(host, port, reload, workers, log_level, env):
    """
    启动 FastAPI 服务器
    """
    click.echo(f"🚀 启动 {settings.app_name} v{settings.app_version}")
    click.echo(f"📍 环境: {env}")
    click.echo(f"🌐 地址: http://{host}:{port}")
    click.echo(f"📊 日志级别: {log_level}")

    if reload:
        click.echo("🔄 开发模式 - 启用自动重载")
        workers = 1
    else:
        click.echo(f"⚡ 生产模式 - {workers} 个工作进程")

    os.environ["ENVIRONMENT"] = env

    try:
        uvicorn.run(
            # 使用新的模块路径
            "backend.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level=log_level,
            access_log=True,
            loop="auto",
            http="auto",
        )
    except KeyboardInterrupt:
        click.echo("\n👋 服务器已停止")
    except Exception as e:
        click.echo(f"❌ 启动失败: {e}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """Ore 项目命令行工具"""
    pass


# 将 start_server 添加到 cli 组中
cli.add_command(start_server)

if __name__ == "__main__":
    cli()
