import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import Config

logger = logging.getLogger(__name__)


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理并转发来自监控用户的消息"""
    message = update.message
    if not message:
        return

    sender = message.from_user
    if not sender:
        return

    # 检查发送者是否在监控列表中
    username = sender.username
    if not username:
        return

    if username.lower() not in Config.MONITORED_USERNAMES:
        return

    # 转发消息到目标群
    try:
        await message.forward(chat_id=Config.TARGET_GROUP_ID)
        logger.info(f"已转发来自 @{username} 的消息")
    except TelegramError as e:
        logger.error(f"转发消息失败: {e}")


async def log_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """记录聊天 ID，用于配置时获取群组 ID"""
    message = update.message
    if message and message.chat:
        logger.info(f"收到消息 - 聊天ID: {message.chat.id}, 聊天标题: {message.chat.title or '私聊'}")
