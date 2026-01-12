import logging
from telegram.ext import Application, MessageHandler, CommandHandler, filters

from config import Config
from handlers import (
    cmd_start,
    cmd_setadmin,
    cmd_setsource,
    cmd_settarget,
    cmd_adduser,
    cmd_removeuser,
    cmd_listusers,
    cmd_status,
    forward_message,
)

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

    # 创建 Application
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # 注册命令处理器
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_start))
    application.add_handler(CommandHandler("setadmin", cmd_setadmin))
    application.add_handler(CommandHandler("setsource", cmd_setsource))
    application.add_handler(CommandHandler("settarget", cmd_settarget))
    application.add_handler(CommandHandler("adduser", cmd_adduser))
    application.add_handler(CommandHandler("removeuser", cmd_removeuser))
    application.add_handler(CommandHandler("listusers", cmd_listusers))
    application.add_handler(CommandHandler("status", cmd_status))

    # 添加消息转发处理器（处理所有非命令消息）
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, forward_message)
    )

    # 启动 Bot
    logger.info("Bot 启动中...")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
