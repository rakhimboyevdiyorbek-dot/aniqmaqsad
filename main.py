"""
Spreadsheet Template Sotish Bot
Yarim avtomatik to'lov tizimi bilan
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== SOZLAMALAR ==============
BOT_TOKEN = "8571861434:AAHW__tWMy9XDpzb4B3H7xvkui3vQkcVgYM"
ADMIN_ID = 5964206416
TEMPLATE_PRICE = "29 999"
SHEETS_LINK = "https://docs.google.com/spreadsheets/d/1xwmlGXard9MiXC0r3PfKMCZ7joDhYqs3QU0AKTvEASY/edit?usp=sharing"

# To'lov ma'lumotlari
PAYMENT_INFO = {
    "click": {
        "name": "Click",
        "details": "📱 Click ilova orqali:\nKarta raqami: 5614 6821 0202 3795\nEgasi: Diyorbek Raximboyev"
    },
    "payme": {
        "name": "Payme",
        "details": "📱 Payme ilova orqali:\nKarta raqami: 5614 6821 0202 3795\nEgasi: Diyorbek Raximboyev"
    },
    "paynet": {
        "name": "Paynet",
        "details": "🏪 Paynet terminal orqali:\nKarta raqami: 5614 6821 0202 3795\nEgasi: Diyorbek Raximboyev"
    },
    "uzum": {
        "name": "Uzum Bank",
        "details": "📱 Uzum Bank ilova orqali:\nKarta raqami: 5614 6821 0202 3795\nEgasi: Diyorbek Raximboyev"
    }
}

# ============== MATNLAR ==============
WELCOME_POST = """
🎯 <b>Spreadsheet Template</b>

Sizning biznesingiz/shaxsiy moliyangiz uchun professional Excel/Google Sheets shablon!

✅ Avtomatik hisob-kitob
✅ Chiroyli dizayn
✅ Oson foydalanish
✅ Video qo'llanma bilan

💰 Narxi: <b>{price} so'm</b>

Quyidagi tugmalar orqali batafsil ma'lumot oling 👇
""".format(price=TEMPLATE_PRICE)

REVIEWS = [
    """⭐⭐⭐⭐⭐
    
<b>Aziz, tadbirkor:</b>
"Juda qulay shablon ekan! Endi hisoblarimni 10 daqiqada qilaman, oldin 2 soat ketardi."
""",
    """⭐⭐⭐⭐⭐

<b>Malika, frilanser:</b>
"Daromad va xarajatlarimni kuzatish osonlashdi. Har oyda qancha pul sarflaganimni aniq ko'ryapman."
""",
    """⭐⭐⭐⭐⭐

<b>Bobur, do'kon egasi:</b>
"Ombor hisobini shu shablon bilan yuritaman. Qaysi mahsulot ko'p sotilayotganini bir qarashda ko'raman."
"""
]

TUTORIALS = [
    """📖 <b>1-qadam: Shablonni ochish</b>

1. Sizga yuborilgan Google Sheets linkini oching
2. "File" → "Make a copy" bosing
3. O'z Google Drive'ingizga saqlang

Tayyor! Endi o'zingizning nusxangiz bor.""",
    
    """📖 <b>2-qadam: Ma'lumot kiritish</b>

1. Sariq kataklarga ma'lumot kiriting
2. Yashil kataklar avtomatik hisoblanadi
3. Qizil kataklarni o'zgartirmang (formulalar)

💡 Maslahat: Har kuni 5 daqiqa vaqt ajrating""",
    
    """📖 <b>3-qadam: Hisobotlarni ko'rish</b>

1. "Dashboard" varag'ini oching
2. Barcha grafiklar avtomatik yangilanadi
3. Oylik/haftalik hisobotlarni PDF qilib saqlang

🎉 Tabriklaymiz! Siz professionalday ishlamoqdasiz!"""
]

# ============== CONVERSATION STATES ==============
NAME, PHONE, MAIN_MENU, PAYMENT_SELECT, WAITING_RECEIPT = range(5)

# ============== FOYDALANUVCHILAR BAZASI ==============
# Oddiy dict - production uchun database ishlatish kerak
users_db = {}
orders_db = {}

# ============== HANDLERS ==============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bot ishga tushganda ism so'raydi"""
    user = update.effective_user
    
    await update.message.reply_text(
        f"Assalomu alaykum! 👋\n\n"
        f"Aniq maqsad botiga xush kelibsiz!\n\n"
        f"Davom etish uchun ismingizni yozing:"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ismni saqlash va telefon so'rash"""
    user_id = update.effective_user.id
    name = update.message.text.strip()
    
    # Foydalanuvchini bazaga qo'shish
    users_db[user_id] = {"name": name, "phone": None}
    
    # Telefon raqam uchun tugma
    keyboard = [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Rahmat, {name}! ✅\n\n"
        f"Endi telefon raqamingizni yuboring.\n"
        f"Quyidagi tugmani bosing 👇",
        reply_markup=reply_markup
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Telefonni saqlash va asosiy menyuni ko'rsatish"""
    user_id = update.effective_user.id
    
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    
    users_db[user_id]["phone"] = phone
    
    # Asosiy menyuni ko'rsatish
    return await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asosiy menyu bilan post yuborish"""
    keyboard = [
        [InlineKeyboardButton("💬 Foydalanganlar fikrlari", callback_data="reviews")],
        [InlineKeyboardButton("📖 Qo'llanma", callback_data="tutorial")],
        [InlineKeyboardButton("🛒 Xarid qilish", callback_data="buy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Agar callback_query bo'lsa
    if update.callback_query:
        await update.callback_query.message.reply_text(
            WELCOME_POST,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            WELCOME_POST,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    return MAIN_MENU

async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Otzivlarni ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    for review in REVIEWS:
        await query.message.reply_text(review, parse_mode='HTML')
    
    # Orqaga tugmasi
    keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Siz ham mamnun mijozlarimizdan biri bo'ling! 🎉",
        reply_markup=reply_markup
    )
    return MAIN_MENU

async def show_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Qo'llanmani ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    for tutorial in TUTORIALS:
        await query.message.reply_text(tutorial, parse_mode='HTML')
    
    # Orqaga tugmasi
    keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Savollar bo'lsa, bemalol yozing! 💬",
        reply_markup=reply_markup
    )
    return MAIN_MENU

async def show_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """To'lov turlarini ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📱 Click", callback_data="pay_click")],
        [InlineKeyboardButton("📱 Payme", callback_data="pay_payme")],
        [InlineKeyboardButton("🏪 Paynet", callback_data="pay_paynet")],
        [InlineKeyboardButton("📱 Uzum Bank", callback_data="pay_uzum")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"💳 <b>To'lov</b>\n\n"
        f"Summa: <b>{TEMPLATE_PRICE} so'm</b>\n\n"
        f"Qulay to'lov turini tanlang 👇",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    return PAYMENT_SELECT

async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """To'lov turini qayta ishlash"""
    query = update.callback_query
    await query.answer()
    
    payment_type = query.data.replace("pay_", "")
    payment_info = PAYMENT_INFO.get(payment_type)
    
    if not payment_info:
        return PAYMENT_SELECT
    
    user_id = update.effective_user.id
    
    # Buyurtmani saqlash
    orders_db[user_id] = {
        "user_info": users_db.get(user_id, {}),
        "payment_type": payment_type,
        "status": "pending"
    }
    
    await query.message.reply_text(
        f"💳 <b>{payment_info['name']} orqali to'lov</b>\n\n"
        f"Summa: <b>{TEMPLATE_PRICE} so'm</b>\n\n"
        f"{payment_info['details']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ To'lov qilganingizdan so'ng, <b>chek rasmini</b> shu yerga yuboring.\n\n"
        f"⏱ Tekshirib, 5-10 daqiqada template yuboramiz!",
        parse_mode='HTML'
    )
    
    # Adminga xabar
    user_info = users_db.get(user_id, {})
    await context.bot.send_message(
        ADMIN_ID,
        f"🆕 <b>Yangi buyurtma!</b>\n\n"
        f"👤 Ism: {user_info.get('name', 'Noma\'lum')}\n"
        f"📱 Tel: {user_info.get('phone', 'Noma\'lum')}\n"
        f"💳 To'lov: {payment_info['name']}\n"
        f"🆔 User ID: {user_id}\n\n"
        f"Chek kutilmoqda...",
        parse_mode='HTML'
    )
    
    return WAITING_RECEIPT

async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Chekni qabul qilish va adminga yuborish"""
    user_id = update.effective_user.id
    user_info = users_db.get(user_id, {})
    
    # Adminga chekni yuborish
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_message = (
        f"🧾 <b>Yangi chek!</b>\n\n"
        f"👤 Ism: {user_info.get('name', 'Noma\'lum')}\n"
        f"📱 Tel: {user_info.get('phone', 'Noma\'lum')}\n"
        f"🆔 User ID: {user_id}"
    )
    
    if update.message.photo:
        # Rasm yuborilgan
        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=admin_message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    elif update.message.document:
        # Fayl yuborilgan
        await context.bot.send_document(
            ADMIN_ID,
            update.message.document.file_id,
            caption=admin_message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        # Matn yuborilgan
        await context.bot.send_message(
            ADMIN_ID,
            f"{admin_message}\n\n📝 Xabar: {update.message.text}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    await update.message.reply_text(
        "✅ Chek qabul qilindi!\n\n"
        "⏱ Tekshirilmoqda... 5-10 daqiqada javob beramiz.\n\n"
        "Sabr qilganingiz uchun rahmat! 🙏"
    )
    
    return WAITING_RECEIPT

async def admin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin to'lovni tasdiqlaydi"""
    query = update.callback_query
    await query.answer()
    
    # Faqat admin uchun
    if query.from_user.id != ADMIN_ID:
        return
    
    user_id = int(query.data.replace("confirm_", ""))
    
    # Foydalanuvchiga template yuborish
    await context.bot.send_message(
        user_id,
        f"🎉 <b>Tabriklaymiz!</b>\n\n"
        f"To'lovingiz tasdiqlandi! ✅\n\n"
        f"Mana sizning template'ingiz:\n"
        f"🔗 {SHEETS_LINK}\n\n"
        f"📖 Foydalanish bo'yicha savollar bo'lsa, yozing!\n\n"
        f"Bizni tanlaganingiz uchun rahmat! 🙏",
        parse_mode='HTML'
    )
    
    # Buyurtma statusini yangilash
    if user_id in orders_db:
        orders_db[user_id]["status"] = "confirmed"
    
    # Admin xabarini yangilash
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
        parse_mode='HTML'
    )

async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin to'lovni rad etadi"""
    query = update.callback_query
    await query.answer()
    
    # Faqat admin uchun
    if query.from_user.id != ADMIN_ID:
        return
    
    user_id = int(query.data.replace("reject_", ""))
    
    # Foydalanuvchiga xabar
    await context.bot.send_message(
        user_id,
        "❌ <b>Uzr, to'lov tasdiqlanmadi</b>\n\n"
        "Chekda muammo bor yoki to'lov tushgani aniqlanmadi.\n\n"
        "Iltimos, to'lov qilib, yangi chek yuboring.\n"
        "Yoki savollar bo'lsa, yozing!",
        parse_mode='HTML'
    )
    
    # Buyurtma statusini yangilash
    if user_id in orders_db:
        orders_db[user_id]["status"] = "rejected"
    
    # Admin xabarini yangilash
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
        parse_mode='HTML'
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asosiy menyuga qaytish"""
    query = update.callback_query
    await query.answer()
    return await show_main_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bekor qilish"""
    await update.message.reply_text(
        "Bekor qilindi. Qaytadan boshlash uchun /start yozing."
    )
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yordam"""
    await update.message.reply_text(
        "🤖 <b>Bot buyruqlari:</b>\n\n"
        "/start - Botni boshlash\n"
        "/help - Yordam\n\n"
        "Savollar bo'lsa, yozing!",
        parse_mode='HTML'
    )

# ============== MAIN ==============

def main() -> None:
    """Botni ishga tushirish"""
    
    # Application yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
            MAIN_MENU: [
                CallbackQueryHandler(show_reviews, pattern="^reviews$"),
                CallbackQueryHandler(show_tutorial, pattern="^tutorial$"),
                CallbackQueryHandler(show_payment_options, pattern="^buy$"),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
            ],
            PAYMENT_SELECT: [
                CallbackQueryHandler(process_payment_selection, pattern="^pay_"),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
            ],
            WAITING_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT & ~filters.COMMAND, receive_receipt),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    # Admin callbacks (conversation tashqarisida)
    application.add_handler(CallbackQueryHandler(admin_confirm, pattern="^confirm_"))
    application.add_handler(CallbackQueryHandler(admin_reject, pattern="^reject_"))
    
    # Botni ishga tushirish
    print("Bot ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
