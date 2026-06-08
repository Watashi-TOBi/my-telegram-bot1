from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

HELP_TEXT = """
📖 <b>Full Command Guide</b>
━━━━━━━━━━━━━━━━━━

🤖 <b>General</b>
• /start — Show the welcome message
• /help — Show this guide
• /rules — Show the group rules

━━━━━━━━━━━━━━━━━━
🔨 <b>Ban &amp; Kick</b>  <i>(reply to a user's message)</i>
• /ban — Permanently ban a user
• /kick — Remove a user (they can rejoin)
• /tban <code>[time]</code> — Temporary ban
  ↳ e.g. <code>/tban 30m</code> · <code>/tban 2h</code> · <code>/tban 1d</code>

━━━━━━━━━━━━━━━━━━
🔇 <b>Mute</b>  <i>(reply to a user's message)</i>
• /mute — Permanently mute a user
• /unmute — Remove mute from a user
• /tmute <code>[time]</code> — Temporarily mute
  ↳ e.g. <code>/tmute 10m</code> · <code>/tmute 1h</code>

━━━━━━━━━━━━━━━━━━
⚠️ <b>Warnings</b>  <i>(reply to a user's message)</i>
• /warn <code>[reason]</code> — Warn a user (auto-ban at 3)
• /unwarn — Remove the last warning
• /warns — Check a user's warning count
• /resetwarns — Clear all warnings for a user

━━━━━━━━━━━━━━━━━━
📌 <b>Pin Messages</b>  <i>(reply to a message)</i>
• /pin — Pin the replied message
• /pin silent — Pin without notification
• /unpin — Unpin a message
• /unpinall — Unpin every pinned message

━━━━━━━━━━━━━━━━━━
👑 <b>Admin Roles</b>  <i>(reply to a user's message)</i>
• /promote — Promote user to admin
• /demote — Remove admin rights

━━━━━━━━━━━━━━━━━━
🗑️ <b>Purge</b>  <i>(reply to the first message to delete)</i>
• /purge — Delete all messages from replied msg to /purge

━━━━━━━━━━━━━━━━━━
🔒 <b>Locks</b>
• /lock <code>[type]</code> — Restrict content type for everyone
• /unlock <code>[type]</code> — Remove the restriction
• /locks — Show current lock status
  ↳ Types: <code>text</code> · <code>media</code> · <code>sticker</code> · <code>gif</code> · <code>poll</code> · <code>link</code>

━━━━━━━━━━━━━━━━━━
💬 <b>Filters</b>  <i>(keyword auto-replies)</i>
• /filter <code>[word] [reply]</code> — Set an auto-reply
  ↳ e.g. <code>/filter hello Hi there!</code>
• /filters — List all active filters
• /stop <code>[word]</code> — Remove a filter

━━━━━━━━━━━━━━━━━━
📋 <b>Rules</b>
• /setrules <code>[text]</code> — Set the group rules
  ↳ e.g. <code>/setrules Be respectful. No spam.</code>
• /rules — Show the group rules

━━━━━━━━━━━━━━━━━━
🚨 <b>Report</b>  <i>(reply to a bad message)</i>
• /report <code>[reason]</code> — Alert all admins instantly

━━━━━━━━━━━━━━━━━━
🎉 <b>Fun</b>
• /love <code>[Name1] [Name2]</code> — Calculate love %
  ↳ e.g. <code>/love Alice Bob</code>
• /crush — Reveal someone's secret crush  <i>(reply, groups only)</i>
  ↳ Reply to any user to expose their crush!
• /q — Turn a message into a quote sticker  <i>(reply)</i>
• /kang — Steal a sticker into your own pack  <i>(reply to a sticker)</i>
  ↳ Start me in DM first to create your pack

━━━━━━━━━━━━━━━━━━
🤖 <b>AI Chat</b>
• Message me privately — I always reply
• @mention me in a group — I reply when tagged
""".strip()

# Plain-text version (same content, no HTML) kept for reference
HELP_TEXT_PLAIN = """
📖 Full Command Guide
━━━━━━━━━━━━━━━━━━

🤖 General
• /start — Show the welcome message
• /help — Show this guide
• /rules — Show the group rules

━━━━━━━━━━━━━━━━━━
🔨 Ban & Kick  (reply to a user's message)
• /ban — Permanently ban a user
• /kick — Remove a user (they can rejoin)
• /tban [time] — Temporary ban
  ↳ e.g. /tban 30m · /tban 2h · /tban 1d

━━━━━━━━━━━━━━━━━━
🔇 Mute  (reply to a user's message)
• /mute — Permanently mute a user
• /unmute — Remove mute from a user
• /tmute [time] — Temporarily mute
  ↳ e.g. /tmute 10m · /tmute 1h

━━━━━━━━━━━━━━━━━━
⚠️ Warnings  (reply to a user's message)
• /warn [reason] — Warn a user (auto-ban at 3)
• /unwarn — Remove the last warning
• /warns — Check a user's warning count
• /resetwarns — Clear all warnings for a user

━━━━━━━━━━━━━━━━━━
📌 Pin Messages  (reply to a message)
• /pin — Pin the replied message
• /pin silent — Pin without notification
• /unpin — Unpin a message
• /unpinall — Unpin every pinned message

━━━━━━━━━━━━━━━━━━
👑 Admin Roles  (reply to a user's message)
• /promote — Promote user to admin
• /demote — Remove admin rights

━━━━━━━━━━━━━━━━━━
🗑️ Purge  (reply to the first message to delete)
• /purge — Delete all messages from replied msg to /purge

━━━━━━━━━━━━━━━━━━
🔒 Locks
• /lock [type] — Restrict content type for everyone
• /unlock [type] — Remove the restriction
• /locks — Show current lock status
  ↳ Types: text · media · sticker · gif · poll · link

━━━━━━━━━━━━━━━━━━
💬 Filters  (keyword auto-replies)
• /filter [word] [reply] — Set an auto-reply
  ↳ e.g. /filter hello Hi there!
• /filters — List all active filters
• /stop [word] — Remove a filter

━━━━━━━━━━━━━━━━━━
📋 Rules
• /setrules [text] — Set the group rules
  ↳ e.g. /setrules Be respectful. No spam.
• /rules — Show the group rules

━━━━━━━━━━━━━━━━━━
🚨 Report  (reply to a bad message)
• /report [reason] — Alert all admins instantly

━━━━━━━━━━━━━━━━━━
🎉 Fun
• /love [Name1] [Name2] — Calculate love %
  ↳ e.g. /love Alice Bob

━━━━━━━━━━━━━━━━━━
🤖 AI Chat
• Message me privately — I always reply
• @mention me in a group — I reply when tagged
""".strip()


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Start", callback_data="show_start")],
    ])
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML", reply_markup=keyboard)


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Start", callback_data="show_start")],
    ])
    await query.message.reply_text(
        text=HELP_TEXT,
        parse_mode="HTML",
        reply_markup=keyboard,
    )
