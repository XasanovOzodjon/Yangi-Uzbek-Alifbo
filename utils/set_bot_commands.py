from telegram import BotCommand


async def set_default_commands(application):
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Botni ishga tushirish"),
            BotCommand("settings", "Bot sozlamalari"),
            BotCommand("help", "Yordam va qo'llanma"),
        ]
    )
