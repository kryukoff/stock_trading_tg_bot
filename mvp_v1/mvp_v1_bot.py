token = "" # token
file = ".xlsx" # xls filename

import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext, MessageHandler, Filters


SELECT_ROLE, SELECT_SERIE, SELECT_NUMBER, SELECT_IPHONE_MODEL, SELECT_MEMORY, \
    SELECT_COLOR, SELECT_SIM_TYPE, SELLER_TEXT = range(8)

buyers = []
sellers = {}


def read_iphone_series():
    df = pd.read_excel(file)
    return df["serie"].unique().tolist()


def read_iphone_numbers(selected_serie):
    df = pd.read_excel(file)
    return df[df["serie"] == selected_serie]["number"].unique().tolist()


def read_iphone_models(selected_serie, selected_number):
    df = pd.read_excel(file)
    return df[(df["serie"] == selected_serie) & (df["number"] == selected_number)]["model"].unique()


def read_iphone_memories(selected_serie, selected_number, selected_model):
    df = pd.read_excel(file)
    return df[
        (df["serie"] == selected_serie) &
        (df["number"] == selected_number) &
        (df["model"] == selected_model)
    ]["Memory"].unique()


def read_iphone_colors(selected_serie, selected_number, selected_model, selected_memory):
    df = pd.read_excel(file)
    return df[
        (df["serie"] == selected_serie) &
        (df["number"] == selected_number) &
        (df["model"] == selected_model) &
        (df["Memory"] == selected_memory)
    ]["Color"].unique()


def read_iphone_sim_types(selected_serie, selected_number, selected_model, selected_memory, selected_color):
    df = pd.read_excel(file)
    return df[
        (df["serie"] == selected_serie) &
        (df["number"] == selected_number) &
        (df["model"] == selected_model) &
        (df["Memory"] == selected_memory) &
        (df["Color"] == selected_color)
    ]["Sim"].unique()


def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Покупатель", callback_data="buyer")],
        [InlineKeyboardButton("Продавец", callback_data="seller")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Вы покупатель или продавец?", reply_markup=reply_markup)

    return SELECT_ROLE


def button_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    if query.data == "buyer":
        buyer_id = update.effective_user.id
        if sellers:
            for seller_username, seller_info in sellers.items():
                context.bot.send_message(
                    buyer_id,
                    f"Предложение продавца: {seller_info['text']}\nИмя продавца: {seller_username}\n"
                    f"Серия: {seller_info['serie']}\nНомер: {seller_info['number']}\n"
                    f"Модель: {seller_info['model']}\nПамять: {seller_info['memory']}\n"
                    f"Опция1: {seller_info['color']}\nОпция2: {seller_info['sim_type']}\n"
                    f"Цена: {seller_info['price']}"
                )
        else:
            buyers.append(update.effective_user)
            query.edit_message_text("Вы покупатель. Ожидаем появления продавцов.")

    elif query.data == "seller":
        query.edit_message_text("Вы продавец. \nВАЖНО: у вас должен быть настроен телеграм-юзернейм @username \
                                \nПожалуйста выберите тип товара:")
        iphone_series = read_iphone_series()
        keyboard = [
            [InlineKeyboardButton(serie, callback_data=serie)] for serie in iphone_series
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text("Пожалуйста выберите тип товара:", reply_markup=reply_markup)

        # Initialize seller_info dictionary
        context.user_data["seller_info"] = {}

        return SELECT_SERIE

    return ConversationHandler.END


def select_serie(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    selected_serie = query.data
    context.user_data["seller_info"]["serie"] = selected_serie

    query.edit_message_text(f"Вы выбрали: {selected_serie}. Теперь выберите номер:")

    numbers = read_iphone_numbers(selected_serie)
    keyboard = [
        [InlineKeyboardButton(number, callback_data=number)] for number in numbers
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("Пожалуйста выберите номер:", reply_markup=reply_markup)

    return SELECT_NUMBER


def select_number(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    selected_number = query.data
    context.user_data["seller_info"]["number"] = selected_number

    query.edit_message_text("Пожалуйста выберите модель:")

    models = read_iphone_models(context.user_data["seller_info"]["serie"], selected_number)
    keyboard = [
        [InlineKeyboardButton(model, callback_data=model)] for model in models
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("Пожалуйста выберите модель:", reply_markup=reply_markup)

    return SELECT_IPHONE_MODEL


def select_iphone_model(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    selected_model = query.data
    context.user_data["seller_info"]["model"] = selected_model

    query.edit_message_text(f"Вы выбрали: {selected_model}. Теперь выберите память:")

    memories = read_iphone_memories(
        context.user_data["seller_info"]["serie"],
        context.user_data["seller_info"]["number"],
        selected_model
    )
    keyboard = [
        [InlineKeyboardButton(memory, callback_data=memory)] for memory in memories
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("Пожалуйста выберите память:", reply_markup=reply_markup)

    return SELECT_MEMORY


def select_memory(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    selected_memory = query.data
    context.user_data["seller_info"]["memory"] = selected_memory

    query.edit_message_text(f"Вы выбрали: {selected_memory}. Теперь выберите опцию1:")

    colors = read_iphone_colors(
        context.user_data["seller_info"]["serie"],
        context.user_data["seller_info"]["number"],
        context.user_data["seller_info"]["model"],
        selected_memory
    )
    keyboard = [
        [InlineKeyboardButton(color, callback_data=color)] for color in colors
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("Пожалуйста выберите опцию1:", reply_markup=reply_markup)

    return SELECT_COLOR


def select_color(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    selected_color = query.data
    context.user_data["seller_info"]["color"] = selected_color

    query.edit_message_text(f"Вы выбрали: {selected_color}. Теперь выберите опцию2:")

    sim_types = read_iphone_sim_types(
        context.user_data["seller_info"]["serie"],
        context.user_data["seller_info"]["number"],
        context.user_data["seller_info"]["model"],
        context.user_data["seller_info"]["memory"],
        selected_color
    )
    keyboard = [
        [InlineKeyboardButton(sim_type, callback_data=sim_type)] for sim_type in sim_types
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text("Пожалуйста выберите опцию2:", reply_markup=reply_markup)

    return SELECT_SIM_TYPE


def select_sim_type(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    selected_sim_type = query.data
    context.user_data["seller_info"]["sim_type"] = selected_sim_type

    query.edit_message_text("Пожалуйтста введите цену вашего предложения:")

    # Update user_data to pass it to the next state
    context.user_data["seller_id"] = update.effective_user.username

    return SELLER_TEXT


def receive_text(update: Update, context: CallbackContext) -> int:
    if "seller_id" not in context.user_data:
        update.message.reply_text("Вы не продавец. Напечатайте /start чтобы начать как продавец.")
        return ConversationHandler.END

    seller_id = context.user_data["seller_id"]
    context.user_data["seller_info"]["text"] = update.message.text

    query_text = (
        f"Цена продавца: {context.user_data['seller_info']['text']}\n"
        f"Контакт продавца: t.me/{seller_id}\n"
        f"Тип: {context.user_data['seller_info']['serie']}\n"
        f"Номер: {context.user_data['seller_info']['number']}\n"
        f"Модель: {context.user_data['seller_info']['model']}\n"
        f"Память: {context.user_data['seller_info']['memory']}\n"
        f"Опция1: {context.user_data['seller_info']['color']}\n"
        f"Опция2: {context.user_data['seller_info']['sim_type']}\n"
        f"Цена: {update.message.text}"
    )

    for buyer in buyers:
        context.bot.send_message(buyer.id, query_text)

    buyers.clear()
    sellers[seller_id] = context.user_data["seller_info"]

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    query = update.message
    query.message.reply_text("Операция отменена.")
    return ConversationHandler.END


def main():
    updater = Updater(token)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ROLE: [CallbackQueryHandler(button_callback)],
            SELECT_SERIE: [CallbackQueryHandler(select_serie)],
            SELECT_NUMBER: [CallbackQueryHandler(select_number)],
            SELECT_IPHONE_MODEL: [CallbackQueryHandler(select_iphone_model)],
            SELECT_MEMORY: [CallbackQueryHandler(select_memory)],
            SELECT_COLOR: [CallbackQueryHandler(select_color)],
            SELECT_SIM_TYPE: [CallbackQueryHandler(select_sim_type)],
            SELLER_TEXT: [MessageHandler(Filters.text & ~Filters.command, receive_text)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
