# LMAO Bot — Setup Guide

Hi! This guide will help you get a Discord bot running on your computer. The bot lets people on your Discord server keep track of tabletop RPG characters, spend in-game money, and run weekly item auctions. Everything saves to a Google spreadsheet so the numbers don't get lost.

This guide is written so that **anyone** can follow it, even if you've never written code or used a terminal before. If a step looks scary, just take it one tiny piece at a time. You can do this!

>  **One important rule before you start:** the bot uses a secret password called a "token". If anyone else gets your token, they can make your bot do bad things. **Never** put it on Discord, never put it on YouTube, never share it with anyone — not even your friends. We'll talk about this again later.

---

## What you'll need

Before we start, you need a few things. Don't install anything yet — just check that you have these:

1. **A computer** running Windows, macOS, or Linux. Any of them will work.
2. **A Discord account** that owns (or can manage) the server you want to add the bot to. If you don't manage a server, you can make a free one — click the **+** button on the left side of Discord and pick "Create My Own".
3. **A Google account** (a regular Gmail account is fine).
4. **About an hour** of patience. The first time is the hardest. After this you'll never have to do it again.

---

## Step 1: Install Python

Python is the language the bot is written in. Your computer needs it to run the bot.

### On Windows

1. Go to **https://www.python.org/downloads/** in your web browser.
2. Click the big yellow button that says **"Download Python 3.x.x"** (the x's will be numbers — anything 3.10 or higher is fine).
3. Open the file you just downloaded.
4. **VERY IMPORTANT:** at the bottom of the installer window there's a checkbox that says **"Add Python to PATH"** or **"Add python.exe to PATH"**.  **Tick that box.** If you forget this, nothing in this guide will work and you'll have to uninstall Python and start over.
5. Click **"Install Now"**.
6. Wait for it to finish, then close the installer.

### On macOS

1. Go to **https://www.python.org/downloads/** in your web browser.
2. Click the big yellow button that says **"Download Python 3.x.x"**.
3. Open the `.pkg` file you downloaded and follow the installer. You can click "Continue" through every screen.

### On Linux

You probably already have Python. Open a terminal and type:

```
python3 --version
```

If it says something like `Python 3.11.4`, you're good. If not, install it with your package manager (for example, `sudo apt install python3 python3-pip` on Ubuntu).

### Did it work?

To check, you need to open a **terminal**:

- **Windows:** press the **Windows key**, type `cmd`, and press Enter. A black window will open.
- **macOS:** press **Cmd + Space**, type `terminal`, and press Enter.
- **Linux:** you already know how, you're cool.

In that black window, type this exactly and press Enter:

```
python --version
```

(On macOS and Linux you may need to type `python3 --version` instead.)

If you see something like `Python 3.11.4`, **it worked!**  You can close the terminal for now.

---

## Step 2: Download the bot files

You need three files: `bot.py`, `README.md` (the guide you're reading right now), and `.env.example`. You probably got them from whoever sent you this guide.

1. Make a new folder somewhere easy to find. The Desktop is fine. Call it something like `MyBot`.
2. Put all three files inside that folder.

That's it. Easy step!

---

## Step 3: Install the Python packages the bot needs

The bot uses some extra Python tools that don't come with Python by default. We need to install them.

1. Open a terminal again (see Step 1 if you forgot how).
2. We need to get into the folder where you put the bot. Type `cd `, then a space, then **drag your `MyBot` folder from your Desktop into the terminal window** and let go. The path will appear automatically. Press Enter.

   So you'll see something like:
   ```
   cd C:\Users\YourName\Desktop\MyBot
   ```
   or on Mac:
   ```
   cd /Users/YourName/Desktop/MyBot
   ```

3. Now type this exactly and press Enter:

   ```
   pip install -U discord.py gspread google-auth google-api-python-client pytz apscheduler python-dotenv
   ```

   (If `pip` doesn't work, try `pip3` instead.)

4. You'll see a lot of text scroll past. That's normal — it's downloading and installing the tools. Wait for it to finish. It might take a minute or two.

5. When you see your prompt come back (the line ending in `>` or `$`), it's done.

### Did it work?

If the last few lines say something like `Successfully installed ...`, **it worked!** If you see red error text, scroll up and read the first error message — it usually tells you what went wrong. The most common problem is having no internet, so check your wi-fi.

---

## Step 4: Make a Discord bot account

A "bot" in Discord is just a special kind of user account that a program controls instead of a person.

1. Go to **https://discord.com/developers/applications** and log in with your Discord account.
2. Click the purple **"New Application"** button in the top right.
3. Give it a name (like `MyAwesomeBot`), tick the "I agree" box, and click **"Create"**.
4. On the left side, click **"Bot"**.
5. You'll see a section called **"Privileged Gateway Intents"**. Turn ON these two switches:
   -  **Server Members Intent**
   -  **Message Content Intent**

   Scroll down and click **"Save Changes"** if it asks.
6. Scroll back up. Find the button that says **"Reset Token"** and click it. It will warn you. Click **"Yes, do it!"**.
7. A long string of letters and numbers will appear. **This is your bot's secret password (the "token").** Click the **"Copy"** button next to it.
8. Open a new text file on your computer (Notepad on Windows, TextEdit on Mac) and paste the token into it. **Don't save the file anywhere public.** This is just so you don't lose the token before we use it in Step 9.

   >  **REMINDER:** This token is secret. Don't show anyone. If you do show someone by accident, come back to this page and click "Reset Token" again — that makes the old one stop working.

---

## Step 5: Invite the bot to your Discord server

The bot exists now, but it's not in your server yet. Let's fix that.

1. Still on the developer page, click **"OAuth2"** in the left sidebar.
2. Click **"URL Generator"** (it might be a sub-item).
3. In the **"Scopes"** box, tick:
   -  **bot**
   -  **applications.commands**
4. A new box called **"Bot Permissions"** will appear below. Tick these:
   -  Send Messages
   -  Embed Links
   -  Read Message History
   -  Create Public Threads
   -  Send Messages in Threads
   -  Manage Threads
5. At the very bottom, you'll see a long URL. Click **"Copy"** next to it.
6. Paste that URL into a new browser tab and press Enter.
7. Discord will ask which server to add the bot to. Pick your server and click **"Authorize"**. Solve the "I'm not a robot" puzzle if it shows one.

You should now see your bot in your Discord server's member list, marked as offline (with a grey dot). It'll come online once we finish setup.

---

## Step 6: Make a Google Sheet for the bot

The bot stores all the character data in a Google spreadsheet so nothing gets lost.

1. Go to **https://sheets.google.com** and click the big colorful **"+"** to make a new blank sheet.
2. Click the words **"Untitled spreadsheet"** at the top and rename it to something like `Bot Data`.
3. In the very first row (row 1), you need to type these column headers, **one in each cell, exactly as written**:

   | A          | B             | C     | D  | E  | F   | G       | H       | I        |
   |------------|---------------|-------|----|----|-----|---------|---------|----------|
   | PlayerName | CharacterName | Level | MP | DT | Ryo | SpentMP | SpentDT | SpentRyo |

   So cell A1 is `PlayerName`, B1 is `CharacterName`, and so on through I1 being `SpentRyo`.

4. Look at the URL of your sheet in the browser. It will look something like:

   ```
   https://docs.google.com/spreadsheets/d/1abc123XYZ.../edit
   ```

   Copy that whole URL and paste it into the same Notepad/TextEdit file where you saved your bot token. We'll need it in Step 9.

---

## Step 7: Give the bot permission to read your sheet

This is the trickiest part of the whole guide. Take a deep breath. We're going to make a "robot Google account" that the bot uses to talk to your spreadsheet.

1. Go to **https://console.cloud.google.com/** and log in with the same Google account that owns your sheet.
2. At the very top of the page, you'll see a project picker (it might say "Select a project"). Click it, then click **"New Project"** in the popup. Name it `BotProject` and click **"Create"**. Wait a few seconds — there's a notification when it's done.
3. Make sure your new project is selected at the top.
4. In the search bar at the top of the page, type **"Google Sheets API"** and click the result.
5. Click the blue **"Enable"** button. Wait a few seconds.
6. Click the back arrow and search for **"Google Drive API"**. Click it and click **"Enable"** too.
7. Now in the search bar, type **"Service Accounts"** and click the result (under "IAM & Admin").
8. Click **"+ Create Service Account"** at the top.
9. Give it a name like `bot-account` and click **"Create and Continue"**.
10. Skip the next two screens by clicking **"Continue"** then **"Done"**.
11. You'll see your new service account in a list. Click on its name (it'll look like an email address ending in `.iam.gserviceaccount.com`).
12. Click the **"Keys"** tab at the top.
13. Click **"Add Key"** → **"Create new key"**.
14. Pick **"JSON"** and click **"Create"**.
15. A file will download to your computer. **Move this file into your `MyBot` folder** and rename it to exactly `credentials.json`.

    >  **This file is also secret!** It's like another password. Don't share it.

16. Open `credentials.json` in Notepad or TextEdit. Find the line that says `"client_email": "bot-account@..."` and copy just the email address (the part inside the quotes after `"client_email":`).
17. Go back to your Google Sheet from Step 6. Click the green **"Share"** button in the top right.
18. Paste the email address you just copied into the box, make sure it says **"Editor"** (not "Viewer"), uncheck "Notify people", and click **"Share"**.

The bot can now read and write to your sheet! 

---

## Step 8: Set up the auction sheet (optional)

The bot has a feature where it can post random items for people to bid on. If you want to use it, you need a second spreadsheet for the items.

1. Go to **https://sheets.google.com** and make another new sheet. Name it exactly `LMAO Resources`.
2. Click the tab at the bottom (probably called "Sheet1") and rename it to `Auction`.
3. Set up the columns like this. The bot expects items grouped by rank (E is easiest, S is the rarest). Each rank gets two columns: a name and a description.

   | A (E item) | B (E desc) | C (D item) | D (D desc) | E (C item) | F (C desc) | G (B item) | H (B desc) | I (A item) | J (A desc) | K (S item) | L (S desc) |
   |------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|

4. Type whatever item names and descriptions you want. Leave blank rows alone — the bot ignores them. You don't need to fill every rank.
5. Just like before, click **"Share"** and add the same `bot-account@...` email as Editor.

If you don't want auctions at all, you can skip this step. Just don't run the `!auction` command and don't set up the weekly schedule.

---

## Step 9: Fill in the `.env` file

Almost done! Now we tell the bot all the secret stuff it needs to know.

1. Open the `MyBot` folder. You should see a file called `.env.example`. Make a copy of it in the same folder and rename the copy to just `.env` (with the dot at the front and **no** `.example` on the end).

   > **Note for Windows users:** Windows hides files that start with a dot. To make this easier, open the folder in File Explorer, click **"View"** at the top, and tick **"File name extensions"** and **"Hidden items"**.

2. Open `.env` in Notepad or TextEdit (right-click → "Open with" → Notepad).

3. You'll see a bunch of lines like `DISCORD_BOT_TOKEN=`. After each `=`, you need to paste in the right value. **Don't put any spaces or quotes around the values.**

   Here's what each line means:

   - **`DISCORD_BOT_TOKEN=`** Paste the bot token from Step 4 here.
   - **`AUTHORIZED_USER_IDS=`** Paste your own Discord user ID here. To get it: in Discord, click the gear icon at the bottom left → **"Advanced"** → turn on **"Developer Mode"**. Then close settings, right-click your own name in any chat, and click **"Copy User ID"**. Paste the long number here. If you want more than one person to be allowed, separate them with commas, no spaces (like `123,456,789`).
   - **`SUPPORT_CHANNEL_ID=`** This is for an optional feature: any message someone sends in this channel will automatically get a thread created on it (handy for support questions). Right-click the channel name in your Discord server and click **"Copy Channel ID"** (you need Developer Mode on for this, see above). Paste the number here. **If you don't want this feature, leave it blank.**
   - **`AUCTION_CHANNEL_ID=`** The channel where the bot should post the weekly auction. Right-click → **"Copy Channel ID"**. **Leave blank to skip.**
   - **`CREATEPLAYER_ROLES=`** The names of Discord roles that are allowed to create new players. The default is `Gamemaster`. If your role is called something else, put that name here. Multiple roles separated by commas.
   - **`SHEET_URL=`** Paste the URL of your main Google Sheet from Step 6 here.
   - **`GOOGLE_CREDENTIALS_PATH=`** This is just `credentials.json` (which is the default). Don't change it unless you put the file somewhere else.
   - **`AUCTION_RESOURCE_BOOK=`** This is just `LMAO Resources` (the default). Only change it if you named your auction sheet something different in Step 8.

4. **Save the file.** Make sure when you save it, it's still called `.env` and not `.env.txt`. In Notepad, when you save, change "Save as type" to **"All Files"** to make sure it doesn't add `.txt`.

---

## Step 10: Run the bot!

The moment of truth.

1. Open a terminal in your `MyBot` folder again (like in Step 3).

2. Type:

   ```
   python bot.py
   ```

   (Or `python3 bot.py` on Mac/Linux.)

3. If everything is set up right, you'll see something like:

   ```
   Logged in as MyAwesomeBot#1234.
   ```

   **🎉 Your bot is alive!** Go check your Discord server — your bot should now have a green dot next to its name in the member list.

4. To test it, type `!random` in any channel where the bot can see messages. It should reply with a random clan and class.

5. **To stop the bot,** click the terminal window and press **Ctrl + C**. The bot will go offline.

6. **To start it again** later, you just need to do steps 1 and 2 above. You don't have to redo any of the setup.

>  The bot only runs while the terminal window is open and the program is running. If you close the terminal or shut down your computer, the bot goes offline. Keeping a bot running 24/7 is a more advanced topic — for now, just run it when you want to use it.

---

## How to use the bot

Once the bot is online, anyone in your Discord server can type these in any channel:

### Anyone can use:
- **`!random`** — picks a random clan and class. Fun for making new characters.
- **`!displayplayer Naruto`** — shows your character's stats. (Replace `Naruto` with your character's name.)
- **`!addmp Naruto 5 finished a mission`** — adds 5 MP to your character. The last part is a note that gets saved to the spreadsheet so you remember why.
- **`!spendmp Naruto 3 bought a scroll`** — subtracts 3 MP and writes a note.
- **`!adddt`** / **`!spenddt`** — same idea but for DT.
- **`!addryo`** / **`!spendryo`** — same idea but for Ryo (in-game money).
- **`!setlevel Naruto 5`** — sets your character's level.

### Only people with the right role can use:
- **`!createplayer Alice#1234 Naruto 1`** — creates a new character. The first part is the Discord username of the player who'll own it. Only people with the role you set in `CREATEPLAYER_ROLES` can run this.

### Only people whose ID is in `AUTHORIZED_USER_IDS` can use:
- **`!auction E 3 D 2`** — posts 3 random E-rank items and 2 random D-rank items in the current channel for people to bid on. You can mix any ranks you want.

### Things the bot does on its own:
- **Every Wednesday at noon (Chicago time)**, the bot automatically posts a fresh auction in the channel you set as `AUCTION_CHANNEL_ID`.
- **In the support channel** (if you set one), every new message gets a thread created on it automatically.

---

## Help! Something went wrong

Don't panic. Here are the most common problems and how to fix them.

### "I see red text and the bot won't start."

Read the **first** red error message (not the last one). Usually it tells you exactly what's missing.

- **`DISCORD_BOT_TOKEN is not set`** — your `.env` file is missing or in the wrong place. Make sure it's named exactly `.env` (not `.env.txt`) and is in the same folder as `bot.py`. Make sure you actually put your token after the `=` sign.
- **`SHEET_URL is not set`** — same as above, but for the sheet URL line.
- **`PrivilegedIntentsRequired`** — go back to Step 4 and make sure you turned on both "Server Members Intent" and "Message Content Intent" on the Discord developer page.
- **`SpreadsheetNotFound`** — you forgot to share the sheet with the `bot-account@...` email from `credentials.json`. Go back to Step 7, item 17.
- **`FileNotFoundError: credentials.json`** — the credentials file isn't in your `MyBot` folder, or it's named something different. Make sure it's there and named exactly `credentials.json`.

### "The bot is online but doesn't respond to commands."

- Make sure you're typing the command in a channel the bot can see. Right-click the channel → "Edit Channel" → "Permissions" and make sure your bot's role is allowed to read and send messages there.
- Make sure you're using `!` at the start of the command, with no space.
- Make sure you turned on **Message Content Intent** in Step 4. Without it, the bot literally cannot read what people are typing.

### "I lost my token / I think someone saw it."

Go back to https://discord.com/developers/applications, click your bot, click "Bot", click "Reset Token", and copy the new one. Then paste the new token into your `.env` file. The old one will stop working immediately, so anyone who saw it can't use it anymore.

### "It worked yesterday but doesn't work today."

The most likely cause is your computer went to sleep or you closed the terminal. The bot only runs while the terminal window is open. Open a new terminal, `cd` into your `MyBot` folder, and run `python bot.py` again.

### "Something else is broken."

Read the error message carefully. Search the exact error text on Google. Usually someone else has had the same problem and there's an answer on a website called Stack Overflow.

---

## Keeping your secrets safe

Quick reminder of the rules:

1. **Never share your bot token.** It's in your `.env` file. If you ever upload your bot to the internet (like to GitHub), make sure `.env` is **not** included.
2. **Never share your `credentials.json`** file. Same deal.
3. If you accidentally share either of them, **reset them immediately** (see the troubleshooting section above for the token; for credentials, go back to Step 7 and create a new key).

If you ever upload this bot to GitHub or share the folder with someone, make a file called `.gitignore` in your `MyBot` folder and put this in it:

```
.env
credentials.json
__pycache__/
```

This tells Git to leave your secrets alone.

---

## Things you can change

Once you're comfortable with the basics, you can open `bot.py` in any text editor and change things:

- **The clan and class lists** for `!random` are near the top of the file, in `table32` and `table11`. You can put your own setting's stuff in there.
- **What ranks the weekly auction posts** is the line `AUCTION_DEFAULT_PAIRS = [("E", 2), ("D", 2), ("C", 2)]`. The numbers are how many items per rank.
- **When the weekly auction posts** is the line that says `CronTrigger(day_of_week="wed", hour=12, minute=0)`. Change `wed` to `mon`, `tue`, `thu`, `fri`, `sat`, or `sun`. Change the hour (in 24-hour time) and minute to whatever you want.
- **The columns the bot expects in your sheet** are in the `COLS` dictionary. If you rename or reorder columns, you'll need to update this.

Be careful when editing — Python is picky about indentation (spaces at the start of lines). If something stops working after you edit, undo your change and try again.

---

## Where everything lives

Your `MyBot` folder should look like this when you're done:

```
MyBot/
├── bot.py             ← the bot itself
├── credentials.json   ← Google access (SECRET)
├── .env               ← Discord token + settings (SECRET)
├── .env.example       ← the template (you can delete or keep)
└── README.md          ← this guide
```

That's it! You did it. If you got this far on your own, you should be proud — this is real grown-up programmer stuff. Welcome to the club. 🎉
