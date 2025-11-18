"""题目导入脚本 - 运行后自动创建表并导入题目"""
from db_manager import DatabaseManager
from db_manager import get_user_data_dir
import os
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
        },

        # 第1章 1.2 小节（Основные возможности библиотек компьютерного зрения）
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 1,
            "question_text": "Какая библиотека широко используется для обработки изображений в Python?",
            "option_a": "OpenCV",
            "option_b": "TensorFlow",
            "option_c": "Django",
            "option_d": "NumPy",
            "correct_answer": "A"
        },
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 2,
            "question_text": "Что позволяет делать библиотека OpenCV?",
            "option_a": "Обрабатывать и анализировать изображения в реальном времени",
            "option_b": "Создавать веб-приложения",
            "option_c": "Оптимизировать базы данных",
            "option_d": "Разрабатывать мобильные игры",
            "correct_answer": "A"
        },
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 3,
            "question_text": "Какая библиотека специализируется на компьютерном зрении с использованием глубокого обучения?",
            "option_a": "PyTorch Vision",
            "option_b": "Pandas",
            "option_c": "Matplotlib",
            "option_d": "Scikit-learn",
            "correct_answer": "A"
        },
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 4,
            "question_text": "Что такое Haar cascades в OpenCV?",
            "option_a": "Метод для обнаружения объектов (например, лиц)",
            "option_b": "Алгоритм сжатия изображений",
            "option_c": "Функция для изменения размера видео",
            "option_d": "Инструмент для создания анимаций",
            "correct_answer": "A"
        },
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 5,
            "question_text": "Какая функция OpenCV используется для чтения изображений из файла?",
            "option_a": "cv2.imread()",
            "option_b": "cv2.write()",
            "option_c": "cv2.load()",
            "option_d": "cv2.read_image()",
            "correct_answer": "A"
        },
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 6,
            "question_text": "Что позволяет делать библиотека PIL/Pillow?",
            "option_a": "Базовую обработку изображений (обрезка, изменение размера)",
            "option_b": "Создание нейросетей",
            "option_c": "Анализ сетевых пакетов",
            "option_d": "Обработка естественного языка",
            "correct_answer": "A"
        },
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 7,
            "question_text": "Какая библиотека предоставляет предобученные модели для обнаружения объектов?",
            "option_a": "Detectron2",
            "option_b": "Flask",
            "option_c": "Requests",
            "option_d": "NLTK",
            "correct_answer": "A"
        },
        {
            "chapter_num": 1,
            "section_num": 2,
            "question_num": 8,
            "question_text": "Какой формат изображения не поддерживается большинством библиотек компьютерного зрения?",
            "option_a": ".exe",
            "option_b": ".jpg",
            "option_c": ".png",
            "option_d": ".bmp",
            "correct_answer": "A"
        },

        # 第2章 1.1 小节（Пиксели, цветовые пространства）
        {
            "chapter_num": 2,
            "section_num": 1,
            "question_num": 1,
            "question_text": "Что такое пиксель в цветном изображении?",
            "option_a": "Комбинация значений каналов красного, зеленого и синего (RGB)",
            "option_b": "Одно число, определяющее яркость",
            "option_c": "Тип файла для хранения изображений",
            "option_d": "Алгоритм сглаживания границ",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 1,
            "question_num": 2,
            "question_text": "Какое из цветовых пространств используется в большинстве цифровых камер?",
            "option_a": "RGB",
            "option_b": "CMYK",
            "option_c": "HSV",
            "option_d": "YUV",
            "correct_answer": "A"
        },
            {
        "chapter_num": 2,
        "section_num": 1,
        "question_num": 3,
        "question_text": "В каком диапазоне находятся значения каналов в цветовом пространстве RGB для 8-битных изображений?",
        "option_a": "0-255",
        "option_b": "0-100",
        "option_c": "1-1024",
        "option_d": "-128 до 127",
        "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 1,
            "question_num": 4,
            "question_text": "Что означает буква H в цветовом пространстве HSV?",
            "option_a": "Оттенок (Hue)",
            "option_b": "Яркость (Brightness)",
            "option_c": "Насыщенность (Saturation)",
            "option_d": "Контраст (Contrast)",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 1,
            "question_num": 5,
            "question_text": "Как получить черно-белое изображение из цветного RGB?",
            "option_a": "Вычислить среднее значение каналов R, G и B для каждого пикселя",
            "option_b": "Удалить канал синего цвета",
            "option_c": "Умножить все каналы на 0.5",
            "option_d": "Преобразовать в цветовое пространство CMYK",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 1,
            "question_num": 6,
            "question_text": "Какое цветовое пространство удобно использовать для сегментации объектов по яркости?",
            "option_a": "HSV (благодаря каналу V — яркости)",
            "option_b": "RGB (благодаря каналу R — красному)",
            "option_c": "CMYK (благодаря каналу K — черному)",
            "option_d": "YUV (благодаря каналу Y — цвету)",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 1,
            "question_num": 7,
            "question_text": "Что произойдет с пикселем, если значение его канала в RGB превысит 255 при обработке?",
            "option_a": "Значение будет обрезано до 255 (сaturation)",
            "option_b": "Изображение испортится шумом",
            "option_c": "Значение автоматически уменьшится в 2 раза",
            "option_d": "Канал перестанет отображаться",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 1,
            "question_num": 8,
            "question_text": "Для какой области применения чаще используется цветовое пространство CMYK?",
            "option_a": "Печатная промышленность",
            "option_b": "Электронные дисплеи",
            "option_c": "Мобильные камеры",
            "option_d": "Медицинская визуализация",
            "correct_answer": "A"
        },
        {
        "chapter_num": 2,
        "section_num": 2,
        "question_num": 1,
        "question_text": "Какая функция OpenCV используется для преобразования изображения из RGB в HSV?",
        "option_a": "cv2.cvtColor() с параметром cv2.COLOR_BGR2HSV",
        "option_b": "cv2.convert() с параметром 'rgb2hsv'",
        "option_c": "cv2.transform_color() с кодом 1",
        "option_d": "cv2.change_space() с режимом 'hsv'",
        "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 2,
            "question_num": 2,
            "question_text": "Как извлечь красный канал из изображения в формате RGB?",
            "option_a": "Использовать индексацию: red_channel = img[:, :, 2]",
            "option_b": "Применить функцию cv2.get_red()",
            "option_c": "Преобразовать изображение в grayscale и разделить на каналы",
            "option_d": "Умножить изображение на матрицу [1, 0, 0]",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 2,
            "question_num": 3,
            "question_text": "Почему преобразование в HSV упрощает сегментацию объектов по цвету?",
            "option_a": "Канал H (оттенок) независим от яркости, что облегчает выделение цвета",
            "option_b": "HSV имеет больше каналов, чем RGB",
            "option_c": "HSV использует целые числа, а RGB — дробные",
            "option_d": "HSV автоматически удаляет шум",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 2,
            "question_num": 4,
            "question_text": "Какая функция OpenCV разделяет изображение на отдельные каналы?",
            "option_a": "cv2.split()",
            "option_b": "cv2.separate()",
            "option_c": "cv2.divide_channels()",
            "option_d": "cv2.extract()",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 2,
            "question_num": 5,
            "question_text": "Как объединить отдельные каналы обратно в цветное изображение?",
            "option_a": "Использовать функцию cv2.merge()",
            "option_b": "Сложить каналы поэлементно",
            "option_c": "Преобразовать каждый канал в grayscale и объединить",
            "option_d": "Использовать cv2.concat() с осью 2",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 2,
            "question_num": 6,
            "question_text": "В чем разница между форматами BGR и RGB в OpenCV?",
            "option_a": "Порядок каналов: BGR — синий, зеленый, красный; RGB — красный, зеленый, синий",
            "option_b": "BGR используется для видео, RGB — для статичных изображений",
            "option_c": "BGR поддерживает больше цветов, чем RGB",
            "option_d": "BGR хранит каналы в 16-битном формате, RGB — в 8-битном",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 2,
            "question_num": 7,
            "question_text": "Какое преобразование цветового пространства обычно применяется для уменьшения цветового шума?",
            "option_a": "Преобразование в grayscale (уменьшение количества каналов)",
            "option_b": "Преобразование в CMYK",
            "option_c": "Увеличение насыщенности в HSV",
            "option_d": "Перестановка каналов в RGB",
            "correct_answer": "A"
        },
        {
            "chapter_num": 2,
            "section_num": 2,
            "question_num": 8,
            "question_text": "В каком диапазоне значения канала S (насыщенность) в цветовом пространстве HSV для 8-битных изображений?",
            "option_a": "0-255",
            "option_b": "0-360",
            "option_c": "0-100",
            "option_d": "1-10",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 1,
            "question_text": "Какая функция OpenCV используется для изменения размера изображения?",
            "option_a": "cv2.resize()",
            "option_b": "cv2.scale()",
            "option_c": "cv2.resize_image()",
            "option_d": "cv2.change_size()",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 2,
            "question_text": "Как сохранить пропорции изображения при масштабировании?",
            "option_a": "Использовать один коэффициент масштабирования для ширины и высоты",
            "option_b": "Увеличивать ширину в 2 раза, а высоту в 3 раза",
            "option_c": "Преобразовать изображение в квадрат перед масштабированием",
            "option_d": "Использовать функцию cv2.ignore_ratio()",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 3,
            "question_text": "Какая единица измерения углов используется в функциях поворота изображений OpenCV?",
            "option_a": "Градусы",
            "option_b": "Радианы",
            "option_c": "Десятичные градусы",
            "option_d": "Секунды",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 4,
            "question_text": "Что такое центр вращения изображения?",
            "option_a": "Точка (x, y) относительно которой происходит вращение (часто центр изображения)",
            "option_b": "Верхний левый угол изображения",
            "option_c": "Точка пересечения диагоналей кадра",
            "option_d": "Любая точка на границе изображения",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 5,
            "option_a": "INTER_LINEAR ( билинейная интерполяция)",
            "option_b": "INTER_NEAREST (ближайший сосед)",
            "option_c": "INTER_AREA (интерполяция по площади)",
            "option_d": "INTER_CUBIC (бикубическая интерполяция)",
            "question_text": "Какой метод интерполяции лучше использовать для увеличения изображения с минимальными искажениями?",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 6,
            "question_text": "Какая функция OpenCV используется для отражения (зеркального переворачивания) изображения?",
            "option_a": "cv2.flip()",
            "option_b": "cv2.mirror()",
            "option_c": "cv2.reflect()",
            "option_d": "cv2.turn()",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 7,
            "question_text": "Как вырезать прямоугольную область из изображения в OpenCV?",
            "option_a": "Использовать индексацию: cropped = img[y1:y2, x1:x2]",
            "option_b": "Вызвать функцию cv2.crop(img, x1, y1, x2, y2)",
            "option_c": "Преобразовать изображение в массив и удалить лишние строки/столбцы",
            "option_d": "Использовать маску с нулями в невыбранных областях",
            "correct_answer": "A"
        },
        {
            "chapter_num": 3,
            "section_num": 1,
            "question_num": 8,
            "question_text": "Что произойдет с изображением при повороте на 180 градусов?",
            "option_a": "Изображение будет перевернуто как по горизонтали, так и по вертикали",
            "option_b": "Изображение сдвинется влево на пол ширины",
            "option_c": "Будет создан новый кадр с черными полями",
            "option_d": "Цвета изображения инвертируются",
            "correct_answer": "A"
        },
            {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 1,
        "question_text": "Какая функция OpenCV применяет Гауссово размытие?",
        "option_a": "cv2.GaussianBlur()",
        "option_b": "cv2.blurGaussian()",
        "option_c": "cv2.gaussian_filter()",
        "option_d": "cv2.soften()",
        "correct_answer": "A"
    },
    {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 2,
        "question_text": "Какого размера ядро используется для размытия по среднему (box blur) в OpenCV?",
        "option_a": "Нечетного размера (например, 3x3, 5x5)",
        "option_b": "Только 2x2",
        "option_c": "Только 10x10",
        "option_d": "Четного размера (например, 4x4)",
        "correct_answer": "A"
    },
    {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 3,
        "question_text": "Какой фильтр эффективно удаляет шум типа 'соль и перец'?",
        "option_a": "Медианный фильтр",
        "option_b": "Гауссово размытие",
        "option_c": "Линейное размытие",
        "option_d": "Фильтр Собеля",
        "correct_answer": "A"
    },
    {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 4,
        "question_text": "Какой ядро используется для повышения резкости изображения?",
        "option_a": "Ядро с положительным значением в центре и отрицательными на краях (например, [[0, -1, 0], [-1, 5, -1], [0, -1, 0]])",
        "option_b": "Ядро со всеми положительными значениями (например, [[1, 1, 1], [1, 1, 1], [1, 1, 1]])",
        "option_c": "Ядро с нулевыми значениями в центре",
        "option_d": "Ядро 1x1 с значением 2",
        "correct_answer": "A"
    },
    {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 5,
        "question_text": "Что сохраняет билатеральное фильтрование при размытии изображения?",
        "option_a": "Краевые линии (границы объектов)",
        "option_b": "Шум",
        "option_c": "Мелкие детали",
        "option_d": "Яркость фона",
        "correct_answer": "A"
    },
    {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 6,
        "question_text": "Для чего используется фильтр Собеля?",
        "option_a": "Обнаружение краев по горизонтали и вертикали",
        "option_b": "Удаление цветового шума",
        "option_c": "Увеличение контраста",
        "option_d": "Преобразование изображения в grayscale",
        "correct_answer": "A"
    },
    {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 7,
        "question_text": "Как влияет размытие на краевые линии изображения?",
        "option_a": "Сглаживает их, увеличивая ширину",
        "option_b": "Усиливает их, делая более резкими",
        "option_c": "Изменяет их цвет",
        "option_d": "Удаляет их полностью",
        "correct_answer": "A"
    },
    {
        "chapter_num": 3,
        "section_num": 2,
        "question_num": 8,
        "question_text": "Что определяет параметр sigma в Гауссовом фильтре?",
        "option_a": "Степень размытия (больше значение — сильнее размытие)",
        "option_b": "Размер ядра",
        "option_c": "Количество итераций фильтрации",
        "option_d": "Контрастность результата",
        "correct_answer": "A"
    },
        {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 1,
        "question_text": "Какой алгоритм обнаружения краев известен своей точностью и используется для выделения тонких и плавных границ?",
        "option_a": "Алгоритм Кэнни",
        "option_b": "Алгоритм Лапласа",
        "option_c": "Оператор Робертса",
        "option_d": "Фильтр Щарра",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 2,
        "question_text": "Какая функция OpenCV реализует алгоритм Кэнни для обнаружения краев?",
        "option_a": "cv2.Canny()",
        "option_b": "cv2.edgeCanny()",
        "option_c": "cv2.detectEdges()",
        "option_d": "cv2.cannyEdge()",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 3,
        "question_text": "Какое из основных этапов алгоритма Кэнни отвечает за удаление шумов перед обнаружением краев?",
        "option_a": "Гауссово размытие",
        "option_b": "Определение градиента",
        "option_c": "Нейтрализация немаксимальных значений",
        "option_d": "Пороговая обработка с гистерезисом",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 4,
        "question_text": "Оператор Собеля используется для вычисления градиента изображения в каких направлениях?",
        "option_a": "Горизонтальном и вертикальном",
        "option_b": "Диагональных (45° и 135°)",
        "option_c": "Только горизонтальном",
        "option_d": "Только вертикальном",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 5,
        "question_text": "Что измеряет градиент изображения при обнаружении краев?",
        "option_a": "Скорость изменения яркости пикселей",
        "option_b": "Среднюю яркость области",
        "option_c": "Количество цветов в кадре",
        "option_d": "Размер объекта",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 6,
        "question_text": "Как влияет повышение нижнего порога в алгоритме Кэнни на результат?",
        "option_a": "Уменьшает количество обнаруженных краев (оставляет только самые контрастные)",
        "option_b": "Увеличивает количество шумовых краев",
        "option_c": "Сглаживает границы больше",
        "option_d": "Изменяет направление краев",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 7,
        "question_text": "Какой оператор использует вторую производную для обнаружения краев?",
        "option_a": "Оператор Лапласа",
        "option_b": "Оператор Собеля",
        "option_c": "Алгоритм Кэнни",
        "option_d": "Фильтр Прюитта",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 1,
        "question_num": 8,
        "question_text": "Почему алгоритм Кэнни использует два порога (верхний и нижний)?",
        "option_a": "Чтобы сохранить связность краев (нижний порог продолжает слабые участки, соединенные с сильными)",
        "option_b": "Чтобы обработать светлые и темные области отдельно",
        "option_c": "Чтобы разделить горизонтальные и вертикальные краи",
        "option_d": "Чтобы уменьшить размер изображения",
        "correct_answer": "A"
    },
        {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 1,
        "question_text": "Какая функция OpenCV используется для поиска контуров на бинарном изображении?",
        "option_a": "cv2.findContours()",
        "option_b": "cv2.detectContours()",
        "option_c": "cv2.getContours()",
        "option_d": "cv2.extractContours()",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 2,
        "question_text": "Что такое контур в компьютерном зрении?",
        "option_a": "Последовательность точек, образующих границу объекта",
        "option_b": "Средняя яркость объекта",
        "option_c": "Цветовой диапазон объекта",
        "option_d": "Тип фильтра для обработки изображения",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 3,
        "question_text": "Какой параметр в функции cv2.findContours() определяет, сохранять ли все точки контура или только их упрощенную версию?",
        "option_a": "mode (например, cv2.CHAIN_APPROX_SIMPLE для упрощения)",
        "option_b": "method (например, cv2.LINE_8 для типа связи)",
        "option_c": "threshold (порог контура)",
        "option_d": "color (цвет контура)",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 4,
        "question_text": "Какая функция OpenCV рисует найденные контуры на изображении?",
        "option_a": "cv2.drawContours()",
        "option_b": "cv2.plotContours()",
        "option_c": "cv2.showContours()",
        "option_d": "cv2.renderContours()",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 5,
        "question_text": "Что возвращает функция cv2.contourArea()?",
        "option_a": "Площадь, ограниченную контуром",
        "option_b": "Длину контура",
        "option_c": "Количество точек в контуре",
        "option_d": "Центр масс контура",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 6,
        "question_text": "Как получить ограничивающий прямоугольник для контура?",
        "option_a": "Использовать функцию cv2.boundingRect()",
        "option_b": "Вычислить среднюю координату точек контура",
        "option_c": "Преобразовать контур в бинарное изображение",
        "option_d": "Использовать оператор Собеля на контуре",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 7,
        "question_text": "Что такое иерархия контуров?",
        "option_a": "Отношение вложенности контуров (родительские и дочерние)",
        "option_b": "Упорядочение контуров по площади",
        "option_c": "Список цветов контуров",
        "option_d": "Метод сортировки контуров по направлению",
        "correct_answer": "A"
    },
    {
        "chapter_num": 4,
        "section_num": 2,
        "question_num": 8,
        "question_text": "Какой метод используется для аппроксимации контура простым многоугольником (например, квадратом вместо сложной формы)?",
        "option_a": "Метод Дугласа-Пекера (cv2.approxPolyDP())",
        "option_b": "Гауссово размытие контура",
        "option_c": "Преобразование контура в grayscale",
        "option_d": "Фильтрация контура медианным фильтром",
        "correct_answer": "A"
    },
        {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 1,
        "question_text": "Какой алгоритм используется для обнаружения углов на изображении (например, углов шахматной доски)?",
        "option_a": "Алгоритм Харриса (Harris Corner Detection)",
        "option_b": "Алгоритм Кэнни",
        "option_c": "Гауссово размытие",
        "option_d": "Медианный фильтр",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 2,
        "question_text": "Какая функция OpenCV реализует детектор углов Харриса?",
        "option_a": "cv2.cornerHarris()",
        "option_b": "cv2.harrisCorners()",
        "option_c": "cv2.detectCorners()",
        "option_d": "cv2.findCorners()",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 3,
        "question_text": "Что такое ключевая точка на изображении?",
        "option_a": "Уникальная точка, стабильная относительно преобразований (поворота, масштабирования)",
        "option_b": "Любая точка на границе объекта",
        "option_c": "Точка с максимальной яркостью",
        "option_d": "Центр изображения",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 4,
        "question_text": "Какой алгоритм извлекает ключевые точки, устойчивые к изменениям масштаба?",
        "option_a": "SIFT (Scale-Invariant Feature Transform)",
        "option_b": "Оператор Собеля",
        "option_c": "Алгоритм Кэнни",
        "option_d": "Метод Дугласа-Пекера",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 5,
        "question_text": "Что описывает дескриптор ключевой точки?",
        "option_a": "Локальные особенности области вокруг точки (например, направление градиентов)",
        "option_b": "Размер изображения",
        "option_c": "Цвет ключевой точки",
        "option_d": "Расстояние до ближайшего контура",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 6,
        "question_text": "Какую текстуру описывает метод GLCM (Gray-Level Co-Occurrence Matrix)?",
        "option_a": "Распределение отношений между яркостями соседних пикселей",
        "option_b": "Среднюю яркость изображения",
        "option_c": "Количество углов в текстуре",
        "option_d": "Размер пятен на текстуре",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 7,
        "question_text": "Зачем используется детектор FAST (Features from Accelerated Segment Test)?",
        "option_a": "Быстрое обнаружение ключевых точек в реальном времени",
        "option_b": "Улучшение контраста изображения",
        "option_c": "Преобразование цветовых пространств",
        "option_d": "Удаление шумов типа 'соль и перец'",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 1,
        "question_num": 8,
        "question_text": "Какой параметр влияет на чувствительность детектора углов Харриса?",
        "option_a": "Коэффициент k (от 0.04 до 0.06)",
        "option_b": "Размер ядра Гауссового фильтра",
        "option_c": "Порог яркости",
        "option_d": "Количество итераций",
        "correct_answer": "A"
    },
        {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 1,
        "question_text": "Какая функция OpenCV используется для шаблонного сопоставления (поиска участка изображения в другом изображении)?",
        "option_a": "cv2.matchTemplate()",
        "option_b": "cv2.findTemplate()",
        "option_c": "cv2.matchPattern()",
        "option_d": "cv2.searchTemplate()",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 2,
        "question_text": "Что означает параметр method в функции cv2.matchTemplate()?",
        "option_a": "Алгоритм вычисления сходства между шаблоном и участком изображения",
        "option_b": "Размер шаблона",
        "option_c": "Цветовая палитра для отображения результатов",
        "option_d": "Количество итераций сопоставления",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 3,
        "question_text": "Какой метод сопоставления шаблонов подходит для поиска объектов при изменении освещения?",
        "option_a": "TM_CCOEFF_NORMED (нормированный коэффициент корреляции)",
        "option_b": "TM_SQDIFF (квадратичная разница)",
        "option_c": "TM_SQDIFF_NORMED (нормированная квадратичная разница)",
        "option_d": "TM_CCORR (кросс-корреляция)",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 4,
        "question_text": "Что такое кросс-сопоставление ключевых точек?",
        "option_a": "Сравнение дескрипторов ключевых точек двух изображений для поиска соответствий",
        "option_b": "Сравнение размеров объектов в изображениях",
        "option_c": "Преобразование цветовых пространств двух изображений",
        "option_d": "Удаление несовпадающих участков изображений",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 5,
        "question_text": "Какой алгоритм используется для эффективного сопоставления дескрипторов ключевых точек?",
        "option_a": "FLANN (Fast Library for Approximate Nearest Neighbors)",
        "option_b": "Алгоритм Кэнни",
        "option_c": "Медианный фильтр",
        "option_d": "Гауссово размытие",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 6,
        "question_text": "Какой тест помогает отфильтровать неправильные соответствия при сопоставлении ключевых точек?",
        "option_a": "Тест ближайшего соседа (k-nearest neighbor, k=2)",
        "option_b": "Тест на контрастность",
        "option_c": "Тест на размер объекта",
        "option_d": "Тест на яркость",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 7,
        "question_text": "Почему шаблонное сопоставление не подходит для поиска объектов при масштабировании или повороте?",
        "option_a": "Шаблон строго привязан к исходному размеру и ориентации",
        "option_b": "Оно работает только с черно-белыми изображениями",
        "option_c": "Оно требует слишком много вычислительных ресурсов",
        "option_d": "Оно не учитывает цвет объекта",
        "correct_answer": "A"
    },
    {
        "chapter_num": 5,
        "section_num": 2,
        "question_num": 8,
        "question_text": "Как найти координаты лучших совпадений при шаблонном сопоставлении?",
        "option_a": "Использовать функцию cv2.minMaxLoc() для поиска экстремумов в матрице сходства",
        "option_b": "Сравнить все пиксели изображения вручную",
        "option_c": "Преобразовать результат в бинарное изображение и найти контуры",
        "option_d": "Вычислить среднюю яркость участков изображения",
        "correct_answer": "A"
    },
    ]
    
    # 3. 导入题目到指定数据库
    success = db.import_questions_to_db(
        questions_data,
        db_path=os.path.join(os.environ['LOCALAPPDATA'], 'ComputerVisionLearning','questions.db')
    )
    if success:
        print("题目导入完成！")
    else:
        print("题目导入失败，请检查路径和数据格式。")

if __name__ == "__main__":
    main()