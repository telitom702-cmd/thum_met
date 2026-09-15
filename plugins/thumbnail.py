# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import random
import os
from PIL import Image
import time
from pyrogram import enums
from plugins.script import Translation
from pyrogram import Client
from plugins.database.add import AddUser
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
from plugins.functions.help_Nekmo_ffmpeg import take_screen_shot
import psutil
import shutil
import string
import asyncio
from asyncio import TimeoutError
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, ForceReply
from plugins.functions.forcesub import handle_force_subscribe
from plugins.database.database import db
from plugins.config import Config
from plugins.settings.settings import *
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes

# ইউজারের নতুন নামের টেক্সট সেভ করে রাখার জন্য ডিকশনারি
user_rename_data = {}

@Client.on_message(filters.photo & ~filters.reply)
async def save_photo(bot, update):
    await AddUser(bot, update)
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, update)
      if fsub == 400:
        return
    download_location = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(update.from_user.id) + ".jpg"
    )
    await bot.download_media(
        message=update,
        file_name=download_location
    )
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.SAVED_CUSTOM_THUMB_NAIL,
    )
    await db.set_thumbnail(update.from_user.id, thumbnail=update.photo.file_id)


@Client.on_message(filters.command(["delthumb"]))
async def delete_thumbnail(bot, update):
    await AddUser(bot, update)
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, update)
      if fsub == 400:
        return
    download_location = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(update.from_user.id)
    )
    try:
        os.remove(download_location + ".jpg")
    except:
        pass
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DEL_ETED_CUSTOM_THUMB_NAIL,
    )
    await db.set_thumbnail(update.from_user.id, thumbnail=None)

@Client.on_message(filters.command("showthumb"))
async def viewthumbnail(bot, update):
    await AddUser(bot, update)
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, update)
      if fsub == 400:
        return   
    thumbnail = await db.get_thumbnail(update.from_user.id)
    if thumbnail is not None:
        await bot.send_photo(
        chat_id=update.chat.id,
        photo=thumbnail,
        caption=f"YOUR THUMBNAIL 🏞",
        reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🗑️ 𝙳𝙴𝙻𝙴𝚃𝙴 𝚃𝙷𝚄𝙼𝙱𝙽𝙰𝙸𝙻", callback_data="deleteThumbnail", style=enums.ButtonStyle.DANGER)]]
                ),
         )
    else:
        await update.reply_text(text=f"𝙽𝙾 𝚃𝙷𝚄𝙼𝙱𝙽𝙰𝙸𝙻 😐")


@Client.on_callback_query(filters.regex(r"^deleteThumbnail$"))
async def delete_thumb_callback(bot, query: CallbackQuery):
    user_id = query.from_user.id
    download_location = os.path.join(Config.DOWNLOAD_LOCATION, str(user_id))
    try:
        os.remove(download_location + ".jpg")
    except:
        pass
    await db.set_thumbnail(user_id, thumbnail=None)
    try:
        await query.message.edit_text("**আপনার কাস্টম থাম্বনেইল সফলভাবে ডিলিট করা হয়েছে!** 🗑️✅")
    except MessageNotModified:
        pass
    await query.answer("থাম্বনেইল ডিলিট হয়েছে!", show_alert=False)


async def Gthumb01(bot, update):
    thumb_image_path = f"{Config.DOWNLOAD_LOCATION}/{str(update.from_user.id)}.jpg"
    db_thumbnail = await db.get_thumbnail(update.from_user.id)
    if db_thumbnail is not None:
        thumbnail = await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
        Image.open(thumbnail).convert("RGB").save(thumbnail)
        img = Image.open(thumbnail)
        img.resize((100, 100))
        img.save(thumbnail, "JPEG")
    else:
        thumbnail = None
    return thumbnail

async def Gthumb02(bot, update, duration, download_directory):
    thumb_image_path = f"{Config.DOWNLOAD_LOCATION}/{str(update.from_user.id)}.jpg"
    db_thumbnail = await db.get_thumbnail(update.from_user.id)
    
    if db_thumbnail is not None:
        return await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
    elif duration > 1:
        return await take_screen_shot(download_directory, os.path.dirname(download_directory), random.randint(0, duration - 1))
    else:
        return None

async def Mdata01(download_directory):
    width = 0
    height = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
    return width, height, duration

async def Mdata02(download_directory):
    width = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")
    return width, duration

async def Mdata03(download_directory):
    metadata = extractMetadata(createParser(download_directory))
    return (
        metadata.get('duration').seconds
        if metadata is not None and metadata.has("duration")
        else 0
    )


# =========================================================
# ভিডিও রিসিভ করে বাটন দেখানোর কোড
# =========================================================
@Client.on_message((filters.video | (filters.document & filters.video)) & filters.private)
async def video_handler(bot, update):
    await AddUser(bot, update)
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    if update.video:
        file_name = update.video.file_name or f"Video_{update.from_user.id}.mp4"
    else:
        file_name = update.document.file_name or f"Video_{update.from_user.id}.mp4"

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✏️ Rename", callback_data="rename_video")],
            [InlineKeyboardButton("⏭️ Skip", callback_data="skip_rename")]
        ]
    )

    await update.reply_text(
        text=f"**ভিডিও রিসিভ করেছি ✅**\n\n📁 ফাইলের নাম: `{file_name}`\n\nনিচের বাটন থেকে Rename অথবা Skip করুন।",
        reply_markup=buttons,
        quote=True
    )


# =========================================================
# বাটনে ক্লিক করলে যে কাজ হবে (Rename বা Skip)
# =========================================================
@Client.on_callback_query(filters.regex("^(rename|skip)"))
async def callback_handler(bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    video_message = query.message.reply_to_message
    if not video_message or not (video_message.video or video_message.document):
        await query.answer("মূল ফাইল পাওয়া যায়নি!", show_alert=True)
        return

    if data == "rename_video":
        # ডিকশনারিতে ভিডিওর মেসেজ আইডি সেভ করে রাখছি
        user_rename_data[user_id] = video_message.id
        
        await query.message.edit_text(
            text="**প্লিজ ফাইলের জন্য একটি নতুন নাম লিখুন (এক্সটেনশন ছাড়া, যেমন: My Video):**",
            reply_markup=ForceReply(selective=True)
        )
        await query.answer("নতুন নাম লিখুন...")

    elif data == "skip_rename":
        if video_message.video:
            file_name = video_message.video.file_name or f"Video_{user_id}.mp4"
        else:
            file_name = video_message.document.file_name or f"Video_{user_id}.mp4"
        
        await query.message.edit_text(f"**Skip করা হয়েছে ⏭️\nআগের নাম ব্যবহার করা হচ্ছে:** `{file_name}`\n\n**ডাউনলোড শুরু হচ্ছে... ⏳**")
        await query.answer("আগের নামেই আপলোড হচ্ছে...")
        
        await process_video(bot, query.message, video_message, file_name)


# =========================================================
# ইউজার যখন নতুন নাম লিখে রিপ্লাই দিবে তখন কাজ হবে
# =========================================================
@Client.on_message(filters.private & filters.reply & filters.text & ~filters.bot)
async def process_rename(bot, update):
    if not update.reply_to_message or not update.reply_to_message.from_user:
        return
    if update.reply_to_message.from_user.id != bot.me.id:
        return

    user_id = update.from_user.id
    
    # ডিকশনারি থেকে ভিডিওর আইডি বের করা
    video_msg_id = user_rename_data.get(user_id)
    if not video_msg_id:
        return

    new_name = update.text.strip()
    if not new_name.lower().endswith(('.mp4', '.mkv', '.webm', '.avi')):
        file_name = f"{new_name}.mp4"
    else:
        file_name = new_name
    
    # ডিকশনারি থেকে ডাটা ডিলিট করা
    user_rename_data.pop(user_id, None)
    
    video_message = await bot.get_messages(update.chat.id, video_msg_id)
    
    if not video_message or not (video_message.video or video_message.document):
        await update.reply_text("⚠️ কিছু ভুল হয়েছে, মূল ফাইল পাওয়া যায়নি!")
        return

    m = await update.reply_text(f"**নতুন নাম সেট করা হয়েছে:** `{file_name}`\n\n**ডাউনলোড শুরু হচ্ছে... ⏳**")
    
    await process_video(bot, m, video_message, file_name)


# =========================================================
# মূল ডাউনলোড এবং আপলোড প্রসেস (আগের কোড)
# =========================================================
async def process_video(bot, m, video_message, file_name):
    user_id = video_message.from_user.id
    
    download_location = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(user_id),
        f"{video_message.id}_{file_name}"
    )
    
    try:
        c_time = time.time()
        file = await bot.download_media(
            message=video_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                "**ডাউনলোড হচ্ছে... ⏳**",
                m,
                c_time
            )
        )
        
        width, height, duration = await Mdata01(file)
        thumb_image_path = await Gthumb02(bot, video_message, duration, file)
        
        await m.edit_text("**প্রসেস সম্পন্ন ✅\nথাম্বনেইল সহ ভিডিও পাঠানো হচ্ছে... 🚀**")
        
        u_time = time.time()
        await bot.send_video(
            chat_id=video_message.chat.id,
            video=file,
            duration=duration,
            width=width,
            height=height,
            supports_streaming=True,
            thumb=thumb_image_path,
            caption=f"**এখানে আপনার ভিডিও 🎬**\n\nনাম: `{file_name}`",
            file_name=file_name,
            progress=progress_for_pyrogram,
            progress_args=(
                "**আপলোড হচ্ছে... 🚀**",
                m,
                u_time
            )
        )
        
        await m.delete()
        
    except Exception as e:
        try:
            await m.edit_text(f"**এরর হয়েছে ❌\nকারণ: {e}**")
        except MessageNotModified:
            pass
        
    finally:
        try:
            if 'file' in locals() and os.path.lexists(file):
                os.remove(file)
            if 'thumb_image_path' in locals() and thumb_image_path and os.path.lexists(thumb_image_path):
                os.remove(thumb_image_path)
        except Exception as e:
            logger.warning(f"Error cleaning up files: {e}")
