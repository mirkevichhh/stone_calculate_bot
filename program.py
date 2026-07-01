import telebot
from telebot import types

TOKEN = "YOUR_TOKEN_HERE" 
bot = telebot.TeleBot(TOKEN)
user_data = {}
ADMIN_ID = YOUR_TELEGRAM_ID
admin_stats = {
    'unique_users': set(), 
    'total_details': 0
}

@bot.message_handler(commands=["stats","admin"])
def admin_panel(message):
    chat_id = message.chat.id
    if chat_id == ADMIN_ID:
        users_count = len(admin_stats['unique_users'])
        details_count = admin_stats['total_details']
        
        text = (
            "👑 **ПАНЕЛЬ АДМІНІСТРАТОРА** 👑\n\n"
            f"👥 Унікальних клієнтів: **{users_count}**\n"
            f"🧱 Прораховано деталей: **{details_count}**\n"
        )
        bot.send_message(chat_id, text, parse_mode='Markdown')
        
@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    user_id = message.from_user.id
    user_name = message.from_user.username
    admin_stats['unique_users'].add(chat_id)
    
    if chat_id != ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, f" Хтось новий запустив бота!\n Ім'я: {first_name}\n Прізвище: {last_name}\n Нікнейм: @{user_name}\n ID: {user_id}")
        except:
            pass
    
    user_data[chat_id] = {
        'total_weight': 0,  
        'total_S_margin': 0, 
        'total_S': 0,       
        'items_count': 0,
        'current_V': 0,    
        'current_S_margin': 0, 
        'current_S': 0
    }
    
    povidomlenia = bot.send_message(chat_id, "Привіт! Починаємо новий розрахунок.\nНапишіть розміри першої деталі: товщина, довжина та висота через пробіл в см.")
    bot.register_next_step_handler(povidomlenia, inputing)
    
@bot.message_handler(commands=["help"])
def send_help(message):
    chat_id = message.chat.id
    help_text = (
        "📌 **Інструкція по використанню бота:**\n\n"
        "1. Натисніть /start для початку нового розрахунку.\n"
        "2. Введіть розміри деталі (товщина, довжина, висота) через пробіл в см.\n"
        "3. Виберіть матеріал зі списку.\n"
        "4. Після додавання деталей ви можете додати ще або завершити розрахунок.\n"
        "5. Після завершення ви отримаєте підсумок замовлення.\n\n"
        "👇 **Якщо ви знайшли помилку в роботі бота, просто опишіть її в повідомленні нижче.**\n"
        "*(Це автоматична форма. Ми не зможемо вам відповісти, але обов'язково виправимо баг у майбутньому)*\n\n"
        "▶️ Щоб просто продовжити роботу, натисніть /start"
    )
    povidomlenia = bot.send_message(chat_id, help_text, parse_mode='Markdown')
    bot.register_next_step_handler(povidomlenia, receive_problem)
    
def receive_problem(message):
    chat_id = message.chat.id
    problem_text = message.text
    if problem_text == '/start':
        send_welcome(message)
        return
    
    user_name = message.from_user.first_name
    username = message.from_user.username
    bot.send_message(chat_id, "✅ Дякуємо! Ваше повідомлення успішно надіслано розробнику.\n\nЩоб почати розрахунки, натисніть /start")
    
    try:
        message_to_admin = f"Повідомлення від користувача {user_name} (@{username}):\n{problem_text}"
        bot.send_message(ADMIN_ID, message_to_admin)
    except:
        pass


def inputing(message):
    chat_id = message.chat.id
    
    if message.text and message.text.startswith('/'):
        bot.clear_step_handler_by_chat_id(chat_id) 
        if message.text == '/start':
            send_welcome(message)
        elif message.text == '/help':
            send_help(message) 
        elif message.text == '/over':
            bot.send_message(chat_id, "🛑 Розрахунок скасовано.\n▶️ Натисніть /start для нового замовлення.")
        return
    try:
        large, weight, hight = map(float, message.text.split())
        large *= 0.01
        weight *= 0.01
        hight *= 0.01
        
        V = large * weight * hight
        S = 2 * (large * weight + large * hight + weight * hight)
        S_by_masters = S * 0.15 + S
        
        
        user_data[chat_id]['current_V'] = V
        user_data[chat_id]['current_S_margin'] = S_by_masters
        user_data[chat_id]['current_S'] = S
        
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("1. Базальт", "2. Габро", "3. Лабрадорит")
        markup.add('4. Лезниківський', '5. Капустянський')
        markup.add('6. Покостівський', '7. Жадківський')
        
        povidomlenia = bot.send_message(chat_id, "Виберіть матеріал для цієї деталі:", reply_markup=markup)
        bot.register_next_step_handler(povidomlenia, stone_selection)
        
    except ValueError:
        povidomlenia = bot.send_message(chat_id, "Будь ласка, введіть три числа через пробіл.")
        bot.register_next_step_handler(povidomlenia, inputing)

def stone_selection(message):
    chat_id = message.chat.id
    if message.text and message.text.startswith('/'):
        bot.clear_step_handler_by_chat_id(chat_id)
        if message.text == '/start': send_welcome(message)
        elif message.text == '/help': send_help(message)
        elif message.text == '/over': bot.send_message(chat_id, "🛑 Розрахунок скасовано.\n▶️ Натисніть /start")
        return
    stone_type = message.text
    
    
    current_data = user_data.get(chat_id, {})
    V = current_data.get('current_V', 0)
    S_margin = current_data.get('current_S_margin', 0)
    S = current_data.get('current_S', 0)
    
    if 'Базальт' in stone_type: 
        p = 2950; 
        material_name = "Базальту"
    elif 'Габро' in stone_type: 
        p = 3000; 
        material_name = "Габра"
    elif 'Лабрадорит' in stone_type: 
        p = 2700; 
        material_name = "Лабрадориту"
    elif 'Лезниківський' in stone_type: 
        p = 2650; 
        material_name = "Лезниківського граніту"
    elif 'Капустянський' in stone_type: 
        p = 2750; 
        material_name = "Капустянського граніту"
    elif 'Покостівський' in stone_type: 
        p = 2740; 
        material_name = "Покостівського граніту"
    elif 'Жадківський' in stone_type: 
        p = 2730; 
        material_name = "Жадківського граніту" 
    else:
        povidomlenia = bot.send_message(chat_id, "Будь ласка, виберіть матеріал зі списку.")
        bot.register_next_step_handler(povidomlenia, stone_selection)
        return
    m = V * p
    
    user_data[chat_id]['total_weight'] += m
    user_data[chat_id]['total_S_margin'] += S_margin
    user_data[chat_id]['total_S'] += S
    user_data[chat_id]['items_count'] += 1
    admin_stats['total_details'] += 1
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("➕ Додати ще деталь")
    markup.add("✅ Завершити і показати загальну статистику")
    
    bot.send_message(
        chat_id, 
        f"Деталь з {material_name} ({round(m, 2)} кг) додано!\nЩо робимо далі?",
        reply_markup=markup
    )

    bot.register_next_step_handler(message, next_action)

def next_action(message):
    chat_id = message.chat.id
    if message.text and message.text.startswith('/'):
        bot.clear_step_handler_by_chat_id(chat_id)
        if message.text == '/start': send_welcome(message)
        elif message.text == '/help': send_help(message)
        elif message.text == '/over': bot.send_message(chat_id, "🛑 Розрахунок скасовано.\n▶️ Натисніть /start")
        return
    choice = message.text
    
    if choice and "Додати" in choice:
        
        hide_markup = types.ReplyKeyboardRemove()
        povidomlenia = bot.send_message(chat_id, "Напишіть розміри наступної деталі: товщина, довжина та висота в см:", reply_markup=hide_markup)
        bot.register_next_step_handler(povidomlenia, inputing)
        
    elif choice and "Завершити" in choice:
        
        current_data = user_data.get(chat_id, {})
        t_weight = current_data.get('total_weight', 0)
        t_area = current_data.get('total_S_margin', 0)
        count = current_data.get('items_count', 0)
        t_surface_area = current_data.get('total_S', 0)
        hide_markup = types.ReplyKeyboardRemove()
        final_text = (
            f" **ПІДСУМОК ЗАМОВЛЕННЯ:**\n\n"
            f"Кількість деталей: **{count} шт.**\n"
            f"Загальна маса: **{round(t_weight, 2)} кг**\n"
            f"Площа від виробників(+15%): **{round(t_area, 2)} кв. м**\n"
            f"Чиста площа: **{round(t_surface_area, 2)} кв. м**\n\n"
            f"Щоб почати нове замовлення з нуля, натисніть /start"
        )
        bot.send_message(chat_id, final_text, parse_mode='Markdown', reply_markup=hide_markup)
    else:
        povidomlenia = bot.send_message(chat_id, "Будь ласка, оберіть одну з опцій.")
        bot.register_next_step_handler(povidomlenia, next_action)
        
        
@bot.message_handler(commands=["over"])
def cancel_order(message):
    chat_id = message.chat.id

    bot.clear_step_handler_by_chat_id(chat_id)
    bot.send_message(chat_id, "🛑 Поточний розрахунок скасовано. Усі незбережені дані очищено.\n\n▶️ Щоб почати нове замовлення, натисніть /start")

commands = [
    types.BotCommand("start", "Почати новий розрахунок"),
    types.BotCommand("help", "Інструкція та підтримка"),
    types.BotCommand("over", "Закінчити розрахунок та очистити дані"),
]

bot.set_my_commands(commands)
bot.polling(none_stop=True)