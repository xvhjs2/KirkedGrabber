import colorama
import threading

from pystyle import *
from datetime import datetime
from colorama import *

lock = threading.Lock()

class Ascii:
    def __init__(self):
        self.banner = None

    def _ascii(self):
        return '''

  █████▒██▀███  ▓█████ ▓█████ ▓█████▄  ▒█████   ███▄ ▄███▓
▓██   ▒▓██ ▒ ██▒▓█   ▀ ▓█   ▀ ▒██▀ ██▌▒██▒  ██▒▓██▒▀█▀ ██▒
▒████ ░▓██ ░▄█ ▒▒███   ▒███   ░██   █▌▒██░  ██▒▓██    ▓██░
░▓█▒  ░▒██▀▀█▄  ▒▓█  ▄ ▒▓█  ▄ ░▓█▄   ▌▒██   ██░▒██    ▒██ 
░▒█░   ░██▓ ▒██▒░▒████▒░▒████▒░▒████▓ ░ ████▓▒░▒██▒   ░██▒
 ▒ ░   ░ ▒▓ ░▒▓░░░ ▒░ ░░░ ▒░ ░ ▒▒▓  ▒ ░ ▒░▒░▒░ ░ ▒░   ░  ░
 ░       ░▒ ░ ▒░ ░ ░  ░ ░ ░  ░ ░ ▒  ▒   ░ ▒ ▒░ ░  ░      ░
 ░ ░     ░░   ░    ░      ░    ░ ░  ░ ░ ░ ░ ▒  ░      ░   
          ░        ░  ░   ░  ░   ░        ░ ░         ░   
                               ░                          
'''

    def ascii(self):
        asc = self._ascii()
        self.banner = Colorate.Horizontal(Colors.blue_to_red, asc, 1)
        return self.banner
    def ascii2(self, text):
        asc = self._ascii() + '\t' + text
        self.banner = Colorate.Horizontal(Colors.blue_to_red, asc, 1)
        return self.banner


class Logging:
    def inp(action, msg):
        mg = f'''\n┏━[kirkedgrabber@{action}] [{msg}]
┃
┃
┗━[xvhjs2@kirkedgrabber]──$  '''
        lock.acquire()
        inp = input(Colorate.Horizontal(Colors.blue_to_red, mg, 1))
        lock.release()
        return inp
    
    def inp2(msg):
        lock.acquire()
        inp = input(Colorate.Horizontal(Colors.blue_to_red, 'xvhjs2@kirkedgrabber >', 1) + " " + Fore.BLUE + 'INPUT ' + Colorate.Horizontal(Colors.blue_to_red, msg, 1))
        lock.release()
        return inp
    
    def success(msg):
        now = datetime.now()
        d = now.strftime('%H:%M:%S')

        lock.acquire()
        print(Colorate.Horizontal(Colors.blue_to_red, f'{d} >', 1) + " " + Fore.GREEN + 'SUCCESS ' + Colorate.Horizontal(Colors.blue_to_red, msg, 1))

        lock.release()
        return msg
    
    def fail(msg):
        now = datetime.now()
        d = now.strftime('%H:%M:%S')

        lock.acquire()
        print(Colorate.Horizontal(Colors.blue_to_red, f'{d} >', 1) + " " + Fore.RED + 'FAILED ' + Colorate.Horizontal(Colors.blue_to_red, msg, 1))
        lock.release()
        return msg
        
    def info(msg):
        now = datetime.now()
        d = now.strftime('%H:%M:%S')
        
        lock.acquire()
        print(Colorate.Horizontal(Colors.blue_to_red, f'{d} >', 1) + " " + Fore.YELLOW + 'INFO ' + Colorate.Horizontal(Colors.blue_to_red, msg, 1))
        lock.release()
        return msg
    

    
class Options:
    def options(self):
        self.opt = '''
        [01] Set C2
        [02] Toggle Browsing Data
        [03] Toggle Discord Account Grabber
        [04] Toggle Game Session Grabber
        [05] Toggle Webcam Grabber
        [06] Block Anti-Virus Websites
        [07] Toggle Anti-VM
        [08] Toggle UAC Bypass
        [09] Save Settings
        [10] Compile
        '''
        self.opti = Colorate.Horizontal(Colors.blue_to_purple, self.opt, 1)
        return self.opti

