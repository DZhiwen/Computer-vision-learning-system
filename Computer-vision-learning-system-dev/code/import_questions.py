"""题目导入脚本 - 运行后自动创建表并导入题目"""
from db_manager import DatabaseManager

def main():
    # 1. 初始化数据库管理器
    db = DatabaseManager()
    
    # 2. 示例题目数据（替换为你的实际题目，可批量添加）
    questions_data = [
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
        # 此处可添加更多题目（按章节、小节、题号顺序）
        # ... 重复上述格式，补充1-7章x.1和x.2小节的8道题
    ]
    
    # 3. 导入题目到指定数据库
    success = db.import_questions_to_db(
        questions_data,
        db_path=r"C:\Users\Wang_Yihao\AppData\Local\ComputerVisionLearning\questions.db"
    )
    if success:
        print("题目导入完成！")
    else:
        print("题目导入失败，请检查路径和数据格式。")

if __name__ == "__main__":
    main()