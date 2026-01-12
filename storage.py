import json
import os
from typing import Set, Optional

CONFIG_FILE = "bot_config.json"


class Storage:
    """持久化存储配置"""

    def __init__(self):
        self.source_group_id: Optional[int] = None
        self.target_group_id: Optional[int] = None
        self.monitored_usernames: Set[str] = set()
        self.admin_id: Optional[int] = None
        self._load()

    def _load(self):
        """从 JSON 文件加载配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.source_group_id = data.get("source_group_id")
                    self.target_group_id = data.get("target_group_id")
                    self.monitored_usernames = set(data.get("monitored_usernames", []))
                    self.admin_id = data.get("admin_id")
            except Exception:
                pass

    def _save(self):
        """保存配置到 JSON 文件"""
        data = {
            "source_group_id": self.source_group_id,
            "target_group_id": self.target_group_id,
            "monitored_usernames": list(self.monitored_usernames),
            "admin_id": self.admin_id,
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def set_source_group(self, group_id: int):
        self.source_group_id = group_id
        self._save()

    def set_target_group(self, group_id: int):
        self.target_group_id = group_id
        self._save()

    def set_admin(self, user_id: int):
        self.admin_id = user_id
        self._save()

    def add_user(self, username: str):
        self.monitored_usernames.add(username.lower().lstrip("@"))
        self._save()

    def remove_user(self, username: str) -> bool:
        username = username.lower().lstrip("@")
        if username in self.monitored_usernames:
            self.monitored_usernames.remove(username)
            self._save()
            return True
        return False

    def is_configured(self) -> bool:
        return bool(self.source_group_id and self.target_group_id and self.monitored_usernames)


# 全局存储实例
storage = Storage()
