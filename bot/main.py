import logging
from telegram import Update, BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    CallbackQueryHandler,
    filters,
)

from config import TELEGRAM_TOKEN

from handlers.start          import start_handler, commands_callback, back_callback
from handlers.help           import help_handler, help_callback
from handlers.admin          import ban_handler, kick_handler
from handlers.mute           import mute_handler, unmute_handler, tmute_handler
from handlers.tban           import tban_handler
from handlers.warn           import warn_handler, unwarn_handler, warns_handler, resetwarns_handler
from handlers.purge          import purge_handler
from handlers.pin            import pin_handler, unpin_handler, unpinall_handler
from handlers.promote        import promote_handler, demote_handler
from handlers.rules          import rules_handler, setrules_handler
from handlers.report         import report_handler
from handlers.filter_handler import (
    filter_handler, stop_filter_handler, list_filters_handler, check_filters,
)
from handlers.lock           import lock_handler, unlock_handler, locks_handler
from handlers.welcome        import member_update_handler
from utils.members           import track as track_member
from handlers.fun            import love_handler, crush_handler
from handlers.quote_sticker  import quote_handler, kang_handler
from handlers.ai_chat        import ai_chat_handler
from handlers.anime          import (
    hug_handler, kiss_handler, slap_handler, pat_handler,
    cuddle_handler, poke_handler, bite_handler, punch_handler,
    wink_handler, baka_handler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

_PRIVATE_COMMANDS = [
    BotCommand("start",      "Show the welcome message"),
    BotCommand("help",       "Full command guide"),
    BotCommand("love",       "Love compatibility calculator"),
    BotCommand("crush",      "Reveal someone's secret crush (reply)"),
    BotCommand("q",          "Turn a message into a quote sticker (reply)"),
    BotCommand("kang",       "Steal a sticker into your pack (reply)"),
    BotCommand("hug",        "Hug someone (reply)"),
    BotCommand("kiss",       "Kiss someone (reply)"),
    BotCommand("slap",       "Slap someone (reply)"),
    BotCommand("pat",        "Pat someone (reply)"),
    BotCommand("cuddle",     "Cuddle someone (reply)"),
    BotCommand("poke",       "Poke someone (reply)"),
    BotCommand("bite",       "Bite someone (reply)"),
    BotCommand("punch",      "Punch someone (reply)"),
    BotCommand("wink",       "Wink at someone (reply)"),
    BotCommand("kick",       "Kick someone (reply)"),
    BotCommand("baka",       "Call someone a baka! (reply)"),
]

_GROUP_COMMANDS = [
    BotCommand("start",      "Welcome message"),
    BotCommand("help",       "Full command guide"),
    BotCommand("rules",      "Show group rules"),
    BotCommand("report",     "Report a user to admins"),
    BotCommand("love",       "Love compatibility — /love Name1 Name2"),
    BotCommand("crush",      "Secret crush reveal (reply to a user)"),
    BotCommand("q",          "Quote sticker from a message (reply)"),
    BotCommand("kang",       "Steal a sticker into your pack (reply)"),
    BotCommand("hug",        "Hug someone (reply)"),
    BotCommand("kiss",       "Kiss someone (reply)"),
    BotCommand("slap",       "Slap someone (reply)"),
    BotCommand("pat",        "Pat someone (reply)"),
    BotCommand("cuddle",     "Cuddle someone (reply)"),
    BotCommand("poke",       "Poke someone (reply)"),
    BotCommand("bite",       "Bite someone (reply)"),
    BotCommand("punch",      "Punch someone (reply)"),
    BotCommand("wink",       "Wink at someone (reply)"),
    BotCommand("baka",       "Call someone a baka! (reply)"),
    BotCommand("ban",        "Ban a user (reply)"),
    BotCommand("kick",       "Kick a user (reply)"),
    BotCommand("tban",       "Temp-ban — /tban 1h (reply)"),
    BotCommand("mute",       "Mute a user (reply)"),
    BotCommand("unmute",     "Unmute a user (reply)"),
    BotCommand("tmute",      "Temp-mute — /tmute 30m (reply)"),
    BotCommand("warn",       "Warn a user (reply)"),
    BotCommand("unwarn",     "Remove a warning (reply)"),
    BotCommand("warns",      "Check warnings (reply)"),
    BotCommand("resetwarns", "Clear all warnings (reply)"),
    BotCommand("purge",      "Delete messages from reply to here"),
    BotCommand("pin",        "Pin a message (reply)"),
    BotCommand("unpin",      "Unpin a message"),
    BotCommand("unpinall",   "Unpin all messages"),
    BotCommand("promote",    "Promote to admin (reply)"),
    BotCommand("demote",     "Remove admin rights (reply)"),
    BotCommand("lock",       "Lock content type — /lock media"),
    BotCommand("unlock",     "Unlock content type — /unlock media"),
    BotCommand("locks",      "Show lock status"),
    BotCommand("filter",     "Add keyword filter — /filter hi Hello!"),
    BotCommand("filters",    "List active filters"),
    BotCommand("stop",       "Remove a filter — /stop hi"),
    BotCommand("setrules",   "Set group rules — /setrules text"),
]


async def _set_commands(app) -> None:
    await app.bot.set_my_commands(_PRIVATE_COMMANDS, scope=BotCommandScopeAllPrivateChats())
    await app.bot.set_my_commands(_GROUP_COMMANDS,   scope=BotCommandScopeAllGroupChats())
    logger.info("Bot commands registered.")


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(_set_commands).build()

    # ── General ────────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start",  start_handler))
    app.add_handler(CommandHandler("help",   help_handler))
    app.add_handler(CommandHandler("love",   love_handler))
    app.add_handler(CommandHandler("crush",  crush_handler))
    app.add_handler(CommandHandler("q",      quote_handler))
    app.add_handler(CommandHandler("kang",   kang_handler))

    # ── Anime / fun interaction ────────────────────────────────────────────────
    app.add_handler(CommandHandler("hug",    hug_handler))
    app.add_handler(CommandHandler("kiss",   kiss_handler))
    app.add_handler(CommandHandler("slap",   slap_handler))
    app.add_handler(CommandHandler("pat",    pat_handler))
    app.add_handler(CommandHandler("cuddle", cuddle_handler))
    app.add_handler(CommandHandler("poke",   poke_handler))
    app.add_handler(CommandHandler("bite",   bite_handler))
    app.add_handler(CommandHandler("punch",  punch_handler))
    app.add_handler(CommandHandler("wink",   wink_handler))
    app.add_handler(CommandHandler("baka",   baka_handler))

    # ── Callback buttons ───────────────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(help_callback,     pattern="^show_help$"))
    app.add_handler(CallbackQueryHandler(commands_callback, pattern="^show_commands$"))
    app.add_handler(CallbackQueryHandler(back_callback,     pattern="^show_start$"))

    # ── Admin — ban/kick ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("ban",  ban_handler))
    app.add_handler(CommandHandler("kick", kick_handler))
    app.add_handler(CommandHandler("tban", tban_handler))

    # ── Admin — mute ───────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("mute",   mute_handler))
    app.add_handler(CommandHandler("unmute", unmute_handler))
    app.add_handler(CommandHandler("tmute",  tmute_handler))

    # ── Admin — warnings ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("warn",       warn_handler))
    app.add_handler(CommandHandler("unwarn",     unwarn_handler))
    app.add_handler(CommandHandler("warns",      warns_handler))
    app.add_handler(CommandHandler("resetwarns", resetwarns_handler))

    # ── Admin — messages ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("purge",    purge_handler))
    app.add_handler(CommandHandler("pin",      pin_handler))
    app.add_handler(CommandHandler("unpin",    unpin_handler))
    app.add_handler(CommandHandler("unpinall", unpinall_handler))

    # ── Admin — roles ──────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("promote", promote_handler))
    app.add_handler(CommandHandler("demote",  demote_handler))

    # ── Admin — locks ──────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("lock",   lock_handler))
    app.add_handler(CommandHandler("unlock", unlock_handler))
    app.add_handler(CommandHandler("locks",  locks_handler))

    # ── Group info ─────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("rules",    rules_handler))
    app.add_handler(CommandHandler("setrules", setrules_handler))
    app.add_handler(CommandHandler("report",   report_handler))

    # ── Keyword filters ────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("filter",  filter_handler))
    app.add_handler(CommandHandler("filters", list_filters_handler))
    app.add_handler(CommandHandler("stop",    stop_filter_handler))

    # ── Member join/leave ──────────────────────────────────────────────────────
    app.add_handler(ChatMemberHandler(member_update_handler, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, member_update_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_update_handler))

    # ── Member tracker (runs on every group message so /crush has data) ────────
    async def _track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        msg = update.effective_message
        user = update.effective_user
        chat = update.effective_chat
        if user and chat and chat.type in ("group", "supergroup"):
            track_member(chat.id, user.id, user.first_name)

    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, _track), group=0)

    # ── Message handlers (filters run before AI chat) ──────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters),   group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_handler), group=2)

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
