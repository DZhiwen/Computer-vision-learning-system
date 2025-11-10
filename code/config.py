"""
配置管理模块 - Configuration Manager
统一管理应用程序配置
"""
import json
import os
from db_manager import get_user_data_dir

class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "language": "ru",  # 默认俄语
        "theme": "light",  # 主题：light/dark
        "font_size": 10,
        "auto_save": True,
        "show_hints": True,
        "animation_enabled": True,
        "last_chapter": 0,
        "window_size": {"width": 972, "height": 636}
    }
    
    def __init__(self):
        self.config_dir = get_user_data_dir()
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                print(f"配置加载失败: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        self.save_config()
    
    def reset(self):
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()