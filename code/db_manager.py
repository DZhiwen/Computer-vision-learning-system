import sqlite3
import os
import json
import hashlib
import sys

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和PyInstaller打包后的环境
    Получение абсолютного пути к ресурсу, совместимого с средой разработки и упакованной средой PyInstaller"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """获取用户数据目录
    Получение директории пользовательских данных"""
    # 在Windows上使用AppData/Local，在Linux/Mac上使用~/.local/share
    # Использование AppData/Local в Windows и ~/.local/share в Linux/Mac
    if sys.platform == 'win32':
        app_data = os.path.join(os.environ['LOCALAPPDATA'], 'ComputerVisionLearning')
    else:
        app_data = os.path.expanduser('~/.local/share/ComputerVisionLearning')
    
    # 确保目录存在
    # Убедиться, что директория существует
    if not os.path.exists(app_data):
        os.makedirs(app_data)
    
    return app_data

class DatabaseManager:
    def __init__(self, db_path=None):
        # 如果没有指定数据库路径，则使用用户数据目录
        # Если путь к базе данных не указан, используем директорию пользовательских данных
        if db_path is None:
            db_path = os.path.join(get_user_data_dir(), "cv_learning.db")
            
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构
        Инициализация структуры таблиц базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        # Создание таблицы пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建进度表
        # Создание таблицы прогресса
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            progress_value REAL DEFAULT 0.0,
            progress_data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 创建章节进度表
        # Создание таблицы прогресса по главам
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapter_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chapter_index INTEGER NOT NULL,
            step_index INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, chapter_index, step_index)
        )
        ''')
        
     
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chapter_index INTEGER NOT NULL,
            section_index INTEGER NOT NULL,
            question_index INTEGER NOT NULL,
            selected_answer TEXT,
            is_correct INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, chapter_index, section_index, question_index)
        )
        ''')

        conn.commit()
        conn.close()
    
    def register_user(self, username, password, name=None):
        """注册新用户
        Регистрация нового пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户名是否已存在
            # Проверка существования имени пользователя
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                return False  # 用户名已存在 / Имя пользователя уже существует
            
            # 对密码进行哈希处理
            # Хеширование пароля
            hashed_password = self._hash_password(password)
            
            # 插入新用户
            # Вставка нового пользователя
            cursor.execute(
                "INSERT INTO users (username, password, name) VALUES (?, ?, ?)",
                (username, hashed_password, name)
            )
            
            conn.commit()
            conn.close()
            return True  # 注册成功 / Регистрация успешна
        except Exception as e:
            print(f"注册用户时出错: {e} / Ошибка при регистрации пользователя: {e}")
            return False
    
    def check_login(self, username, password):
        """验证用户登录
        Проверка входа пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 对输入的密码进行哈希处理
            # Хеширование введенного пароля
            hashed_password = self._hash_password(password)
            
            # 查询用户
            # Запрос пользователя
            cursor.execute(
                "SELECT id, name FROM users WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            return user  # 如果验证成功，返回用户ID和名称 / Если проверка успешна, возвращает ID и имя пользователя
        except Exception as e:
            print(f"验证登录时出错: {e} / Ошибка при проверке входа: {e}")
            return None
    
    def update_progress(self, user_id, progress_value, progress_data):
        """更新用户总体进度
        Обновление общего прогресса пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 将进度数据转换为JSON字符串
            # Преобразование данных прогресса в JSON строку
            progress_json = json.dumps(progress_data)
            
            # 检查是否已有进度记录
            # Проверка наличия записи о прогрессе
            cursor.execute("SELECT id FROM progress WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                # 更新现有记录
                # Обновление существующей записи
                cursor.execute(
                    "UPDATE progress SET progress_value = ?, progress_data = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (progress_value, progress_json, user_id)
                )
            else:
                # 创建新记录
                # Создание новой записи
                cursor.execute(
                    "INSERT INTO progress (user_id, progress_value, progress_data) VALUES (?, ?, ?)",
                    (user_id, progress_value, progress_json)
                )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新进度时出错: {e} / Ошибка при обновлении прогресса: {e}")
            return False
    
    def save_chapter_progress(self, user_id, chapter_index, step_index, completed):
        """保存章节进度
        Сохранение прогресса по главам"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 使用REPLACE INTO来处理可能的冲突（相同的用户、章节和步骤）
            # Использование REPLACE INTO для обработки возможных конфликтов (тот же пользователь, глава и шаг)
            cursor.execute(
                "REPLACE INTO chapter_progress (user_id, chapter_index, step_index, completed, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (user_id, chapter_index, step_index, completed)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存章节进度时出错: {e} / Ошибка при сохранении прогресса главы: {e}")
            return False
    
    def get_chapter_progress(self, user_id):
        """获取用户章节进度
        Получение прогресса пользователя по главам"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询用户的所有章节进度
            # Запрос всего прогресса пользователя по главам
            cursor.execute(
                "SELECT chapter_index, step_index, completed FROM chapter_progress WHERE user_id = ?",
                (user_id,)
            )
            
            progress_data = {}
            for chapter_index, step_index, completed in cursor.fetchall():
                if chapter_index not in progress_data:
                    progress_data[chapter_index] = {}
                progress_data[chapter_index][step_index] = completed
            
            conn.close()
            return progress_data
        except Exception as e:
            print(f"Ошибка при получении прогресса по главам: {e}")
            return {}
    
    def _hash_password(self, password):
        """对密码进行哈希处理
        Хеширование пароля"""
        # 使用SHA-256哈希算法
        # Использование алгоритма хеширования SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def save_quiz_answer(self, user_id, chapter_index, section_index, question_index, selected_answer, is_correct):
        """保存用户答题记录
        Сохранение ответов пользователя на вопросы теста"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 使用REPLACE INTO来处理可能的冲突（相同的用户、章节、小节和问题）
            cursor.execute(
                "REPLACE INTO quiz_answers (user_id, chapter_index, section_index, question_index, selected_answer, is_correct, updated_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (user_id, chapter_index, section_index, question_index, selected_answer, is_correct)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存答题记录时出错: {e} / Ошибка при сохранении ответа на вопрос: {e}")
            return False

    def get_quiz_answers(self, user_id):
        """获取用户所有答题记录
        Получение всех ответов пользователя на вопросы"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询用户的所有答题记录
            cursor.execute(
                "SELECT chapter_index, section_index, question_index, selected_answer, is_correct FROM quiz_answers WHERE user_id = ?",
                (user_id,)
            )
            
            answers_data = {}
            for chapter_index, section_index, question_index, selected_answer, is_correct in cursor.fetchall():
                if chapter_index not in answers_data:
                    answers_data[chapter_index] = {}
                if section_index not in answers_data[chapter_index]:
                    answers_data[chapter_index][section_index] = {}
                
                answers_data[chapter_index][section_index][question_index] = {
                    'selected_answer': selected_answer,
                    'is_correct': is_correct
                }
            
            conn.close()
            return answers_data
        except Exception as e:
            print(f"Ошибка при получении ответов на вопросы: {e}")
            return {}