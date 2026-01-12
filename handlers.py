import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from storage import storage

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """检查用户是否是管理员"""
    return storage.admin_id is None or user_id == storage.admin_id


# ============ 管理命令 ============

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """开始命令 - 显示帮助"""
    help_text = """
🤖 *Telegram 转发 Bot*

*命令列表:*
/setadmin - 设置自己为管理员（仅首次）
/setsource - 设置源群组（在源群中发送）
/settarget - 设置目标群组（在目标群中发送）
/adduser @username - 添加监控用户
/removeuser @username - 移除监控用户
/listusers - 查看监控用户列表
/status - 查看当前配置
/help - 显示此帮助

*使用流程:*
1. 私聊发送 /setadmin 设置管理员
2. 在源群发送 /setsource
3. 在目标群发送 /settarget
4. 用 /adduser @xxx 添加要监控的用户
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cmd_setadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """设置管理员"""
    user_id = update.effective_user.id

    if storage.admin_id is None:
        storage.set_admin(user_id)
        await update.message.reply_text(f"✅ 已设置你为管理员\n你的 ID: `{user_id}`", parse_mode="Markdown")
    elif storage.admin_id == user_id:
        await update.message.reply_text("你已经是管理员了")
    else:
        await update.message.reply_text("❌ 管理员已存在")


async def cmd_setsource(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """设置源群组"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ 只有管理员可以使用此命令")
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ 请在群组中使用此命令")
        return

    storage.set_source_group(chat.id)
    await update.message.reply_text(
        f"✅ 已设置源群组\n"
        f"群组: {chat.title}\n"
        f"ID: `{chat.id}`",
        parse_mode="Markdown"
    )


async def cmd_settarget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """设置目标群组"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ 只有管理员可以使用此命令")
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ 请在群组中使用此命令")
        return

    storage.set_target_group(chat.id)
    await update.message.reply_text(
        f"✅ 已设置目标群组\n"
        f"群组: {chat.title}\n"
        f"ID: `{chat.id}`",
        parse_mode="Markdown"
    )


async def cmd_adduser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """添加监控用户"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ 只有管理员可以使用此命令")
        return

    if not context.args:
        await update.message.reply_text("用法: /adduser @username")
        return

    username = context.args[0].lstrip("@").lower()
    storage.add_user(username)
    await update.message.reply_text(f"✅ 已添加监控用户: @{username}")


async def cmd_removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """移除监控用户"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ 只有管理员可以使用此命令")
        return

    if not context.args:
        await update.message.reply_text("用法: /removeuser @username")
        return

    username = context.args[0].lstrip("@").lower()
    if storage.remove_user(username):
        await update.message.reply_text(f"✅ 已移除监控用户: @{username}")
    else:
        await update.message.reply_text(f"❌ 用户 @{username} 不在监控列表中")


async def cmd_listusers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """列出监控用户"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ 只有管理员可以使用此命令")
        return

    if not storage.monitored_usernames:
        await update.message.reply_text("监控列表为空")
        return

    users = "\n".join([f"• @{u}" for u in sorted(storage.monitored_usernames)])
    await update.message.reply_text(f"*监控用户列表:*\n{users}", parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """查看当前配置"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ 只有管理员可以使用此命令")
        return

    source = f"`{storage.source_group_id}`" if storage.source_group_id else "未设置"
    target = f"`{storage.target_group_id}`" if storage.target_group_id else "未设置"
    users = ", ".join([f"@{u}" for u in storage.monitored_usernames]) or "无"
    admin = f"`{storage.admin_id}`" if storage.admin_id else "未设置"

    status_text = f"""
*当前配置:*
• 管理员 ID: {admin}
• 源群组 ID: {source}
• 目标群组 ID: {target}
• 监控用户: {users}

*状态:* {"✅ 已配置完成" if storage.is_configured() else "⚠️ 配置不完整"}
"""
    await update.message.reply_text(status_text, parse_mode="Markdown")


# ============ 消息转发 ============

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理并转发来自监控用户的消息"""
    message = update.message
    if not message:
        return

    # 检查配置是否完整
    if not storage.is_configured():
        return

    # 检查是否来自源群组
    if message.chat.id != storage.source_group_id:
        return

    sender = message.from_user
    if not sender:
        return

    # 检查发送者是否在监控列表中
    username = sender.username
    if not username:
        return

    if username.lower() not in storage.monitored_usernames:
        return

    # 转发消息到目标群
    try:
        await message.forward(chat_id=storage.target_group_id)
        logger.info(f"已转发来自 @{username} 的消息")
    except TelegramError as e:
        logger.error(f"转发消息失败: {e}")
