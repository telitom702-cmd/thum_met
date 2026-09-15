import os
import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ForceReply
from pyrogram.errors import MessageNotModified

# ====== ভিডিও রিসিভ করার সময় বাটন দেখানোর হ্যান্ডলার ======
@Client.on_message(filters.video & filters.private)
async def video_handler(bot, update):
    await AddUser(bot, update)
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    # শুধু দুটি বাটন: Rename এবং Skip
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✏️ Rename", callback_data="rename_video")],
            [InlineKeyboardButton("⏭️ Skip", callback_data="skip_rename")]
        ]
    )

    await update.reply_text(
        text=f"**ভিডিও রিসিভ করেছি ✅**\n\n📁 ফাইলের বর্তমান নাম: `{update.video.file_name}`\n\nনিচের বাটন থেকে Rename অথবা Skip করুন।",
        reply_markup=buttons,
        quote=True
    )


# ====== বাটনে ক্লিক করার পর কাজ করার হ্যান্ডলার ======
@Client.on_callback_query(filters.regex("^(rename|skip)"))
async def callback_handler(bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    # বটকে রিপ্লাই করে যে মেসেজে ভিডিও দেওয়া হয়েছিল সেটি বের করা
    video_message = query.message.reply_to_message
    
    if data == "rename_video":
        # ইউজারকে নতুন নাম লেখার জন্য ForceReply দেওয়া হলো
        await query.message.edit_text(
            text="**প্লিজ ফাইলের জন্য একটি নতুন নাম লিখুন (এক্সটেনশন ছাড়া, যেমন: My Video):**",
            reply_markup=ForceReply(selective=True)
        )
        await query.answer("নতুন নাম লিখুন...")

    elif data == "skip_rename":
        # আগের অরিজিনাল নামটাই নেওয়া হলো
        file_name = video_message.video.file_name or f"Video_{user_id}.mp4"
        
        await query.message.edit_text(f"**Skip করা হয়েছে ⏭️\nআগের নাম ব্যবহার করা হচ্ছে:** `{file_name}`\n\nডাউনলোড শুরু হচ্ছে... ⏳**")
        await query.answer("আগের নামেই আপলোড হচ্ছে...")
        
        # সরাসরি প্রসেস ফাংশনে পাঠানো হলো
        await process_video(bot, query.message, video_message, file_name)


# ====== ইউজার যখন নতুন নাম লিখবে তখন কাজ করার হ্যান্ডলার ======
@Client.on_message(filters.private & filters.reply)
async def process_rename(bot, update):
    # চেক করা হচ্ছে এটি বটের রিপ্লাই মেসেজের উত্তর কিনা
    if not update.reply_to_message or not update.reply_to_message.from_user:
        return
    if update.reply_to_message.from_user.id != bot.me.id:
        return

    # ইউজারের দেওয়া নতুন নাম
    new_name = update.text.strip()
    file_name = f"{new_name}.mp4"
    
    # বটের রিপ্লাই মেসেজ থেকে মূল ভিডিও মেসেজ বের করা (রিপ্লাই টু রিপ্লাই)
    video_message = update.reply_to_message.reply_to_message
    
    if not video_message or not video_message.video:
        await update.reply_text("⚠️ কিছু ভুল হয়েছে, মূল ফাইল পাওয়া যায়নি!")
        return

    m = await update.reply_text(f"**নতুন নাম সেট করা হয়েছে:** `{file_name}`\n\n**ডাউনলোড শুরু হচ্ছে... ⏳**")
    
    # মূল প্রসেস ফাংশনে পাঠানো হলো
    await process_video(bot, m, video_message, file_name)


# ====== মূল ডাউনলোড ও আপলোড ফাংশন ======
async def process_video(bot, m, video_message, file_name):
    download_location = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(video_message.from_user.id),
        file_name
    )
    
    try:
        c_time = time.time()
        file = await bot.download_media(
            message=video_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=("**ডাউনলোড হচ্ছে... ⏳**", m, c_time)
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
            progress_args=("**আপলোড হচ্ছে... 🚀**", m, u_time)
        )
        
        await m.delete()
        
    except Exception as e:
        try:
            await m.edit_text(f"**এরর হয়েছে ❌\nকারণ: {e}**")
        except MessageNotModified:
            pass
        
    finally:
        # সার্ভার থেকে ফাইল ডিলিট করে সার্ভার ক্লিন রাখা
        try:
            if 'file' in locals() and os.path.lexists(file):
                os.remove(file)
            if 'thumb_image_path' in locals() and thumb_image_path and os.path.lexists(thumb_image_path):
                os.remove(thumb_image_path)
        except Exception as e:
            logger.warning(f"Error cleaning up files: {e}")
