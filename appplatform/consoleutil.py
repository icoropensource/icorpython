# -*- coding: utf-8 -*-
import sys
import msvcrt
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)


class KeyCode(object):

    def __init__(self, key='', name='', code=-1):
        self.key = key
        self.name = name
        self.code = code

    def __repr__(self):
        return '<%s>(%s)[%d]' % (self.key, self.name, self.code)


class ConsoleUtil(object):

    def __init__(self):
        self.lines = []
        self.prompt = ' '

    def PrintWarning(self, *args):
        print Back.WHITE + Fore.RED + Style.BRIGHT + ' '.join(args)

    def PrintInfo(self, *args):
        print Back.BLUE + Fore.YELLOW + Style.BRIGHT + ' '.join(args)

    def PrintError(self, *args):
        print Back.RED + Fore.YELLOW + Style.BRIGHT + ' '.join(args)

    def PrintHelp(self, *args):
        print Back.BLACK + Fore.GREEN + Style.BRIGHT + ' '.join(args)

    def PrintText(self, *args):
        print Fore.YELLOW + Style.BRIGHT + ' '.join(args)

    def GetKeyCode(self):
        key = msvcrt.getch()
        code = ord(key)
        if key == '\x03':    # Ctrl C
            return KeyCode(name='CTRL+C')
        elif key == '\x1c':    # Ctrl \
            return KeyCode(name='EXIT')
        elif key in ['\xe0', '\x00']:
            key = msvcrt.getch()
            code = ord(key)
            if key == 'H':
                return KeyCode(key=key, name='KEY_UP', code=code)
            elif key == 'K':
                return KeyCode(key=key, name='KEY_LEFT', code=code)
            elif key == 'P':
                return KeyCode(key=key, name='KEY_DOWN', code=code)
            elif key == 'M':
                return KeyCode(key=key, name='KEY_RIGHT', code=code)
            elif key == 'R':
                return KeyCode(key=key, name='KEY_INSERT', code=code)
            elif key == 'S':
                return KeyCode(key=key, name='KEY_DELETE', code=code)
            elif key == 'G':
                return KeyCode(key=key, name='KEY_HOME', code=code)
            elif key == 'O':
                return KeyCode(key=key, name='KEY_END', code=code)
            elif key == 'I':
                return KeyCode(key=key, name='KEY_PAGEUP', code=code)
            elif key == 'Q':
                return KeyCode(key=key, name='KEY_PAGEDOWN', code=code)
            elif (code >= 59) and (code <= 68):
                return KeyCode(key=key, name='F%d' % (code - 58, ), code=code)
            elif code == 133:
                return KeyCode(key=key, name='F11', code=code)
            elif code == 134:
                return KeyCode(key=key, name='F12', code=code)
        if key == '\x1b':
            return KeyCode(key=key, name='KEY_ESCAPE', code=code)
        elif key == '\x0d':
            return KeyCode(key=key, name='KEY_ENTER', code=code)
        elif key == '\x08':
            return KeyCode(key=key, name='KEY_BACKSPACE', code=code)
        elif key == '\x09':
            return KeyCode(key=key, name='KEY_TAB', code=code)
        return KeyCode(key=key, code=code)

    def ClearLine(self):
        alen = len(self.lines[self.current_line])
        print '%s \r' % (' ' * (alen + len(self.prompt) + 4 + 2), ),

    def Prompt(self, acursor=1):
        aline = self.lines[self.current_line]
        scursor = ''
        if acursor:
            scursor = Back.WHITE + Fore.YELLOW + Style.BRIGHT + '|' + Back.BLACK + Fore.YELLOW + Style.BRIGHT
        print Back.BLACK + Fore.GREEN + Style.BRIGHT + self.prompt + '<%02d>' % self.current_line + Back.BLACK + Fore.YELLOW + Style.BRIGHT + aline[:self.cursor_position] + scursor + aline[self.cursor_position:] + ' \r',

    def Input(self, aline='', atext=''):
        if atext:
            print Back.BLACK + Fore.GREEN + Style.BRIGHT + atext
        self.lines = [x for x in self.lines if x]
        self.lines.append(aline)
        self.current_line = len(self.lines) - 1
        self.cursor_position = len(self.lines[self.current_line])
        while 1:
            self.Prompt()
            aline = self.lines[self.current_line]
            alen = len(aline)
            akey = self.GetKeyCode()
            if akey.name == 'KEY_ENTER':
                self.Prompt(acursor=0)
                aline = self.lines.pop(self.current_line)
                self.lines.append(aline)
                print
                return aline
            if akey.name in ['CTRL+C', 'EXIT', 'KEY_ESCAPE']:
                self.Prompt(acursor=0)
                print
                return None
            if akey.name == 'KEY_LEFT':
                self.cursor_position = max(self.cursor_position - 1, 0)
            elif akey.name == 'KEY_RIGHT':
                self.cursor_position = min(self.cursor_position + 1, alen)
            elif akey.name in ['KEY_UP', 'KEY_PAGEUP']:
                self.ClearLine()
                self.current_line = max(self.current_line - 1, 0)
                self.cursor_position = len(self.lines[self.current_line])
            elif akey.name in ['KEY_DOWN', 'KEY_PAGEDOWN']:
                self.ClearLine()
                self.current_line = min(self.current_line + 1, len(self.lines) - 1)
                self.cursor_position = len(self.lines[self.current_line])
            elif akey.name == 'KEY_HOME':
                self.cursor_position = 0
            elif akey.name == 'KEY_END':
                self.cursor_position = len(aline)
            elif akey.name == 'KEY_BACKSPACE':
                if self.cursor_position > 0:
                    self.lines[self.current_line] = aline[:self.cursor_position - 1] + aline[self.cursor_position:]
                    self.cursor_position = self.cursor_position - 1
            elif akey.name == 'KEY_DELETE':
                self.lines[self.current_line] = aline[:self.cursor_position] + aline[self.cursor_position + 1:]
            elif akey.key and not akey.name:
                self.lines[self.current_line] = aline[:self.cursor_position] + akey.key + aline[self.cursor_position:]
                self.cursor_position = self.cursor_position + 1
