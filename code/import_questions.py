"""题目导入脚本 - 运行后自动创建表并导入题目"""
from db_manager import DatabaseManager
from db_manager import get_user_data_dir
import os

def get_default_questions():
    """返回默认题目数据（仅1.1章节）"""
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

def main():
    """导入题目到数据库"""
    db = DatabaseManager()
    questions_data = get_default_questions()
    
    success = db.import_questions_to_db(questions_data)
    if success:
        print("题目导入成功！")
    else:
        print("题目导入失败！")

if __name__ == "__main__":
    main()
