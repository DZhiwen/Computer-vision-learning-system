"""
学习统计模块 - Statistics Manager
负责从数据库提取统计数据，支持热力图、时长估算和章节进度
"""
from datetime import datetime, timedelta
import sqlite3
import os
import sys

class StatisticsManager:
    """统计管理器"""
    
    def __init__(self, user_id, db_path=None):
        self.user_id = user_id
        
        if db_path is None:
            try:
                if sys.platform == 'win32':
                    app_data = os.path.join(os.environ['LOCALAPPDATA'], 'ComputerVisionLearning')
                else:
                    app_data = os.path.expanduser('~/.local/share/ComputerVisionLearning')
                
                if not os.path.exists(app_data):
                    os.makedirs(app_data)
                self.db_path = os.path.join(app_data, "cv_learning.db")
            except:
                self.db_path = "cv_learning.db"
        else:
            self.db_path = db_path
    
    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None

    def get_total_stats(self):
        """获取总体统计数据"""
        conn = self._get_connection()
        if not conn:
            return {"total": 0, "correct": 0, "accuracy": 0, "hours": 0}
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM quiz_answers WHERE user_id = ?", (self.user_id,))
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM quiz_answers WHERE user_id = ? AND is_correct = 1", (self.user_id,))
            correct = cursor.fetchone()[0]
            
            accuracy = (correct / total * 100) if total > 0 else 0
            
            # 估算总学习时长 (小时)
            # 假设：每题3分钟，每个章节步骤15分钟
            cursor.execute("SELECT COUNT(*) FROM chapter_progress WHERE user_id = ?", (self.user_id,))
            steps = cursor.fetchone()[0]
            
            total_minutes = (total * 3) + (steps * 15)
            hours = round(total_minutes / 60, 1)
            
            return {
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 1),
                "hours": hours
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total": 0, "correct": 0, "accuracy": 0, "hours": 0}
        finally:
            if conn: conn.close()

    def get_activity_heatmap_data(self):
        """获取热力图数据"""
        conn = self._get_connection()
        if not conn: return {}
        
        data = {}
        try:
            cursor = conn.cursor()
            # 聚合 quiz_answers 和 chapter_progress 的活动
            # 这里简化为只统计答题活动，你也可以用 UNION ALL 把 chapter_progress 加进来
            query = """
                SELECT date(updated_at) as day, COUNT(*) as count
                FROM quiz_answers 
                WHERE user_id = ? 
                AND updated_at > date('now', '-1 year')
                GROUP BY date(updated_at)
            """
            try:
                cursor.execute(query, (self.user_id,))
                for row in cursor.fetchall():
                    if row['day']: data[row['day']] = row['count']
            except:
                # Fallback for non-standard date strings
                cursor.execute("SELECT updated_at FROM quiz_answers WHERE user_id = ?", (self.user_id,))
                for row in cursor.fetchall():
                    ts = str(row[0])
                    if len(ts) >= 10:
                        d = ts[:10]
                        data[d] = data.get(d, 0) + 1
            return data
        except Exception as e:
            print(f"Error heatmap: {e}")
            return {}
        finally:
            if conn: conn.close()

    def get_weekly_study_time(self):
        """
        获取最近7天的学习时长（分钟）
        返回: [('Mon', 45), ('Tue', 120), ...]
        """
        conn = self._get_connection()
        if not conn: return []
        
        # 初始化过去7天的数据结构
        daily_minutes = {}
        today = datetime.now().date()
        days_list = []
        
        # 生成最近7天的日期列表（从6天前到今天）
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            daily_minutes[d_str] = 0
            # 俄语星期简写
            weekday_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][d.weekday()]
            days_list.append({"date": d_str, "label": weekday_ru, "value": 0})

        try:
            cursor = conn.cursor()
            
            # 1. 统计答题时间 (每题3分钟)
            cursor.execute("""
                SELECT date(updated_at), COUNT(*) 
                FROM quiz_answers 
                WHERE user_id = ? AND updated_at > date('now', '-7 days')
                GROUP BY date(updated_at)
            """, (self.user_id,))
            
            for row in cursor.fetchall():
                d = row[0]
                if d in daily_minutes:
                    daily_minutes[d] += row[1] * 3
            
            # 2. 统计章节学习时间 (每步15分钟)
            cursor.execute("""
                SELECT date(updated_at), COUNT(*) 
                FROM chapter_progress 
                WHERE user_id = ? AND updated_at > date('now', '-7 days')
                GROUP BY date(updated_at)
            """, (self.user_id,))
            
            for row in cursor.fetchall():
                d = row[0]
                if d in daily_minutes:
                    daily_minutes[d] += row[1] * 15
            
            # 填充结果列表
            for item in days_list:
                item["value"] = daily_minutes[item["date"]]
                
            return days_list
            
        except Exception as e:
            print(f"Error weekly stats: {e}")
            return days_list
        finally:
            if conn: conn.close()

    def get_chapter_progress_stats(self):
        """
        获取各章节进度
        返回: {chapter_index: {'completed': 5, 'total': 20, 'percent': 25}, ...}
        """
        conn = self._get_connection()
        stats = {}
        
        # 预定义每个章节的大致总任务数（或者你可以从 questions.db 动态获取）
        # 这里为了演示效果，假设每个章节有不同数量的任务
        chapter_totals = {1: 15, 2: 20, 3: 18, 4: 25, 5: 20, 6: 15, 7: 10}
        chapter_names = {
            1: "Введение", 
            2: "Обработка изображений", 
            3: "Признаки и дескрипторы", 
            4: "Сегментация",
            5: "Обнаружение объектов",
            6: "Распознавание лиц",
            7: "Нейронные сети"
        }
        
        for i in range(1, 8):
            stats[i] = {
                "name": chapter_names.get(i, f"Глава {i}"),
                "completed": 0,
                "total": chapter_totals.get(i, 20),
                "percent": 0
            }
            
        if not conn: return stats
        
        try:
            cursor = conn.cursor()
            # 统计已完成的步骤
            cursor.execute("""
                SELECT chapter_index, COUNT(*) 
                FROM chapter_progress 
                WHERE user_id = ? AND completed = 1
                GROUP BY chapter_index
            """, (self.user_id,))
            
            for row in cursor.fetchall():
                idx = row[0]
                if idx in stats:
                    stats[idx]["completed"] = row[1]
                    # 简单的百分比计算
                    pct = int((row[1] / stats[idx]["total"]) * 100)
                    stats[idx]["percent"] = min(100, pct)
            
            return stats
        except Exception as e:
            print(f"Error chapter stats: {e}")
            return stats
        finally:
            if conn: conn.close()
