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
            "👑 **ADMIN PANEL** 👑\n\n"
            f"👥 Unique clients: **{users_count}**\n"
            f"🧱 Calculated details: **{details_count}**\n"
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
            bot.send_message(ADMIN_ID, f" Someone new started the bot!\n First Name: {first_name}\n Last Name: {last_name}\n Username: @{user_name}\n ID: {user_id}")
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
    
    povidomlenia = bot.send_message(chat_id, "Hello! Starting a new calculation.\nPlease enter the dimensions of the first detail: thickness, length, and height separated by spaces in cm.")
    bot.register_next_step_handler(povidomlenia, inputing)
    
@bot.message_handler(commands=["help"])
def send_help(message):
    chat_id = message.chat.id
    help_text = (
        "📌 **Bot usage instructions:**\n\n"
        "1. Press /start to begin a new calculation.\n"
        "2. Enter detail dimensions (thickness, length, height) separated by a space in cm.\n"
        "3. Select a material from the list.\n"
        "4. After adding details, you can add more or finish the calculation.\n"
        "5. After finishing, you will get the order summary.\n\n"
        "👇 **If you found an error in the bot, please describe it in a message below.**\n"
        "*(This is an automated form. We cannot reply, but we will fix the bug in the future)*\n\n"
        "▶️ To just continue working, press /start"
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
    bot.send_message(chat_id, "✅ Thank you! Your message has been successfully sent to the developer.\n\nTo start calculating, press /start")
    
    try:
        message_to_admin = f"🚨 **FEEDBACK / ERROR FROM USER**\n\nFrom: {user_name} (@{username}):\nMessage: {problem_text}"
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
            bot.send_message(chat_id, "🛑 Calculation canceled.\n▶️ Press /start for a new order.")
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
        markup.add("1. Basalt", "2. Gabbro", "3. Labradorite")
        markup.add('4. Leznikovsky', '5. Kapustyansky')
        markup.add('6. Pokostovsky', '7. Zhadkovsky')
        
        povidomlenia = bot.send_message(chat_id, "Select a material for this detail:", reply_markup=markup)
        bot.register_next_step_handler(povidomlenia, stone_selection)
        
    except ValueError:
        povidomlenia = bot.send_message(chat_id, "Please enter three numbers separated by spaces.")
        bot.register_next_step_handler(povidomlenia, inputing)

def stone_selection(message):
    chat_id = message.chat.id
    if message.text and message.text.startswith('/'):
        bot.clear_step_handler_by_chat_id(chat_id)
        if message.text == '/start': send_welcome(message)
        elif message.text == '/help': send_help(message)
        elif message.text == '/over': bot.send_message(chat_id, "🛑 Calculation canceled.\n▶️ Press /start")
        return
    stone_type = message.text
    
    
    current_data = user_data.get(chat_id, {})
    V = current_data.get('current_V', 0)
    S_margin = current_data.get('current_S_margin', 0)
    S = current_data.get('current_S', 0)
    
    if 'Basalt' in stone_type: 
        p = 2950; 
        material_name = "Basalt"
    elif 'Gabbro' in stone_type: 
        p = 3000; 
        material_name = "Gabbro"
    elif 'Labradorite' in stone_type: 
        p = 2700; 
        material_name = "Labradorite"
    elif 'Leznikovsky' in stone_type: 
        p = 2650; 
        material_name = "Leznikovsky granite"
    elif 'Kapustyansky' in stone_type: 
        p = 2750; 
        material_name = "Kapustyansky granite"
    elif 'Pokostovsky' in stone_type: 
        p = 2740; 
        material_name = "Pokostovsky granite"
    elif 'Zhadkovsky' in stone_type: 
        p = 2730; 
        material_name = "Zhadkovsky granite" 
    else:
        povidomlenia = bot.send_message(chat_id, "Please select a material from the list.")
        bot.register_next_step_handler(povidomlenia, stone_selection)
        return
    m = V * p
    
    user_data[chat_id]['total_weight'] += m
    user_data[chat_id]['total_S_margin'] += S_margin
    user_data[chat_id]['total_S'] += S
    user_data[chat_id]['items_count'] += 1
    admin_stats['total_details'] += 1
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("➕ Add another detail")
    markup.add("✅ Finish and show overall summary")
    
    bot.send_message(
        chat_id, 
        f"Detail made of {material_name} ({round(m, 2)} kg) added!\nWhat should we do next?",
        reply_markup=markup
    )

    bot.register_next_step_handler(message, next_action)

def next_action(message):
    chat_id = message.chat.id
    if message.text and message.text.startswith('/'):
        bot.clear_step_handler_by_chat_id(chat_id)
        if message.text == '/start': send_welcome(message)
        elif message.text == '/help': send_help(message)
        elif message.text == '/over': bot.send_message(chat_id, "🛑 Calculation canceled.\n▶️ Press /start")
        return
    choice = message.text
    
    if choice and "Add" in choice:
        
        hide_markup = types.ReplyKeyboardRemove()
        povidomlenia = bot.send_message(chat_id, "Enter the dimensions of the next detail: thickness, length, and height in cm:", reply_markup=hide_markup)
        bot.register_next_step_handler(povidomlenia, inputing)
        
    elif choice and "Finish" in choice:
        
        current_data = user_data.get(chat_id, {})
        t_weight = current_data.get('total_weight', 0)
        t_area = current_data.get('total_S_margin', 0)
        count = current_data.get('items_count', 0)
        t_surface_area = current_data.get('total_S', 0)
        hide_markup = types.ReplyKeyboardRemove()
        final_text = (
            f" **ORDER SUMMARY:**\n\n"
            f"Number of details: **{count} pcs.**\n"
            f"Total weight: **{round(t_weight, 2)} kg**\n"
            f"Manufacturer's area (+15%): **{round(t_area, 2)} sq. m**\n"
            f"Clean surface area: **{round(t_surface_area, 2)} sq. m**\n\n"
            f"To start a new order from scratch, press /start"
        )
        bot.send_message(chat_id, final_text, parse_mode='Markdown', reply_markup=hide_markup)
    else:
        povidomlenia = bot.send_message(chat_id, "Please select one of the options.")
        bot.register_next_step_handler(povidomlenia, next_action)
        
        
@bot.message_handler(commands=["over"])
def cancel_order(message):
    chat_id = message.chat.id

    bot.clear_step_handler_by_chat_id(chat_id)
    bot.send_message(chat_id, "🛑 Current calculation canceled. All unsaved data cleared.\n\n▶️ To start a new order, press /start")

commands = [
    types.BotCommand("start", "Start a new calculation"),
    types.BotCommand("help", "Instructions and support"),
    types.BotCommand("over", "Finish calculation and clear data"),
]

bot.set_my_commands(commands)
bot.polling(none_stop=True)
