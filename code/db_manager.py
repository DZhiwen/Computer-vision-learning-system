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


class SubjectiveDBManager:
    """主观题数据库管理器"""
    def __init__(self):
        self.db_path = os.path.join(get_user_data_dir(), 'subjective_questions.db')
        self.init_database()
    
    def init_database(self):
        """初始化主观题数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 题目表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjective_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_num INTEGER NOT NULL,
                section_num INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                scoring_criteria TEXT,
                UNIQUE(chapter_num, section_num)
            )''')

            # 用户回答表 (新增)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_subjective_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chapter_num INTEGER NOT NULL,
                section_num INTEGER NOT NULL,
                user_answer TEXT,
                ai_score INTEGER,
                ai_feedback TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, chapter_num, section_num)
            )''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"初始化主观题数据库失败: {e}")
    
    def get_subjective_question(self, chapter_num, section_num):
        """获取指定章节的主观题"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT question_text, scoring_criteria
            FROM subjective_questions
            WHERE chapter_num = ? AND section_num = ?
            ''', (chapter_num, section_num))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # 解析评分标准JSON
                criteria = result[1]
                try:
                    if criteria:
                        criteria = json.loads(criteria)
                except:
                    pass

                return {
                    "text": result[0], # 统一键名为 text
                    "question_text": result[0],
                    "score_criteria": criteria, # 统一键名为 score_criteria
                    "scoring_criteria": criteria,
                    "full_score": 10 # 默认满分10分，也可以存储在数据库中
                }
            return None
        except Exception as e:
            print(f"获取主观题失败: {e}")
            return None
    
    def save_subjective_question(self, chapter_num, section_num, question_text, scoring_criteria):
        """保存主观题"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 确保存储为JSON字符串
            if isinstance(scoring_criteria, dict):
                scoring_criteria = json.dumps(scoring_criteria, ensure_ascii=False)

            cursor.execute('''
            INSERT OR REPLACE INTO subjective_questions 
            (chapter_num, section_num, question_text, scoring_criteria)
            VALUES (?, ?, ?, ?)
            ''', (chapter_num, section_num, question_text, scoring_criteria))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存主观题失败: {e}")
            return False

    def save_user_subjective_answer(self, user_id, chapter_num, section_num, user_answer):
        """保存用户主观题答案"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 使用 INSERT OR REPLACE 或 ON CONFLICT UPDATE
            cursor.execute('''
            INSERT INTO user_subjective_answers (user_id, chapter_num, section_num, user_answer, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, chapter_num, section_num) DO UPDATE SET
            user_answer=excluded.user_answer,
            updated_at=CURRENT_TIMESTAMP
            ''', (user_id, chapter_num, section_num, user_answer))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存用户主观题答案失败: {e}")
            return False

    def save_ai_score(self, user_id, chapter_num, section_num, ai_score, ai_feedback):
        """保存AI评分结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE user_subjective_answers
            SET ai_score = ?, ai_feedback = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chapter_num = ? AND section_num = ?
            ''', (ai_score, ai_feedback, user_id, chapter_num, section_num))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存AI评分失败: {e}")
            return False
            
    def get_user_subjective_answer(self, user_id, chapter_num, section_num):
        """获取用户的主观题答案和评分"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT user_answer, ai_score, ai_feedback
            FROM user_subjective_answers
            WHERE user_id = ? AND chapter_num = ? AND section_num = ?
            ''', (user_id, chapter_num, section_num))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "user_answer": result[0],
                    "ai_score": result[1],
                    "ai_feedback": result[2]
                }
            return None
        except Exception as e:
            print(f"获取用户主观题答案失败: {e}")
            return None


class DatabaseManager:
    def __init__(self, db_path=None):
        # 如果没有指定数据库路径，则使用用户数据目录
        # Если путь к базе данных не указан, используем директорию пользовательских данных
        if db_path is None:
            db_path = os.path.join(get_user_data_dir(), "cv_learning.db")
            
        self.db_path = db_path
        self.init_database()
        
        # 初始化题库（新增）
        self.questions_db_path = os.path.join(get_user_data_dir(), 'questions.db')
        self.init_questions_database()
        
        # 新增：初始化主观题专用DB
        self.subjective_db = SubjectiveDBManager()
    
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

    def init_questions_database(self):
        """初始化题库数据库（新增方法）"""
        # 检查题库是否已存在
        if os.path.exists(self.questions_db_path):
            # 检查是否有数据
            conn = sqlite3.connect(self.questions_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quiz_questions'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.execute("SELECT COUNT(*) FROM quiz_questions")
                count = cursor.fetchone()[0]
                conn.close()
                
                if count > 0:
                    # 题库已存在且有数据，无需初始化
                    return
            else:
                conn.close()
        
        # 创建题库表并导入默认题目
        conn = sqlite3.connect(self.questions_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_num INTEGER NOT NULL CHECK(chapter_num BETWEEN 1 AND 7),
            section_num INTEGER NOT NULL CHECK(section_num BETWEEN 1 AND 2),
            question_num INTEGER NOT NULL CHECK(question_num BETWEEN 1 AND 8),
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
            UNIQUE(chapter_num, section_num, question_num)
        )
        ''')
        
        # 导入默认题目
        default_questions = self.get_default_questions()
        for q in default_questions:
            cursor.execute('''
            INSERT OR IGNORE INTO quiz_questions 
            (chapter_num, section_num, question_num, question_text, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (q["chapter_num"], q["section_num"], q["question_num"], q["question_text"], 
            q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_answer"]))
        
        conn.commit()
        conn.close()
        print(f"题库已初始化，共导入 {len(default_questions)} 道题目")

    

    def get_quiz_questions(self, chapter_num, section_num):
        """读取指定章节-小节的8道题（仅支持section_num=1/2）"""
        try:
            conn = sqlite3.connect(self.questions_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT question_num, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM quiz_questions
            WHERE chapter_num = ? AND section_num = ?
            ORDER BY question_num LIMIT 8''',
            (chapter_num, section_num))
            
            questions = {}
            for q_num, q_text, opt_a, opt_b, opt_c, opt_d, correct in cursor.fetchall():
                questions[q_num] = {
                    "text": q_text,
                    "options": {"A": opt_a, "B": opt_b, "C": opt_c, "D": opt_d},
                    "correct": correct
                }
            conn.close()
            return questions
        except Exception as e:
            print(f"读取题目失败: {e}")
            return {}

    def import_questions_to_db(self, questions_data, db_path=None):
        """
        导入题目数据到指定数据库
        questions_data格式：[{"chapter_num":1, "section_num":1, "question_num":1, ...}]
        """
        if db_path is None:
            db_path = self.questions_db_path
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_num INTEGER NOT NULL CHECK(chapter_num BETWEEN 1 AND 7),
                section_num INTEGER NOT NULL CHECK(section_num BETWEEN 1 AND 2),
                question_num INTEGER NOT NULL CHECK(question_num BETWEEN 1 AND 8),
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
                UNIQUE(chapter_num, section_num, question_num)
            )''')
            
            for q in questions_data:
                cursor.execute('''
                INSERT OR IGNORE INTO quiz_questions 
                (chapter_num, section_num, question_num, question_text, option_a, option_b, option_c, option_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (q["chapter_num"], q["section_num"], q["question_num"], q["question_text"], 
                q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_answer"]))
            
            conn.commit()
            conn.close()
            print(f"成功导入 {len(questions_data)} 道题目到 {db_path}")
            return True
        except Exception as e:
            print(f"导入题目失败: {e}")
            return False

    def register_user(self, username, password, name=None):
        """注册新用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                return False
            
            hashed_password = self._hash_password(password)
            
            cursor.execute(
                "INSERT INTO users (username, password, name) VALUES (?, ?, ?)",
                (username, hashed_password, name)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"注册用户时出错: {e}")
            return False
    
    def check_login(self, username, password):
        """验证用户登录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = self._hash_password(password)
            
            cursor.execute(
                "SELECT id, name FROM users WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {"user_id": result[0], "name": result[1]}
            return None
        except Exception as e:
            print(f"登录验证时出错: {e}")
            return None
    
    def _hash_password(self, password):
        """对密码进行哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def update_progress(self, user_id, progress_value, progress_data):
        """更新用户进度"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            progress_json = json.dumps(progress_data)
            
            cursor.execute(
                "SELECT id FROM progress WHERE user_id = ?",
                (user_id,)
            )
            
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE progress SET progress_value = ?, progress_data = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (progress_value, progress_json, user_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO progress (user_id, progress_value, progress_data) VALUES (?, ?, ?)",
                    (user_id, progress_value, progress_json)
                )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新进度时出错: {e}")
            return False
    
    def get_progress(self, user_id):
        """获取用户进度"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT progress_value, progress_data FROM progress WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                progress_data = json.loads(result[1]) if result[1] else {}
                return {"progress_value": result[0], "progress_data": progress_data}
            return {"progress_value": 0.0, "progress_data": {}}
        except Exception as e:
            print(f"获取进度时出错: {e}")
            return {"progress_value": 0.0, "progress_data": {}}
    
    def save_chapter_progress(self, user_id, chapter_index, step_index, completed):
        """保存章节进度"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO chapter_progress 
                (user_id, chapter_index, step_index, completed, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, chapter_index, step_index, completed))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存章节进度时出错: {e}")
            return False
    
    def get_chapter_progress(self, user_id):
        """获取章节进度"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT chapter_index, step_index, completed
                FROM chapter_progress
                WHERE user_id = ? AND completed = 1
            ''', (user_id,))
            
            progress_data = {}
            for chapter_idx, step_idx, completed in cursor.fetchall():
                if chapter_idx not in progress_data:
                    progress_data[chapter_idx] = {}
                progress_data[chapter_idx][step_idx] = completed
            
            conn.close()
            return progress_data
        except Exception as e:
            print(f"获取章节进度时出错: {e}")
            return {}
    
    def save_quiz_answer(self, user_id, chapter_index, section_index, question_index, selected_answer, is_correct):
        """保存测试题答案"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO quiz_answers 
                (user_id, chapter_index, section_index, question_index, selected_answer, is_correct, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, chapter_index, section_index, question_index, selected_answer, is_correct))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存答案时出错: {e}")
            return False
    
    def get_quiz_answers(self, user_id):
        """获取用户答题记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT chapter_index, section_index, question_index, selected_answer, is_correct
                FROM quiz_answers
                WHERE user_id = ?
            ''', (user_id,))
            
            answers = {}
            for chapter_idx, section_idx, question_idx, selected_answer, is_correct in cursor.fetchall():
                if chapter_idx not in answers:
                    answers[chapter_idx] = {}
                if section_idx not in answers[chapter_idx]:
                    answers[chapter_idx][section_idx] = {}
                
                answers[chapter_idx][section_idx][question_idx] = {
                    'selected_answer': selected_answer,
                    'is_correct': is_correct
                }
            
            conn.close()
            return answers
        except Exception as e:
            print(f"获取答题记录时出错: {e}")
            return {}

    def ensure_questions_exist(self):
        """确保题库存在，如果不存在则自动导入默认题目"""
        try:
            # 优先使用环境变量指定的题库路径
            env_db = os.environ.get('CVL_QUESTIONS_DB')
            questions_db_path = env_db if env_db and os.path.exists(env_db) \
                else os.path.join(get_user_data_dir(), 'questions.db')
            
            conn = sqlite3.connect(questions_db_path)
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='quiz_questions'
            """)
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                # 表不存在，创建表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter_num INTEGER NOT NULL CHECK(chapter_num BETWEEN 1 AND 7),
                    section_num INTEGER NOT NULL CHECK(section_num BETWEEN 1 AND 2),
                    question_num INTEGER NOT NULL CHECK(question_num BETWEEN 1 AND 8),
                    question_text TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
                    UNIQUE(chapter_num, section_num, question_num)
                )''')
                conn.commit()
            
            # 检查是否有1.1章节的题目
            cursor.execute("""
                SELECT COUNT(*) FROM quiz_questions 
                WHERE chapter_num = 1 AND section_num = 1
            """)
            count = cursor.fetchone()[0]
            
            conn.close()
            
            # 如果没有题目，自动导入
            if count == 0:
                print("检测到题库为空，正在自动导入默认题目...")
                questions_data = self.get_default_questions()
                self.import_questions_to_db(questions_data, questions_db_path)
                print("默认题目导入完成！")
                
            return True
        except Exception as e:
            print(f"初始化题库失败: {e}")
            return False
    @staticmethod
    def get_default_questions():
        """返回默认题目数据（至少覆盖 1.1 章节的8道题）"""
        return [
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 1,
                "question_text": "Что такое компьютерное зрение?",
                "option_a": "Технология обработки текстов",
                "option_b": "Технология распознавания визуальной информации",
                "option_c": "Метод машинного перевода",
                "option_d": "Алгоритм обработки звука",
                "correct_answer": "B"
            },
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 2,
                "question_text": "Какое из нижеперечисленных является основным компонентом компьютерного зрения?",
                "option_a": "Изображение в цифровом формате",
                "option_b": "Текстовый описатель сцены",
                "option_c": "Звуковой сигнал окружающей среды",
                "option_d": "Датчик температуры",
                "correct_answer": "A"
            },
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 3,
                "question_text": "В каком области компьютерное зрение используется для распознавания лиц?",
                "option_a": "Безопасность и доступ control",
                "option_b": "Анализ финансовых рынков",
                "option_c": "Прогнозирование погоды",
                "option_d": "Обработка звуковых записей",
                "correct_answer": "A"
            },
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 4,
                "question_text": "Что такое пиксель?",
                "option_a": "Минимальная единица цифрового изображения",
                "option_b": "Алгоритм сжатия видео",
                "option_c": "Тип графического формата",
                "option_d": "Метод фильтрации звука",
                "correct_answer": "A"
            },
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 5,
                "question_text": "Какая задача относится к компьютерному зрению?",
                "option_a": "Распознавание объектов на фотографии",
                "option_b": "Перевод текста с одного языка на другой",
                "option_c": "Оптимизация баз данных",
                "option_d": "Создание музыки с помощью ИИ",
                "correct_answer": "A"
            },
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 6,
                "question_text": "Что такое цветовое пространство в компьютерном зрении?",
                "option_a": "Метод представления цвета с использованием числовых значений",
                "option_b": "Программа для редактирования фотографий",
                "option_c": "Тип дисплея для вывода изображений",
                "option_d": "Алгоритм сглаживания границ",
                "correct_answer": "A"
            },
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 7,
                "question_text": "Какое из утверждений о компьютерном зрении верно?",
                "option_a": "Оно имитирует способ восприятия мира человеческим зрением",
                "option_b": "Оно работает только с черно-белыми изображениями",
                "option_c": "Не требует использования машинного обучения",
                "option_d": "Используется только в медицинской диагностике",
                "correct_answer": "A"
            },
            {
                "chapter_num": 1,
                "section_num": 1,
                "question_num": 8,
                "question_text": "Какая единица измерения используется для описания разрешения изображения?",
                "option_a": "Пиксели на дюйм (PPI)",
                "option_b": "Мегаватты (МВт)",
                "option_c": "Биты в секунду (бит/с)",
                "option_d": "Гц (герц)",
                "correct_answer": "A"
            }
        ]
