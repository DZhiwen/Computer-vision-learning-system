"""
学习统计模块 - Statistics Manager (最终修复版)
完全适配现有的 DatabaseManager 结构
"""
from datetime import datetime, timedelta
import sqlite3
import os

class StatisticsManager:
    """统计管理器 - 完全兼容现有数据库"""
    
    def __init__(self, user_id, db_path=None):
        self.user_id = user_id
        
        # 如果没有提供数据库路径，使用默认路径
        if db_path is None:
            try:
                from db_manager import get_user_data_dir
                data_dir = get_user_data_dir()
                self.db_path = os.path.join(data_dir, "cv_learning.db")
            except:
                self.db_path = "cv_learning.db"
        else:
            self.db_path = db_path
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def get_study_time_today(self):
        """获取今日学习时长（分钟）
        
        由于原始数据库没有学习时长表，这里基于今天的答题记录估算
        """
        conn = self._get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 统计今天的答题数量，假设每题平均1分钟
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM quiz_answers
                WHERE user_id = ? 
                AND DATE(updated_at) = ?
            """, (self.user_id, today))
            
            result = cursor.fetchone()
            count = result['count'] if result else 0
            
            # 估算学习时长：每道题约1分钟，加上阅读时间
            estimated_time = count * 1.5  # 1.5分钟/题
            
            return int(estimated_time) if estimated_time > 0 else 0
            
        except Exception as e:
            print(f"获取学习时长失败: {e}")
            return 0
        finally:
            conn.close()
    
    def get_study_streak(self):
        """获取连续学习天数
        
        基于 chapter_progress 或 quiz_answers 表的更新时间计算
        """
        conn = self._get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            
            # 获取用户所有活动日期（去重）
            cursor.execute("""
                SELECT DISTINCT DATE(updated_at) as activity_date
                FROM chapter_progress
                WHERE user_id = ?
                UNION
                SELECT DISTINCT DATE(updated_at) as activity_date
                FROM quiz_answers
                WHERE user_id = ?
                ORDER BY activity_date DESC
            """, (self.user_id, self.user_id))
            
            dates = [row['activity_date'] for row in cursor.fetchall()]
            
            if not dates:
                return 0
            
            # 计算连续天数
            streak = 1
            today = datetime.now().date()
            
            # 检查最近一次活动是否是今天或昨天
            last_date = datetime.strptime(dates[0], '%Y-%m-%d').date()
            days_since_last = (today - last_date).days
            
            if days_since_last > 1:
                return 0  # 中断了
            
            # 计算连续天数
            for i in range(len(dates) - 1):
                date1 = datetime.strptime(dates[i], '%Y-%m-%d').date()
                date2 = datetime.strptime(dates[i + 1], '%Y-%m-%d').date()
                diff = (date1 - date2).days
                
                if diff == 1:
                    streak += 1
                else:
                    break
            
            return streak
            
        except Exception as e:
            print(f"获取连续天数失败: {e}")
            return 0
        finally:
            conn.close()
    
    def get_completion_rate(self):
        """获取课程完成率
        
        基于 chapter_progress 表中 completed=1 的记录
        """
        conn = self._get_connection()
        if not conn:
            return 0.0
        
        try:
            cursor = conn.cursor()
            
            # 统计已完成的步骤数
            cursor.execute("""
                SELECT COUNT(*) as completed_count
                FROM chapter_progress
                WHERE user_id = ? AND completed = 1
            """, (self.user_id,))
            
            result = cursor.fetchone()
            completed_count = result['completed_count'] if result else 0
            
            # 假设总共有 7 章，每章 5 个步骤
            total_steps = 7 * 5  # 35 个步骤
            
            completion_rate = (completed_count / total_steps) * 100 if total_steps > 0 else 0.0
            
            return round(completion_rate, 1)
            
        except Exception as e:
            print(f"获取完成率失败: {e}")
            return 0.0
        finally:
            conn.close()
    
    def get_quiz_accuracy(self):
        """获取测验正确率
        
        基于 quiz_answers 表中的 is_correct 字段
        """
        conn = self._get_connection()
        if not conn:
            return 0.0
        
        try:
            cursor = conn.cursor()
            
            # 统计总题数和正确题数
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM quiz_answers
                WHERE user_id = ?
            """, (self.user_id,))
            
            result = cursor.fetchone()
            
            if not result or result['total'] == 0:
                return 0.0
            
            total = result['total']
            correct = result['correct'] if result['correct'] else 0
            
            accuracy = (correct / total) * 100
            
            return round(accuracy, 1)
            
        except Exception as e:
            print(f"获取测验正确率失败: {e}")
            return 0.0
        finally:
            conn.close()
    
    def get_weak_chapters(self):
        """获取薄弱章节（正确率低于70%的章节）
        
        基于 quiz_answers 表按章节统计
        """
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # 按章节统计正确率
            cursor.execute("""
                SELECT 
                    chapter_index,
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM quiz_answers
                WHERE user_id = ?
                GROUP BY chapter_index
            """, (self.user_id,))
            
            chapters = cursor.fetchall()
            
            weak_chapters = []
            for chapter in chapters:
                chapter_index = chapter['chapter_index']
                total = chapter['total']
                correct = chapter['correct'] if chapter['correct'] else 0
                
                accuracy = (correct / total) * 100 if total > 0 else 0
                
                if accuracy < 70:
                    weak_chapters.append({
                        'chapter': f"第{chapter_index + 1}章",
                        'chapter_index': chapter_index,
                        'accuracy': round(accuracy, 1),
                        'total_questions': total,
                        'correct_answers': correct
                    })
            
            # 按正确率排序（从低到高）
            weak_chapters.sort(key=lambda x: x['accuracy'])
            
            return weak_chapters
            
        except Exception as e:
            print(f"获取薄弱章节失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_chapter_statistics(self):
        """获取各章节详细统计"""
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # 按章节统计进度和测验情况
            cursor.execute("""
                SELECT 
                    cp.chapter_index,
                    COUNT(DISTINCT cp.step_index) as completed_steps,
                    SUM(cp.completed) as total_completed,
                    COUNT(qa.id) as quiz_count,
                    SUM(CASE WHEN qa.is_correct = 1 THEN 1 ELSE 0 END) as quiz_correct
                FROM chapter_progress cp
                LEFT JOIN quiz_answers qa 
                    ON cp.user_id = qa.user_id 
                    AND cp.chapter_index = qa.chapter_index
                WHERE cp.user_id = ?
                GROUP BY cp.chapter_index
                ORDER BY cp.chapter_index
            """, (self.user_id,))
            
            chapters = []
            for row in cursor.fetchall():
                chapter_index = row['chapter_index']
                quiz_count = row['quiz_count'] if row['quiz_count'] else 0
                quiz_correct = row['quiz_correct'] if row['quiz_correct'] else 0
                
                accuracy = (quiz_correct / quiz_count * 100) if quiz_count > 0 else 0
                
                chapters.append({
                    'chapter': f"第{chapter_index + 1}章",
                    'chapter_index': chapter_index,
                    'completed_steps': row['completed_steps'],
                    'quiz_count': quiz_count,
                    'quiz_accuracy': round(accuracy, 1)
                })
            
            return chapters
            
        except Exception as e:
            print(f"获取章节统计失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_recent_activity(self, days=7):
        """获取最近N天的活动统计"""
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # 获取最近N天的每日活动
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT 
                    DATE(updated_at) as activity_date,
                    COUNT(DISTINCT chapter_index) as chapters_studied,
                    COUNT(*) as questions_answered,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers
                FROM quiz_answers
                WHERE user_id = ? AND DATE(updated_at) >= ?
                GROUP BY DATE(updated_at)
                ORDER BY activity_date DESC
            """, (self.user_id, start_date))
            
            activities = []
            for row in cursor.fetchall():
                questions = row['questions_answered']
                correct = row['correct_answers'] if row['correct_answers'] else 0
                accuracy = (correct / questions * 100) if questions > 0 else 0
                
                activities.append({
                    'date': row['activity_date'],
                    'chapters_studied': row['chapters_studied'],
                    'questions_answered': questions,
                    'accuracy': round(accuracy, 1)
                })
            
            return activities
            
        except Exception as e:
            print(f"获取最近活动失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_learning_summary(self):
        """获取学习总结（完整版）"""
        return {
            'study_time_today': self.get_study_time_today(),
            'study_streak': self.get_study_streak(),
            'completion_rate': self.get_completion_rate(),
            'quiz_accuracy': self.get_quiz_accuracy(),
            'weak_chapters': self.get_weak_chapters(),
            'chapter_statistics': self.get_chapter_statistics(),
            'recent_activity': self.get_recent_activity()
        }
    
    def get_simple_summary(self):
        """获取简单总结（用于仪表盘显示）"""
        return {
            'study_time_today': self.get_study_time_today(),
            'study_streak': self.get_study_streak(),
            'completion_rate': self.get_completion_rate(),
            'quiz_accuracy': self.get_quiz_accuracy()
        }


# 测试代码
if __name__ == "__main__":
  print("=" * 60)
  print("测试统计模块")
  print("=" * 60)
  
  # 创建测试用户（假设 user_id = 1）
  stats = StatisticsManager(user_id=1)
  
  print("\n1. 简单总结:")
  summary = stats.get_simple_summary()
  for key, value in summary.items():
      print(f"   {key}: {value}")
  
  print("\n2. 薄弱章节:")
  weak = stats.get_weak_chapters()
  if weak:
      for chapter in weak:
          print(f"   {chapter['chapter']}: {chapter['accuracy']}%")
  else:
      print("   暂无数据")
  
  print("\n3. 章节统计:")
  chapters = stats.get_chapter_statistics()
  if chapters:
      for chapter in chapters:
          print(f"   {chapter['chapter']}: 完成{chapter['completed_steps']}步, "
                f"答题{chapter['quiz_count']}题, 正确率{chapter['quiz_accuracy']}%")
  else:
      print("   暂无数据")
  
  print("\n4. 最近7天活动:")
  activities = stats.get_recent_activity(7)
  if activities:
      for activity in activities:
          print(f"   {activity['date']}: 学习{activity['chapters_studied']}章, "
                f"答题{activity['questions_answered']}题, 正确率{activity['accuracy']}%")
  else:
      print("   暂无数据")
  
  print("\n✓ 测试完成")