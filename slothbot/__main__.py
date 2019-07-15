from slothbot.sloth import Sloth
from slothbot.sloth import PasteException

from telegram.ext import Updater, CommandHandler, Dispatcher
from telegram import Bot, Message
import telegram
import logging
import traceback
import re
import sys

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class SlothTelegramBot:
    def __init__(self, token: str):
        self.token: str = token
        self.UPDATER: Updater = None
        self.DISPATCHER: Dispatcher = None
        self.BOT: Bot = None

    def bot_help(self, update, context):
        update.message.reply_text(
            "Merhaba ben ShlothBot.\n`/paste <içerik>` diyerek beni kullanabilirsiniz.\n"
            "Yazdığınız şey bir kod ise hangi dil ile yazıldığını tahmin edeceğim (Yani umarım). Kodunuz ne kadar uzun olursa tahmin etmem o kadar kolaylaşır.",
            parse_mode=telegram.ParseMode.MARKDOWN)

    def bot_paste(self, update, context):
        try:
            matcher = re.match(
                r"/paste\s+((.|\n)+)",
                update.message.text,
                re.MULTILINE)
            if matcher:
                paste_content = matcher.group(1)
            else:
                update.message.reply_text("Hani kod?")
                return 0

            last_message: Message = self.BOT.send_message(
                text="paste.ubuntu.com 'a bağlanıyorum...",
                chat_id=update.message.chat_id)
            sloth = Sloth()
            paste_link: str = sloth.run(
                paste_content, poster=update.message.from_user.username)

            self.BOT.edit_message_text(
                f"Gönderen: @{update.message.from_user.username}\nLink: {paste_link}",
                chat_id=update.message.chat_id,
                message_id=last_message.message_id,
                parse_mode=telegram.ParseMode.MARKDOWN)

            self.BOT.delete_message(chat_id=update.message.chat_id,
                                    message_id=update.message.message_id)

        except PasteException:
            response_text = f"paste.ubuntu.com aşağıdaki hataları listeledi:\n```"
            for error in sloth.errors:
                response_text += f"- {error}\n"
            response_text += "```\n"
            response_text += f"Ilgili kişi: @{update.message.from_user.username}\n"
            self.BOT.send_message(
                text=response_text,
                chat_id=update.message.chat_id,
                message_id=last_message.message_id,
                parse_mode=telegram.ParseMode.MARKDOWN
            )

        except Exception as e:
            self.BOT.send_message(
                text=f"Aman aman aman! @hakancelik hocam bana bi bakın iyi değilim.(Spoiler: {e.__class__.__name__})",
                chat_id=update.message.chat_id)
            traceback.print_exc()

    def run(self):
        self.UPDATER = Updater(self.token, use_context=True)
        self.DISPATCHER = self.UPDATER.dispatcher
        self.BOT = self.UPDATER.bot

        self.DISPATCHER.add_handler(CommandHandler("help", self.bot_help))
        self.DISPATCHER.add_handler(CommandHandler("paste", self.bot_paste))
        self.UPDATER.start_polling()
        self.UPDATER.idle()


def main():
    if len(sys.argv) < 2:
        logger.error("Token not entered!")
    else:
        tbot = SlothTelegramBot(sys.argv[1])
        tbot.run()


if __name__ == '__main__':
    main()
