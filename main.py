import logging
from telegram.ext import Application, MessageHandler, filters

from config import Config
from handlers import forward_message, log_chat_id

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """启动 Bot"""
    # 验证配置
    if not Config.validate():
        return

    logger.info(f"监控用户: {Config.MONITORED_USERNAMES}")
    logger.info(f"源群组 ID: {Config.SOURCE_GROUP_ID}")
    logger.info(f"目标群组 ID: {Config.TARGET_GROUP_ID}")

    # 创建 Application
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # 添加消息处理器 - 只处理源群组的消息
    application.add_handler(
        MessageHandler(
            filters.Chat(Config.SOURCE_GROUP_ID) & ~filters.COMMAND,
            forward_message
        )
    )

    # 添加日志处理器 - 记录所有聊天的 ID（用于配置时获取群组 ID）
    application.add_handler(
        MessageHandler(filters.ALL, log_chat_id),
        group=1  # 放在第二组，不影响主处理器
    )

    # 启动 Bot
    logger.info("Bot 启动中...")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
