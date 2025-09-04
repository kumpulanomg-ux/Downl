import os
import re
import sqlite3
import logging
from threading import Lock
import yt_dlp as youtube_dl
import telebot
from telebot import types
from telebot.util import quick_markup
import time
from datetime import datetime
import urllib.parse

TOKEN = '7690431748:AAHvC8Zy1qnpND5WGfrb2Zmi3Y4c394VMqw'
AbuHamza = 6334408675 

DB = 'IMSWAD.db'
MAX = 50 

#برمجة المبرمج ابو حمزه @IMSWAD
# قناة الملفات الجاهزه @ZIIJW
# اذا احتاجت مساعدة تواصل معي 
#لعنك الله اذا كانت نيتك خمط الملف بدون حقوقي

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

db_lock = Lock()

def clean_filename(filename):
    filename = filename.replace(' ', '_')
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    if len(filename) > MAX:
        filename = filename[:MAX]
    return filename

def init_db():
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            join_date TEXT,
            banned INTEGER DEFAULT 0
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INTEGER PRIMARY KEY,
            channel_username TEXT,
            channel_title TEXT,
            added_date TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            total_users INTEGER DEFAULT 0,
            total_downloads INTEGER DEFAULT 0,
            last_download TEXT
        )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM stats')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO stats (total_users, total_downloads) VALUES (0, 0)')
        
        conn.commit()
        conn.close()

init_db()

#برمجة المبرمج ابو حمزه @IMSWAD
# قناة الملفات الجاهزه @ZIIJW
# اذا احتاجت مساعدة تواصل معي 
#لعنك الله اذا كانت نيتك خمط الملف بدون حقوقي

def add_user(user_id, username, first_name, last_name):
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            join_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, join_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, join_date))
            
            cursor.execute('UPDATE stats SET total_users = total_users + 1')
            conn.commit()
        
        conn.close()

def is_banned(user_id):
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('SELECT banned FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] == 1 if result else False

def ban_user(user_id):
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET banned = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

def unban_user(user_id):
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET banned = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

def add_channel(channel_id, channel_username, channel_title):
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        added_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT OR REPLACE INTO channels (channel_id, channel_username, channel_title, added_date)
        VALUES (?, ?, ?, ?)
        ''', (channel_id, channel_username, channel_title, added_date))
        conn.commit()
        conn.close()

def remove_channel(channel_id):
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
        conn.commit()
        conn.close()

def get_channels():
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id, channel_username, channel_title FROM channels')
        channels = cursor.fetchall()
        conn.close()
        return channels

def increment_downloads():
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('UPDATE stats SET total_downloads = total_downloads + 1, last_download = ?', 
                      (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        conn.commit()
        conn.close()

#برمجة المبرمج ابو حمزه @IMSWAD
# قناة الملفات الجاهزه @ZIIJW
# اذا احتاجت مساعدة تواصل معي 
#لعنك الله اذا كانت نيتك خمط الملف بدون حقوقي

def get_stats():
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('SELECT total_users, total_downloads, last_download FROM stats')
        stats = cursor.fetchone()
        conn.close()
        return stats

def get_all_users():
    with db_lock:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE banned = 0')
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users

def check_subscription(user_id):
    channels = get_channels()
    if not channels:
        return True
    
    for channel_id, _, _ in channels:
        try:
            chat_member = bot.get_chat_member(channel_id, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            logger.error(f"Error checking subscription for user {user_id} in channel {channel_id}: {e}")
            return False
    return True

def send_subscription_message(chat_id):
    channels = get_channels()
    if not channels:
        return
    
    message = "⚠️ يجب عليك الاشتراك في القنوات التالية لاستخدام البوت:\n"
    keyboard = types.InlineKeyboardMarkup()
    
    for channel_id, channel_username, channel_title in channels:
        message += f"- [{channel_title}](https://t.me/{channel_username})\n"
        keyboard.add(types.InlineKeyboardButton(
            text=f"{channel_title}",
            url=f"https://t.me/{channel_username}"
        ))
    
    keyboard.add(types.InlineKeyboardButton(
        text="✅ تحقق من الاشتراك",
        callback_data="check_subscription"
    ))
    
    bot.send_message(chat_id, message, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    
    add_user(user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    
    if not check_subscription(user_id):
        send_subscription_message(message.chat.id)
        return
    
    welcome_text = """
    🎬 مرحبًا بك في بوت تحميل الفيديوهات!
    
    فقط أرسل رابط الفيديو من أي منصة وسأقوم بتحميله لك.
    
    📌 المدعومة: YouTube, Instagram, Twitter, TikTok, Facebook وغيرها.
    """
    
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != AbuHamza:
        return
    
    keyboard = quick_markup({
        'حظر مستخدم': {'callback_data': 'ban_user'},
        'إلغاء حظر': {'callback_data': 'unban_user'},
        'الإحصائيات': {'callback_data': 'stats'},
        'اذاعة': {'callback_data': 'broadcast'},
        'إضافة قناة': {'callback_data': 'add_channel'},
        'حذف قناة': {'callback_data': 'remove_channel'},
        'عرض القنوات': {'callback_data': 'list_channels'}
    }, row_width=2)
    
    bot.send_message(message.chat.id, "👨‍💻 مرجبا بك عزيزي الادمن في لوحة التحكم الخاصة ببوتك", reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_video_links(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return
    
    add_user(user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    
    if not check_subscription(user_id):
        send_subscription_message(message.chat.id)
        return
    
    text = message.text.strip()
    
    if not any(domain in text for domain in ['http://', 'https://', 'www.']):
        bot.reply_to(message, "⚠️ يرجى إرسال رابط فيديو صالح.")
        return
    
    wait_msg = bot.reply_to(message, "⏳ جاري معالجة طلبك، يرجى الانتظار...")
    
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '%(id)s.%(ext)s', 
            'restrictfilenames': True,  
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(text, download=False)
            video_title = info_dict.get('title', 'video')
            video_id = info_dict.get('id', 'video')
            video_url = info_dict.get('url', None)
            thumbnail = info_dict.get('thumbnail', None)
            duration = info_dict.get('duration', 0)
            
            safe_title = clean_filename(video_title)
            out_file = f"{video_id}.mp4"
            
            bot.edit_message_text(
                f"📥 جاري تحميل: {video_title[:50]}...",
                chat_id=message.chat.id,
                message_id=wait_msg.message_id
            )
            
            ydl.download([text])
            
            if os.path.exists(out_file):
                bot.edit_message_text(
                    f"📤 جاري رفع: {video_title[:50]}...",
                    chat_id=message.chat.id,
                    message_id=wait_msg.message_id
                )
                
                share_url = f"https://t.me/share/url?url={urllib.parse.quote(text)}"
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(
                    text="🔄 مشاركة الفيديو",
                    url=share_url
                ))
                
                with open(out_file, 'rb') as video:
                    bot.send_video(
                        chat_id=message.chat.id,
                        video=video,
                        caption=f"🎬 {video_title}\n🔗 {text}",
                        duration=duration,
                        reply_markup=keyboard
                    )
                
                os.remove(out_file)
                increment_downloads()
            else:
                bot.edit_message_text(
                    "❌ تعذر العثور على الفيديو بعد التحميل.",
                    chat_id=message.chat.id,
                    message_id=wait_msg.message_id
                )
        
        bot.delete_message(message.chat.id, wait_msg.message_id)
        
    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        error_msg = "❌ حدث خطأ أثناء معالجة الفيديو."
        
        if "Unsupported URL" in str(e):
            error_msg = "⚠️ الرابط غير مدعوم أو غير صحيح."
        elif "Private video" in str(e):
            error_msg = "🔒 الفيديو خاص ولا يمكن تحميله."
        elif "Copyright" in str(e):
            error_msg = "⛔ الفيديو محمي بحقوق النشر ولا يمكن تحميله."
        
        bot.edit_message_text(
            error_msg,
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    
    if call.data == 'check_subscription':
        if check_subscription(user_id):
            bot.answer_callback_query(call.id, "✅ أنت مشترك في جميع القنوات المطلوبة!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "⚠️ لم يتم التحقق من اشتراكك في جميع القنوات!")
    
    elif user_id != AbuHamza:
        bot.answer_callback_query(call.id, "⛔ ليس لديك صلاحية الوصول إلى هذه الأوامر.")
        return
    
    elif call.data == 'ban_user':
        msg = bot.send_message(call.message.chat.id, "أرسل ايدي المستخدم الذي تريد حظره:")
        bot.register_next_step_handler(msg, process_ban_user)
    
    elif call.data == 'unban_user':
        msg = bot.send_message(call.message.chat.id, "أرسل ايدي المستخدم الذي تريد إلغاء حظره:")
        bot.register_next_step_handler(msg, process_unban_user)
    
    elif call.data == 'stats':
        total_users, total_downloads, last_download = get_stats()
        stats_text = f"""
        📊 إحصائيات البوت:
        
        👥 إجمالي المستخدمين: {total_users}
        📥 إجمالي التحميلات: {total_downloads}
        🕒 آخر تحميل: {last_download or 'غير متوفر'}
        """
        bot.edit_message_text(
            stats_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    
    elif call.data == 'broadcast':
        msg = bot.send_message(call.message.chat.id, "أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:")
        bot.register_next_step_handler(msg, process_broadcast)
    
    elif call.data == 'add_channel':
        msg = bot.send_message(call.message.chat.id, "أرسل يوزر القناة أو الايدي الخاص بها (يجب أن يكون البوت مشرفًا فيها):")
        bot.register_next_step_handler(msg, process_add_channel)
    
    elif call.data == 'remove_channel':
        channels = get_channels()
        if not channels:
            bot.answer_callback_query(call.id, "لا توجد قنوات إجبارية مضافّة.")
            return
        
        keyboard = types.InlineKeyboardMarkup()
        for channel_id, channel_username, channel_title in channels:
            keyboard.add(types.InlineKeyboardButton(
                text=f"❌ {channel_title}",
                callback_data=f"remove_channel_{channel_id}"
            ))
        
        bot.edit_message_text(
            "اختر القناة التي تريد حذفها:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    
    elif call.data == 'list_channels':
        channels = get_channels()
        if not channels:
            bot.answer_callback_query(call.id, "لا توجد قنوات إجبارية مضافّة.")
            return
        
        channels_text = "📋 قائمة القنوات الإجبارية:\n"
        for channel_id, channel_username, channel_title in channels:
            channels_text += f"- {channel_title} (@{channel_username}) - ID: {channel_id}\n"
        
        bot.edit_message_text(
            channels_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    
    elif call.data.startswith('remove_channel_'):
        channel_id = int(call.data.split('_')[2])
        remove_channel(channel_id)
        bot.answer_callback_query(call.id, f"تم حذف القناة بنجاح.")
        bot.edit_message_text(
            "✅ تم حذف القناة بنجاح.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

def process_ban_user(message):
    try:
        user_id = int(message.text)
        ban_user(user_id)
        bot.reply_to(message, f"✅ تم حظر المستخدم {user_id} بنجاح.")
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال ايدي مستخدم صحيح (أرقام فقط).")

def process_unban_user(message):
    try:
        user_id = int(message.text)
        unban_user(user_id)
        bot.reply_to(message, f"✅ تم إلغاء حظر المستخدم {user_id} بنجاح.")
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال ايدي مستخدم صحيح (أرقام فقط).")

def process_broadcast(message):
    users = get_all_users()
    total = len(users)
    success = 0
    
    progress_msg = bot.send_message(message.chat.id, f"جاري الإرسال لـ {total} مستخدم... (0/{total})")
    
    for index, user_id in enumerate(users, 1):
        try:
            bot.copy_message(user_id, message.chat.id, message.message_id)
            success += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
        
        if index % 10 == 0 or index == total:
            bot.edit_message_text(
                f"جاري الإرسال لـ {total} مستخدم... ({success}/{total})",
                chat_id=progress_msg.chat.id,
                message_id=progress_msg.message_id
            )
    
    bot.edit_message_text(
        f"✅ تم إرسال الإشعار بنجاح إلى {success} من أصل {total} مستخدم.",
        chat_id=progress_msg.chat.id,
        message_id=progress_msg.message_id
    )

def process_add_channel(message):
    try:
        channel_input = message.text.strip()
        
        if channel_input.startswith('@'):
            channel_input = channel_input[1:]
        
        try:
            chat = bot.get_chat(channel_input)
            channel_id = chat.id
            channel_username = chat.username
            channel_title = chat.title
            
            add_channel(channel_id, channel_username, channel_title)
            bot.reply_to(message, f"✅ تمت إضافة القناة {channel_title} (@{channel_username}) بنجاح.")
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            bot.reply_to(message, "❌ تعذر العثور على القناة. تأكد من أن البوت مشرف فيها وأن اليوزر صحيح.")
    except Exception as e:
        logger.error(f"Error in process_add_channel: {e}")
        bot.reply_to(message, "❌ حدث خطأ أثناء معالجة طلبك.")

def run_bot():
    while True:
        try:
            logger.info("Starting bot...")
            bot.polling(none_stop=True, interval=2, timeout=30)
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True)
            time.sleep(10)

from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    print("Starting bot...")
    bot.polling(none_stop=True, interval=2, timeout=30)

if __name__ == "__main__":
    # شغل البوت في Thread
    threading.Thread(target=run).start()
    # خلي Flask يفضل فاتح البورت
    app.run(host="0.0.0.0", port=10000)
