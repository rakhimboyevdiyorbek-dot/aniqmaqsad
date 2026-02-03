"""
Spreadsheet Template Sotish Bot
Yarim avtomatik to'lov tizimi bilan
Railway/Server uchun tayyorlangan
"""

import logging
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ============== SOZLAMALAR ==============
# Tokenni ENV'dan olamiz (Railway Variables: BOT_TOKEN)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. Railway -> Variables'da BOT_TOKEN qo‘shing.")

ADMIN_ID = int(os.getenv("ADMIN_ID", "5964206416"))
TEMPLATE_PRICE = os.getenv("TEMPLATE_PRICE", "29 999")
SHEETS_LINK = os.getenv(
    "SHEETS_LINK",
    "https://docs.google.com/spreadsheets/d/1xwmlGXard9MiXC0r3PfKMCZ7joDhYqs3QU0AKTvEASY/edit?usp=sharing",
)

CARD_NUMBER = os.getenv("CARD_NUMBER", "5614 6821 0202 3795")
CARD_OWNER = os.getenv("CARD_OWNER", "Diyorbek Raximboyev")

# To'lov ma'lumotlari
PAYMENT_INFO = {
    "click": {
        "name": "Click",
        "details": f"📱 Click ilova orqali:\nKarta raqami: {CARD_NUMBER}\nEgasi: {CARD_OWNER}",
    },
    "payme": {
        "name": "Payme",
        "details": f"📱 Payme ilova orqali:\nKarta raqami: {CARD_NUMBER}\nEgasi: {CARD_OWNER}",
    },
    "paynet": {
        "name": "Paynet",
        "details": f"🏪 Paynet terminal orqali:\nKarta raqami: {CARD_NUMBER}\nEgasi: {CARD_OWNER}",
    },
    "uzum": {
        "name": "Uzum Bank",
        "details": f"📱 Uzum Bank ilova orqali:\nKarta raqami: {CARD_NUMBER}\nEgasi: {CARD_OWNER}",
    },
}

# ============== MATNLAR ==============
WELCOME_POST = f"""
🎯 <b>Spreadsheet Template</b>

Sizning biznesingiz/shaxsiy moliyangiz uchun professional Excel/Google Sheets shablon!

✅ Avtomatik hisob-kitob
✅ Chiroyli dizayn
✅ Oson foydalanish
✅ Video qo'llanma bilan

💰 Narxi: <b>{TEMPLATE_PRICE} so'm</b>

Quyidagi tugmalar orqali batafsil ma'lumot oling 👇
"""

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
""",
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
🎉 Tabriklaymiz! Siz professionalday ishlamoqdasiz!""",
]

# ============== CONVERSATION STATES ==============
NAME, PHONE, MAIN_MENU, PAYMENT_SELECT, WAITING_RECEIPT = range(5)

# ============== FOYDALANUVCHILAR BAZASI ==============
users_db = {}
orders_db = {}

# ============== HANDLERS ==============


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "Aniq maqsad botiga xush kelibsiz!\n\n"
        "Davom etish uchun ismingizni yozing:"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    name = update.message.text.strip()

    users_db[user_id] = {"name": name, "phone": None}

    keyboard = [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        f"Rahmat, {name}! ✅\n\n"
        "Endi telefon raqamingizni yuboring.\n"
        "Quyidagi tugmani bosing 👇",
        reply_markup=reply_markup,
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    users_db[user_id]["phone"] = phone
    return await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("💬 Foydalanganlar fikrlari", callback_data="reviews")],
        [InlineKeyboardButton("📖 Qo'llanma", callback_data="tutorial")],
        [InlineKeyboardButton("🛒 Xarid qilish", callback_data="buy")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(
            WELCOME_POST, parse_mode="HTML", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(WELCOME_POST, parse_mode="HTML", reply_markup=reply_markup)

    return MAIN_MENU


async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    for review in REVIEWS:
        await query.message.reply_text(review, parse_mode="HTML")

    keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")]]
    await query.message.reply_text(
        "Siz ham mamnun mijozlarimizdan biri bo'ling! 🎉",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return MAIN_MENU


async def show_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    for tutorial in TUTORIALS:
        await query.message.reply_text(tutorial, parse_mode="HTML")

    keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")]]
    await query.message.reply_text(
        "Savollar bo'lsa, bemalol yozing! 💬",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return MAIN_MENU


async def show_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📱 Click", callback_data="pay_click")],
        [InlineKeyboardButton("📱 Payme", callback_data="pay_payme")],
        [InlineKeyboardButton("🏪 Paynet", callback_data="pay_paynet")],
        [InlineKeyboardButton("📱 Uzum Bank", callback_data="pay_uzum")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")],
    ]

    await query.message.reply_text(
        f"💳 <b>To'lov</b>\n\n"
        f"Summa: <b>{TEMPLATE_PRICE} so'm</b>\n\n"
        "Qulay to'lov turini tanlang 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return PAYMENT_SELECT


async def process_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    payment_type = query.data.replace("pay_", "")
    payment_info = PAYMENT_INFO.get(payment_type)
    if not payment_info:
        return PAYMENT_SELECT

    user_id = update.effective_user.id

    orders_db[user_id] = {
        "user_info": users_db.get(user_id, {}),
        "payment_type": payment_type,
        "status": "pending",
    }

    await query.message.reply_text(
        f"💳 <b>{payment_info['name']} orqali to'lov</b>\n\n"
        f"Summa: <b>{TEMPLATE_PRICE} so'm</b>\n\n"
        f"{payment_info['details']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ To'lov qilganingizdan so'ng, <b>chek rasmini</b> shu yerga yuboring.\n\n"
        "⏱ Tekshirib, 5-10 daqiqada template yuboramiz!",
        parse_mode="HTML",
    )

    user_info = users_db.get(user_id, {})
    await context.bot.send_message(
        ADMIN_ID,
        "🆕 <b>Yangi buyurtma!</b>\n\n"
        f"👤 Ism: {user_info.get('name', 'Nomaʼlum')}\n"
        f"📱 Tel: {user_info.get('phone', 'Nomaʼlum')}\n"
        f"💳 To'lov: {payment_info['name']}\n"
        f"🆔 User ID: {user_id}\n\n"
        "Chek kutilmoqda...",
        parse_mode="HTML",
    )

    return WAITING_RECEIPT


async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_info = users_db.get(user_id, {})

    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_message = (
        "🧾 <b>Yangi chek!</b>\n\n"
        f"👤 Ism: {user_info.get('name', 'Nomaʼlum')}\n"
        f"📱 Tel: {user_info.get('phone', 'Nomaʼlum')}\n"
        f"🆔 User ID: {user_id}"
    )

    if update.message.photo:
        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=admin_message,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    elif update.message.document:
        await context.bot.send_document(
            ADMIN_ID,
            update.message.document.file_id,
            caption=admin_message,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    else:
        await context.bot.send_message(
            ADMIN_ID,
            f"{admin_message}\n\n📝 Xabar: {update.message.text}",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    await update.message.reply_text(
        "✅ Chek qabul qilindi!\n\n"
        "⏱ Tekshirilmoqda... 5-10 daqiqada javob beramiz.\n\n"
        "Sabr qilganingiz uchun rahmat! 🙏"
    )
    return WAITING_RECEIPT


async def admin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.replace("confirm_", ""))

    await context.bot.send_message(
        user_id,
        "🎉 <b>Tabriklaymiz!</b>\n\n"
        "To'lovingiz tasdiqlandi! ✅\n\n"
        f"Mana sizning template'ingiz:\n🔗 {SHEETS_LINK}\n\n"
        "📖 Foydalanish bo'yicha savollar bo'lsa, yozing!\n\n"
        "Bizni tanlaganingiz uchun rahmat! 🙏",
        parse_mode="HTML",
    )

    if user_id in orders_db:
        orders_db[user_id]["status"] = "confirmed"

    if query.message.caption:
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
            parse_mode="HTML",
        )
    else:
        await query.edit_message_text("✅ <b>TASDIQLANDI</b>", parse_mode="HTML")


async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.replace("reject_", ""))

    await context.bot.send_message(
        user_id,
        "❌ <b>Uzr, to'lov tasdiqlanmadi</b>\n\n"
        "Chekda muammo bor yoki to'lov tushgani aniqlanmadi.\n\n"
        "Iltimos, to'lov qilib, yangi chek yuboring.\n"
        "Yoki savollar bo'lsa, yozing!",
        parse_mode="HTML",
    )

    if user_id in orders_db:
        orders_db[user_id]["status"] = "rejected"

    if query.message.caption:
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
            parse_mode="HTML",
        )
    else:
        await query.edit_message_text("❌ <b>RAD ETILDI</b>", parse_mode="HTML")


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    return await show_main_menu(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Bekor qilindi. Qaytadan boshlash uchun /start yozing.")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 <b>Bot buyruqlari:</b>\n\n"
        "/start - Botni boshlash\n"
        "/help - Yordam\n\n"
        "Savollar bo'lsa, yozing!",
        parse_mode="HTML",
    )


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
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
                MessageHandler(
                    filters.PHOTO | filters.Document.ALL | (filters.TEXT & ~filters.COMMAND),
                    receive_receipt,
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(admin_confirm, pattern="^confirm_"))
    application.add_handler(CallbackQueryHandler(admin_reject, pattern="^reject_"))

    print("Bot ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
