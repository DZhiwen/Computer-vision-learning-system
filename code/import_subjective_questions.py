"""主观题导入脚本 - 导入题目和评分标准到专用数据库"""
from db_manager import DatabaseManager

def main():
    db = DatabaseManager()

    # 主观题数据（含评分标准，可批量添加）
    subjective_questions_data = [
        {
            "chapter_num": 1,
            "section_num": 1,
            "question_text": "Опишите основные применения компьютерного зрения в медицине.",
            "score_criteria": {
                "keywords": ["диагностика", "медицинские снимки", "опухоли", "патологии", "ультразвуковые исследования"],
                "points": [
                    "Упоминание диагностики заболеваний по снимкам（3）",
                    "Примеры: рентген, МРТ, УЗИ（3）",
                    "Выделение опухолей/патологий（2）",
                    "Структурированный ответ（2）"
                ],
                "full_score": 10
            }
        },
        # 可添加更多章节的主观题...
    ]

    # 导入到主观题专用数据库
    db.subjective_db.import_subjective_questions(subjective_questions_data)
    print("主观题导入完成！")

if __name__ == "__main__":
    main()