import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from yandex_translate import YandexTranslate

tr = YandexTranslate(TOKEN)

CHOOSING, ECHOING, TRANSLATING = range(3)

def start(bot, update):
    update.message.reply_text("Hi! Choose /echo or /translate\nYou can use /done to quit this conversation")
    return CHOOSING

def echo(bot, update):
    update.message.reply_text('Echoing!\n/back to change your choice')
    return ECHOING

def translate(bot, update):
    update.message.reply_text('Translating!\n/back to change your choice')
    return TRANSLATING

def back(bot, update):
    update.message.reply_text('Choose again: /echo or /translate')
    return CHOOSING

def echo_message(bot, update):
    update.message.reply_text(update.effective_message.text)

def translate_message(bot, update):
    lang = tr.detect(update.message.text)
    if lang == 'ru':
        m = "RU-EN:\n" + tr.translate(update.message.text, 'ru-en')['text'][0].strip('"\'')
        update.message.reply_text(m)
    elif lang == 'en':
        m = "EN-RU:\n" + tr.translate(update.message.text, 'en-ru')['text'][0].strip('"\'')
        update.message.reply_text(m)
    else:
        update.message.reply_text('Я таких языков не знаю!')

def done(bot, update):
    update.message.reply_text("It's all over now!\n/start again?")
    return ConversationHandler.END

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)




if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = TOKEN
    NAME = "tfs-bot2"

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [CommandHandler('echo', echo), CommandHandler('translate', translate)],
            ECHOING: [MessageHandler(Filters.text, echo_message), CommandHandler('back', back)],
            TRANSLATING: [MessageHandler(Filters.text, translate_message), CommandHandler('back', back)]
        },

        fallbacks=[CommandHandler('done', done)]
    )
    # dp.add_handler(MessageHandler(Filters.text, translate_message))
    # Add handlers
    dp.add_handler(conv_handler)
    # dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('echo', start))
    # dp.add_handler(CommandHandler('translate', start))
    # dp.add_handler(MessageHandler(Filters.text, echo))
    # dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    updater.idle()
