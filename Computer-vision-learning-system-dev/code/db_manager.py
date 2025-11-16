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
        # 新增题目表（适配1-7章，仅x.1和x.2小节）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_num INTEGER NOT NULL CHECK(chapter_num BETWEEN 1 AND 7),  -- 章节1-7（替换#为--）
            section_num INTEGER NOT NULL CHECK(section_num BETWEEN 1 AND 2), -- 仅x.1和x.2小节（替换#为--）
            question_num INTEGER NOT NULL CHECK(question_num BETWEEN 1 AND 8), -- 每小节8道题（UI固定）（替换#为--）
            question_text TEXT NOT NULL,     -- 题目文本（替换#为--）
            option_a TEXT NOT NULL,          -- 选项A（替换#为--）
            option_b TEXT NOT NULL,          -- 选项B（替换#为--）
            option_c TEXT NOT NULL,          -- 选项C（替换#为--）
            option_d TEXT NOT NULL,          -- 选项D（替换#为--）
            correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')), -- 正确答案（替换#为--）
            UNIQUE(chapter_num, section_num, question_num)  -- 联合唯一约束（替换#为--）
        )
        ''')
        conn.commit()
        conn.close()

    def get_quiz_questions(self, chapter_num, section_num):
        """读取指定章节-小节的8道题（仅支持section_num=1/2）"""
        try:
            questions_db_path = r"C:\Users\Wang_Yihao\AppData\Local\ComputerVisionLearning\questions.db"
            conn = sqlite3.connect(questions_db_path)
            cursor = conn.cursor()
            
            # 仅查询小节1或2的题目，且按题目序号1-8排序
            cursor.execute('''
            SELECT question_num, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM quiz_questions
            WHERE chapter_num = ? AND section_num = ?
            ORDER BY question_num LIMIT 8''',  # 适配UI的8道题
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
        # 新增：题目数据导入方法（帮助你将题目插入数据库）
    def import_questions_to_db(self, questions_data, db_path=None):
        """
        导入题目数据到指定数据库
        questions_data格式：[{"chapter_num":1, "section_num":1, "question_num":1, "question_text":"...", "option_a":"...", "option_b":"...", "option_c":"...", "option_d":"...", "correct_answer":"A"}]
        """
        if db_path is None:
            db_path = r"C:\Users\Wang_Yihao\AppData\Local\ComputerVisionLearning\questions.db"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # 确保表存在（兼容首次导入）
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
            # 批量插入题目（忽略重复）
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
        

class SubjectiveDBManager:
    def __init__(self):
        # 主观题专用数据库路径（与选择题分离）
        self.db_path = os.path.join(get_user_data_dir(), "subjective_questions.db")
        self.init_db()

    def init_db(self):
        """创建主观题表和用户答案表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. 主观题表（存储题目+评分标准）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjective_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_num INTEGER NOT NULL CHECK(chapter_num BETWEEN 1 AND 7),
            section_num INTEGER NOT NULL CHECK(section_num BETWEEN 1 AND 2),
            question_num INTEGER NOT NULL DEFAULT 9,  
            question_text TEXT NOT NULL,  
            score_criteria TEXT NOT NULL,  
            full_score INTEGER NOT NULL DEFAULT 10,  
            UNIQUE(chapter_num, section_num, question_num)
        )''')

        # 2. 用户主观题答案表（存储答案+AI评分）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjective_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chapter_num INTEGER NOT NULL,
            section_num INTEGER NOT NULL,
            question_num INTEGER NOT NULL,
            user_answer TEXT NOT NULL,  
            ai_score INTEGER,  
            ai_feedback TEXT,  
            scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, chapter_num, section_num, question_num)
        )''')

        conn.commit()
        conn.close()

    # 新增：导入主观题（含评分标准）
    def import_subjective_questions(self, questions_data):
        """questions_data格式：[{"chapter_num":1, "section_num":1, "question_text":"...", "score_criteria":{"keywords":["..."], "points":["..."], "full_score":10}}]"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for q in questions_data:
            # 评分标准转为JSON字符串存储
            criteria_json = json.dumps(q["score_criteria"], ensure_ascii=False)
            cursor.execute('''
            INSERT OR IGNORE INTO subjective_questions 
            (chapter_num, section_num, question_text, score_criteria, full_score)
            VALUES (?, ?, ?, ?, ?)''',
            (q["chapter_num"], q["section_num"], q["question_text"], criteria_json, q["score_criteria"]["full_score"]))
        conn.commit()
        conn.close()
        print(f"成功导入 {len(questions_data)} 道主观题到专用数据库")

    # 新增：获取主观题（含评分标准）
    def get_subjective_question(self, chapter_num, section_num):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT question_text, score_criteria, full_score 
        FROM subjective_questions 
        WHERE chapter_num=? AND section_num=? AND question_num=9''',
        (chapter_num, section_num))
        result = cursor.fetchone()
        conn.close()
        if result:
            # 评分标准JSON转字典
            return {
                "text": result[0],
                "score_criteria": json.loads(result[1]),
                "full_score": result[2]
            }
        return None

    # 新增：保存用户主观题答案（待评分）
    def save_user_subjective_answer(self, user_id, chapter_num, section_num, user_answer):
        """保存用户主观题答案（返回布尔值表示成功/失败）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 执行REPLACE（存在则更新，不存在则插入）
            cursor.execute('''
            REPLACE INTO subjective_answers 
            (user_id, chapter_num, section_num, question_num, user_answer)
            VALUES (?, ?, ?, 9, ?)''',
            (user_id, chapter_num, section_num, user_answer))
            
            conn.commit()
            conn.close()
            print(f"✅ 用户{user_id} 章节{chapter_num}小节{section_num} 主观题答案保存成功")
            return True  # 保存成功返回True
        except Exception as e:
            # 输出具体错误（如表未创建、权限不足）
            print(f"❌ 保存主观题答案失败：{str(e)}")
            conn.close() if 'conn' in locals() else None
            return False  # 保存失败返回False

    # 新增：保存AI评分结果
    def save_ai_score(self, user_id, chapter_num, section_num, ai_score, ai_feedback):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE subjective_answers 
        SET ai_score=?, ai_feedback=?, scored_at=CURRENT_TIMESTAMP
        WHERE user_id=? AND chapter_num=? AND section_num=? AND question_num=9''',
        (ai_score, ai_feedback, user_id, chapter_num, section_num))
        conn.commit()
        conn.close()

    # 新增：获取用户主观题答案+评分
    def get_user_subjective_answer(self, user_id, chapter_num, section_num):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT user_answer, ai_score, ai_feedback 
        FROM subjective_answers 
        WHERE user_id=? AND chapter_num=? AND section_num=? AND question_num=9''',
        (user_id, chapter_num, section_num))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "user_answer": result[0],
                "ai_score": result[1],
                "ai_feedback": result[2]
            }
        return None