"""
多语言支持模块 - Language Manager
支持俄语、英语、中文切换
"""
import json
import os

class LanguageManager:
    """语言管理器"""
    
    LANGUAGES = {
        "ru": "Русский",
        "en": "English",
        "zh": "中文"
    }
    
    # 内置翻译字典
    TRANSLATIONS = {
        "ru": {
            "login": "Вход",
            "register": "Регистрация",
            "username": "Имя пользователя",
            "password": "Пароль",
            "logout": "Выход",
            "next_page": "Следующая страница",
            "next_chapter": "Следующая глава",
            "submit": "Отправить",
            "progress": "Прогресс",
            "settings": "Настройки",
            "language": "Язык",
            "theme": "Тема",
            "about": "О программе"
        },
        "en": {
            "login": "Login",
            "register": "Register",
            "username": "Username",
            "password": "Password",
            "logout": "Logout",
            "next_page": "Next Page",
            "next_chapter": "Next Chapter",
            "submit": "Submit",
            "progress": "Progress",
            "settings": "Settings",
            "language": "Language",
            "theme": "Theme",
            "about": "About"
        },
        "zh": {
            "login": "登录",
            "register": "注册",
            "username": "用户名",
            "password": "密码",
            "logout": "登出",
            "next_page": "下一页",
            "next_chapter": "下一章",
            "submit": "提交",
            "progress": "进度",
            "settings": "设置",
            "language": "语言",
            "theme": "主题",
            "about": "关于"
        }
    }
    
    def __init__(self, language="ru"):
        self.current_language = language
    
    def set_language(self, lang_code):
        """设置当前语言"""
        if lang_code in self.LANGUAGES:
            self.current_language = lang_code
            return True
        return False
    
    def get_text(self, key):
        """获取翻译文本"""
        return self.TRANSLATIONS.get(
            self.current_language, {}
        ).get(key, key)
    
    def get_all_texts(self):
        """获取当前语言的所有翻译"""
        return self.TRANSLATIONS.get(self.current_language, {})
    
    @classmethod
    def get_available_languages(cls):
        """获取可用语言列表"""
        return cls.LANGUAGES