#! /usr/bin/env python3
# pylint: disable=C0103
# pylint: disable=C0301

import os
import shutil
import datetime
import re
import psutil

class Backup():
    """Generates backups"""

    def __init__(self):
        self.location = os.path.expanduser('~\\Documents\\Paradox Interactive\\')    # Location of the Paradox Interactive folder
        self.backupLocation = self.location + 'Ironman Backup\\'                     # Location of backup folder
        self.euSuffix = '_Backup'                                                    # To ignore _Backup eu4 files
        self.hoiTemp = '_temp'                                                       # To ignore _temp hoi4 files

        print('Working in directory ' + self.location)

    def startup(self):
        """Finds game to be saved"""
        message = ''
        game = self.currentGame()

        if not os.path.isdir(self.backupLocation+'\\'+game):
            print('making '+self.backupLocation+game)
            os.makedirs(self.backupLocation+'\\'+game)
            message += 'making '+self.backupLocation+game+'\n'

        if game == 'Stellaris':
            message += self.stellarisSave()
        elif os.path.exists(self.location + game + '\\save games'):
            message += self.genSave(game)
        else:
            message += 'Please launch a game!'
        return message

    def genSave(self, game):
        """Generic save"""
        message = ''
        file = self.findNew(game)
        ext = self.getEXT(game)
        file = self.rmEXT(file, ext)
        if not file.endswith(self.euSuffix) and not file.endswith(self.hoiTemp) and ext != '':
            if not os.path.exists(self.backupLocation+game+'\\'+file):
                print('making ' + self.backupLocation+game+'\\'+file)
                message += 'making ' + self.backupLocation+game+'\\'+file+'\n'
                os.makedirs(self.backupLocation+game+'\\'+file)
            shutil.copy(self.location+game+'\\save games\\'+file+ext,
                        self.backupLocation+game+'\\'+file+'\\'+file+'-'+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%y %H%M%S')+ext)
            print(file+ext+' copied at ' +
                  datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'))
            message += file+ext+' copied at '+datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        return message

    def stellarisSave(self):
        """Save for Stellaris"""
        message = ''
        folder = self.findNew('Stellaris')
        if os.path.exists(self.location+'Stellaris\\save games\\'+folder+'\\ironman.sav'):
            if not os.path.isdir(self.backupLocation+'Stellaris\\'+folder):
                print('making ' + self.backupLocation+'Stellaris\\'+folder)
                message += 'making ' + self.backupLocation+'Stellaris\\'+folder
                os.makedirs(self.backupLocation+'Stellaris\\'+folder)
            shutil.copy(self.location+'Stellaris\\save games\\'+folder+'\\ironman.sav',
                        self.backupLocation+'Stellaris\\'+folder+'\\ironman-'+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%y %H%M%S') + '.sav')
            print('ironman.sav copied at ' +
                  datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'))
            message += 'ironman.sav copied at '+datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        return message

    def loadList(self, game):
        """Return a list of all files/folders in a location"""
        if game != '':
            i = 0
            l = os.listdir(self.backupLocation+game)
            while i < len(l):
                index = i
                update = os.path.getmtime(self.backupLocation+game+'\\'+l[i])
                j = index + 1
                while j < len(l):
                    updateComp = os.path.getmtime(self.backupLocation+game+'\\'+l[j])
                    if update < updateComp:
                        index = j
                    j += 1
                moving = l[index]
                l[index] = l[i]
                l[i] = moving
                i += 1
            return l
        else:
            l = os.listdir(self.backupLocation+game)
            return sorted(l)

    def genLoad(self, game, folder, filename):
        """Generic load"""
        cut = re.sub(r'-\d\d-\d\d-\d\d\s\d{6}', '', filename)
        shutil.copy(self.backupLocation+game+'\\'+folder+'\\'+filename,
                    self.location+game+'\\save games\\'+cut)

    def stellarisLoad(self, game, folder, filename):
        """Stellaris load"""
        cut = re.sub(r'-\d\d-\d\d-\d\d\s\d{6}', '', filename)
        shutil.copy(self.backupLocation+game+'\\'+folder+'\\'+filename,
                    self.location+game+'\\save games\\'+folder+'\\'+cut)

    def currentGame(self):
        """Find what game is currently running"""
        try:
            for pid in psutil.pids():
                p = psutil.Process(pid)
                if p.name() == 'stellaris.exe':
                    return "Stellaris"
                elif p.name() == 'eu4.exe':
                    return 'Europa Universalis IV'
                elif p.name() == 'CK2game.exe':
                    return 'Crusader Kings II'
                elif p.name() == 'hoi4.exe':
                    return 'Hearts of Iron IV'
                elif p.name() == 'imperator.exe':
                    return 'Imperator'
                elif p.name() == 'victoria2.exe' or p.name() == 'v2game.exe':
                    return 'Victoria II'
            print('Please launch a game!')
            return ''
        except:
            print('Issue detecting the game, trying again.')
            return self.currentGame()

    def findNew(self, game):
        """Find most recently updated file"""
        i = 0
        latestUpdateIndex = 0
        latestUpdate = 0.1
        saves = os.listdir(self.location+game+'\\save games')
        while i < len(saves):
            if not os.path.isdir(self.location+game+'\\save games\\'+saves[i]) or game == 'Stellaris':
                update = os.path.getmtime(self.location+game+'\\save games\\'+saves[i])
                if update > latestUpdate:
                    latestUpdate = update
                    latestUpdateIndex = i
            i += 1
        return saves[latestUpdateIndex]

    def getEXT(self, game):
        """Grab return extension"""
        if game == 'Europa Universalis IV':
            return '.eu4'
        elif game == 'Crusader Kings II':
            return '.ck2'
        elif game == 'Hearts of Iron IV':
            return '.hoi4'
        elif game == 'Imperator':
            return '.rome'
        elif game == 'Victoria II':
            return '.v2'
        else:
            print("I haven't played this game before!")
            return ''

    def rmEXT(self, file, ext):
        """Remove file extension"""
        cut = re.compile(r'(.*)' + ext)
        snip = cut.search(file)
        return snip.group(1)

if __name__ == "__main__":
    backup = Backup()
    backup.startup()
