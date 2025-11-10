"""
统计仪表板 - Dashboard Window
显示学习统计和进度分析
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QGroupBox, QListWidget
)
from PySide6.QtCore import Qt
from statistics import StatisticsManager

class DashboardWindow(QDialog):
    """统计仪表板对话框"""
    
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.stats = StatisticsManager(user_id)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Статистика обучения / Learning Statistics")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("📊 Ваша статистика / Your Statistics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db;")
        layout.addWidget(title)
        
        # 获取统计数据
        summary = self.stats.get_learning_summary()
        
        # 今日学习时长
        time_group = QGroupBox("⏱️ Время обучения сегодня / Study Time Today")
        time_layout = QVBoxLayout()
        time_label = QLabel(f"{summary['study_time_today']} минут / minutes")
        time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2ecc71;")
        time_layout.addWidget(time_label)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # 连续学习天数
        streak_group = QGroupBox("🔥 Серия дней / Study Streak")
        streak_layout = QVBoxLayout()
        streak_label = QLabel(f"{summary['study_streak']} дней подряд / days in a row")
        streak_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        streak_layout.addWidget(streak_label)
        streak_group.setLayout(streak_layout)
        layout.addWidget(streak_group)
        
        # 完成率
        completion_group = QGroupBox("✅ Прогресс курса / Course Progress")
        completion_layout = QVBoxLayout()
        
        completion_bar = QProgressBar()
        completion_bar.setValue(int(summary['completion_rate']))
        completion_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        completion_layout.addWidget(completion_bar)
        
        completion_label = QLabel(f"{summary['completion_rate']:.1f}% завершено / completed")
        completion_layout.addWidget(completion_label)
        completion_group.setLayout(completion_layout)
        layout.addWidget(completion_group)
        
        # 测验正确率
        quiz_group = QGroupBox("🎯 Точность тестов / Quiz Accuracy")
        quiz_layout = QVBoxLayout()
        
        quiz_bar = QProgressBar()
        quiz_bar.setValue(int(summary['quiz_accuracy']))
        quiz_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #2ecc71;
            }
        """)
        quiz_layout.addWidget(quiz_bar)
        
        quiz_label = QLabel(f"{summary['quiz_accuracy']:.1f}% правильных ответов / correct")
        quiz_layout.addWidget(quiz_label)
        quiz_group.setLayout(quiz_layout)
        layout.addWidget(quiz_group)
        
        # 薄弱章节
        if summary['weak_chapters']:
            weak_group = QGroupBox("⚠️ Слабые главы / Weak Chapters")
            weak_layout = QVBoxLayout()
            
            weak_list = QListWidget()
            for chapter in summary['weak_chapters']:
                weak_list.addItem(
                    f"Глава {chapter['chapter']}: {chapter['accuracy']:.1f}%"
                )
            weak_layout.addWidget(weak_list)
            weak_group.setLayout(weak_layout)
            layout.addWidget(weak_group)
        
        self.setLayout(layout)