from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  
CORS(app)


GEMINI_API_KEY = "AIzaSyDaXKzSOujg24gO53kvrdFC9grXFex8wU4"  


genai.configure(api_key=GEMINI_API_KEY)


SYSTEM_PROMPT = """Ты — AI-помощник "KegrosAI" для абитуриентов Казахстана на сайте KegrosKZ.
Ты помогаешь выбирать университеты, готовиться к поступлению и отвечаешь на вопросы об образовании.

О САЙТЕ:
- KegrosKZ — агрегатор университетов Казахстана
- Есть страницы: Назарбаев Университет (НУ), КБТУ, МУИТ/IITU и другие
- Показываем реальные отзывы и скрытую информацию

ЧТО ТЫ ЗНАЕШЬ:
1. НАЗАРБАЕВ УНИВЕРСИТЕТ (НУ):
   - Топ-1 в Казахстане
   - Международные стандарты
   - Обучение на английском
   - Высокая стоимость (10-12 млн за 4 года)
   - 80% студентов на грантах
   - Нужны: SAT, IELTS, мотивационное письмо

2. КБТУ:
   - Лучший технический вуз
   - Сильные направления: нефтегаз, IT
   - Британские дипломы
   - Стоимость: 2.5-3 млн/год
   - 25% грантов на каждом факультете

3. МУИТ (IITU):
   - IT-вуз №1
   - Хакатоны каждые 2 недели
   - 98% трудоустройство в IT
   - Стоимость: 2.8-3.5 млн/год
   - 30% грантов, 30% скидок

4. ОБЩАЯ ИНФОРМАЦИЯ:
   - ЕНТ: 120+ баллов для грантов
   - Гранты: государственные, целевые, "Болашак"
   - Общежития: 50к-200к тенге/семестр
   - Средняя зарплата выпускников IT: 700к-1.2м тенге

ТВОЙ СТИЛЬ:
- Дружелюбный, используй эмодзи 🎓📚🏫
- Говори на "ты"
- Будь конкретным, приводи примеры
- Если не знаешь — честно говори
- Всегда советуй проверять на официальных сайтах

Начинай с приветствия и объясни свои возможности."""

# Храним историю чатов в памяти (в продакшене используй БД)
chat_sessions = {}

def get_gemini_response(user_message, history):
    """Получаем ответ от Gemini AI"""
    try:
        # Создаем модель
        model = genai.GenerativeModel('gemini-pro')
        
        # Формируем полный промпт
        prompt = f"""{SYSTEM_PROMPT}

История диалога:
{history}

Пользователь: {user_message}

KegrosAI:"""
        
        # Генерируем ответ
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 1000,
            }
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        return "Извини, у меня временные технические трудности. Попробуй задать вопрос позже! 😔"

@app.route('/')
def home():
    """Главная страница"""
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    """Страница чата"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API для общения с AI"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
        # Инициализируем или получаем историю
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        history = chat_sessions[session_id]
        
        # Добавляем сообщение пользователя в историю
        history.append({'role': 'user', 'content': user_message, 'time': datetime.now().isoformat()})
        
        # Получаем ответ от Gemini
        ai_response = get_gemini_response(user_message, "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]]))
        
        # Добавляем ответ AI в историю
        history.append({'role': 'assistant', 'content': ai_response, 'time': datetime.now().isoformat()})
        
        # Ограничиваем историю (последние 10 сообщений)
        if len(history) > 10:
            history = history[-10:]
        
        chat_sessions[session_id] = history
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Ошибка в API: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

@app.route('/api/clear_chat', methods=['POST'])
def clear_chat():
    """Очистка истории чата"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in chat_sessions:
            chat_sessions[session_id] = []
        
        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    """Новый чат"""
    try:
        data = request.json
        old_session_id = data.get('session_id', 'default')
        new_session_id = f"session_{datetime.now().timestamp()}"
        
        # Создаем новую сессию
        chat_sessions[new_session_id] = []
        
        return jsonify({
            'success': True,
            'new_session_id': new_session_id,
            'message': 'Новый чат создан'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=True)