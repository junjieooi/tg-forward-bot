import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.BOT_TOKEN:
            print("错误: 请在 .env 文件中设置 BOT_TOKEN")
            return False
        return True
