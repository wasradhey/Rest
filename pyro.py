import os
import uuid
import string
import random
import requests
import time
import json
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.enums import ParseMode, ChatMemberStatus

# Bot configuration
API_ID = 25009640
API_HASH = "c55f00011863ecc5a0a6e5f194e725ab"
BOT_TOKEN = "8451495689:AAHNt7S9FW7KB2fClL6_Ws_frXR2vpx04JQ"

# Admin IDs
ADMIN_IDS = [8331345905, 8330843046]

# Channel configuration
CHANNEL_USERNAME = "radheyhu"  # Without @
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# Global dictionary to track ongoing operations
ongoing_operations = {}

# Initialize Pyrogram client
app = Client(
    "instagram_reset_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

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

async def check_membership(user_id):
    try:
        chat_member = await app.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

def is_admin(user_id):
    return user_id in ADMIN_IDS

@app.on_message(filters.command("start"))
async def send_welcome(client, message: Message):
    user_name = message.from_user.first_name
    if is_admin(message.from_user.id):
        admin_text = f"👑 Welcome back, Admin {user_name}!\n\n"
    else:
        admin_text = ""
        
    if not await check_membership(message.from_user.id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")]
        ])
        welcome_msg = f"{admin_text}📢 Please join our channel to use this bot:\n{CHANNEL_LINK}"
        await message.reply_text(welcome_msg, reply_markup=keyboard)
    else:
        await show_main_menu(message)

@app.on_callback_query(filters.regex("^verify_join$"))
async def verify_join(client, callback_query: CallbackQuery):
    if await check_membership(callback_query.from_user.id):
        await callback_query.message.delete()
        await show_main_menu(callback_query.message)
    else:
        await callback_query.answer("You haven't joined the channel yet!", show_alert=True)

async def show_main_menu(message: Message):
    if is_admin(message.from_user.id):
        admin_status = "👑 Admin"
    else:
        admin_status = "👤 User"
        
    menu_text = f"""
🔧 **Instagram Password Reset** 

**Bot BY** : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)

**Available commands** :
/rstt - Reset password for single account
/bulkk - Reset passwords for multiple accounts
/help - Show help information

📌 **How to use** :
1. For single account: /rstt
2. For multiple accounts: /bulkk
3. Separate multiple accounts with commas or new lines
"""
    await message.reply_text(menu_text, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("help"))
async def show_help(client, message: Message):
    help_text = """
📖 **Help Guide**

/rstt - Reset password for a single Instagram account
/bulkk - Reset passwords for multiple accounts

⚙️ **Usage**:
Single account:
/rstt then enter username or email

Multiple accounts:
/bulkk then enter usernames/emails separated by commas or new lines
Example: 
account1
account2
account3

🔐 **Note**: This bot sends official Instagram password reset requests.
"""
    await message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("stats"))
async def show_stats(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ This command is only available for admins!")
        return
        
    bot_info = await app.get_me()
    stats_text = f"""
📊 **Bot Statistics**

👑 Admins: {len(ADMIN_IDS)}
📢 Channel: @{CHANNEL_USERNAME}
🤖 Bot: @{bot_info.username}
🛠️ Creator: [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
"""
    await message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("rstt"))
async def start_reset(client, message: Message):
    if not await check_membership(message.from_user.id):
        await send_welcome(client, message)
        return
        
    msg = await message.reply_text("📨 Reply to this message with your Instagram username or email.")
    
    # Store the message to handle the response
    ongoing_operations[message.chat.id] = {
        "type": "single_reset",
        "msg_id": msg.id
    }

@app.on_message(filters.command("bulkk"))
async def start_bulk_reset(client, message: Message):
    if not await check_membership(message.from_user.id):
        await send_welcome(client, message)
        return
        
    msg = await message.reply_text("📝 Enter multiple usernames/emails :")
    
    # Store the message to handle the response
    ongoing_operations[message.chat.id] = {
        "type": "bulk_reset",
        "msg_id": msg.id
    }

async def process_single_reset(client, message: Message, original_msg_id: int):
    target = message.text.strip()
    if target.lower() in ['/rstt', '/bulkk', '/help', '/start', '/stats']:
        await message.reply_text("❌ Command not allowed as input. Please try again.")
        return
    
    # Show processing message
    processing_msg = await message.reply_text(f"🔁 Processing to send reset to `{target}`", parse_mode=ParseMode.MARKDOWN)
    
    reset_tool = PasswordResetTool(target)
    result, time_taken = reset_tool.send_password_reset()
    
    # Extract info from response
    extracted_info = extract_info_from_response(result)
    obfuscated_info = extracted_info if extracted_info else "Not available"
    
    bot_info = await app.get_me()
    username = message.from_user.username if message.from_user.username else 'N/A'
    
    if "obfuscated_email" in result or "username" in result:
        success_message = f"""
🦚 **Instagram Pass Reset**

👤 **Requested by** : [{message.from_user.first_name}](@{username})
📌 Target : `{target}`
📬 Obfuscated Info : `{obfuscated_info}`
⏱️ Speed : `{time_taken}`
🤖 Processed by: @{bot_info.username}
🧠 Dev : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
🎯 Bot : @rdhresetbot

✅ Password reset link sent successfully!
"""
        await processing_msg.edit_text(success_message, parse_mode=ParseMode.MARKDOWN)
    else:
        error_message = f"""
🦚 **Instagram Pass Reset**

👤 **Requested by** : [{message.from_user.first_name}](@{username})
📌 Target : `{target}`
📬 Obfuscated Info : `{obfuscated_info}`
⏱️ Speed : `{time_taken}`
🤖 Processed by: @{bot_info.username}
🧠 Dev : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
🎯 Bot : @rdhresetbot

❌ Failed to send reset link!
📛 Reason: `{result if len(result) < 100 else result[:100] + '...'}`
"""
        await processing_msg.edit_text(error_message, parse_mode=ParseMode.MARKDOWN)

async def process_bulk_reset(client, message: Message, original_msg_id: int):
    text = message.text.strip()
    if text.lower() in ['/rstt', '/bulkk', '/help', '/start', '/stats']:
        await message.reply_text("❌ Command not allowed as input. Please try again.")
        return
    
    # Parse input (comma or newline separated)
    targets = [t.strip() for t in text.replace('\n', ',').split(',') if t.strip()]
    targets = targets[:5]  # Limit to 5 targets
    
    if not targets:
        await message.reply_text("❌ No valid usernames/emails provided")
        return
    
    processing_msg = await message.reply_text(f"⏳ Processing {len(targets)} accounts...")
    
    success_count = 0
    results = []
    bot_info = await app.get_me()
    username = message.from_user.username if message.from_user.username else 'N/A'
    
    for i, target in enumerate(targets, 1):
        # Show processing for each account
        status_msg = await message.reply_text(f"🔁 Processing {i}/{len(targets)}: Sending reset to `{target}`", parse_mode=ParseMode.MARKDOWN)
        
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
🔰 **Reset Successful**

📌 Target: `{target}`
📬 Obfuscated Info: `{obfuscated_info}`
⏱️ Speed: `{time_taken}`
✅ Status: Reset link sent successfully!

Trying to reset the next user...
"""
            await status_msg.edit_text(success_result, parse_mode=ParseMode.MARKDOWN)
        else:
            result_text = f"❌ `{target}`: Failed 📛 {result[:50]}{'...' if len(result) > 50 else ''}"
            
            # Show failure result for this account
            error_result = f"""
🔰 **Reset Failed**

📌 Target: `{target}`
📬 Obfuscated Info: `{obfuscated_info}`
⏱️ Speed: `{time_taken}`
❌ Status: Failed to send reset link!
📛 Reason: `{result if len(result) < 100 else result[:100] + '...'}`

Moving to next account...
"""
            await status_msg.edit_text(error_result, parse_mode=ParseMode.MARKDOWN)
        
        results.append(result_text)
        await asyncio.sleep(2)  # Wait a bit before showing the next account
        
        # Delete the status message after a delay
        await asyncio.sleep(1)
        try:
            await status_msg.delete()
        except:
            pass
    
    # Show final summary
    report = "\n".join(results)
    summary = f"\n\n📊 Summary: {success_count} successful, {len(targets)-success_count} failed"
    
    final_message = f"""
📋 **Bulk Reset Results**

{report}

{summary}

👤 **Requested by** : [{message.from_user.first_name}](@{username})
🤖 Processed by: @{bot_info.username}
**Dev** : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/boloradhey)
🎯 **Bot** : @rdhresetbot
"""
    await processing_msg.edit_text(final_message, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.text & ~filters.command)
async def handle_text_messages(client, message: Message):
    # Check if this is a response to a previous command
    chat_id = message.chat.id
    
    if chat_id in ongoing_operations:
        operation_type = ongoing_operations[chat_id]["type"]
        original_msg_id = ongoing_operations[chat_id]["msg_id"]
        
        if operation_type == "single_reset":
            await process_single_reset(client, message, original_msg_id)
        elif operation_type == "bulk_reset":
            await process_bulk_reset(client, message, original_msg_id)
        
        # Clean up
        del ongoing_operations[chat_id]
    else:
        if await check_membership(message.from_user.id):
            await message.reply_text("ℹ️ Please use /rstt for single account or /bulkk for multiple accounts")
        else:
            await send_welcome(client, message)

# For Render hosting
from flask import Flask
from threading import Thread

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

async def main():
    keep_alive()
    print("Bot is running...")
    print(f"Admin IDs: {ADMIN_IDS}")
    print(f"Channel: @{CHANNEL_USERNAME}")
    await app.start()
    await asyncio.sleep(1)
    print("Bot started successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())