"""
数据库扩展辅助工具
用于添加统计功能所需的新表
"""
import sqlite3
import os

def extend_database(db_path=None):
    """扩展数据库，添加统计功能所需的表"""
    
    if db_path is None:
        try:
            from db_manager import get_user_data_dir
            data_dir = get_user_data_dir()
            db_path = os.path.join(data_dir, "cv_learning.db")
        except:
            db_path = "cv_learning.db"
    
    print(f"正在扩展数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 学习时长记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_date DATE NOT NULL,
                duration_minutes INTEGER DEFAULT 0,
                chapters_studied TEXT
            )
        """)
        print("✓ 创建 study_sessions 表")
        
        # 2. 每日登录记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_date DATE NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建 login_history 表")
        
        # 3. 测验详细记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chapter TEXT NOT NULL,
                question_id TEXT NOT NULL,
                user_answer TEXT,
                correct_answer TEXT,
                is_correct BOOLEAN,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建 quiz_details 表")
        
        # 4. 成就系统表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                requirement TEXT
            )
        """)
        print("✓ 创建 achievements 表")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ 创建 user_achievements 表")
        
        # 5. 插入一些示例成就
        achievements = [
            ("初学者", "完成第一章", "🎓", "chapter_1_complete"),
            ("勤奋学习", "连续学习7天", "🔥", "streak_7_days"),
            ("测验高手", "测验正确率达到90%", "🎯", "quiz_90_percent"),
            ("完美主义者", "完成所有章节", "⭐", "all_chapters_complete")
        ]
        
        for name, desc, icon, req in achievements:
            cursor.execute("""
                INSERT OR IGNORE INTO achievements 
                (name, description, icon, requirement)
                VALUES (?, ?, ?, ?)
            """, (name, desc, icon, req))
        
        print("✓ 插入示例成就")
        
        conn.commit()
        conn.close()
        
        print("\n数据库扩展完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库扩展失败: {e}")
        return False

def check_database_structure(db_path=None):
    """检查数据库结构"""
    
    if db_path is None:
        try:
            from db_manager import get_user_data_dir
            data_dir = get_user_data_dir()
            db_path = os.path.join(data_dir, "cv_learning.db")
        except:
            db_path = "cv_learning.db"
    
    print(f"检查数据库: {db_path}\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        
        print("现有表:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"      {col[1]} ({col[2]})")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("数据库扩展工具")
    print("=" * 60)
    print()
    
    # 检查当前结构
    check_database_structure()
    
    # 扩展数据库
    print("\n" + "=" * 60)
    extend_database()
    
    # 再次检查
    print("\n" + "=" * 60)
    check_database_structure()