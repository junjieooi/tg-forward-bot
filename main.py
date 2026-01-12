import logging
from pyrogram import Client

from config import Config
from handlers import register_handlers

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """启动客户端"""
    # 验证配置
    if not Config.validate():
        return

    # 创建 Pyrogram 客户端（用户模式）
    app = Client(
        name="forwarder_session",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        phone_number=Config.PHONE_NUMBER if Config.PHONE_NUMBER else None,
        workdir="."
    )

    # 注册处理器
    register_handlers(app)

    # 启动客户端
    logger.info("正在启动客户端...")
    logger.info("首次运行需要输入验证码")
    app.run()


if __name__ == "__main__":
    main()
