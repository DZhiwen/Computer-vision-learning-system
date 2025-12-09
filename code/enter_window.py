import os
import sys
from PySide6.QtWidgets import (
    QWidget, QTreeWidget, QStackedWidget, QProgressBar, QPushButton,
    QVBoxLayout, QTabWidget, QTabBar, QTreeWidgetItem, QTextEdit, QTextBrowser,
    QRadioButton 
)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QColor
from db_manager import DatabaseManager, resource_path
import resources_rc 
import io
from contextlib import redirect_stdout

class EnterWindow(QWidget):
    def __init__(self, user_id, parent=None):
        super(EnterWindow, self).__init__(parent)
        
        # 保存用户ID以便保存进度
        # Сохранение ID пользователя для сохранения прогресса
        self.user_id = user_id
        self.db = DatabaseManager()
        
        # 动态加载 Enter.ui 文件
        # Динамическая загрузка файла Enter.ui
        ui_file_path = resource_path(os.path.join("ui", "Enter.ui"))
        ui_file = QFile(ui_file_path)
        
        if not ui_file.open(QIODevice.ReadOnly):
            # 无法打开UI文件
            # Невозможно открыть UI файл
            print(f"Невозможно открыть UI файл: {ui_file_path}")
            return
            
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)


        # 绑定登出按钮
        # Привязка кнопки выхода
        self.ui.findChild(QWidget, "Logout").clicked.connect(self.close)
        self.setWindowTitle("Модуль обучения компьютерному зрению - Основной интерфейс")

        # 初始化课程状态
        # Инициализация состояния курса
        self.current_chapter = 0  # 当前章节索引  # Текущий индекс главы
        self.current_step = 0     # 当前步骤（章节中的标签页） # Текущий шаг (вкладка в главе)
        self.completed_chapters = {}  # 已完成章节 {章节索引: {步骤索引: 完成}} # Завершенные главы {индекс_главы: {индекс_шага: завершено}}
        
        self.user_answers = {}
        
        self.course_map = [
            # 章节及其对应页面
            # Главы и их соответствие страницам
            ("Глава 1. Введение в компьютерное зрение", [
                ("1.1. Основные понятия и применения", "page1_1", 0), # (名称, 页面id, 标签索引) # (название, id страницы, индекс вкладки)
                ("1.2. Основные возможности библиотек компьютерного зрения", "page1_2", 0),
                ("1.3. Практическое задание", "page1_3", 0)
            ]),
            ("Глава 2. Азы работы с изображениями", [
                ("2.1. Пиксели, цветовые пространства", "page2_1", 0),
                ("2.2. Фильтрация изображений", "page2_2", 0),
                ("2.3. Практическое задание", "page2_3", 0)
            ]),
            ("Глава 3. Преобразование признаков", [
                ("3.1. Выделение контуров и углов", "page3_1", 0),
                ("3.2. SIFT, SURF и ORB", "page3_2", 0),
                ("3.3. Практическое задание", "page3_3", 0)
            ]),
            ("Глава 4. Обнаружение объектов", [
                ("4.1. Каскады Хаара", "page4_1", 0),
                ("4.2. Современные методы (YOLO, SSD)", "page4_2", 0),
                ("4.3. Практическое задание", "page4_3", 0)
            ]),
            ("Глава 5. Сегментация изображений", [
                ("5.1. Классическая сегментация", "page5_1", 0),
                ("5.2. Нейросетевые подходы (U-Net, Mask R-CNN)", "page5_2", 0),
                ("5.3. Практическое задание", "page5_3", 0)
            ]),
            ("Глава 6. Генеративно-состязательные модели (GAN)", [
                ("6.1. Основы GAN", "page6_1", 0),
                ("6.2. StyleGAN и CycleGAN", "page6_2", 0),
                ("6.3. Практическое задание", "page6_3", 0)
            ]),
            ("Глава 7. Оценка глубины (Depth Estimation)", [
                ("7.1. Стереозрение и нейросети", "page7_1", 0),
                ("7.2. Применение в AR и робототехнике", "page7_2", 0),
                ("7.3. Практическое задание", "page7_3", 0)
            ])
        ]
        
        # 已完成标签的颜色
        # Определение цвета заголовка завершенной вкладки
        self.completed_color = "#329600"  # 绿色 # Зеленый
        self.selected_completed_color = "#55ff00"  # 选中时的色

        # 总共按钮数量
        # Общее количество кнопок
        self.total_buttons = 49
        
        self.init_components()
        
        # 加载用户进度
        # Загрузка прогресса пользователя
        self.load_user_progress()
        self.load_user_answers()  
        # 更新界面显示
        # Обновление отображения интерфейса
        self.update_display()

    def init_components(self):
        """初始化界面组件连接
        Инициализация соединений компонентов интерфейса
        """
        self.course_tree = self.ui.findChild(QTreeWidget, "courseTree")
        self.course_tree.itemClicked.connect(self.on_course_selected)
        self.stacked_widget = self.ui.findChild(QStackedWidget, "stackedWidget")
        self.progress_bar = self.ui.findChild(QProgressBar, "progressBar")
        
        # 根据课程结构填充树状菜单
        # Заполнение древовидного меню из структуры курса
        self.populate_course_tree()
        
        # 提前保存每章的TabWidget
        # Предварительное сохранение TabWidget для каждой главы
        self.chapter_tabs = []
        self.page_indices = {}  # 页面索引字典 # Словарь для быстрого доступа к индексам страниц
        
        # 查找所有页面和标签页
        # Находим все страницы и вкладки
        for chapter_idx in range(1, 8):  # 7 глав
            for section_idx in range(1, 4):  # 3 раздела в каждой главе
                page_name = f"page{chapter_idx}_{section_idx}"
                page = self.stacked_widget.findChild(QWidget, page_name)
                if page:
                    # 查找 stackedWidget 中的页面索引
                    # Находим индекс страницы в stackedWidget
                    for j in range(self.stacked_widget.count()):
                        if self.stacked_widget.widget(j) == page:
                            self.page_indices[page_name] = j
                            break
                    
                    # 查找当前页面的TabWidget
                    # Находим TabWidget для текущей страницы
                    tab_widget = page.findChild(QTabWidget, f"contentTabs{chapter_idx}_{section_idx}")
                    if tab_widget:
                        tab_widget.currentChanged.connect(self.update_current_position)
                        self.chapter_tabs.append(tab_widget)
                    else:
                        # 没有TabWidget的页面加入None
                        # Добавляем None для страниц без TabWidget
                        self.chapter_tabs.append(None)
        
        self.connect_next_buttons()
        self.connect_code_buttons()
        self.connect_question_submit_buttons()
    def connect_question_submit_buttons(self):
        """
        连接所有测试题的提交按钮
        """
        for chapter_idx in range(1, 8):  # 7 chapters
            for section_idx in range(1, 4):  # 3 sections per chapter
                for q_idx in range(1, 9):  # 每节最多8题
                    btn_name = f"submitButton{chapter_idx}_{section_idx}_{q_idx}"
                    btn = self.ui.findChild(QPushButton, btn_name)
                    if btn:
                        btn.clicked.connect(self.handle_question_submit)
    
    def handle_question_submit(self):
        """处理测试题提交按钮点击，判断正误并高亮
        Обработка нажатия кнопки отправки ответа на вопрос теста"""
        sender = self.sender()
        if not sender:
            return

        btn_name = sender.objectName()  # submitButtonx_y_z
        if not btn_name.startswith("submitButton"):
            return

        # 解析出题号
        try:
            chapter_idx, section_idx, q_idx = btn_name[len("submitButton"):].split('_')
            chapter_idx = int(chapter_idx) - 1  # 转换为0-索引
            section_idx = int(section_idx) - 1  # 转换为0-索引
            q_idx = int(q_idx)
        except Exception:
            return

        # 正确答案按钮名
        correct_radio_name = f"radioButton{chapter_idx+1}_{section_idx+1}_{q_idx}_r"

        # 找到所有radioButton
        radio_buttons = []
        correct_radio = self.ui.findChild(QRadioButton, correct_radio_name)
        if correct_radio:
            radio_buttons.append(correct_radio)

        # 如果没找到全部radio，尝试直接找groupBox下所有QRadioButton
        if len(radio_buttons) < 4:
            group_box_name = f"groupBox{chapter_idx+1}_{section_idx+1}_{q_idx}"
            group_box = self.ui.findChild(QWidget, group_box_name)
            if group_box:
                radio_buttons = group_box.findChildren(QRadioButton)

        # 判断选择
        selected_radio = None
        for rb in radio_buttons:
            if rb.isChecked():
                selected_radio = rb
                break

        # 恢复所有按钮颜色
        for rb in radio_buttons:
            rb.setStyleSheet("")

        if not selected_radio:
            # 没有选择
            return

        is_correct = (selected_radio.objectName() == correct_radio_name)
        
        if is_correct:
            # 正确
            selected_radio.setStyleSheet("color: white; background-color: #4CAF50;")
        else:
            # 错误
            selected_radio.setStyleSheet("color: white; background-color: #e74c3c;")
            # 正确选项也高亮为绿色
            if correct_radio:
                correct_radio.setStyleSheet("color: white; background-color: #4CAF50;")
        
        # 保存答题记录到数据库
        self.db.save_quiz_answer(
            self.user_id,
            chapter_idx,
            section_idx,
            q_idx,
            selected_radio.objectName(),  # 保存选择的按钮名称
            1 if is_correct else 0
        )
        
        # 更新本地答题记录
        if chapter_idx not in self.user_answers:
            self.user_answers[chapter_idx] = {}
        if section_idx not in self.user_answers[chapter_idx]:
            self.user_answers[chapter_idx][section_idx] = {}
        
        self.user_answers[chapter_idx][section_idx][q_idx] = {
            'selected_answer': selected_radio.objectName(),
            'is_correct': 1 if is_correct else 0
        }

    def connect_code_buttons(self):
        """连接所有代码运行按钮
        Подключение всех кнопок запуска кода
        """
        for chapter_idx in range(1, 8):  # 7 глав
            # 只连接每章的第3页（实践页面）
            # Подключаем только 3-ю страницу каждой главы (практическое задание)
            btn_name = f"codeButton{chapter_idx}_3"
            btn = self.ui.findChild(QPushButton, btn_name)
            if btn:
                btn.clicked.connect(self.run_code)
                btn.setText("Запустить код")  # 设置按钮文本 # Устанавливаем текст кнопки

    def run_code(self):
        """运行Python代码
        Запуск Python-кода
        """
        sender = self.sender()
        if not sender:
            return
            
        # 从按钮名称获取章节和页面信息
        # Получаем информацию о главе и странице из имени кнопки
        btn_name = sender.objectName()  # codeButtonX_Y
        if not btn_name.startswith("codeButton"):
            return
            
        chapter_page = btn_name[len("codeButton"):]  # X_Y
        parts = chapter_page.split('_')
        if len(parts) != 2:
            return
            
        chapter_idx, page_idx = parts
        
        # 查找对应的文本编辑器和输出区域
        # Находим соответствующий текстовый редактор и область вывода
        text_edit = self.ui.findChild(QTextEdit, f"textEdit{chapter_idx}_{page_idx}")
        text_browser = self.ui.findChild(QTextBrowser, f"textBrowser{chapter_idx}_{page_idx}")
        
        if not text_edit or not text_browser:
            return
            
        # 获取代码并执行
        # Получаем код и выполняем его
        code = text_edit.toPlainText()
        if not code.strip():
            text_browser.setPlainText("Пожалуйста, введите код для выполнения")
            return
            
        # 捕获标准输出并执行代码
        # Перехватываем стандартный вывод и выполняем код
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                exec(code)
            result = output.getvalue()
            text_browser.setPlainText(result if result else "Код выполнен успешно")
        except Exception as e:
            text_browser.setPlainText(f"Ошибка: {str(e)}")

    def populate_course_tree(self):
        """填充课程树状菜单
        Заполнение древовидного меню курса
        """
        self.course_tree.clear()
        
        # 根据课程结构创建树节点
        # Создание элементов дерева на основе структуры курса
        for chapter_name, sections in self.course_map:
            chapter_item = QTreeWidgetItem(self.course_tree)
            chapter_item.setText(0, chapter_name)
            
            for section_name, _, _ in sections:
                section_item = QTreeWidgetItem(chapter_item)
                section_item.setText(0, section_name)
        
        # 展开所有树节点方便查看
        # Раскрыть все элементы дерева для лучшей видимости
        self.course_tree.expandAll()

    def connect_next_buttons(self):
        """连接所有'下一页'和'下一章节'按钮
        Подключение всех кнопок Next Page и Next Chapter
        """
        # 查找并连接所有 Next Page 按钮 (按照新命名规则)
        # Поиск и подключение всех кнопок Next Page (по новым правилам именования)
        for chapter_idx in range(1, 8):  # 7 глав
            for section_idx in range(1, 4):  # 每章3节
                for tab_idx in range(1, 5):  # 每节最多4个标签页
                    btn_name = f"nextPageButton{chapter_idx}_{section_idx}_{tab_idx}"
                    btn = self.ui.findChild(QPushButton, btn_name)
                    if btn:
                        btn.clicked.connect(self.next_page)
        
        # 查找并连接所有 Next Chapter 按钮
        # Поиск и подключение всех кнопок Next Chapter
        for chapter_idx in range(1, 8):  # 7 глав
            for section_idx in range(1, 4):  # 每章3节
                btn_name = f"nextChapterButton{chapter_idx}_{section_idx}"
                btn = self.ui.findChild(QPushButton, btn_name)
                if btn:
                    btn.clicked.connect(self.next_chapter)

    def update_current_position(self, index):
        """切换Tab时更新当前位置
        Обновление текущей позиции при смене вкладки
        """
        sender = self.sender()
        if sender:
            # 根据信号发送者确定章节索引
            # Определяем индекс главы по отправителю сигнала
            for chapter_idx, tab_widget in enumerate(self.chapter_tabs):
                if tab_widget == sender:
                    # 只更新当前位置
                    # Обновляем только текущую позицию
                    self.find_chapter_and_section(tab_widget, index)
                    break
        
        self.update_tab_colors()  # 新增此行

    def find_chapter_and_section(self, tab_widget, tab_index):
        """通过TabWidget和标签索引查找对应章节和小节
        Поиск соответствующей главы и раздела по TabWidget и индексу вкладки
        """
        for chapter_idx, (_, sections) in enumerate(self.course_map):
            for section_idx, (_, page_name, _) in enumerate(sections):
                page_idx = self.page_indices.get(page_name, -1)
                if page_idx >= 0:
                    page = self.stacked_widget.widget(page_idx)
                    if page:
                        # 使用新的命名规则查找TabWidget
                        # Используем новые правила именования для поиска TabWidget
                        chapter_num, section_num = page_name.replace("page", "").split("_")
                        current_tab = page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")
                        if current_tab == tab_widget:
                            self.current_chapter = chapter_idx
                            self.current_step = tab_index
                            return

    def on_course_selected(self, item):
        """处理点击课程树节点事件
        Обработка события клика по элементу дерева курса
        """
        # 获取选中项文本
        # Получаем текст выбранного элемента
        selected_text = item.text(0)
        
        # 查找对应章节和小节
        # Ищем соответствующую главу и раздел
        parent = item.parent()
        
        if parent:  # 如果是小节（章节的子项） # Если это раздел (подпункт главы)
            chapter_name = parent.text(0)
            section_name = selected_text
            
            # 查找对应页面和标签
            # Найти соответствующую страницу и вкладку
            for chapter_idx, (name, sections) in enumerate(self.course_map):
                if name == chapter_name:
                    for section_idx, (s_name, page_name, tab_idx) in enumerate(sections):
                        if s_name == section_name:
                            # 跳转到选中页面和标签
                            # Переходим к выбранной странице и вкладке
                            self.current_chapter = chapter_idx
                            self.current_step = tab_idx
                            
                            # 显示页面
                            # Показываем страницу
                            page_idx = self.page_indices.get(page_name, -1)
                            if page_idx >= 0:
                                self.stacked_widget.setCurrentIndex(page_idx)
                                
                                # 选中标签
                                # Выбираем вкладку
                                # 使用新的命名规则查找TabWidget
                                # Используем новые правила именования для поиска TabWidget
                                chapter_num, section_num = page_name.replace("page", "").split("_")
                                tab_widget = self.stacked_widget.currentWidget().findChild(
                                    QTabWidget, f"contentTabs{chapter_num}_{section_num}")
                                if tab_widget:
                                    tab_widget.setCurrentIndex(tab_idx)
                            
                            self.update_display()
                            return
    

    
    def next_page(self):
        """处理'下一页'按钮点击
        Обработка нажатия кнопки Next Page
        """
        # 获取当前TabWidget
        # Получаем текущий TabWidget
        current_page_idx = self.stacked_widget.currentIndex()
        current_page = self.stacked_widget.widget(current_page_idx)
        current_page_name = current_page.objectName()
        
        # 使用新的命名规则查找TabWidget
        # Используем новые правила именования для поиска TabWidget
        chapter_num, section_num = current_page_name.replace("page", "").split("_")
        tab_widget = current_page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")
        
        if tab_widget:
            # 标记当前标签为已完成
            # Отмечаем текущую вкладку как завершенную
            self.mark_tab_completed(current_page_idx, tab_widget.currentIndex())
            
            # 如果还有下一标签则切换
            # Переходим к следующей вкладке если возможно
            if tab_widget.currentIndex() < tab_widget.count() - 1:
                tab_widget.setCurrentIndex(tab_widget.currentIndex() + 1)
                self.current_step = tab_widget.currentIndex()
                # 保存进度
                # Сохраняем прогресс
                self.save_progress()
            else:
                # 如果是最后一标签，跳到下一页面第一标签
                # Если это последняя вкладка, переходим к первой вкладке следующей страницы
                self.next_chapter()

    def next_chapter(self):
        """处理'下一章节'按钮点击
        Обработка нажатия кнопки Next Chapter
        """
        # 标记当前标签为已完成
        # Отмечаем текущую вкладку как завершенную
        current_page_idx = self.stacked_widget.currentIndex()
        current_page = self.stacked_widget.widget(current_page_idx)
        current_page_name = current_page.objectName()
        
        # 使用新的命名规则查找TabWidget
        # Используем новые правила именования для поиска TabWidget
        chapter_num, section_num = current_page_name.replace("page", "").split("_")
        tab_widget = current_page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")
        
        if tab_widget:
            self.mark_tab_completed(current_page_idx, tab_widget.currentIndex())
        
        # 检查是否是最后一章最后一节
        # Проверяем, является ли это последней главой и разделом
        
        # 查找下一个章节和页面
        # Находим следующую главу и страницу
        for chapter_idx, (_, sections) in enumerate(self.course_map):
            for section_idx, (_, page_name, _) in enumerate(sections):
                page_idx = self.page_indices.get(page_name, -1)
                if page_idx == current_page_idx:
                    # 当前章节还有下一个小节
                    # Если есть еще разделы в текущей главе
                    if section_idx + 1 < len(sections):
                        next_page_name = sections[section_idx + 1][1]
                        next_page_idx = self.page_indices.get(next_page_name, -1)
                        if next_page_idx >= 0:
                            self.stacked_widget.setCurrentIndex(next_page_idx)
                            next_page = self.stacked_widget.widget(next_page_idx)
                            
                            # 使用新的命名规则查找TabWidget
                            # Используем новые правила именования для поиска TabWidget
                            next_chapter_num, next_section_num = next_page_name.replace("page", "").split("_")
                            next_tab_widget = next_page.findChild(
                                QTabWidget, f"contentTabs{next_chapter_num}_{next_section_num}")
                            
                            if next_tab_widget:
                                next_tab_widget.setCurrentIndex(0)
                            self.current_chapter = chapter_idx
                            self.current_step = 0
                            self.save_progress()
                            self.update_display()
                            return
                    # 如果是本章最后一节，跳到下一章第一节
                    # Если это последний раздел в главе, переходим к первому разделу следующей главы
                    elif chapter_idx + 1 < len(self.course_map):
                        next_chapter = self.course_map[chapter_idx + 1]
                        next_page_name = next_chapter[1][0][1]  # 下一章第一节页面
                        next_page_idx = self.page_indices.get(next_page_name, -1)
                        if next_page_idx >= 0:
                            self.stacked_widget.setCurrentIndex(next_page_idx)
                            next_page = self.stacked_widget.widget(next_page_idx)
                            
                            # 使用新的命名规则查找TabWidget
                            # Используем новые правила именования для поиска TabWidget
                            next_chapter_num, next_section_num = next_page_name.replace("page", "").split("_")
                            next_tab_widget = next_page.findChild(
                                QTabWidget, f"contentTabs{next_chapter_num}_{next_section_num}")
                            
                            if next_tab_widget:
                                next_tab_widget.setCurrentIndex(0)
                            self.current_chapter = chapter_idx + 1
                            self.current_step = 0
                            self.save_progress()
                            self.update_display()
                            return

    def mark_tab_completed(self, page_idx, tab_idx):
        """标记指定标签为已完成
        Отмечает указанную вкладку как завершенную
        """
        # 通过页面索引查找对应章节和小节
        # Находим соответствующую главу и раздел по индексу страницы
        current_page = self.stacked_widget.widget(page_idx)
        current_page_name = current_page.objectName()
        
        # 使用新的命名规则查找TabWidget
        # Используем новые правила именования для поиска TabWidget
        chapter_num, section_num = current_page_name.replace("page", "").split("_")
        tab_widget = current_page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")
        
        if tab_widget and 0 <= tab_idx < tab_widget.count():
            # 设置标签标题颜色为绿色
            # Устанавливаем зеленый цвет для заголовка вкладки
            tab_bar = tab_widget.tabBar()
            tab_bar.setTabTextColor(tab_idx, QColor(self.completed_color))
            
            # 查找章节和小节以保存进度
            # Находим главу и секцию для сохранения прогресса
            for chapter_idx, (_, sections) in enumerate(self.course_map):
                for section_idx, (_, page_name, _) in enumerate(sections):
                    if page_name == current_page_name:
                        # 保存进度到本地结构
                        # Сохраняем прогресс в локальной структуре
                        if chapter_idx not in self.completed_chapters:
                            self.completed_chapters[chapter_idx] = {}
                        
                        # 用section_idx和tab_idx组合作唯一key
                        # Используем комбинацию section_idx и tab_idx как ключ
                        step_key = section_idx * 10 + tab_idx  # 唯一key # Уникальный ключ для каждой вкладки
                        self.completed_chapters[chapter_idx][step_key] = 1
                        
                        # 保存到数据库
                        # Сохраняем в базу данных
                        self.db.save_chapter_progress(
                            self.user_id, 
                            chapter_idx, 
                            step_key, 
                            1
                        )
                        return

    def update_display(self):
        """刷新所有界面元素
        Обновление всех элементов интерфейса
        """
        self.update_tab_colors()  # 刷新标签颜色 # Обновляем цвета вкладок
        self.update_progress()    # 刷新进度条 # Обновляем индикатор прогресса
        self.highlight_current_course()  # 高亮当前课程树节点 # Подсвечиваем текущий элемент курса

    def update_tab_colors(self):
        """根据进度刷新所有标签颜色"""
        # 获取当前显示的页面和TabWidget
        current_page = self.stacked_widget.currentWidget()
        current_tab_widget = None
        if current_page:
            page_name = current_page.objectName()
            chapter_num, section_num = page_name.replace("page", "").split("_")
            current_tab_widget = current_page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")

        # 遍历所有页面
        for page_idx in range(self.stacked_widget.count()):
            page = self.stacked_widget.widget(page_idx)
            if not page or not page.objectName().startswith("page"):
                continue

            # 获取当前页面的TabWidget
            page_name = page.objectName()
            chapter_num, section_num = page_name.replace("page", "").split("_")
            tab_widget = page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")
            if not tab_widget:
                continue

            # 遍历所有标签页
            tab_bar = tab_widget.tabBar()
            for tab_idx in range(tab_widget.count()):
                # 检查是否为当前显示的标签页且已完成
                is_current = (tab_widget == current_tab_widget and 
                            tab_idx == tab_widget.currentIndex())
                
                # 检查是否已完成
                chapter_idx, section_idx = self._get_chapter_section_by_page_name(page_name)
                step_key = section_idx * 10 + tab_idx
                is_completed = (
                    chapter_idx in self.completed_chapters and 
                    step_key in self.completed_chapters[chapter_idx]
                )

                # 设置颜色
                if is_completed:
                    if is_current:
                        tab_bar.setTabTextColor(tab_idx, QColor(self.selected_completed_color))
                    else:
                        tab_bar.setTabTextColor(tab_idx, QColor(self.completed_color))

    def _get_chapter_section_by_page_name(self, page_name):
        """通过页面名获取章节和小节索引"""
        for chapter_idx, (_, sections) in enumerate(self.course_map):
            for section_idx, (_, p_name, _) in enumerate(sections):
                if p_name == page_name:
                    return chapter_idx, section_idx
        return -1, -1

    def update_progress(self):
        """刷新进度条
        Обновляет индикатор прогресса
        """
        # 计算总进度 - 基于已完成按钮数量
        # Расчет общего прогресса - на основе количества нажатых кнопок
        completed_tabs = 0
        
        # 统计已完成标签数
        # Подсчитываем количество завершенных вкладок
        for chapter in self.completed_chapters:
            completed_tabs += len(self.completed_chapters[chapter])
        
        # 刷新进度条 - 基于总按钮数
        # Обновляем индикатор прогресса - на основе общего количества кнопок
        progress_percentage = int((completed_tabs / self.total_buttons) * 100)
        self.progress_bar.setValue(progress_percentage)
        
        # 刷新用户总进度到数据库
        # Обновляем общий прогресс пользователя
        self.db.update_progress(
            self.user_id, 
            progress_percentage / 100.0, 
            self.completed_chapters
        )
        

    def highlight_current_course(self):
        """高亮当前课程树节点
        Подсвечивает текущий элемент в дереве курса
        """
        # 查找当前页面
        # Находим текущую страницу
        current_page_idx = self.stacked_widget.currentIndex()
        current_page = self.stacked_widget.widget(current_page_idx)
        if not current_page:
            return
            
        current_page_name = current_page.objectName()
        
        # 查找对应章节和小节
        # Ищем соответствующую главу и раздел
        for chapter_idx, (chapter_name, sections) in enumerate(self.course_map):
            for section_idx, (section_name, page_name, _) in enumerate(sections):
                if page_name == current_page_name:
                    # 查找树中对应节点
                    # Находим соответствующий элемент в дереве
                    root = self.course_tree.invisibleRootItem()
                    for i in range(root.childCount()):
                        chapter_item = root.child(i)
                        if chapter_item.text(0) == chapter_name:
                            for j in range(chapter_item.childCount()):
                                section_item = chapter_item.child(j)
                                if section_item.text(0) == section_name:
                                    self.course_tree.setCurrentItem(section_item)
                                    return

    def load_user_progress(self):
        """加载用户进度
        Загрузка прогресса пользователя
        """
        # 获取进度数据
        # Получаем данные о прогрессе
        progress_data = self.db.get_chapter_progress(self.user_id)
        
        # 刷新本地进度结构
        # Обновляем локальную структуру прогресса
        self.completed_chapters = progress_data
        
        # 恢复用户最后位置
        # Восстанавливаем последнюю позицию пользователя
        if progress_data:
            # 有进度的用户——恢复最后位置
            # Для пользователя с прогрессом - восстанавливаем последнюю позицию
            # 找到最后完成的标签
            # Находим последнюю завершенную вкладку
            last_chapter = max(progress_data.keys())
            last_steps = progress_data[last_chapter]
            
            if last_steps:
                last_step = max(last_steps.keys())
                
                # 恢复到对应页面和标签
                # Восстанавливаем позицию
                section_idx = last_step // 10
                tab_idx = last_step % 10
                
                # 跳转到对应页面和标签
                # Переходим к соответствующей странице и вкладке
                if 0 <= last_chapter < len(self.course_map):
                    sections = self.course_map[last_chapter][1]
                    if 0 <= section_idx < len(sections):
                        page_name = sections[section_idx][1]
                        page_idx = self.page_indices.get(page_name, -1)
                        
                        if page_idx >= 0:
                            self.stacked_widget.setCurrentIndex(page_idx)
                            page = self.stacked_widget.widget(page_idx)
                            
                            # 使用新的命名规则查找TabWidget
                            # Используем новые правила именования для поиска TabWidget
                            chapter_num, section_num = page_name.replace("page", "").split("_")
                            tab_widget = page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")
                            
                            if tab_widget and 0 <= tab_idx < tab_widget.count():
                                tab_widget.setCurrentIndex(tab_idx)
                                self.current_chapter = last_chapter
                                self.current_step = tab_idx
        else:
            # 新用户——显示第一章第一节
            # Для новых пользователей - показываем первый раздел первой главы
            page_idx = self.page_indices.get("page1_1", -1)
            if page_idx >= 0:
                self.stacked_widget.setCurrentIndex(page_idx)
                page = self.stacked_widget.widget(page_idx)
                tab_widget = page.findChild(QTabWidget, "contentTabs1_1")
                if tab_widget:
                    tab_widget.setCurrentIndex(0)
                
                # 设置当前章节和步骤
                # Устанавливаем текущую главу и шаг
                self.current_chapter = 0
                self.current_step = 0

    def save_progress(self):
        """保存当前进度
        Сохраняет текущий прогресс
        """
        self.update_progress()
    
    def set_user_name(self, name):
        """设置用户名显示
        Устанавливает отображение имени пользователя
        """
        enter_name_widget = self.ui.findChild(QWidget, "enter_name")
        if enter_name_widget:
            enter_name_widget.setText(name)

    def load_user_answers(self):
        """加载用户答题记录
        Загрузка ответов пользователя на вопросы"""
        # 获取答题记录数据
        self.user_answers = self.db.get_quiz_answers(self.user_id)
        
        # 恢复答题状态到界面
        self.restore_quiz_answers()   

    def restore_quiz_answers(self):
        """恢复答题状态到界面
        Восстановление состояния ответов на вопросы в интерфейсе"""
        if not self.user_answers:
            return
            
        # 遍历所有已保存的答题记录
        for chapter_idx in self.user_answers:
            for section_idx in self.user_answers[chapter_idx]:
                for question_idx in self.user_answers[chapter_idx][section_idx]:
                    answer_data = self.user_answers[chapter_idx][section_idx][question_idx]
                    selected_answer = answer_data['selected_answer']
                    is_correct = answer_data['is_correct']
                    
                    # 找到对应的单选按钮并设置选中状态
                    radio_name = f"radioButton{chapter_idx+1}_{section_idx+1}_{question_idx}"
                    radio_button = self.ui.findChild(QRadioButton, selected_answer)
                    
                    if radio_button:
                        radio_button.setChecked(True)
                        
                        # 如果已提交，显示正确/错误的颜色
                        if is_correct:
                            radio_button.setStyleSheet("color: white; background-color: #4CAF50;")
                        else:
                            radio_button.setStyleSheet("color: white; background-color: #e74c3c;")
                            
                            # 找到正确答案并高亮
                            correct_radio_name = f"radioButton{chapter_idx+1}_{section_idx+1}_{question_idx}_r"
                            correct_radio = self.ui.findChild(QRadioButton, correct_radio_name)
                            if correct_radio:
                                correct_radio.setStyleSheet("color: white; background-color: #4CAF50;")
