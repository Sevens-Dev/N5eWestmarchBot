import os
import asyncio
import random
from datetime import datetime, timedelta, UTC

import discord
from discord.ext import commands
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Optional: load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ==========================================================
# CONFIGURATION — All values pulled from environment variables.
# See README.md for setup instructions.
# ==========================================================

def _env_int(name: str, default: int = 0) -> int:
    val = os.getenv(name, "").strip()
    try:
        return int(val) if val else default
    except ValueError:
        return default

def _env_int_list(name: str) -> list[int]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return []
    out = []
    for piece in raw.split(","):
        piece = piece.strip()
        if piece.isdigit():
            out.append(int(piece))
    return out

# --- Discord ---
BOT_TOKEN            = os.getenv("DISCORD_BOT_TOKEN", "").strip()
AUTHORIZED_USER_IDS  = _env_int_list("AUTHORIZED_USER_IDS")
SUPPORT_CHANNEL_ID   = _env_int("SUPPORT_CHANNEL_ID")
AUCTION_CHANNEL_ID   = _env_int("AUCTION_CHANNEL_ID")

# --- Google Sheets ---
SHEET_URL              = os.getenv("SHEET_URL", "").strip()
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json").strip()
AUCTION_RESOURCE_BOOK   = os.getenv("AUCTION_RESOURCE_BOOK", "LMAO Resources").strip()

# --- Authorization roles for createplayer ---
# Comma-separated role NAMES, e.g. "Gopher,Toggy,Gamemaster"
CREATEPLAYER_ROLES = [r.strip() for r in os.getenv("CREATEPLAYER_ROLES", "Gamemaster").split(",") if r.strip()]

if not BOT_TOKEN:
    raise SystemExit("DISCORD_BOT_TOKEN is not set. See README.md.")
if not SHEET_URL:
    raise SystemExit("SHEET_URL is not set. See README.md.")


# Auction Globals
AUCTION_HISTORY_SHEET = "AuctionHistory"
AUCTION_RECENT_WINDOW_DAYS = 15  # how long to keep items "on cooldown"
AUCTION_DEFAULT_PAIRS = [("E", 2), ("D", 2), ("C", 2)]  # edit as you like

scheduler = AsyncIOScheduler(timezone=pytz.timezone("America/Chicago"))


# --------------------------
# Discord bot setup
# --------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class LMAOBot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(RandomTables(self))

bot = LMAOBot(command_prefix='!', intents=intents)

# --------------------------
# Google Sheets setup
# --------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open_by_url(SHEET_URL).sheet1

# Raw Sheets API (notes)
sheets_service = build("sheets", "v4", credentials=creds)
SPREADSHEET_ID = SHEET_URL.split("/d/")[1].split("/")[0]

# --------------------------
# Player sheet column mapping
# --------------------------
COLS = {
    "PlayerName": 1,
    "CharacterName": 2,
    "Level": 3,
    "MP": 4,
    "DT": 5,
    "Ryo": 6,
    "SpentMP": 7,
    "SpentDT": 8,
    "SpentRyo": 9,
}


class RandomTables(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.table32 = {
            1:"Aburame", 2:"Akimichi", 3:"Bakuton", 4:"Fuma", 5:"Futton",
            6:"Hatake", 7:"Hebi", 8:"Hoshigaki", 9:"Hozuki", 10:"Hyuga",
            11:"Inuzuka", 12:"Jiton", 13:"Jugo", 14:"Kaguya", 15:"Kurama",
            16:"Kuru", 17:"Namikaze", 18:"Nara", 19:"Non-Clan", 20:"Ranton",
            21:"Ryu", 22:"Sarutobi", 23:"Senju", 24:"Shakuton", 25:"Shikigami",
            26:"Shoton", 27:"Tsuchigumo", 28:"Uchiha", 29:"Uzumaki", 30:"Yamanaka",
            31:"Yoton", 32:"Yuki"
        }
        self.table11 = {
            1:"Genjutsu Specialist", 2:"Hunter Nin", 3:"Intelligence Operative",
            4:"Ninjutsu Specialist", 5:"Taijutsu Specialist", 6:"Weapon Specialist",
            7:"Science Nin", 8:"Puppet Master", 9:"Scout Nin", 10:"Cooking Nin",
            11:"Medic Nin"
        }

    @commands.command(name="random")
    async def randchar(self, ctx):
        roll32 = random.randint(1, 32)
        roll11 = random.randint(1, 11)
        result32 = self.table32[roll32]
        result11 = self.table11[roll11]
        await ctx.send(
            f"**Roll (1–32): {roll32}**\n{result32}\n\n"
            f"**Roll (1–11): {roll11}**\n{result11}"
        )


# --------------------------
# Helpers (Player sheet)
# --------------------------
def append_note(cell, text):
    try:
        metadata = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_id = metadata['sheets'][0]['properties']['sheetId']

        row_idx = cell.row - 1
        col_idx = cell.col - 1

        result = sheets_service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID,
            ranges=[f"{cell.row}:{cell.row}"],
            includeGridData=True
        ).execute()

        cell_data = result['sheets'][0]['data'][0]['rowData'][0]['values']
        old_note = cell_data[col_idx].get('note', '')

        timestamp = datetime.now().strftime("%m/%d")
        new_note = f"{old_note}\n{text} ({timestamp})" if old_note else f"{text} ({timestamp})"

        body = {
            "requests": [
                {
                    "updateCells": {
                        "rows": [{"values": [{"note": new_note}]}],
                        "fields": "note",
                        "start": {"sheetId": sheet_id, "rowIndex": row_idx, "columnIndex": col_idx}
                    }
                }
            ]
        }

        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body
        ).execute()

    except Exception as e:
        print(f"[NOTE ERROR] {e}")


# --- Owner-aware character helpers ---
def find_character_rows(character_name: str) -> list[int]:
    names = sheet.col_values(COLS["CharacterName"])
    rows = []
    for idx, name in enumerate(names[1:], start=2):
        if (name or "").strip().lower() == character_name.strip().lower():
            rows.append(idx)
    return rows

def find_character_row_by_owner(character_name: str, owner_str: str) -> int | None:
    for r in find_character_rows(character_name):
        owner = sheet.cell(r, COLS["PlayerName"]).value or ""
        if owner.strip() == owner_str.strip():
            return r
    rows = find_character_rows(character_name)
    if len(rows) == 1:
        return rows[0]
    return None

def list_character_owners(character_name: str) -> list[str]:
    owners = []
    for r in find_character_rows(character_name):
        owners.append((sheet.cell(r, COLS["PlayerName"]).value or "Unknown").strip())
    seen, out = set(), []
    for o in owners:
        if o not in seen:
            seen.add(o)
            out.append(o)
    return out


# --------------------------
# Player commands
# --------------------------
@bot.command()
@commands.has_any_role(*CREATEPLAYER_ROLES)
async def createplayer(ctx, discordname, charactername, level: int):
    if find_character_row_by_owner(charactername, discordname):
        await ctx.send(f"`{discordname}` already owns a character named `{charactername}`.")
        return
    row = [discordname, charactername, level, 0, 0, 0, 0, 0, 0]
    sheet.append_row(row)
    await ctx.send(f"Player `{discordname}` with character `{charactername}` created at level {level}.")

@bot.command()
async def displayplayer(ctx, charactername):
    owner_str = str(ctx.author)
    row_idx = find_character_row_by_owner(charactername, owner_str)

    if not row_idx:
        rows = find_character_rows(charactername)
        if not rows:
            await ctx.send(f"Character `{charactername}` not found.")
            return
        owners = ", ".join(list_character_owners(charactername))
        await ctx.send(
            f"Multiple characters named `{charactername}` exist, but you don't own one.\n"
            f"Current owners: {owners}"
        )
        return

    headers = sheet.row_values(1)
    row = sheet.row_values(row_idx)

    lines = []
    for i, header in enumerate(headers):
        header = (header or "").strip()
        if not header:
            continue
        value = row[i] if i < len(row) else ""
        lines.append(f"**{header}:** {value}")

    info = "\n".join(lines)
    await ctx.send(f"**{charactername} (yours) Info:**\n{info}")

async def modify_resource(ctx, charactername, col_name, amount: int, note, subtract=False):
    owner_str = str(ctx.author)
    row_idx = find_character_row_by_owner(charactername, owner_str)
    if not row_idx:
        rows = find_character_rows(charactername)
        if not rows:
            await ctx.send(f"Character `{charactername}` not found.")
        else:
            await ctx.send(f"You don't own `{charactername}`. Use the exact name of a character you own.")
        return

    owner = sheet.cell(row_idx, COLS["PlayerName"]).value
    if owner != str(ctx.author):
        await ctx.send(f"You do not own `{charactername}`. Only `{owner}` can modify this character.")
        return

    col = COLS[col_name]
    current = sheet.cell(row_idx, col).value
    current = int(current) if current.isdigit() else 0

    change = -amount if subtract else amount
    new_val = current + change
    if new_val < 0:
        await ctx.send(f"{col_name} can't go below 0.")
        return

    sheet.update_cell(row_idx, col, new_val)
    append_note(sheet.cell(row_idx, col), f"{'+' if change > 0 else ''}{change} | {note}")

    if subtract:
        spent_col = f"Spent{col_name}"
        spent_idx = COLS.get(spent_col)
        if spent_idx:
            spent_val = sheet.cell(row_idx, spent_idx).value
            spent_val = int(spent_val) if spent_val.isdigit() else 0
            new_spent = spent_val + amount
            sheet.update_cell(row_idx, spent_idx, new_spent)
            append_note(sheet.cell(row_idx, spent_idx), f"+{amount} | {note}")

    await ctx.send(f"{col_name} updated for `{charactername}`: {current} -> {new_val}")


@bot.command()
async def addmp(ctx, charactername, amount: int, *, note): await modify_resource(ctx, charactername, "MP", amount, note)

@bot.command()
async def spendmp(ctx, charactername, amount: int, *, note): await modify_resource(ctx, charactername, "MP", amount, note, subtract=True)

@bot.command()
async def adddt(ctx, charactername, amount: int, *, note): await modify_resource(ctx, charactername, "DT", amount, note)

@bot.command()
async def spenddt(ctx, charactername, amount: int, *, note): await modify_resource(ctx, charactername, "DT", amount, note, subtract=True)

@bot.command()
async def addryo(ctx, charactername, amount: int, *, note): await modify_resource(ctx, charactername, "Ryo", amount, note)

@bot.command()
async def spendryo(ctx, charactername, amount: int, *, note): await modify_resource(ctx, charactername, "Ryo", amount, note, subtract=True)


@bot.command()
async def setlevel(ctx, charactername, level: int):
    owner_str = str(ctx.author)
    row_idx = find_character_row_by_owner(charactername, owner_str)
    if not row_idx:
        rows = find_character_rows(charactername)
        if not rows:
            await ctx.send(f"Character `{charactername}` not found.")
        else:
            await ctx.send(f"You don't own `{charactername}`. Use a character you own.")
        return
    sheet.update_cell(row_idx, COLS["Level"], level)
    append_note(sheet.cell(row_idx, COLS["Level"]), f"Level set to {level}")
    await ctx.send(f"Level for `{charactername}` set to {level}.")


def _open_ws(title: str):
    return gc.open_by_url(SHEET_URL).worksheet(title)

def _get_or_create_history_ws():
    try:
        return _open_ws(AUCTION_HISTORY_SHEET)
    except Exception:
        sh = gc.open_by_url(SHEET_URL)
        ws = sh.add_worksheet(title=AUCTION_HISTORY_SHEET, rows=1000, cols=3)
        ws.update('A1:C1', [["DateUTC","Rank","Name"]])
        return ws

def _load_recent_history(window_days: int) -> dict[str, set[str]]:
    ws = _get_or_create_history_ws()
    vals = ws.get_all_values()
    recent_by_rank: dict[str, set[str]] = {}
    if len(vals) < 2:
        return recent_by_rank

    cutoff = datetime.now(UTC) - timedelta(days=window_days)
    for row in vals[1:]:
        if len(row) < 3:
            continue
        date_s, rank, name = row[0].strip(), row[1].strip().upper(), (row[2] or "").strip()
        try:
            dt = datetime.fromisoformat(date_s.replace("Z","+00:00"))
        except Exception:
            try:
                dt = datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            except Exception:
                continue
        if dt >= cutoff:
            recent_by_rank.setdefault(rank, set()).add(name.lower())
    return recent_by_rank

def _record_history(picked: list[tuple[str,str]], rank: str):
    ws = _get_or_create_history_ws()
    now_iso = datetime.now(UTC).isoformat()
    rows = [[now_iso, rank, name] for (name, _desc) in picked]
    if rows:
        ws.append_rows(rows)

async def run_auction_in_channel(channel: discord.TextChannel, pairs: list[tuple[str, int]]):
    rank_cols = {"E": (0, 1), "D": (2, 3), "C": (4, 5), "B": (6, 7), "A": (8, 9), "S": (10, 11)}

    auction_sheet = gc.open(AUCTION_RESOURCE_BOOK).worksheet("Auction")
    data = auction_sheet.get_all_values()
    recent = _load_recent_history(AUCTION_RECENT_WINDOW_DAYS)

    total_posted = 0

    for rank, count in pairs:
        rank = rank.upper()
        if rank not in rank_cols:
            await channel.send(f"Invalid rank: {rank}")
            continue

        item_col, desc_col = rank_cols[rank]
        items = [(row[item_col], row[desc_col]) for row in data[1:]
                 if len(row) > item_col and (row[item_col] or "").strip()]

        if not items:
            await channel.send(f"{rank}-Rank: No items found.")
            continue

        recent_names = recent.get(rank, set())
        fresh = [(n, d) for (n, d) in items if n.strip().lower() not in recent_names]
        stale = [(n, d) for (n, d) in items if n.strip().lower() in recent_names]

        picked: list[tuple[str, str]] = []
        if fresh:
            k = min(count, len(fresh))
            picked.extend(random.sample(fresh, k))
        if len(picked) < count:
            remaining = count - len(picked)
            stale_pool = [(n, d) for (n, d) in stale if (n, d) not in picked]
            if stale_pool:
                k = min(remaining, len(stale_pool))
                picked.extend(random.sample(stale_pool, k))

        if not picked:
            await channel.send(f"{rank}-Rank: Not enough items to auction.")
            continue

        for name, desc in picked:
            embed = discord.Embed(
                title=f"{rank}-Rank Auction Item: {name}",
                description=desc or "*No description*",
                color=discord.Color.orange()
            )
            msg = await channel.send(embed=embed)
            await msg.create_thread(name=f"{rank}-Rank: {name}"[:100])
            total_posted += 1
            await asyncio.sleep(0.2)

        _record_history(picked, rank)

    now = datetime.now(UTC)
    end_ts = int((now + timedelta(hours=72)).timestamp())
    await channel.send(f"All auctions will end in exactly 72 hours: <t:{end_ts}:F>")

    return total_posted



# --------------------------
# Auction command
# --------------------------
@bot.command(name="auction")
async def auction(ctx, *args):
    if ctx.author.id not in AUTHORIZED_USER_IDS:
        await ctx.send("You're not authorized to run this command.")
        return

    if len(args) % 2 != 0:
        await ctx.send("Please provide rank and count in pairs, e.g., `!auction E 3 D 5`")
        return

    try:
        pairs = [(args[i].upper(), int(args[i + 1])) for i in range(0, len(args), 2)]
    except ValueError:
        await ctx.send("Invalid format. Example usage: `!auction E 3 D 5`")
        return

    try:
        posted = await run_auction_in_channel(ctx.channel, pairs)
        await ctx.send(f"Posted {posted} auction item(s).")
    except Exception as e:
        await ctx.send(f"Error posting auction: {e}")


async def weekly_auction_job():
    if not AUCTION_CHANNEL_ID:
        return
    try:
        channel = await bot.fetch_channel(AUCTION_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            print(f"[WeeklyAuction] Target {AUCTION_CHANNEL_ID} is not a text channel.")
            return
        await run_auction_in_channel(channel, AUCTION_DEFAULT_PAIRS)
    except Exception as e:
        print(f"[WeeklyAuction ERROR] {e}")


# --------------------------
# on_ready: scheduler + persistent views
# --------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")

    try:
        if not scheduler.running:
            if not any(j.id == "weekly-auction" for j in scheduler.get_jobs()):
                scheduler.add_job(
                    weekly_auction_job,
                    CronTrigger(day_of_week="wed", hour=12, minute=0),
                    id="weekly-auction",
                    replace_existing=True,
                    misfire_grace_time=3600
                )
            scheduler.start()
    except Exception as e:
        print(f"[Scheduler] {e}")


@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)

    if (
        message.author.bot
        or not SUPPORT_CHANNEL_ID
        or message.channel.id != SUPPORT_CHANNEL_ID
        or getattr(message, "has_thread", False)
        or message.type is not discord.MessageType.default
    ):
        return

    base = (message.content or "").strip()
    if base:
        name = (base[:80] + "…") if len(base) > 80 else base
    else:
        ts = discord.utils.format_dt(message.created_at, style="t")
        name = f"Support • {message.author.display_name} • {ts}"

    try:
        await message.create_thread(
            name=name if name else "Support Discussion",
            auto_archive_duration=1440
        )
    except Exception as e:
        print(f"[SupportThread ERROR] {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


# --------------------------
# Run the bot
# --------------------------
bot.run(BOT_TOKEN)
