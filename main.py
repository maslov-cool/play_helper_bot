# Импортируем необходимые классы.
# @game_by_coding_lover_bot --> ник в тг
import logging
import random
from telegram import ReplyKeyboardMarkup
import asyncio
from telegram.ext import Application, CommandHandler


# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
BOT_TOKEN = '7722897085:AAGx_nP3cZMhBfzD6sOdlOuMW-wtCykLbIU'

reply_keyboard = [['/dice', '/timer']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


reply_keyboard_dice = [['/one_hexagonal_cube', '/two_hexagonal_cubes'],
                       ['/twenty_sided_cube', '/back']]
markup_dice = ReplyKeyboardMarkup(reply_keyboard_dice, one_time_keyboard=True)


reply_keyboard_timer = [['/thirty_seconds', '/one_minute'],
                       ['/five_minutes', '/back']]
markup_timer = ReplyKeyboardMarkup(reply_keyboard_timer, one_time_keyboard=True)


reply_keyboard_timer_time = [['/close']]
markup_timer_time = ReplyKeyboardMarkup(reply_keyboard_timer_time, one_time_keyboard=True)


async def start(update, context):
    await update.message.reply_text('''👋 Привет! Я бот-помощник для игр 🎲⏱
Выбери, чем я могу помочь:
- бросать кубик
- засечь определенное время''', reply_markup=markup)


async def dice(update, context):
    await update.message.reply_text('''Выбери, какой кубик бросить:
- 🎲 кинуть один шестигранный кубик,
- 🎲🎲 кинуть 2 шестигранных кубика одновременно,
- 🧊 кинуть 20-гранный кубик,
- 🔙 вернуться назад.''', reply_markup=markup_dice)


async def timer(update, context):
    await update.message.reply_text('''Выбери время для таймера:
- ⏱ 30 секунд,
- ⏱ 1 минута,
- ⏱ 5 минут,
- 🔙 вернуться назад''', reply_markup=markup_timer)


async def one_hexagonal_cube(update, context):
    await update.message.reply_text('Кидаю один шестигранный кубик')
    await asyncio.sleep(1)
    await update.message.reply_text('...')
    await asyncio.sleep(1)
    await update.message.reply_text('🎲 Выпало: ' + str(random.randint(1, 6)))


async def two_hexagonal_cubes(update, context):
    await update.message.reply_text('''Кидаю два шестигранных кубика''')
    await asyncio.sleep(1)
    await update.message.reply_text('...')
    await asyncio.sleep(1)
    await update.message.reply_text('🎲 Выпало: ' + str(random.randint(1, 6)) + ' и ' + str(random.randint(1, 6)))


async def twenty_sided_cube(update, context):
    await update.message.reply_text('''Кидаю 20-гранный кубик''')
    await asyncio.sleep(1)
    await update.message.reply_text('...')
    await asyncio.sleep(1)
    await update.message.reply_text('🎲 Выпало: ' + str(random.randint(1, 20)))


async def thirty_seconds(update, context):
    await update.message.reply_text('⏱ Засек 30 секунд...', reply_markup=markup_timer_time)
    context.user_data['timer'] = 30
    await set_timer(update, context)


async def one_minute(update, context):
    await update.message.reply_text('''⏱ Засек 1 минуту...''', reply_markup=markup_timer_time)
    context.user_data['timer'] = 60
    await set_timer(update, context)


async def five_minutes(update, context):
    await update.message.reply_text('''⏱ Засек 5 минут...''', reply_markup=markup_timer_time)
    context.user_data['timer'] = 300
    await set_timer(update, context)


async def back(update, context):
    await start(update, context)


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# Обычный обработчик, как и те, которыми мы пользовались раньше.
async def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, context.user_data['timer'], chat_id=chat_id, name=str(chat_id),
                               data=context.user_data['timer'])

    text = f'Вернусь через {update.message.text.split()[1]} с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def task(context):
    """Выводит сообщение"""
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! {context.user_data['timer']}c. прошли!')


async def unset_timer(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = '⏹️ Таймер сброшен.' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)
    await timer(update, context)


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчик в приложении.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("timer", timer))
    application.add_handler(CommandHandler("close", unset_timer))
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("one_hexagonal_cube", one_hexagonal_cube))
    application.add_handler(CommandHandler("two_hexagonal_cubes", two_hexagonal_cubes))
    application.add_handler(CommandHandler("twenty_sided_cube", twenty_sided_cube))
    application.add_handler(CommandHandler("thirty_seconds", thirty_seconds))
    application.add_handler(CommandHandler("one_minute", one_minute))
    application.add_handler(CommandHandler("five_minutes", five_minutes))
    application.add_handler(CommandHandler("back", back))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()


