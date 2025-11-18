"""AI评分工具类 - 复用现有AI助手配置"""
import requests
import json
from settings_window import SettingsManager
import os
from db_manager import get_user_data_dir
class AIScorer:
    def __init__(self):
        self.settings = SettingsManager()
        self.ai_type = self.settings.get("ai_assistant", "deepseek")  # 读取用户选择的AI助手
        self.api_keys = self._load_api_keys()  # 从配置文件加载API密钥

    def _load_api_keys(self):
        """从配置文件读取API密钥（需用户在设置中配置）"""
        config_path = os.path.join(get_user_data_dir(), "ai_api_keys.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"deepseek": "", "qwen": ""}

    def score_subjective_answer(self, question_text, user_answer, score_criteria):
        """
        AI评分核心方法
        question_text: 主观题题目
        user_answer: 用户答案
        score_criteria: 评分标准（字典）
        返回：(ai_score, ai_feedback)
        """
        # 构建评分提示词（明确要求AI按得分点打分）
        prompt = f"""
        Ты являешься экспертом по компьютерному зрению. Оцени ответ пользователя по следующим правилам:
        1. Вопрос: {question_text}
        2. Максимальный балл: {score_criteria['full_score']}
        3. Ключевые слова для оценки: {', '.join(score_criteria['keywords'])}
        4. Пункты для оценки:
        {chr(10).join([f"- {p}" for p in score_criteria['points']])}
        5. Ответ пользователя: {user_answer}
        
        Требования к твоему ответу:
        - Сначала выведи итоговый балл цифрой (без текста), например: 8
        - Затем выведи комментарий (по-русски), объяснив, какие пункты выполнены, какие нет.
        - Не добавляй лишнюю информацию, строго следуй формату.
        """

        # 调用对应AI API
        try:
            if self.ai_type == "deepseek":
                return self._call_deepseek_api(prompt)
            elif self.ai_type == "qwen":
                return self._call_qwen_api(prompt)
            else:
                return None, "Не выбран AI ассистент"
        except Exception as e:
            return None, f"AI评分失败: {str(e)}"

    def _call_deepseek_api(self, prompt):
        """调用DeepSeek API"""
        api_key = self.api_keys.get("deepseek", "")
        if not api_key:
            return None, "Пожалуйста, настройте ключ API DeepSeek в настройках."
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3  # 降低随机性，保证评分一致性
        }
        response = requests.post(url, json=data, timeout=30)
        result = response.json()["choices"][0]["message"]["content"].split(chr(10), 1)
        ai_score = int(result[0].strip()) if result[0].strip().isdigit() else None
        ai_feedback = result[1].strip() if len(result) > 1 else "无评语"
        return ai_score, ai_feedback

    def _call_qwen_api(self, prompt):
        """调用Qwen API（类似DeepSeek，需替换对应URL和参数）"""
        api_key = self.api_keys.get("qwen", "")
        if not api_key:
            return None, "Пожалуйста, настройте ключ API Qwen в настройках."
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "qwen-turbo",
            "input": {"messages": [{"role": "user", "content": prompt}]},
            "parameters": {"temperature": 0.3}
        }
        response = requests.post(url, json=data, timeout=30)
        result = response.json()["output"]["choices"][0]["message"]["content"].split(chr(10), 1)
        ai_score = int(result[0].strip()) if result[0].strip().isdigit() else None
        ai_feedback = result[1].strip() if len(result) > 1 else "无评语"
        return ai_score, ai_feedback