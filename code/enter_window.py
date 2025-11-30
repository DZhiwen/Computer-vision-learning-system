import os
import sys
from PySide6.QtWidgets import (
    QWidget, QTreeWidget, QStackedWidget, QProgressBar, QPushButton,
    QVBoxLayout, QHBoxLayout, QTabWidget, QTabBar, QTreeWidgetItem, 
    QTextEdit, QTextBrowser, QRadioButton ,QScrollArea,QGroupBox,QLabel,QMessageBox
)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QColor
from db_manager import DatabaseManager, resource_path
import resources_rc 
import io
from contextlib import redirect_stdout
from config import ConfigManager
from language import LanguageManager
from settings_window import SettingsWindow
from dashboard_window import DashboardWindow

from PySide6.QtCore import Qt
from ai_scorer import AIScorer

class EnterWindow(QWidget):
    def __init__(self, user_id, parent=None):
        super(EnterWindow, self).__init__(parent)
        
        self.user_id = user_id
        self.db = DatabaseManager()
        self.db.ensure_questions_exist()
        self.config = ConfigManager()
        self.lang_manager = LanguageManager(self.config.get('language', 'ru'))

        window_size = self.config.get('window_size')
        if window_size:
            self.resize(window_size['width'], window_size['height'])
        
        ui_file_path = resource_path(os.path.join("ui", "Enter.ui"))
        ui_file = QFile(ui_file_path)
        
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Невозможно открыть UI файл: {ui_file_path}")
            return
            
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)


        self.ui.findChild(QWidget, "Logout").clicked.connect(self.close)
        self.setWindowTitle("Модуль обучения компьютерному зрению - Основной интерфейс")
        self.add_toolbar_buttons()
        
        self.current_chapter = 0
        self.current_step = 0
        self.completed_chapters = {}
        self.user_answers = {}
        
        self.course_map = [
            ("Глава 1. Введение в компьютерное зрение", [
                ("1.1. Основные понятия и применения", "page1_1", 0),
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
        
        self.completed_color = "#329600"
        self.selected_completed_color = "#55ff00"

        self.total_buttons = 49
        
        self.init_components()
        
        self.load_user_progress()
        self.load_user_answers()  
        self.update_display()
        

    def init_components(self):
        """初始化界面组件连接"""
        self.course_tree = self.ui.findChild(QTreeWidget, "courseTree")
        self.course_tree.itemClicked.connect(self.on_course_selected)
        self.stacked_widget = self.ui.findChild(QStackedWidget, "stackedWidget")
        self.progress_bar = self.ui.findChild(QProgressBar, "progressBar")
        
        self.populate_course_tree()
        
        self.chapter_tabs = []
        self.page_indices = {}
        
        for chapter_idx in range(1, 8):
            for section_idx in range(1, 4):
                page_name = f"page{chapter_idx}_{section_idx}"
                page = self.stacked_widget.findChild(QWidget, page_name)
                if page:
                    for j in range(self.stacked_widget.count()):
                        if self.stacked_widget.widget(j) == page:
                            self.page_indices[page_name] = j
                            break
                    
                    tab_widget = self.get_tab_widget_by_page(page)
                    if tab_widget:
                        tab_widget.currentChanged.connect(self.update_current_position)
                        self.chapter_tabs.append(tab_widget)
                    else:
                        self.chapter_tabs.append(None)
        
        self.connect_next_buttons()
        self.connect_code_buttons()
        self.connect_question_submit_buttons()

    def get_tab_widget_by_page(self, page):
        """通过页面对象获取对应的TabWidget（封装重复逻辑）"""
        page_name = page.objectName()
        if not page_name.startswith("page"):
            return None
        chapter_num, section_num = page_name.replace("page", "").split("_")
        return page.findChild(QTabWidget, f"contentTabs{chapter_num}_{section_num}")

    def connect_question_submit_buttons(self):
        """连接所有测试题的提交按钮"""
        for chapter_idx in range(1, 8):
            for section_idx in range(1, 4):
                for q_idx in range(1, 9):
                    btn_name = f"submitButton{chapter_idx}_{section_idx}_{q_idx}"
                    btn = self.ui.findChild(QPushButton, btn_name)
                    if btn:
                        btn.clicked.connect(self.handle_question_submit)
    
    def handle_question_submit(self):
        """处理测试题提交按钮点击，判断正误并高亮"""
        sender = self.sender()
        if not sender or not sender.objectName().startswith("submitButton"):
            return

        try:
            chapter_idx, section_idx, q_idx = sender.objectName()[len("submitButton"):].split('_')
            chapter_idx = int(chapter_idx) - 1
            section_idx = int(section_idx) - 1
            q_idx = int(q_idx)
        except Exception:
            return

        correct_radio_name = f"radioButton{chapter_idx+1}_{section_idx+1}_{q_idx}_r"
        radio_buttons = []
        correct_radio = self.ui.findChild(QRadioButton, correct_radio_name)
        if correct_radio:
            radio_buttons.append(correct_radio)

        if len(radio_buttons) < 4:
            group_box = self.ui.findChild(QWidget, f"groupBox{chapter_idx+1}_{section_idx+1}_{q_idx}")
            if group_box:
                radio_buttons = group_box.findChildren(QRadioButton)

        selected_radio = next((rb for rb in radio_buttons if rb.isChecked()), None)
        if not selected_radio:
            return

        for rb in radio_buttons:
            rb.setStyleSheet("")

        is_correct = (selected_radio.objectName() == correct_radio_name)
        
        if is_correct:
            selected_radio.setStyleSheet("color: white; background-color: #4CAF50;")
        else:
            selected_radio.setStyleSheet("color: white; background-color: #e74c3c;")
            if correct_radio:
                correct_radio.setStyleSheet("color: white; background-color: #4CAF50;")
        
        self.db.save_quiz_answer(
            self.user_id, chapter_idx, section_idx, q_idx,
            selected_radio.objectName(), 1 if is_correct else 0
        )
        
        if chapter_idx not in self.user_answers:
            self.user_answers[chapter_idx] = {}
        if section_idx not in self.user_answers[chapter_idx]:
            self.user_answers[chapter_idx][section_idx] = {}
        
        self.user_answers[chapter_idx][section_idx][q_idx] = {
            'selected_answer': selected_radio.objectName(),
            'is_correct': 1 if is_correct else 0
        }

    def connect_code_buttons(self):
        """连接所有代码运行按钮"""
        for chapter_idx in range(1, 8):
            btn_name = f"codeButton{chapter_idx}_3"
            btn = self.ui.findChild(QPushButton, btn_name)
            if btn:
                btn.clicked.connect(self.run_code)
                btn.setText("Запустить код")

    def run_code(self):
        """运行Python代码"""
        sender = self.sender()
        if not sender or not sender.objectName().startswith("codeButton"):
            return
            
        chapter_page = sender.objectName()[len("codeButton"):]
        parts = chapter_page.split('_')
        if len(parts) != 2:
            return
            
        chapter_idx, page_idx = parts
        
        text_edit = self.ui.findChild(QTextEdit, f"textEdit{chapter_idx}_{page_idx}")
        text_browser = self.ui.findChild(QTextBrowser, f"textBrowser{chapter_idx}_{page_idx}")
        
        if not text_edit or not text_browser:
            return
            
        code = text_edit.toPlainText()
        if not code.strip():
            text_browser.setPlainText("Пожалуйста, введите код для выполнения")
            return
            
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                exec(code)
            result = output.getvalue()
            text_browser.setPlainText(result if result else "Код выполнен успешно")
        except Exception as e:
            text_browser.setPlainText(f"Ошибка: {str(e)}")

    def populate_course_tree(self):
        """填充课程树状菜单"""
        self.course_tree.clear()
        
        for chapter_name, sections in self.course_map:
            chapter_item = QTreeWidgetItem(self.course_tree)
            chapter_item.setText(0, chapter_name)
            
            for section_name, _, _ in sections:
                section_item = QTreeWidgetItem(chapter_item)
                section_item.setText(0, section_name)
        
        self.course_tree.expandAll()

    def connect_next_buttons(self):
        """连接所有'下一页'和'下一章节'按钮"""
        for chapter_idx in range(1, 8):
            for section_idx in range(1, 4):
                for tab_idx in range(1, 5):
                    btn = self.ui.findChild(QPushButton, f"nextPageButton{chapter_idx}_{section_idx}_{tab_idx}")
                    if btn:
                        btn.clicked.connect(self.next_page)
        
        for chapter_idx in range(1, 8):
            for section_idx in range(1, 4):
                btn = self.ui.findChild(QPushButton, f"nextChapterButton{chapter_idx}_{section_idx}")
                if btn:
                    btn.clicked.connect(self.next_chapter)

    def update_current_position(self, index):
        """切换Tab时更新当前位置"""
        sender = self.sender()
        if sender:
            for chapter_idx, tab_widget in enumerate(self.chapter_tabs):
                if tab_widget == sender:
                    self.find_chapter_and_section(tab_widget, index)
                    break
        
        self.update_tab_colors()

    def find_chapter_and_section(self, tab_widget, tab_index):
        """通过TabWidget和标签索引查找对应章节和小节"""
        for chapter_idx, (_, sections) in enumerate(self.course_map):
            for section_idx, (_, page_name, _) in enumerate(sections):
                page_idx = self.page_indices.get(page_name, -1)
                if page_idx >= 0:
                    page = self.stacked_widget.widget(page_idx)
                    if page and self.get_tab_widget_by_page(page) == tab_widget:
                        self.current_chapter = chapter_idx
                        self.current_step = tab_index
                        return

    def on_course_selected(self, item):
        """处理点击课程树节点事件"""
        selected_text = item.text(0)
        parent = item.parent()
        
        if parent:
            chapter_name = parent.text(0)
            section_name = selected_text
            
            for chapter_idx, (name, sections) in enumerate(self.course_map):
                if name == chapter_name:
                    for section_idx, (s_name, page_name, tab_idx) in enumerate(sections):
                        if s_name == section_name:
                            self.current_chapter = chapter_idx
                            self.current_step = tab_idx
                            
                            page_idx = self.page_indices.get(page_name, -1)
                            if page_idx >= 0:
                                self.stacked_widget.setCurrentIndex(page_idx)
                                
                                page = self.stacked_widget.currentWidget()
                                tab_widget = self.get_tab_widget_by_page(page)
                                if tab_widget:
                                    tab_widget.setCurrentIndex(tab_idx)
                            
                            self.update_display()
                            return
    

    
    def next_page(self):
        """处理'下一页'按钮点击"""
        current_page = self.stacked_widget.currentWidget()
        if not current_page:
            return
            
        tab_widget = self.get_tab_widget_by_page(current_page)
        if not tab_widget:
            return
            
        self.mark_tab_completed(current_page, tab_widget.currentIndex())
        
        if tab_widget.currentIndex() < tab_widget.count() - 1:
            tab_widget.setCurrentIndex(tab_widget.currentIndex() + 1)
            self.current_step = tab_widget.currentIndex()
            self.save_progress()
        else:
            self.next_chapter()

    def next_chapter(self):
        """处理'下一章节'按钮点击"""
        current_page = self.stacked_widget.currentWidget()
        if not current_page:
            return
            
        tab_widget = self.get_tab_widget_by_page(current_page)
        if tab_widget:
            self.mark_tab_completed(current_page, tab_widget.currentIndex())
        
        current_page_name = current_page.objectName()
        current_page_idx = self.page_indices.get(current_page_name, -1)
        if current_page_idx == -1:
            return

        for chapter_idx, (_, sections) in enumerate(self.course_map):
            for section_idx, (_, page_name, _) in enumerate(sections):
                if self.page_indices.get(page_name, -1) == current_page_idx:
                    if section_idx + 1 < len(sections):
                        next_page_name = sections[section_idx + 1][1]
                        next_page_idx = self.page_indices.get(next_page_name, -1)
                        if next_page_idx >= 0:
                            self.stacked_widget.setCurrentIndex(next_page_idx)
                            next_page = self.stacked_widget.widget(next_page_idx)
                            next_tab_widget = self.get_tab_widget_by_page(next_page)
                            
                            if next_tab_widget:
                                next_tab_widget.setCurrentIndex(0)
                            self.current_chapter = chapter_idx
                            self.current_step = 0
                            self.save_progress()
                            self.update_display()
                            return
                    elif chapter_idx + 1 < len(self.course_map):
                        next_chapter = self.course_map[chapter_idx + 1]
                        next_page_name = next_chapter[1][0][1]
                        next_page_idx = self.page_indices.get(next_page_name, -1)
                        if next_page_idx >= 0:
                            self.stacked_widget.setCurrentIndex(next_page_idx)
                            next_page = self.stacked_widget.widget(next_page_idx)
                            next_tab_widget = self.get_tab_widget_by_page(next_page)
                            
                            if next_tab_widget:
                                next_tab_widget.setCurrentIndex(0)
                            self.current_chapter = chapter_idx + 1
                            self.current_step = 0
                            self.save_progress()
                            self.update_display()
                            return

    def mark_tab_completed(self, page, tab_idx):
        """标记指定标签为已完成"""
        tab_widget = self.get_tab_widget_by_page(page)
        if not tab_widget or not (0 <= tab_idx < tab_widget.count()):
            return
            
        tab_bar = tab_widget.tabBar()
        tab_bar.setTabTextColor(tab_idx, QColor(self.completed_color))
        
        page_name = page.objectName()
        for chapter_idx, (_, sections) in enumerate(self.course_map):
            for section_idx, (_, p_name, _) in enumerate(sections):
                if p_name == page_name:
                    if chapter_idx not in self.completed_chapters:
                        self.completed_chapters[chapter_idx] = {}
                    
                    step_key = section_idx * 10 + tab_idx
                    self.completed_chapters[chapter_idx][step_key] = 1
                    
                    self.db.save_chapter_progress(
                        self.user_id, chapter_idx, step_key, 1
                    )
                    return

    def update_display(self):
        """刷新所有界面元素"""
        self.update_tab_colors()
        self.update_progress()
        self.highlight_current_course()

    def update_tab_colors(self):
        """根据进度刷新所有标签颜色"""
        current_page = self.stacked_widget.currentWidget()
        current_tab_widget = self.get_tab_widget_by_page(current_page) if current_page else None

        for page_idx in range(self.stacked_widget.count()):
            page = self.stacked_widget.widget(page_idx)
            if not page or not page.objectName().startswith("page"):
                continue

            tab_widget = self.get_tab_widget_by_page(page)
            if not tab_widget:
                continue

            tab_bar = tab_widget.tabBar()
            for tab_idx in range(tab_widget.count()):
                is_current = (tab_widget == current_tab_widget and 
                            tab_idx == tab_widget.currentIndex())
                
                chapter_idx, section_idx = self._get_chapter_section_by_page_name(page.objectName())
                step_key = section_idx * 10 + tab_idx
                is_completed = (
                    chapter_idx in self.completed_chapters and 
                    step_key in self.completed_chapters[chapter_idx]
                )

                if is_completed:
                    tab_bar.setTabTextColor(tab_idx, QColor(self.selected_completed_color) if is_current else QColor(self.completed_color))

    def _get_chapter_section_by_page_name(self, page_name):
        """通过页面名获取章节和小节索引"""
        for chapter_idx, (_, sections) in enumerate(self.course_map):
            for section_idx, (_, p_name, _) in enumerate(sections):
                if p_name == page_name:
                    return chapter_idx, section_idx
        return -1, -1

    def update_progress(self):
        """刷新进度条"""
        completed_tabs = sum(len(chapter) for chapter in self.completed_chapters.values())
        progress_percentage = int((completed_tabs / self.total_buttons) * 100)
        self.progress_bar.setValue(progress_percentage)
        
        self.db.update_progress(
            self.user_id, progress_percentage / 100.0, self.completed_chapters
        )
        

    def highlight_current_course(self):
        """高亮当前课程树节点"""
        current_page = self.stacked_widget.currentWidget()
        if not current_page:
            return
            
        current_page_name = current_page.objectName()
        
        for chapter_idx, (chapter_name, sections) in enumerate(self.course_map):
            # 此处原代码不完整，保留原样
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

    def add_toolbar_buttons(self):
        """添加工具栏按钮到界面"""
        try:
            # 在右侧面板顶部添加工具栏
            right_panel = self.ui.findChild(QWidget, "rightPanel")
            if right_panel:
                # 获取右侧面板的布局
                layout = right_panel.layout()
                
                # 创建工具栏框架
                toolbar_frame = QWidget()
                toolbar_layout = QHBoxLayout()
                toolbar_layout.setSpacing(8)
                
                # 设置按钮
                settings_btn = QPushButton("⚙️ Настройки")
                settings_btn.setMinimumHeight(36)
                settings_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #95a5a6;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #7f8c8d;
                    }
                """)
                settings_btn.clicked.connect(self.open_settings)
                
                # 统计按钮
                stats_btn = QPushButton("📊 Статистика")
                stats_btn.setMinimumHeight(36)
                stats_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #9b59b6;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #8e44ad;
                    }
                """)
                stats_btn.clicked.connect(self.open_dashboard)
                
                # 添加弹性空间
                toolbar_layout.addStretch()
                toolbar_layout.addWidget(stats_btn)
                toolbar_layout.addWidget(settings_btn)
                
                toolbar_frame.setLayout(toolbar_layout)
                
                # 将工具栏插入到布局的顶部
                layout.insertWidget(0, toolbar_frame)
                
        except Exception as e:
            print(f"添加工具栏按钮失败: {e}")

    def open_settings(self):
        """打开设置窗口"""
        try:
            dialog = SettingsWindow(self)
            if dialog.exec():
                # 应用新设置
                self.apply_settings()
        except Exception as e:
            print(f"打开设置窗口失败: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "ошибка", f"Невозможно открыть окно настроек: {e}")

    def open_dashboard(self):
        """打开统计仪表板"""
        try:
            dialog = DashboardWindow(self.user_id, self)
            dialog.exec()
        except Exception as e:
            print(f"打开统计仪表板失败: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "ошибка", f"Невозможно открыть панель статистики.: {e}")

    def apply_settings(self):
        """应用设置"""
        try:
            # 应用字体大小
            font_size = self.config.get('font_size', 10)
            font = self.font()
            font.setPointSize(font_size)
            self.setFont(font)
            
            # 应用语言设置（需要重启应用生效）
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Настройки применены / Settings Applied",
                "Некоторые настройки вступят в силу после перезапуска приложения.\n"
                "Some settings will take effect after restarting the application."
            )
        except Exception as e:
            print(f"应用设置失败: {e}")

    def closeEvent(self, event):
        """窗口关闭事件 - 保存窗口大小"""
        try:
            self.config.set('window_size', {
                'width': self.width(),
                'height': self.height()
            })
        except Exception as e:
            print(f"保存窗口大小失败: {e}")
        
        event.accept()




    def init_components(self):
            """初始化界面组件连接（补充加载题目）"""
            self.course_tree = self.ui.findChild(QTreeWidget, "courseTree")
            self.course_tree.itemClicked.connect(self.on_course_selected)
            self.stacked_widget = self.ui.findChild(QStackedWidget, "stackedWidget")
            self.progress_bar = self.ui.findChild(QProgressBar, "progressBar")
            
            self.populate_course_tree()
            self.chapter_tabs = []
            self.page_indices = {}
            for chapter_idx in range(1, 8):
                for section_idx in range(1, 4):
                    page_name = f"page{chapter_idx}_{section_idx}"
                    page = self.stacked_widget.findChild(QWidget, page_name)
                    if page:
                        for j in range(self.stacked_widget.count()):
                            if self.stacked_widget.widget(j) == page:
                                self.page_indices[page_name] = j
                                break
                        tab_widget = page.findChild(QTabWidget, f"contentTabs{chapter_idx}_{section_idx}")
                        if tab_widget:
                            tab_widget.currentChanged.connect(self.update_current_position)
                            self.chapter_tabs.append(tab_widget)
                        else:
                            self.chapter_tabs.append(None)
            
            self.connect_next_buttons()
            self.connect_code_buttons()
            self.connect_question_submit_buttons()
            self.load_quiz_questions_to_ui()  # 新增：加载题目到UI（关键）

    def load_quiz_questions_to_ui(self):
        """动态填充数据库题目到UI（适配UI原始命名，不改动UI）"""
        for chapter_idx in range(1, 8):
            for section_idx in [1, 2]:
                questions = self.db.get_quiz_questions(chapter_idx, section_idx)
                if not questions:
                    continue
                
                for q_num in range(1, 9):
                    group_box_name = f"groupBox{chapter_idx}_{section_idx}_{q_num}"
                    group_box = self.ui.findChild(QWidget, group_box_name)
                    if not group_box:
                        continue
                    
                    radios = group_box.findChildren(QRadioButton)
                    radios = [r for r in radios if r.objectName().startswith(f"radioButton{chapter_idx}_{section_idx}_")]
                    if len(radios) != 4:
                        continue
                    
                    q_data = questions.get(q_num, {})
                    if q_data:
                        group_box.setTitle(q_data.get("text", f"Вопрос {q_num}"))
                        options = q_data.get("options", {"A":"", "B":"", "C":"", "D":""})
                        for i, (opt_key, opt_text) in enumerate(options.items()):
                            if i < len(radios):
                                radios[i].setText(f"{opt_key}. {opt_text}")
                                
                                # === 以下是新增的代码块 ===
                                # 修复新用户已选问题：强制重置状态
                                radios[i].setAutoExclusive(False) # 暂时关闭互斥，以便取消选中
                                radios[i].setChecked(False)       # 取消选中
                                radios[i].setAutoExclusive(True)  # 恢复互斥
                                radios[i].setStyleSheet("")       # 清除颜色样式
                                # ========================
                
                self.add_subjective_question_ui(chapter_idx, section_idx)

    def add_subjective_question_ui(self, chapter_idx, section_idx):
        """
        为指定章节-小节动态创建第9题主观题UI（无需改Enter.ui）
        chapter_idx: 章节号（1-7）
        section_idx: 小节号（1-2，仅x.1/x.2有测试题）
        """
        # --------------------------
        # 1. 找到当前小节的测试题标签页（如1.1小节的"Тестовое задание"标签页）
        # --------------------------
        # 测试题标签页命名规则：tab{章节}_{小节}_3（3表示第三个标签页，对应"Тестовое задание"）
        tab_name = f"tab{chapter_idx}_{section_idx}_3"
        tab_widget = self.ui.findChild(QWidget, tab_name)
        if not tab_widget:
            print(f"警告：未找到测试题标签页（{tab_name}），跳过主观题添加")
            return

        # --------------------------
        # 2. 找到标签页内的scrollArea（选择题所在的滚动容器）
        # --------------------------
        # 现有选择题的scrollArea无固定名称，通过类型查找（适配UI原始结构）
        scroll_area = tab_widget.findChild(QScrollArea)
        if not scroll_area:
            print(f"警告：章节{chapter_idx}小节{section_idx}的测试题标签页中未找到scrollArea")
            return

        # 找到scrollArea内部的内容容器（所有选择题groupBox都在这个容器里）
        scroll_content = scroll_area.findChild(QWidget, "scrollAreaWidgetContents")
        if not scroll_content:
            # 若未找到默认名称的容器，直接取scrollArea的widget（兼容可能的UI差异）
            scroll_content = scroll_area.widget()
            if not scroll_content:
                print(f"警告：章节{chapter_idx}小节{section_idx}的scrollArea无内容容器")
                return

        # 获取scrollArea的布局（用于添加主观题groupBox）
        scroll_layout = scroll_content.layout()
        if not scroll_layout:
            # 若布局不存在，新建垂直布局（保持和选择题布局一致）
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(16)  # 和选择题groupBox的间距一致
            scroll_content.setLayout(scroll_layout)

        # --------------------------
        # 3. 动态创建主观题的groupBox（模仿选择题的groupBox样式）
        # --------------------------
        subjective_groupbox = QGroupBox()
        # 主观题groupBox命名规则：groupBox{章节}_{小节}_9（9表示第9题）
        subjective_groupbox.setObjectName(f"groupBox{chapter_idx}_{section_idx}_9")
        
        # 从主观题专用数据库加载题目和评分标准（若存在）
        subjective_q = self.db.subjective_db.get_subjective_question(chapter_idx, section_idx)
        if subjective_q:
            # 显示题目+满分（如："9. Опишите основные применения компьютерного зрения...（满分：10分）"）
            groupbox_title = f"9. {subjective_q['text']}（Максимальное количество баллов：{subjective_q['full_score']}балл）"
            subjective_groupbox.setTitle(groupbox_title)
            
            # 生成评分标准提示（显示在输入框占位符中，引导用户）
            score_hint = "\n\nКритерии оценки：\n" + "\n".join([f"- {p}" for p in subjective_q['score_criteria']['points']])
        else:
            # 无数据库题目时显示默认标题
            subjective_groupbox.setTitle("9. Вопрос с развернутым ответом（Субъективные вопросы）")
            score_hint = ""  # 无评分标准时不显示

        # --------------------------
        # 4. 为主观题groupBox创建内部布局（文本输入框 + 提交按钮）
        # --------------------------
        subjective_layout = QHBoxLayout(subjective_groupbox)
        subjective_layout.setSpacing(12)  # 输入框和按钮的间距
        subjective_layout.setContentsMargins(12, 12, 12, 12)  # 内边距

        # --------------------------
        # 5. 新增文本输入框（用户输入主观题答案）
        # --------------------------
        self.subjective_textedit = QTextEdit()
        # 文本输入框命名规则：textEditSubjective{章节}_{小节}_9（后续提交/恢复需用到）
        self.subjective_textedit.setObjectName(f"textEditSubjective{chapter_idx}_{section_idx}_9")
        # 设置占位符（提示输入 + 评分标准）
        self.subjective_textedit.setPlaceholderText(f"Введите ваш ответ здесь...{score_hint}")
        # 样式匹配现有UI（边框、字体、高度）
        self.subjective_textedit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e6ed;
                border-radius: 4px;
                padding: 8px;
                min-height: 120px;
                font-size: 9pt;
                font-family: Segoe UI, Arial, sans-serif; 
            }
            QTextEdit:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        subjective_layout.addWidget(self.subjective_textedit, 1)  # 占满大部分宽度（权重1）

        # --------------------------
        # 6. 新增主观题提交按钮（模仿选择题提交按钮样式）
        # --------------------------
        subjective_submit_btn = QPushButton("Отправить ответ")
        # 按钮命名规则：submitSubjectiveButton{章节}_{小节}_9（后续绑定事件需用到）
        subjective_submit_btn.setObjectName(f"submitSubjectiveButton{chapter_idx}_{section_idx}_9")
        # 样式匹配现有提交按钮（颜色、 hover效果）
        subjective_submit_btn.setStyleSheet("""
             QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                margin-left: 12px;
                min-width: 140px;
                font-size: 9pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        # 绑定提交事件（调用后续的主观题提交方法）
        subjective_submit_btn.clicked.connect(
            lambda: self.handle_subjective_submit(chapter_idx, section_idx, 9)
        )
        subjective_layout.addWidget(subjective_submit_btn)

        # --------------------------
        # 7. 将主观题groupBox添加到scrollArea（在8个选择题后面）
        # --------------------------
        scroll_layout.addWidget(subjective_groupbox)
        # 添加空标签作为分隔（和选择题之间的间距一致）
        scroll_layout.addWidget(QLabel(""))
        print(f"✓ 成功为章节{chapter_idx}小节{section_idx}添加主观题UI")

    def handle_subjective_submit(self, chapter_idx, section_idx, question_idx):
        """
        处理主观题提交：保存答案 + 调用AI评分 + 显示结果
        chapter_idx: 章节号（1-7）
        section_idx: 小节号（1-2）
        question_idx: 题号（固定为9）
        """
        # --------------------------
        # 1. 找到当前主观题的文本输入框（获取用户答案）
        # --------------------------
        textedit_name = f"textEditSubjective{chapter_idx}_{section_idx}_{question_idx}"
        text_edit = self.ui.findChild(QTextEdit, textedit_name)
        if not text_edit:
            QMessageBox.warning(self, "Ошибка", f"Поле ввода субъективного вопроса не найдено.（глава{chapter_idx}Раздел{section_idx}）")
            return

        # 获取用户输入的答案（去除前后空格）
        user_answer = text_edit.toPlainText().strip()
        if not user_answer:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите свои ответы на субъективные вопросы перед отправкой!")
            return

        # --------------------------
        # 2. 保存用户答案到主观题专用数据库（待评分状态）
        # --------------------------
        save_answer_success = self.db.subjective_db.save_user_subjective_answer(
            user_id=self.user_id,
            chapter_num=chapter_idx,
            section_num=section_idx,
            user_answer=user_answer
        )
        if not save_answer_success:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить ответ пользователя. Попробуйте еще раз！")
            return

        # --------------------------
        # 3. 从专用数据库获取主观题信息（题目+评分标准）
        # --------------------------
        subjective_q = self.db.subjective_db.get_subjective_question(
            chapter_num=chapter_idx,
            section_num=section_idx
        )
    # --- 修改后 (请替换为以下代码) ---
        if not subjective_q:
            # 无评分标准时，仅保存答案，不进行AI评分
            QMessageBox.information(
                self, "Успех", 
                f"Ответы на субъективные вопросы сохранены!\n(Глава {chapter_idx}, Раздел {section_idx}: В настоящее время критерии оценки отсутствуют, поэтому оценка с помощью искусственного интеллекта невозможна.)"
            )
            # 更新本地答题记录（用于后续恢复）
            self._update_local_subjective_record(chapter_idx, section_idx, user_answer)
            return

        # --------------------------
        # 4. 调用AI评分工具进行评分
        # --------------------------
        # 显示"评分中"提示（避免用户重复提交）
        loading_msg = QMessageBox(self)  # 实例化QMessageBox
        loading_msg.setWindowTitle("намекать")
        loading_msg.setText("Рейтинг...")
        loading_msg.show()  # 显示消息框

        try:
            # 初始化AI评分器
            ai_scorer = AIScorer()
            # 调用AI评分（传入题目、用户答案、评分标准）
            ai_score, ai_feedback = ai_scorer.score_subjective_answer(
                question_text=subjective_q["text"],
                user_answer=user_answer,
                score_criteria=subjective_q["score_criteria"]
            )
        except Exception as e:
            loading_msg.close()  # 关闭评分中提示
            QMessageBox.critical(self, "Рейтинг не пройден", f"Ошибка в процессе оценки ИИ：{str(e)}")
            return
        finally:
            loading_msg.close()  # 确保无论成功失败，都关闭提示

        # --------------------------
        # 5. 处理AI评分结果（保存+显示）
        # --------------------------
        if ai_score is not None and 0 <= ai_score <= subjective_q["full_score"]:
            # 保存AI评分到专用数据库
            self.db.subjective_db.save_ai_score(
                user_id=self.user_id,
                chapter_num=chapter_idx,
                section_num=section_idx,
                ai_score=ai_score,
                ai_feedback=ai_feedback
            )

            # 显示评分结果（带评语）
            result_text = f"""
            Подсчет очков ИИ завершен!
            глава{chapter_idx}Раздел{section_idx} Субъективные вопросы
            Счет：{ai_score}/{subjective_q["full_score"]}分

            Комментарии ИИ:
            {ai_feedback}
            """
            QMessageBox.information(self, "Результаты рейтинга", result_text.strip())

            # 更新本地答题记录（包含评分）
            self._update_local_subjective_record(
                chapter_idx, section_idx, user_answer, ai_score, ai_feedback
            )

            # 可选：在UI上标记已评分（添加评分标签）
            self._show_subjective_score_ui(chapter_idx, section_idx, ai_score, ai_feedback)
        else:
            # AI评分无效（如API密钥错误、返回格式异常）
            QMessageBox.warning(
                self, "недействительный рейтинг", 
                f"ИИ не выдал верную оценку.\nпричина：{ai_feedback if ai_feedback else 'Неизвестная ошибка'}\nОтвет сохранен и может быть переоценен позже."
            )
            # 仅更新本地答案记录（无评分）
            self._update_local_subjective_record(chapter_idx, section_idx, user_answer)

    def _update_local_subjective_record(self, chapter_idx, section_idx, user_answer, ai_score=None, ai_feedback=None):
        """辅助方法：更新本地答题记录（用于后续恢复）"""
        # 转换为数据库的0基索引（chapter_idx从1→0，section_idx从1→0）
        db_chapter = chapter_idx - 1
        db_section = section_idx - 1

        # 初始化本地记录结构
        if db_chapter not in self.user_answers:
            self.user_answers[db_chapter] = {}
        if db_section not in self.user_answers[db_chapter]:
            self.user_answers[db_chapter][db_section] = {}

        # 保存主观题记录（题号固定为9）
        self.user_answers[db_chapter][db_section][9] = {
            "user_answer": user_answer,
            "ai_score": ai_score,
            "ai_feedback": ai_feedback,
            "is_subjective": True  # 标记为主观题，区别于选择题
        }

    def _show_subjective_score_ui(self, chapter_idx, section_idx, ai_score, ai_feedback):
        """辅助方法：在UI上显示主观题评分结果（添加标签）"""
        # 找到主观题的groupBox
        groupbox_name = f"groupBox{chapter_idx}_{section_idx}_9"
        groupbox = self.ui.findChild(QWidget, groupbox_name)
        if not groupbox:
            return

        # 找到groupBox的布局
        groupbox_layout = groupbox.layout()
        if not groupbox_layout:
            return

        # 移除已存在的评分标签（避免重复添加）
        for i in range(groupbox_layout.count()):
            widget = groupbox_layout.itemAt(i).widget()
            if widget and widget.objectName() == f"scoreLabel{chapter_idx}_{section_idx}_9":
                widget.deleteLater()

        # 创建评分标签（显示得分和评语预览）
        score_label = QLabel()
        score_label.setObjectName(f"scoreLabel{chapter_idx}_{section_idx}_9")
        # 限制评语长度（避免UI过长）
        feedback_preview = ai_feedback[:60] + "..." if len(ai_feedback) > 60 else ai_feedback
        score_label.setText(f"✅ AI评分：{ai_score}分 | Комментарий：{feedback_preview}")
        # 样式匹配现有UI（绿色文字，小字体）
        score_label.setStyleSheet("""
            color: #27ae60;
            font-size: 8pt;
            margin-top: 8px;
            font-weight: bold;
        """)
        score_label.setAlignment(Qt.AlignRight)  # 右对齐，不占用输入框空间

        # 添加标签到groupBox布局（在输入框和按钮下方）
        groupbox_layout.addWidget(score_label)
        

    def _update_local_subjective_record(self, chapter_idx, section_idx, user_answer, ai_score=None, ai_feedback=None):
        """辅助方法：更新本地答题记录（用于后续恢复）"""
        # 转换为数据库的0基索引（chapter_idx从1→0，section_idx从1→0）
        db_chapter = chapter_idx - 1
        db_section = section_idx - 1

        # 初始化本地记录结构
        if db_chapter not in self.user_answers:
            self.user_answers[db_chapter] = {}
        if db_section not in self.user_answers[db_chapter]:
            self.user_answers[db_chapter][db_section] = {}

        # 保存主观题记录（题号固定为9）
        self.user_answers[db_chapter][db_section][9] = {
            "user_answer": user_answer,
            "ai_score": ai_score,
            "ai_feedback": ai_feedback,
            "is_subjective": True  # 标记为主观题，区别于选择题
        }

    def _show_subjective_score_ui(self, chapter_idx, section_idx, ai_score, ai_feedback):
        """辅助方法：在UI上显示主观题评分结果（添加标签）"""
        # 找到主观题的groupBox
        groupbox_name = f"groupBox{chapter_idx}_{section_idx}_9"
        groupbox = self.ui.findChild(QWidget, groupbox_name)
        if not groupbox:
            return

        # 找到groupBox的布局
        groupbox_layout = groupbox.layout()
        if not groupbox_layout:
            return

        # 移除已存在的评分标签（避免重复添加）
        for i in range(groupbox_layout.count()):
            widget = groupbox_layout.itemAt(i).widget()
            if widget and widget.objectName() == f"scoreLabel{chapter_idx}_{section_idx}_9":
                widget.deleteLater()

        # 创建评分标签（显示得分和评语预览）
        score_label = QLabel()
        score_label.setObjectName(f"scoreLabel{chapter_idx}_{section_idx}_9")
        # 限制评语长度（避免UI过长）
        feedback_preview = ai_feedback[:60] + "..." if len(ai_feedback) > 60 else ai_feedback
        score_label.setText(f"✅ AI评分：{ai_score}分 | Комментарий：{feedback_preview}")
        # 样式匹配现有UI（绿色文字，小字体）
        score_label.setStyleSheet("""
            color: #27ae60;
            font-size: 8pt;
            margin-top: 8px;
            font-weight: bold;
        """)
        score_label.setAlignment(Qt.AlignRight)  # 右对齐，不占用输入框空间

        # 添加标签到groupBox布局（在输入框和按钮下方）
        groupbox_layout.addWidget(score_label)



    def handle_question_submit(self):
        """处理答题提交（适配UI原始命名，不改动UI）"""
        sender = self.sender()
        if not sender:
            return
        btn_name = sender.objectName()
        if not btn_name.startswith("submitButton"):
            return
        
        # 解析章节、小节、题号（如submitButton1_1_1 → 1章1节1题）
        try:
            chapter_idx, section_idx, q_idx = btn_name[len("submitButton"):].split('_')
            chapter_idx = int(chapter_idx)
            section_idx = int(section_idx)
            q_idx = int(q_idx)
        except Exception as e:
            print(f"创建主观题UI失败（章节{chapter_idx}小节{section_idx}）：{str(e)}")
            return
        
        # 找到当前题目的容器groupBox
        group_box_name = f"groupBox{chapter_idx}_{section_idx}_{q_idx}"
        group_box = self.ui.findChild(QWidget, group_box_name)
        if not group_box:
            return
        
        # 关键修改1：获取该题所有选项（适配UI原始命名）
        radios = group_box.findChildren(QRadioButton)
        radios = [r for r in radios if r.objectName().startswith(f"radioButton{chapter_idx}_{section_idx}_")]
        if not radios:
            return
        
        # 关键修改2：通过「_r」后缀找到正确选项（UI原始命名规则）
        correct_radio_name = f"radioButton{chapter_idx}_{section_idx}_{q_idx}_r"
        correct_radio = self.ui.findChild(QRadioButton, correct_radio_name)
        
        # 判断用户选择的选项
        selected_radio = None
        for radio in radios:
            if radio.isChecked():
                selected_radio = radio
                break
        if not selected_radio:
            return
        
        # 重置所有选项颜色
        for radio in radios:
            radio.setStyleSheet("")
        
        # 标记正确/错误
        is_correct = (selected_radio.objectName() == correct_radio_name)
        if is_correct:
            selected_radio.setStyleSheet("color: white; background-color: #4CAF50;")
        else:
            selected_radio.setStyleSheet("color: white; background-color: #e74c3c;")
            if correct_radio:
                correct_radio.setStyleSheet("color: white; background-color: #4CAF50;")
        
        # 保存答题记录（提取选项字母A/B/C/D）
        selected_opt = selected_radio.text().split('.')[0] if '.' in selected_radio.text() else ""
        self.db.save_quiz_answer(
            self.user_id,
            chapter_idx - 1,  # 数据库0基索引
            section_idx - 1,  # 数据库0基索引
            q_idx,
            selected_opt,
            1 if is_correct else 0
        )
        
        # 更新本地答题记录
        if chapter_idx - 1 not in self.user_answers:
            self.user_answers[chapter_idx - 1] = {}
        if section_idx - 1 not in self.user_answers[chapter_idx - 1]:
            self.user_answers[chapter_idx - 1][section_idx - 1] = {}
        self.user_answers[chapter_idx - 1][section_idx - 1][q_idx] = {
            'selected_answer': selected_opt,
            'is_correct': 1 if is_correct else 0
        }

    def restore_quiz_answers(self):
        """恢复答题状态（适配UI原始命名，不改动UI）"""
        if not self.user_answers:
            return
        for chapter_idx in self.user_answers:
            for section_idx in self.user_answers[chapter_idx]:
                for question_idx in self.user_answers[chapter_idx][section_idx]:
                    answer_data = self.user_answers[chapter_idx][section_idx][question_idx]
                    selected_opt = answer_data['selected_answer']  # 如"A"
                    is_correct = answer_data['is_correct']
                    
                    # 转换为UI的1基索引
                    ui_chapter = chapter_idx + 1
                    ui_section = section_idx + 1
                    ui_q_num = question_idx
                    
                    # 找到对应的题目容器groupBox
                    group_box_name = f"groupBox{ui_chapter}_{ui_section}_{ui_q_num}"
                    group_box = self.ui.findChild(QWidget, group_box_name)
                    if not group_box:
                        continue
                    
                    # 关键修改：获取该题所有选项（适配UI原始命名）
                    radios = group_box.findChildren(QRadioButton)
                    radios = [r for r in radios if r.objectName().startswith(f"radioButton{ui_chapter}_{ui_section}_")]
                    if not radios:
                        continue
                    
                    # 找到正确答案的RadioButton（通过「_r」后缀）
                    correct_radio_name = f"radioButton{ui_chapter}_{ui_section}_{ui_q_num}_r"
                    correct_radio = self.ui.findChild(QRadioButton, correct_radio_name)
                    
                    # 选中用户之前选择的选项
                    for radio in radios:
                        if radio.text().startswith(f"{selected_opt}."):
                            radio.setChecked(True)
                            # 标记颜色
                            if is_correct:
                                radio.setStyleSheet("color: white; background-color: #4CAF50;")
                            else:
                                radio.setStyleSheet("color: white; background-color: #e74c3c;")
                                # 高亮正确答案
                                if correct_radio:
                                    correct_radio.setStyleSheet("color: white; background-color: #4CAF50;")
                            break
