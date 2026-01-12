import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    PHONE_NUMBER: str = os.getenv("PHONE_NUMBER", "")

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.API_ID:
            print("错误: 请在 .env 文件中设置 API_ID")
            return False
        if not cls.API_HASH:
            print("错误: 请在 .env 文件中设置 API_HASH")
            return False
        return True
