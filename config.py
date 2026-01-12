import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    SOURCE_GROUP_ID: int = int(os.getenv("SOURCE_GROUP_ID", "0"))
    TARGET_GROUP_ID: int = int(os.getenv("TARGET_GROUP_ID", "0"))

    # 解析监控的用户名列表，转为小写集合
    _usernames = os.getenv("MONITORED_USERNAMES", "")
    MONITORED_USERNAMES: set = {
        name.strip().lower()
        for name in _usernames.split(",")
        if name.strip()
    }

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.BOT_TOKEN:
            print("错误: 请设置 BOT_TOKEN")
            return False
        if not cls.SOURCE_GROUP_ID:
            print("错误: 请设置 SOURCE_GROUP_ID")
            return False
        if not cls.TARGET_GROUP_ID:
            print("错误: 请设置 TARGET_GROUP_ID")
            return False
        if not cls.MONITORED_USERNAMES:
            print("错误: 请设置 MONITORED_USERNAMES")
            return False
        return True
