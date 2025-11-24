"""
统计仪表板 - Dashboard Window
包含热力图、周学习时长柱状图和章节圆环进度卡片
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QGroupBox, QWidget, QFrame, QToolTip, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QRect, QSize, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath, QLinearGradient
from statistics import StatisticsManager

# --- 1. 热力图控件 (已修改日期范围) ---
class ActivityHeatmapWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setMinimumHeight(140)
        self.setMinimumWidth(500)
        self.setMouseTracking(True)
        self.colors = [QColor("#ebedf0"), QColor("#9be9a8"), QColor("#40c463"), QColor("#30a14e"), QColor("#216e39")]
        self.box_size = 10
        self.spacing = 3
        self.margin_left = 30
        self.margin_top = 20
        
        # --- 修改部分开始 ---
        # 指定起始日期为 2025年10月1日
        self.start_date = QDate(2025, 10, 1)
        # 结束日期设为起始日期后的一年 (显示一整年的格子)
        self.end_date = self.start_date.addDays(365)
        # --- 修改部分结束 ---

        self.months_ru = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        self.weekdays_ru = ["Пн", "", "Ср", "", "Пт", "", ""]

    def get_color(self, count):
        if count == 0: return self.colors[0]
        if count <= 2: return self.colors[1]
        if count <= 5: return self.colors[2]
        if count <= 9: return self.colors[3]
        return self.colors[4]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = painter.font()
        font.setPointSize(7)
        painter.setFont(font)
        
        # 绘制左侧星期标签
        painter.setPen(QColor("#767676"))
        for i, day_name in enumerate(self.weekdays_ru):
            if day_name:
                y = self.margin_top + i * (self.box_size + self.spacing) + self.box_size - 1
                painter.drawText(0, y, day_name)

        current_draw_date = self.start_date
        col = 0
        last_month_drawn = -1
        
        # 逻辑调整：我们需要确保第一列正确对齐
        # 如果 2025-10-01 是周三，那么第一列的前两个格子（周一、周二）应该是空的
        # 我们不需要回溯日期，而是直接计算每一天的 (col, row) 坐标
        
        # 计算起始日期是星期几 (0=Mon, 6=Sun)
        start_dow = self.start_date.dayOfWeek() - 1
        
        # 遍历每一天
        iter_date = self.start_date
        while iter_date <= self.end_date:
            # 计算这一天相对于起始日期的天数差
            days_diff = iter_date.toJulianDay() - self.start_date.toJulianDay()
            
            # 计算它在网格中的位置
            # 每一列填满7天。
            # 位置 = (起始偏移 + 天数差)
            # 列 = 位置 // 7
            # 行 = 位置 % 7
            
            # 这里的“位置”是相对于网格左上角(0,0)的绝对索引
            # 注意：第一列的行索引必须对应真实的星期几
            # 所以 absolute_index = days_diff + start_dow
            absolute_index = days_diff + start_dow
            
            col = int(absolute_index // 7)
            row = int(absolute_index % 7) # 0=Mon, ... 6=Sun
            
            # 绘制月份标签 (只在每列的第一行上方绘制)
            if row == 0:
                month_idx = iter_date.month() - 1
                # 简单的去重逻辑：如果这个月还没画过，且这一天是该月的前14天内（保证标签大概在月初位置）
                if month_idx != last_month_drawn:
                    # 只有当这一列是该月的开始附近时才画
                    if iter_date.day() <= 14: 
                        x_month = self.margin_left + col * (self.box_size + self.spacing)
                        painter.drawText(x_month, self.margin_top - 5, self.months_ru[month_idx])
                        last_month_drawn = month_idx

            # 获取数据
            date_str = iter_date.toString("yyyy-MM-dd")
            count = self.data.get(date_str, 0)
            
            # 计算矩形坐标
            x = self.margin_left + col * (self.box_size + self.spacing)
            y = self.margin_top + row * (self.box_size + self.spacing)
            
            # 绘制方块
            painter.setBrush(QBrush(self.get_color(count)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRect(x, y, self.box_size, self.box_size), 2, 2)
            
            iter_date = iter_date.addDays(1)

    def mouseMoveEvent(self, event):
        x, y = event.pos().x(), event.pos().y()
        if x < self.margin_left or y < self.margin_top: return
        
        # 反向计算
        col = (x - self.margin_left) // (self.box_size + self.spacing)
        row = (y - self.margin_top) // (self.box_size + self.spacing)
        
        if row > 6: return
        
        # 计算对应的日期
        # absolute_index = col * 7 + row
        # days_diff = absolute_index - start_dow
        start_dow = self.start_date.dayOfWeek() - 1
        absolute_index = col * 7 + row
        days_diff = absolute_index - start_dow
        
        # 如果 days_diff < 0，说明点击的是第一列中起始日期之前的空白处
        if days_diff < 0:
            QToolTip.hideText()
            return
            
        check_date = self.start_date.addDays(days_diff)
        
        if check_date <= self.end_date:
            d_str = check_date.toString("yyyy-MM-dd")
            QToolTip.showText(event.globalPos(), f"{d_str}: {self.data.get(d_str, 0)} задач", self)
        else:
            QToolTip.hideText()

# --- 2. 周学习时长柱状图 (保持不变) ---
class WeeklyChartWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data 
        self.setMinimumSize(300, 140)
        self.setMouseTracking(True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        margin_bottom = 20
        margin_top = 20
        bar_width = (w - 40) / 7 * 0.6
        spacing = (w - 40) / 7
        
        max_val = max([d['value'] for d in self.data]) if self.data else 1
        if max_val == 0: max_val = 60 
        
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        for i, item in enumerate(self.data):
            x = 20 + i * spacing + (spacing - bar_width) / 2
            bar_height = (item['value'] / max_val) * (h - margin_bottom - margin_top)
            y = h - margin_bottom - bar_height
            
            rect = QRectF(x, y, bar_width, bar_height)
            if item['value'] > 0:
                gradient = QLinearGradient(x, h-margin_bottom, x, y)
                gradient.setColorAt(0, QColor("#9be9a8"))
                gradient.setColorAt(1, QColor("#30a14e"))
                painter.setBrush(gradient)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect, 4, 4)
            else:
                painter.setBrush(QColor("#f6f8fa"))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(QRectF(x, h-margin_bottom-2, bar_width, 2), 1, 1)
            
            painter.setPen(QColor("#586069"))
            painter.drawText(QRectF(x - 5, h - margin_bottom + 2, bar_width + 10, 20), 
                           Qt.AlignCenter, item['label'])

    def mouseMoveEvent(self, event):
        w = self.width()
        spacing = (w - 40) / 7
        idx = int((event.pos().x() - 20) / spacing)
        if 0 <= idx < len(self.data):
            val = self.data[idx]['value']
            QToolTip.showText(event.globalPos(), f"{val} мин.", self)

# --- 3. 章节进度圆环卡片 (保持不变) ---
class ChapterProgressCard(QFrame):
    def __init__(self, chapter_num, title, completed, total, percent, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 200)
        self.percent = percent
        self.completed = completed
        self.total = total
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1px solid #0366d6;
                background-color: #f0f6fc;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        
        lbl_title = QLabel(f"Глава {chapter_num}")
        lbl_title.setStyleSheet("color: #586069; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_sub = QLabel(title)
        lbl_sub.setStyleSheet("color: #24292e; font-size: 11px; border: none; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setWordWrap(True)
        lbl_sub.setFixedHeight(30)
        layout.addWidget(lbl_sub)
        
        layout.addStretch()
        
        lbl_stat = QLabel(f"{completed}/{total} задач")
        lbl_stat.setStyleSheet("color: #586069; font-size: 11px; border: none; background: transparent;")
        lbl_stat.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_stat)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        size = 80
        x = (self.width() - size) / 2
        y = 65 
        
        rect = QRectF(x, y, size, size)
        
        pen_bg = QPen(QColor("#ebedf0"), 6)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)
        
        if self.percent > 0:
            pen_prog = QPen(QColor("#28a745"), 6)
            pen_prog.setCapStyle(Qt.RoundCap)
            painter.setPen(pen_prog)
            start_angle = 90 * 16
            span_angle = -self.percent * 3.6 * 16
            painter.drawArc(rect, start_angle, span_angle)
            
        painter.setPen(QColor("#24292e"))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{self.percent}%")

# --- 主窗口 (保持不变) ---
class DashboardWindow(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.stats_manager = StatisticsManager(user_id)
        self.setWindowTitle("Статистика обучения")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #ffffff;")
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        
        self.init_ui()
        
        scroll.setWidget(content_widget)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
    def init_ui(self):
        self.setup_overview_cards()
        self.setup_charts_row()
        self.setup_chapter_grid()

    def setup_overview_cards(self):
        stats = self.stats_manager.get_total_stats()
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        self.create_stat_card(layout, "Всего ответов", str(stats['total']), "#0366d6")
        self.create_stat_card(layout, "Точность", f"{stats['accuracy']:.1f}%", "#28a745")
        self.create_stat_card(layout, "Правильно", str(stats['correct']), "#28a745")
        self.create_stat_card(layout, "Часов обучения", str(stats['hours']), "#6f42c1") 
        
        self.main_layout.addLayout(layout)

    def setup_charts_row(self):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(20)
        
        heatmap_group = QGroupBox("Активность (Год)")
        heatmap_group.setStyleSheet(self.get_group_style())
        hl = QVBoxLayout(heatmap_group)
        hl.addWidget(ActivityHeatmapWidget(self.stats_manager.get_activity_heatmap_data()))
        
        time_group = QGroupBox("Время обучения (7 дней)")
        time_group.setStyleSheet(self.get_group_style())
        tl = QVBoxLayout(time_group)
        tl.addWidget(WeeklyChartWidget(self.stats_manager.get_weekly_study_time()))
        
        row_layout.addWidget(heatmap_group, 2) 
        row_layout.addWidget(time_group, 1)    
        
        self.main_layout.addLayout(row_layout)

    def setup_chapter_grid(self):
        group = QGroupBox("Прогресс по главам")
        group.setStyleSheet(self.get_group_style())
        gl = QVBoxLayout(group)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        chapter_stats = self.stats_manager.get_chapter_progress_stats()
        
        col_count = 4
        for i, (idx, data) in enumerate(chapter_stats.items()):
            row = i // col_count
            col = i % col_count
            card = ChapterProgressCard(
                idx, 
                data['name'], 
                data['completed'], 
                data['total'], 
                data['percent']
            )
            grid.addWidget(card, row, col)
            
        gl.addLayout(grid)
        self.main_layout.addWidget(group)

    def create_stat_card(self, parent_layout, title, value, color_hex):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
            }}
        """)
        vl = QVBoxLayout(frame)
        vl.setContentsMargins(15, 15, 15, 15)
        
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {color_hex}; font-size: 26px; font-weight: bold; border: none;")
        val_lbl.setAlignment(Qt.AlignCenter)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #586069; font-size: 12px; border: none;")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        vl.addWidget(val_lbl)
        vl.addWidget(title_lbl)
        parent_layout.addWidget(frame)

    def get_group_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 20px;
                background-color: #f6f8fa;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = DashboardWindow(user_id=1)
    window.show()
    sys.exit(app.exec())
