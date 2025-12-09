from db_manager import DatabaseManager
from enter_window import EnterWindow
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QTreeWidget, QStackedWidget, QProgressBar, QPushButton, QVBoxLayout, QTabWidget, QTabBar
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QColor
from db_manager import DatabaseManager
import resources_rc 
class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        
        # 动态加载UI文件
        # Динамическая загрузка UI файла
        ui_file_path = os.path.join(os.path.dirname(__file__), "ui", "login.ui")
        ui_file = QFile(ui_file_path)
        
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Невозможно открыть UI файл: {ui_file_path}")
            return
            
        # 使用QUiLoader加载UI
        # Загрузка UI с помощью QUiLoader
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        # 设置中央窗口部件
        # Установка центрального виджета окна
        self.setCentralWidget(self.ui)
        
        self.db = DatabaseManager()
        self.setFixedSize(self.ui.width(), self.ui.height())
        # 设置密码输入框为密码模式
        # Установка режима пароля для полей ввода пароля
        self.ui.findChild(QWidget, "e_password").setEchoMode(self.ui.findChild(QWidget, "e_password").EchoMode.Password)
        self.ui.findChild(QWidget, "e_password1").setEchoMode(self.ui.findChild(QWidget, "e_password1").EchoMode.Password)
        
        # 连接按钮信号到槽函数
        # Подключение сигналов кнопок к слот-функциям
        self.ui.findChild(QWidget, "b_register").clicked.connect(self.show_register_page)
        self.ui.findChild(QWidget, "b_back").clicked.connect(self.show_login_page)
        self.ui.findChild(QWidget, "b_login").clicked.connect(self.login)
        self.ui.findChild(QWidget, "p_register1").clicked.connect(self.register)
        
        # 设置窗口标题
        # Установка заголовка окна
        self.setWindowTitle("Модуль обучения компьютерному зрению")
        
        # 初始化Enter窗口为None
        # Инициализация окна Enter как None
        self.enter_window = None
        
        # 保存当前登录用户ID
        # Сохранение ID текущего пользователя
        self.current_user_id = None
    
    def show_register_page(self):
        """显示注册页面
        Показать страницу регистрации"""
        self.ui.findChild(QWidget, "stackedWidget").setCurrentIndex(1)
        
    def show_login_page(self):
        """显示登录页面
        Показать страницу входа"""
        self.ui.findChild(QWidget, "stackedWidget").setCurrentIndex(0)
    
    def login(self):
        """处理登录请求
        Обработка запроса на вход"""
        login = self.ui.findChild(QWidget, "e_login").text().strip()
        password = self.ui.findChild(QWidget, "e_password").text().strip()
        name = self.ui.findChild(QWidget, "e_name").text().strip()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка входа", "Пожалуйста, введите имя пользователя и пароль")
            return
        
        user = self.db.check_login(login, password)
        if user:
            user_id, db_name = user
            self.current_user_id = user_id  # 保存用户ID / Сохранение ID пользователя
            
            # 登录成功
            # Успешный вход
            display_name = name if name else db_name if db_name else login
            QMessageBox.information(self, "Успешный вход", f"Добро пожаловать, {display_name}!")
            
            # 打开Enter.ui界面，传入用户ID
            # Открытие интерфейса Enter.ui с передачей ID пользователя
            self.open_enter_window(display_name, user_id)
        else:
            # 登录失败
            # Ошибка входа
            QMessageBox.warning(self, "Ошибка входа", "Неверное имя пользователя или пароль. Попробуйте снова или зарегистрируйте новую учетную запись")
    
    def open_enter_window(self, user_name, user_id):
        """打开Enter界面
        Открытие интерфейса Enter"""
        # 创建Enter窗口，传入用户ID
        # Создание окна Enter с передачей ID пользователя
        self.enter_window = EnterWindow(user_id)
        # 设置用户名
        # Установка имени пользователя
        self.enter_window.set_user_name(user_name)
        # 显示Enter窗口
        # Отображение окна Enter
        self.enter_window.show()
        # 隐藏登录窗口
        # Скрытие окна входа
        self.hide()
        
        # 当Enter窗口关闭时，重新显示登录窗口
        # При закрытии окна Enter, снова отображается окно входа
        self.enter_window.ui.destroyed.connect(self.show)
    
    def register(self):
        """处理注册请求
        Обработка запроса на регистрацию"""
        username = self.ui.findChild(QWidget, "e_username").text().strip()
        password = self.ui.findChild(QWidget, "e_password1").text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка регистрации", "Пожалуйста, введите имя пользователя и пароль")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка регистрации", "Длина пароля должна быть не менее 6 символов")
            return
        
        # 尝试注册用户
        # Попытка регистрации пользователя
        success = self.db.register_user(username, password)
        if success:
            QMessageBox.information(self, "Успешная регистрация", "Аккаунт создан. Пожалуйста, вернитесь на страницу входа для авторизации")
            # 清空输入框
            # Очистка полей ввода
            self.ui.findChild(QWidget, "e_username").clear()
            self.ui.findChild(QWidget, "e_password1").clear()
            # 返回登录页面
            # Возврат на страницу входа
            self.show_login_page()
        else:
            QMessageBox.warning(self, "Ошибка регистрации", "Имя пользователя уже существует. Пожалуйста, выберите другое имя пользователя")
