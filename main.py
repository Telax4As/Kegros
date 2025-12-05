from google import genai
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с других доменов
sys.stdout.reconfigure(encoding='utf-8')

# Твой ключ Gemini
client = genai.Client(api_key='AIzaSyAxzVm7Z77oSNw2AIQTMzXepGZgihHmAOI')

# Системный промпт для KegrosKZ
SYSTEM_INSTRUCTION = """Ты — консультант по поступлению в вузы Казахстана. Отвечай кратко, по делу, без эмодзи и лишних символов (*, **). 

Правила:
1. Отвечай сразу на вопрос, без вступлений типа "Привет!" или "Отличный выбор!"
2. Используй только обычные предложения, без форматирования
3. Не ставь эмодзи, звёздочки, смайлы
4. Если нужен список — используй обычные цифры с точкой
5. Будь точным и информативным

Твоя роль: давать чёткие, структурированные ответы о вузах, требованиях, экзаменах.

О САЙТЕ:
- Название: KegrosKZ
- Миссия: помощь абитуриентам Казахстана в выборе вузов
- Особенности: реальные отзывы, скрытая информация, рейтинги 2025

ИНФОРМАЦИЯ О ВУЗАХ:

1. НАЗАРБАЕВ УНИВЕРСИТЕТ (НУ) — рейтинг KegrosKZ: 9.8/10
   • Топ-1 в Казахстане
   • Стоимость: 10-12 млн тенге за 4 года
   • Гранты: 80% студентов учатся бесплатно
   • Требования: SAT/ACT, IELTS 6.5+, мотивационное письмо
   • Особенность: международные стандарты, обучение на английском

2. КБТУ — рейтинг KegrosKZ: 8.2/10
   • Лучший технический вуз
   • Сильные направления: нефтегаз, IT
   • Стоимость: 2.5-3 млн тенге/год
   • Гранты: 25% на каждом факультете
   • Особенность: двойные дипломы с британскими вузами

3. МУИТ (IITU) — рейтинг KegrosKZ: 7.5/10
   • IT-вуз №1 в Казахстане
   • Хакатоны каждые 2 недели
   • Трудоустройство: 98% выпускников в IT
   • Стоимость: 2.8-3.5 млн тенге/год
   • Гранты: 30% бесплатного обучения

4. ДРУГИЕ ВУЗЫ:
   • КазНУ им. Аль-Фараби (7.9/10) — крупнейший классический университет
   • ЕНУ им. Гумилева (7.3/10) — сильный гуманитарный вуз
   • КазНИТУ им. Сатпаева (8.0/10) — технический гигант

ОБЩАЯ ИНФОРМАЦИЯ:
• ЕНТ для грантов: 120+ баллов
• Общежития: 50,000-200,000 тенге/семестр
• Зарплаты выпускников: IT — 1.2M, нефтегаз — 1.5M, бизнес — 900K тенге
• Дедлайны: декабрь-февраль (заявки), июнь-июль (результаты)

ТВОЙ СТИЛЬ:
• Имя: KegrosAI (от KegrosKZ)
• Используй эмодзи 🎓🏫📚💰
• Говори на "ты"
• Будь конкретным, приводи цифры и примеры
• Упоминай рейтинги KegrosKZ
• Всегда советуй проверять информацию на официальных сайтах вузов

Примеры ответов:
• "Согласно данным KegrosKZ 2025..."
• "Рейтинг KegrosKZ для этого вуза..."
• "На сайте KegrosKZ мы рекомендуем..."

Начинай с приветствия от имени KegrosKZ."""

# Хранилище чатов (временное, в продакшене используй БД)
chat_sessions = {}

@app.route('/')
def home():
    """Главная страница API"""
    return jsonify({
        'service': 'KegrosKZ AI Assistant',
        'status': 'online',
        'endpoints': {
            '/ask': 'POST - Основной чат с AI',
            '/api/chat': 'POST - Улучшенный чат с историей',
            '/api/clear': 'POST - Очистить историю чата',
            '/api/new': 'POST - Создать новый чат',
            '/api/status': 'GET - Статус сервера'
        },
        'ai_model': 'Gemini 2.5 Flash Lite',
        'version': '1.0'
    })

@app.route('/ask', methods=['POST'])
def ask():
    """Основной endpoint (совместимость с твоим кодом)"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
        # Формируем промпт с системной инструкцией
        full_prompt = f"""Системная инструкция: {SYSTEM_INSTRUCTION}

Пользователь спрашивает: {user_message}

Ответь как KegrosAI от KegrosKZ:"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt
        )
        
        return jsonify({
            'answer': response.text,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Улучшенный endpoint с поддержкой истории"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Введите сообщение'}), 400
        
        # Получаем или создаем историю чата
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        history = chat_sessions[session_id]
        
        # Формируем полный промпт с историей
        history_text = ""
        if history:
            history_text = "\nИстория разговора:\n"
            for msg in history[-5:]:  # Берем последние 5 сообщений
                role = "Пользователь" if msg['role'] == 'user' else "KegrosAI"
                history_text += f"{role}: {msg['content']}\n"
        
        full_prompt = f"""Системная инструкция: {SYSTEM_INSTRUCTION}
{history_text}
Новое сообщение от пользователя: {user_message}

Ответь как KegrosAI от KegrosKZ, учитывая историю разговора:"""
        
        # Получаем ответ от AI
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt
        )
        
        ai_response = response.text.strip()
        
        # Сохраняем в историю
        history.append({
            'role': 'user',
            'content': user_message,
            'time': datetime.now().isoformat()
        })
        history.append({
            'role': 'assistant',
            'content': ai_response,
            'time': datetime.now().isoformat()
        })
        
        # Ограничиваем историю (последние 20 сообщений)
        if len(history) > 20:
            history = history[-20:]
        
        chat_sessions[session_id] = history
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'history_length': len(history),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Очистить историю чата"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        if session_id in chat_sessions:
            chat_sessions[session_id] = []
        
        return jsonify({
            'success': True,
            'message': 'История чата очищена',
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new', methods=['POST'])
def new_chat():
    """Создать новый чат с новым session_id"""
    try:
        data = request.get_json()
        old_session_id = data.get('session_id', 'default')
        
        # Создаем новый уникальный ID
        new_session_id = f"chat_{int(datetime.now().timestamp())}"
        chat_sessions[new_session_id] = []
        
        # Очищаем старую сессию если нужно
        if data.get('clear_old', False) and old_session_id in chat_sessions:
            del chat_sessions[old_session_id]
        
        return jsonify({
            'success': True,
            'new_session_id': new_session_id,
            'message': 'Новый чат создан'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Проверка статуса сервера и AI"""
    try:
        # Проверяем подключение к Gemini
        test_response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents="Hello"
        )
        
        return jsonify({
            'status': 'online',
            'service': 'KegrosKZ AI Assistant',
            'ai_model': 'Gemini 2.5 Flash Lite',
            'ai_status': 'connected',
            'active_sessions': len(chat_sessions),
            'timestamp': datetime.now().isoformat(),
            'endpoints': [
                '/ask (POST) - основной чат',
                '/api/chat (POST) - чат с историей',
                '/api/clear (POST) - очистить чат',
                '/api/new (POST) - новый чат',
                '/api/status (GET) - статус'
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'online',
            'ai_status': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 KEGROSKZ AI ПОМОЩНИК ЗАПУЩЕН!")
    print("=" * 50)
    print("📡 Сервер: http://localhost:5000")
    print("🤖 AI: KegrosAI (Gemini 2.5 Flash Lite)")
    print("🎓 Сайт: KegrosKZ - агрегатор университетов Казахстана")
    print("=" * 50)
    print("📋 Доступные endpoints:")
    print("  • GET  /           - информация о сервисе")
    print("  • POST /ask        - основной чат (совместимость)")
    print("  • POST /api/chat   - улучшенный чат с историей")
    print("  • POST /api/clear  - очистить историю чата")
    print("  • POST /api/new    - создать новый чат")
    print("  • GET  /api/status - статус сервера")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)