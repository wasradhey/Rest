#pylint:disable=W0611
import os
import uuid
import string
import random
import requests
import telebot
import time
import json
from telebot import types


# Initialize bot with your token
bot = telebot.TeleBot("8451495689:AAHNt7S9FW7KB2fClL6_Ws_frXR2vpx04JQ")

# Admin IDs
ADMIN_IDS = [8331345905, 8330843046]

# Channel configuration
CHANNEL_USERNAME = "radheyhu"  # Without @
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# Colors for terminal output
R = "\033[1;31m"
G = "\033[1;32m"
B = "\033[0;94m"
Y = "\033[1;33m"

from flask import Flask
from threading import Thread


app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run_flask).start()
    
class PasswordResetTool:
    def __init__(self, target):
        self.target = target
        if self.target.startswith("@"):
            self.target = self.target[1:]  # Remove @ if provided
        
        if "@" in self.target:
            self.data = {
                "_csrftoken": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
                "user_email": self.target,
                "guid": str(uuid.uuid4()),
                "device_id": str(uuid.uuid4())
            }
        else:
            self.data = {
                "_csrftoken": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
                "username": self.target,
                "guid": str(uuid.uuid4()),
                "device_id": str(uuid.uuid4())
            }

    def send_password_reset(self):
        head = {
            "user-agent": f"Instagram 150.0.0.0.000 Android (29/10; 300dpi; 720x1440; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}/{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; en_GB;)"
        }
        try:
            start_time = time.time()
            req = requests.post(
                "https://i.instagram.com/api/v1/accounts/send_password_reset/",
                headers=head,
                data=self.data,
                timeout=10)
            end_time = time.time()
            time_taken = f"{round(end_time - start_time, 2)}s"
            return req.text, time_taken
        except Exception as e:
            return f"Request failed: {str(e)}", "0s"

def extract_info_from_response(response_text):
    """
    Extract obfuscated email or username from Instagram response
    """
    try:
        # Try to parse JSON response
        data = json.loads(response_text)
        
        # Check for obfuscated_email first
        if "obfuscated_email" in data:
            return data["obfuscated_email"]
        
        # Check for username if obfuscated_email not available
        if "username" in data:
            return f"@{data['username']}"
            
        # If neither is available, return None
        return None
    except:
        # If JSON parsing fails, try string extraction
        try:
            if "obfuscated_email" in response_text:
                return response_text.split('"obfuscated_email": "')[1].split('"')[0]
            elif "username" in response_text:
                return f"@{response_text.split('"username": "')[1].split('"')[0]}"
        except:
            pass
        
        return None

def check_membership(user_id):
    try:
        chat_member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except:
        return False

def is_admin(user_id):
    return user_id in ADMIN_IDS

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    if is_admin(message.from_user.id):
        admin_text = f"👑 Welcome back, Admin {user_name}!\n\n"
    else:
        admin_text = ""
        
    if not check_membership(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ Verify Join", callback_data="verify_join"))
        welcome_msg = f"{admin_text}📢 Please join our channel to use this bot:\n{CHANNEL_LINK}"
        bot.send_message(message.chat.id, welcome_msg, reply_markup=markup)
    else:
        show_main_menu(message)

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(call.message)
    else:
        bot.answer_callback_query(call.id, "You haven't joined the channel yet!", show_alert=True)

def show_main_menu(message):
    if is_admin(message.from_user.id):
        admin_status = "👑 Admin"
    else:
        admin_status = "👤 User"
        
    menu_text = f"""
🔧 *Instagram Password Reset* 

*Bot BY* : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)

*Available commands* :
/rstt - Reset password for single account
/bulkk - Reset passwords for multiple accounts
/help - Show help information

📌 *How to use* :
1. For single account: /reset
2. For multiple accounts: /bulk
3. Separate multiple accounts with commas or new lines
"""
    bot.send_message(message.chat.id, menu_text, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = """
📖 *Help Guide*

/rstt - Reset password for a single Instagram account
/bulkk - Reset passwords for multiple accounts (

⚙️ *Usage*:
Single account:
/rstt then enter username or email

Multiple accounts:
/bulkk then enter usernames/emails separated by commas or new lines
Example: 
account1
account2
account3

🔐 *Note*: This bot sends official Instagram password reset requests.
"""
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ This command is only available for admins!")
        return
        
    stats_text = f"""
📊 *Bot Statistics*

👑 Admins: {len(ADMIN_IDS)}
📢 Channel: @{CHANNEL_USERNAME}
🤖 Bot: @{bot.get_me().username}
🛠️ Creator: [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
"""
    bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")

@bot.message_handler(commands=['rstt'])
def start_reset(message):
    if not check_membership(message.from_user.id):
        send_welcome(message)
        return
        
    msg = bot.send_message(message.chat.id, "📨 Reply to this message with your Instagram username or email.")
    bot.register_next_step_handler(msg, process_single_reset)

def process_single_reset(message):
    target = message.text.strip()
    if target.lower() in ['/rstt', '/bulkk', '/help', '/start', '/stats']:
        bot.send_message(message.chat.id, "❌ Command not allowed as input. Please try again.")
        return
    
    # Show processing message
    processing_msg = bot.send_message(message.chat.id, f"🔁 Processing to send reset to `{target}`", parse_mode="Markdown")
    
    reset_tool = PasswordResetTool(target)
    result, time_taken = reset_tool.send_password_reset()
    
    # Extract info from response
    extracted_info = extract_info_from_response(result)
    obfuscated_info = extracted_info if extracted_info else "Not available"
    
    if "obfuscated_email" in result or "username" in result:
        success_message = f"""
🦚 *Instagram Pass Reset*

👤 *Requested by* : [{message.from_user.first_name}](@{message.from_user.username if message.from_user.username else 'N/A'})
📌 Target : `{target}`
📬 Obfuscated Info : `{obfuscated_info}`
⏱️ Speed : `{time_taken}`
🤖 Processed by: @{bot.get_me().username}
🧠 Dev : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
🎯 Bot : @rdhresetbot

✅ Password reset link sent successfully!
"""
        bot.edit_message_text(success_message, message.chat.id, processing_msg.message_id, parse_mode="Markdown")
    else:
        error_message = f"""
🦚 *Instagram Pass Reset*

👤 *Requested by* : [{message.from_user.first_name}](@{message.from_user.username if message.from_user.username else 'N/A'})
📌 Target : `{target}`
📬 Obfuscated Info : `{obfuscated_info}`
⏱️ Speed : `{time_taken}`
🤖 Processed by: @{bot.get_me().username}
🧠 Dev : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
🎯 Bot : @rdhresetbot

❌ Failed to send reset link!
📛 Reason: `{result if len(result) < 100 else result[:100] + '...'}`
"""
        bot.edit_message_text(error_message, message.chat.id, processing_msg.message_id, parse_mode="Markdown")

@bot.message_handler(commands=['bulkk'])
def start_bulk_reset(message):
    if not check_membership(message.from_user.id):
        send_welcome(message)
        return
        
    msg = bot.send_message(message.chat.id, "📝 Enter multiple usernames/emails :")
    bot.register_next_step_handler(msg, process_bulk_reset)

def process_bulk_reset(message):
    text = message.text.strip()
    if text.lower() in ['/rstt', '/bulkk', '/help', '/start', '/stats']:
        bot.send_message(message.chat.id, "❌ Command not allowed as input. Please try again.")
        return
    
    # Parse input (comma or newline separated)
    targets = [t.strip() for t in text.replace('\n', ',').split(',') if t.strip()]
    targets = targets[:99999]  # Limit to 5 targets
    
    if not targets:
        bot.send_message(message.chat.id, "❌ No valid usernames/emails provided")
        return
    
    processing_msg = bot.send_message(message.chat.id, f"⏳ Processing {len(targets)} accounts...")
    
    success_count = 0
    results = []
    
    for i, target in enumerate(targets, 1):
        # Show processing for each account
        status_msg = bot.send_message(message.chat.id, f"🔁 Processing {i}/{len(targets)}: Sending reset to `{target}`", parse_mode="Markdown")
        
        reset_tool = PasswordResetTool(target)
        result, time_taken = reset_tool.send_password_reset()
        
        # Extract info from response
        extracted_info = extract_info_from_response(result)
        obfuscated_info = extracted_info if extracted_info else "Not available"
        
        if "obfuscated_email" in result or "username" in result:
            result_text = f"✅ `{target}`: Success ⏱️ {time_taken}"
            success_count += 1
            
            # Show success result for this account
            success_result = f"""
🔰 *Reset Successful*

📌 Target: `{target}`
📬 Obfuscated Info: `{obfuscated_info}`
⏱️ Speed: `{time_taken}`
✅ Status: Reset link sent successfully!

Trying to reset the next user...
"""
            bot.edit_message_text(success_result, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        else:
            result_text = f"❌ `{target}`: Failed 📛 {result[:50]}{'...' if len(result) > 50 else ''}"
            
            # Show failure result for this account
            error_result = f"""
🔰 *Reset Failed*

📌 Target: `{target}`
📬 Obfuscated Info: `{obfuscated_info}`
⏱️ Speed: `{time_taken}`
❌ Status: Failed to send reset link!
📛 Reason: `{result if len(result) < 100 else result[:100] + '...'}`

Moving to next account...
"""
            bot.edit_message_text(error_result, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        
        results.append(result_text)
        time.sleep(2)  # Wait a bit before showing the next account
        
        # Delete the status message after a delay
        time.sleep(1)
        try:
            bot.delete_message(message.chat.id, status_msg.message_id)
        except:
            pass
    
    # Show final summary
    report = "\n".join(results)
    summary = f"\n\n📊 Summary: {success_count} successful, {len(targets)-success_count} failed"
    
    final_message = f"""
📋 *Bulk Reset Results*

{report}

{summary}

👤 *Requested by* : [{message.from_user.first_name}](@{message.from_user.username if message.from_user.username else 'N/A'})
🤖 Processed by: @{bot.get_me().username}
*Dev* : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
🎯 *Bot* : @rdhresetbot
"""
    bot.edit_message_text(final_message, message.chat.id, processing_msg.message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "❌ Unknown command. Use /help for available commands.")
    elif check_membership(message.from_user.id):
        bot.send_message(message.chat.id, "ℹ️ Please use /rstt for single account or /bulkk for multiple accounts")
    else:
        send_welcome(message)

if __name__ == "__main__":
    print(f"{G}Bot is running...{R}")
    print(f"{Y}Admin IDs: {ADMIN_IDS}{R}")
    print(f"{B}Channel: @{CHANNEL_USERNAME}{R}")
    bot.infinity_polling()
