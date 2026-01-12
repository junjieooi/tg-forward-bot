import logging
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType
import asyncio

from storage import storage

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """检查用户是否是管理员"""
    return storage.admin_id is None or user_id == storage.admin_id


def is_private_chat(message: Message) -> bool:
    """检查是否是私聊"""
    return message.chat.type == ChatType.PRIVATE


def register_handlers(app: Client):
    """注册所有处理器"""

    @app.on_message()
    async def handle_all_messages(client: Client, message: Message):
        """处理所有消息"""
        try:
            # 检查是否是命令
            if message.text and message.text.startswith("/"):
                await handle_command(client, message)
            else:
                await forward_message(client, message)
        except ValueError as e:
            # 忽略 Pyrogram 的 peer id 解析错误
            if "Peer id invalid" in str(e):
                pass
            else:
                logger.error(f"处理消息时出错: {e}")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")


async def handle_command(client: Client, message: Message):
    """处理命令"""
    text = message.text.strip()
    parts = text.split(maxsplit=1)
    command = parts[0].lower().split("@")[0]  # 移除 @botname
    args = parts[1] if len(parts) > 1 else ""

    user_id = message.from_user.id if message.from_user else 0

    # 只允许在私聊中执行管理命令（或管理员在任何地方）
    if not is_private_chat(message) and not is_admin(user_id):
        return

    if command == "/start" or command == "/help":
        await cmd_start(client, message)
    elif command == "/setadmin":
        await cmd_setadmin(client, message, user_id)
    elif command == "/setsource":
        await cmd_setsource(client, message, user_id)
    elif command == "/settarget":
        await cmd_settarget(client, message, user_id)
    elif command == "/adduser":
        await cmd_adduser(client, message, user_id, args)
    elif command == "/removeuser":
        await cmd_removeuser(client, message, user_id, args)
    elif command == "/listusers":
        await cmd_listusers(client, message, user_id)
    elif command == "/status":
        await cmd_status(client, message, user_id)
    elif command == "/pause":
        await cmd_pause(client, message, user_id)
    elif command == "/resume":
        await cmd_resume(client, message, user_id)


# ============ 管理命令 ============

async def cmd_start(client: Client, message: Message):
    """开始命令 - 显示帮助"""
    help_text = """
🤖 **Telegram 转发 Bot (用户模式)**

**命令列表:**
/setadmin - 设置自己为管理员（仅首次）
/setsource - 设置源群组（在源群中发送）
/settarget - 设置目标群组（在目标群中发送）
/adduser @username - 添加监控用户
/removeuser @username - 移除监控用户
/listusers - 查看监控用户列表
/status - 查看当前配置
/pause - 暂停转发
/resume - 恢复转发
/help - 显示此帮助

**使用流程:**
1. 私聊自己发送 /setadmin 设置管理员
2. 在源群发送 /setsource
3. 在目标群发送 /settarget
4. 用 /adduser @xxx 添加要监控的用户
"""
    await message.reply(help_text)


async def cmd_setadmin(client: Client, message: Message, user_id: int):
    """设置管理员"""
    if storage.admin_id is None:
        storage.set_admin(user_id)
        await message.reply(f"✅ 已设置你为管理员\n你的 ID: `{user_id}`")
    elif storage.admin_id == user_id:
        await message.reply("你已经是管理员了")
    else:
        await message.reply("❌ 管理员已存在")


async def cmd_setsource(client: Client, message: Message, user_id: int):
    """设置源群组"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    chat = message.chat
    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("❌ 请在群组中使用此命令")
        return

    storage.set_source_group(chat.id)
    await message.reply(
        f"✅ 已设置源群组\n"
        f"群组: {chat.title}\n"
        f"ID: `{chat.id}`"
    )


async def cmd_settarget(client: Client, message: Message, user_id: int):
    """设置目标群组"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    chat = message.chat
    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("❌ 请在群组中使用此命令")
        return

    storage.set_target_group(chat.id)
    await message.reply(
        f"✅ 已设置目标群组\n"
        f"群组: {chat.title}\n"
        f"ID: `{chat.id}`"
    )


async def cmd_adduser(client: Client, message: Message, user_id: int, args: str):
    """添加监控用户"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    if not args:
        await message.reply("用法: /adduser @username")
        return

    username = args.split()[0].lstrip("@").lower()
    storage.add_user(username)
    await message.reply(f"✅ 已添加监控用户: @{username}")


async def cmd_removeuser(client: Client, message: Message, user_id: int, args: str):
    """移除监控用户"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    if not args:
        await message.reply("用法: /removeuser @username")
        return

    username = args.split()[0].lstrip("@").lower()
    if storage.remove_user(username):
        await message.reply(f"✅ 已移除监控用户: @{username}")
    else:
        await message.reply(f"❌ 用户 @{username} 不在监控列表中")


async def cmd_listusers(client: Client, message: Message, user_id: int):
    """列出监控用户"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    if not storage.monitored_usernames:
        await message.reply("监控列表为空")
        return

    users = "\n".join([f"• @{u}" for u in sorted(storage.monitored_usernames)])
    await message.reply(f"**监控用户列表:**\n{users}")


async def cmd_status(client: Client, message: Message, user_id: int):
    """查看当前配置"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    source = f"`{storage.source_group_id}`" if storage.source_group_id else "未设置"
    target = f"`{storage.target_group_id}`" if storage.target_group_id else "未设置"
    users = ", ".join([f"@{u}" for u in storage.monitored_usernames]) or "无"
    admin = f"`{storage.admin_id}`" if storage.admin_id else "未设置"
    paused = "⏸️ 已暂停" if storage.is_paused else "▶️ 运行中"

    status_text = f"""
**当前配置:**
• 管理员 ID: {admin}
• 源群组 ID: {source}
• 目标群组 ID: {target}
• 监控用户: {users}
• 转发状态: {paused}

**状态:** {"✅ 已配置完成" if storage.is_configured() else "⚠️ 配置不完整"}
"""
    await message.reply(status_text)


async def cmd_pause(client: Client, message: Message, user_id: int):
    """暂停转发"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    if storage.is_paused:
        await message.reply("已经是暂停状态")
    else:
        storage.pause()
        await message.reply("⏸️ 已暂停转发")


async def cmd_resume(client: Client, message: Message, user_id: int):
    """恢复转发"""
    if not is_admin(user_id):
        await message.reply("❌ 只有管理员可以使用此命令")
        return

    if not storage.is_paused:
        await message.reply("已经在运行中")
    else:
        storage.resume()
        await message.reply("▶️ 已恢复转发")


# ============ 消息转发 ============

async def forward_message(client: Client, message: Message):
    """处理并转发来自监控用户的消息"""
    # 检查是否暂停
    if storage.is_paused:
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

    # 构建转发消息
    try:
        prefix = f"@{username}: "

        if message.text:
            # 纯文字消息
            await client.send_message(
                chat_id=storage.target_group_id,
                text=prefix + message.text
            )
        elif message.photo:
            # 图片
            caption = prefix + (message.caption or "")
            await client.send_photo(
                chat_id=storage.target_group_id,
                photo=message.photo.file_id,
                caption=caption
            )
        elif message.video:
            # 视频
            caption = prefix + (message.caption or "")
            await client.send_video(
                chat_id=storage.target_group_id,
                video=message.video.file_id,
                caption=caption
            )
        elif message.document:
            # 文件
            caption = prefix + (message.caption or "")
            await client.send_document(
                chat_id=storage.target_group_id,
                document=message.document.file_id,
                caption=caption
            )
        elif message.audio:
            # 音频
            caption = prefix + (message.caption or "")
            await client.send_audio(
                chat_id=storage.target_group_id,
                audio=message.audio.file_id,
                caption=caption
            )
        elif message.voice:
            # 语音
            await client.send_voice(
                chat_id=storage.target_group_id,
                voice=message.voice.file_id,
                caption=prefix
            )
        elif message.video_note:
            # 视频圈
            await client.send_message(
                chat_id=storage.target_group_id,
                text=prefix + "[视频圈]"
            )
            await client.send_video_note(
                chat_id=storage.target_group_id,
                video_note=message.video_note.file_id
            )
        elif message.sticker:
            # 贴纸
            await client.send_message(
                chat_id=storage.target_group_id,
                text=prefix + "[贴纸]"
            )
            await client.send_sticker(
                chat_id=storage.target_group_id,
                sticker=message.sticker.file_id
            )
        elif message.animation:
            # GIF
            caption = prefix + (message.caption or "")
            await client.send_animation(
                chat_id=storage.target_group_id,
                animation=message.animation.file_id,
                caption=caption
            )
        else:
            # 其他类型，尝试转发
            await message.forward(chat_id=storage.target_group_id)

        logger.info(f"已转发来自 @{username} 的消息")

    except FloodWait as e:
        logger.warning(f"触发限流，等待 {e.value} 秒")
        await asyncio.sleep(e.value)
    except Exception as e:
        logger.error(f"转发消息失败: {e}")
