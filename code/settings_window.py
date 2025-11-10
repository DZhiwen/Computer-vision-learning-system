"""
设置窗口 - Settings Window (优化版 v3)
用户偏好设置界面
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGroupBox, QCheckBox,
    QSlider, QMessageBox, QSpinBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
import json
import os
import sys

def get_user_data_dir():
    """获取用户数据目录"""
    if sys.platform == 'win32':
        app_data = os.path.join(os.environ['LOCALAPPDATA'], 'ComputerVisionLearning')
    else:
        app_data = os.path.expanduser('~/.local/share/ComputerVisionLearning')
    
    if not os.path.exists(app_data):
        os.makedirs(app_data)
    
    return app_data


class AIWebDialog(QDialog):
    """AI助手网页对话框"""
    
    def __init__(self, url, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1000, 700)
        
        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部工具栏
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                padding: 8px;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QLabel {
                color: white;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        
        # URL标签
        url_label = QLabel(f"🌐 {url}")
        toolbar_layout.addWidget(url_label)
        toolbar_layout.addStretch()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_page)
        toolbar_layout.addWidget(refresh_btn)
        
        # 关闭按钮
        close_btn = QPushButton("✖ 关闭")
        close_btn.clicked.connect(self.close)
        toolbar_layout.addWidget(close_btn)
        
        layout.addWidget(toolbar)
        
        # WebView
        self.web_view = QWebEngineView()
        self.web_view.setUrl(url)
        layout.addWidget(self.web_view)
    
    def refresh_page(self):
        """刷新页面"""
        self.web_view.reload()


class SettingsManager:
    """设置管理器 - 使用JSON文件存储配置"""
    
    DEFAULT_CONFIG = {
        "language": "ru",
        "theme": "light",
        "font_size": 10,
        "auto_save": True,
        "show_hints": True,
        "animation_enabled": True,
        "window_size": {"width": 972, "height": 636},
        "sound_enabled": True,
        "notification_enabled": True,
        "ai_assistant": "deepseek"
    }
    
    # 语言翻译字典
    TRANSLATIONS = {
        "ru": {
            "settings": "Настройки",
            "language": "Язык",
            "display": "Отображение",
            "study": "Обучение",
            "ai_assistant": "AI Помощник",
            "font_size": "Размер шрифта",
            "theme": "Тема",
            "light": "Светлая",
            "dark": "Тёмная",
            "auto_save": "Автосохранение",
            "show_hints": "Показывать подсказки",
            "animation": "Анимация",
            "sound": "Звук",
            "notifications": "Уведомления",
            "save": "Сохранить",
            "cancel": "Отмена",
            "reset": "Сбросить",
            "success": "Успешно",
            "settings_saved": "Настройки сохранены",
            "russian": "Русский",
            "english": "English",
            "chinese": "中文",
            "open_deepseek": "Открыть DeepSeek",
            "open_qwen": "Открыть Qwen",
            "ai_help": "Получить помощь AI"
        },
        "en": {
            "settings": "Settings",
            "language": "Language",
            "display": "Display",
            "study": "Study",
            "ai_assistant": "AI Assistant",
            "font_size": "Font Size",
            "theme": "Theme",
            "light": "Light",
            "dark": "Dark",
            "auto_save": "Auto Save",
            "show_hints": "Show Hints",
            "animation": "Animation",
            "sound": "Sound",
            "notifications": "Notifications",
            "save": "Save",
            "cancel": "Cancel",
            "reset": "Reset to Default",
            "success": "Success",
            "settings_saved": "Settings saved successfully",
            "russian": "Русский",
            "english": "English",
            "chinese": "中文",
            "open_deepseek": "Open DeepSeek",
            "open_qwen": "Open Qwen",
            "ai_help": "Get AI Help"
        },
        "zh": {
            "settings": "设置",
            "language": "语言",
            "display": "显示",
            "study": "学习",
            "ai_assistant": "AI 助手",
            "font_size": "字体大小",
            "theme": "主题",
            "light": "浅色",
            "dark": "深色",
            "auto_save": "自动保存",
            "show_hints": "显示提示",
            "animation": "动画效果",
            "sound": "声音",
            "notifications": "通知",
            "save": "保存",
            "cancel": "取消",
            "reset": "恢复默认",
            "success": "成功",
            "settings_saved": "设置已保存",
            "russian": "Русский",
            "english": "English",
            "chinese": "中文",
            "open_deepseek": "打开 DeepSeek",
            "open_qwen": "打开 Qwen",
            "ai_help": "获取 AI 帮助"
        }
    }
    
    def __init__(self):
        self.config_file = os.path.join(get_user_data_dir(), "settings.json")
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置和加载的配置
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
        except Exception as e:
            print(f"加载配置失败: {e}")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save_config()
    
    def get_translation(self, key):
        """获取翻译文本"""
        lang = self.config.get("language", "ru")
        return self.TRANSLATIONS.get(lang, self.TRANSLATIONS["ru"]).get(key, key)


class SettingsWindow(QDialog):
    """设置窗口"""
    
    settings_changed = Signal(dict)  # 设置改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(self.settings_manager.get_translation("settings"))
        self.setMinimumSize(550, 700)
        self.setModal(True)
        
        # 应用样式 - 修复所有文字颜色问题
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f8fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #3498db;
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 10pt;
                background: transparent;
            }
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #e0e6ed;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
                min-height: 28px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #e0e6ed;
                outline: none;
                font-size: 10pt;
            }
            QComboBox QAbstractItemView::item {
                color: #2c3e50;
                padding: 8px;
                background-color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QSpinBox {
                padding: 6px 10px;
                border: 1px solid #e0e6ed;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
                min-height: 28px;
                font-size: 10pt;
            }
            QSpinBox:hover {
                border-color: #3498db;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #f0f2f5;
                border: none;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e0e6ed;
            }
            QCheckBox {
                spacing: 8px;
                color: #2c3e50;
                background: transparent;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #bdc3c7;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNC42NjY2N0w2IDEyTDIuNjY2NjcgOC42NjY2NyIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
            QPushButton {
                padding: 10px 24px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
                font-size: 10pt;
                color: white;
            }
            QPushButton#saveButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton#saveButton:hover {
                background-color: #2980b9;
            }
            QPushButton#cancelButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton#cancelButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton#resetButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#resetButton:hover {
                background-color: #c0392b;
            }
            QPushButton#deepseekButton {
                background-color: #1abc9c;
                color: white;
                padding: 8px 16px;
            }
            QPushButton#deepseekButton:hover {
                background-color: #16a085;
            }
            QPushButton#qwenButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 16px;
            }
            QPushButton#qwenButton:hover {
                background-color: #e67e22;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 10pt;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 6px 16px;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel(self.settings_manager.get_translation("settings"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e0e6ed;")
        main_layout.addWidget(line)
        
        # 语言设置组
        lang_group = self.create_language_group()
        main_layout.addWidget(lang_group)
        
        # 显示设置组
        display_group = self.create_display_group()
        main_layout.addWidget(display_group)
        
        # 学习设置组
        study_group = self.create_study_group()
        main_layout.addWidget(study_group)
        
        # AI助手设置组
        ai_group = self.create_ai_assistant_group()
        main_layout.addWidget(ai_group)
        
        # 弹簧
        main_layout.addStretch()
        
        # 按钮区域
        button_layout = self.create_button_layout()
        main_layout.addLayout(button_layout)
    
    def create_language_group(self):
        """创建语言设置组"""
        group = QGroupBox(self.settings_manager.get_translation("language"))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.settings_manager.get_translation("language") + ":")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(self.settings_manager.get_translation("russian"), "ru")
        self.lang_combo.addItem(self.settings_manager.get_translation("english"), "en")
        self.lang_combo.addItem(self.settings_manager.get_translation("chinese"), "zh")
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo, 1)
        layout.addLayout(lang_layout)
        
        group.setLayout(layout)
        return group
    
    def create_display_group(self):
        """创建显示设置组"""
        group = QGroupBox(self.settings_manager.get_translation("display"))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 主题选择
        theme_layout = QHBoxLayout()
        theme_label = QLabel(self.settings_manager.get_translation("theme") + ":")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(self.settings_manager.get_translation("light"), "light")
        self.theme_combo.addItem(self.settings_manager.get_translation("dark"), "dark")
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo, 1)
        layout.addLayout(theme_layout)
        
        # 字体大小
        font_layout = QHBoxLayout()
        font_label = QLabel(self.settings_manager.get_translation("font_size") + ":")
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setSuffix(" pt")
        
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_spin, 1)
        layout.addLayout(font_layout)
        
        # 动画效果
        self.animation_check = QCheckBox(self.settings_manager.get_translation("animation"))
        layout.addWidget(self.animation_check)
        
        group.setLayout(layout)
        return group
    
    def create_study_group(self):
        """创建学习设置组"""
        group = QGroupBox(self.settings_manager.get_translation("study"))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 自动保存
        self.auto_save_check = QCheckBox(self.settings_manager.get_translation("auto_save"))
        layout.addWidget(self.auto_save_check)
        
        # 显示提示
        self.hints_check = QCheckBox(self.settings_manager.get_translation("show_hints"))
        layout.addWidget(self.hints_check)
        
        # 声音
        self.sound_check = QCheckBox(self.settings_manager.get_translation("sound"))
        layout.addWidget(self.sound_check)
        
        # 通知
        self.notification_check = QCheckBox(self.settings_manager.get_translation("notifications"))
        layout.addWidget(self.notification_check)
        
        group.setLayout(layout)
        return group
    
    def create_ai_assistant_group(self):
        """创建AI助手设置组"""
        group = QGroupBox(self.settings_manager.get_translation("ai_assistant"))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 说明文字
        info_label = QLabel(self.settings_manager.get_translation("ai_help"))
        info_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        layout.addWidget(info_label)
        
        # AI按钮布局
        ai_buttons_layout = QHBoxLayout()
        ai_buttons_layout.setSpacing(12)
        
        # DeepSeek按钮
        deepseek_btn = QPushButton("🤖 DeepSeek")
        deepseek_btn.setObjectName("deepseekButton")
        deepseek_btn.clicked.connect(lambda: self.open_ai_website("deepseek"))
        deepseek_btn.setToolTip("https://chat.deepseek.com")
        
        # Qwen按钮
        qwen_btn = QPushButton("🤖 Qwen")
        qwen_btn.setObjectName("qwenButton")
        qwen_btn.clicked.connect(lambda: self.open_ai_website("qwen"))
        qwen_btn.setToolTip("https://tongyi.aliyun.com/qianwen")
        
        ai_buttons_layout.addWidget(deepseek_btn)
        ai_buttons_layout.addWidget(qwen_btn)
        
        layout.addLayout(ai_buttons_layout)
        
        group.setLayout(layout)
        return group
    
    def create_button_layout(self):
        """创建按钮布局"""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # 重置按钮
        self.reset_button = QPushButton(self.settings_manager.get_translation("reset"))
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self.reset_settings)
        
        layout.addWidget(self.reset_button)
        layout.addStretch()
        
        # 取消按钮
        self.cancel_button = QPushButton(self.settings_manager.get_translation("cancel"))
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        # 保存按钮
        self.save_button = QPushButton(self.settings_manager.get_translation("save"))
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_settings)
        
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.save_button)
        
        return layout
    
    def open_ai_website(self, ai_type):
        """在应用内打开AI网站"""
        urls = {
            "deepseek": ("https://chat.deepseek.com", "🤖 DeepSeek AI"),
            "qwen": ("https://tongyi.aliyun.com/qianwen", "🤖 Qwen AI")
        }
        
        if ai_type in urls:
            url, title = urls[ai_type]
            # 在应用内打开网页
            web_dialog = AIWebDialog(url, title, self)
            web_dialog.exec()
    
    def load_settings(self):
        """加载设置到UI"""
        # 语言
        lang = self.settings_manager.get("language", "ru")
        index = self.lang_combo.findData(lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        # 主题
        theme = self.settings_manager.get("theme", "light")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # 字体大小
        font_size = self.settings_manager.get("font_size", 10)
        self.font_spin.setValue(font_size)
        
        # 复选框
        self.animation_check.setChecked(self.settings_manager.get("animation_enabled", True))
        self.auto_save_check.setChecked(self.settings_manager.get("auto_save", True))
        self.hints_check.setChecked(self.settings_manager.get("show_hints", True))
        self.sound_check.setChecked(self.settings_manager.get("sound_enabled", True))
        self.notification_check.setChecked(self.settings_manager.get("notification_enabled", True))
    
    def save_settings(self):
        """保存设置"""
        # 保存所有设置
        self.settings_manager.set("language", self.lang_combo.currentData())
        self.settings_manager.set("theme", self.theme_combo.currentData())
        self.settings_manager.set("font_size", self.font_spin.value())
        self.settings_manager.set("animation_enabled", self.animation_check.isChecked())
        self.settings_manager.set("auto_save", self.auto_save_check.isChecked())
        self.settings_manager.set("show_hints", self.hints_check.isChecked())
        self.settings_manager.set("sound_enabled", self.sound_check.isChecked())
        self.settings_manager.set("notification_enabled", self.notification_check.isChecked())
        
        # 保存到文件
        if self.settings_manager.save_config():
            # 发送设置改变信号
            self.settings_changed.emit(self.settings_manager.config)
            
            # 显示成功消息
            QMessageBox.information(
                self,
                self.settings_manager.get_translation("success"),
                self.settings_manager.get_translation("settings_saved")
            )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings")
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self,
            self.settings_manager.get_translation("reset"),
            "Are you sure you want to reset all settings to default?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.settings_manager.reset_to_default():
                self.load_settings()
                QMessageBox.information(self, "Success", "Settings reset to default")
            else:
                QMessageBox.critical(self, "Error", "Failed to reset settings")