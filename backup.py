#! /usr/bin/env python3
# pylint: disable=C0103
# pylint: disable=C0301

import os
import re
import time
import psutil
import shutil
import datetime

class Backup():
    """Generates backups"""
    def __init__(self):
        self.location = os.path.expanduser('~\\Documents\\Paradox Interactive\\')    # Location of the Paradox Interactive folder
        self.backupLocation = self.location + 'Ironman Backup\\'                     # Location of backup folder --TODO: Make customizable.
        self.euSuffix = '_Backup'                                                    # To ignore _Backup eu4 files
        self.hoiTemp = '_temp'                                                       # To ignore _temp hoi4 files

        print('Defaulted to working in directory ' + self.location)
        print('If this is not desired, set a working directory in the File menu before pressing start.')

    def startup(self, dir=''):
        """Finds game to be saved."""
        message = ''
        game = self.currentGame()

        """Sets custom working directory."""
        if dir != '':
            self.location = dir
            self.backupLocation = self.location + 'Ironman Backup\\'
            print('Working in directory ' + self.location)
            message += 'Working in directory ' + self.location + '\n'

        if not os.path.isdir(self.backupLocation + '\\' + game):
            print('Making ' + self.backupLocation + game)
            message += 'Making ' + self.backupLocation + game + '\n'
            os.makedirs(self.backupLocation + '\\' + game)

        if game == 'Stellaris':
            message += self.stellarisSave()
        elif os.path.exists(self.location + game + '\\save games'):
            message += self.genSave(game)
        else:
            message = 'Please launch a supported game!'
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
            # l = os.listdir(self.backupLocation+game)
            rundict = {}
            for folder in os.listdir(self.backupLocation+game):
                rundict[folder] = os.path.getmtime(self.backupLocation+game+'/'+folder)
            print(rundict.items())
            l = list(reversed(sorted(rundict, key=rundict.get)))
            if game.__contains__("/") or game.__contains__("\\"):
                print("Run is " + game)
                return list(reversed(sorted(l)))
            else:
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
        """Find which game is currently running."""
         # According to psutils docs, this is a preferable method.
        try:
            iter = psutil.process_iter()
            for proc in iter:
                try:
                    if proc.name() == 'stellaris.exe':
                        return "Stellaris"
                    elif proc.name() == 'eu4.exe':
                        return 'Europa Universalis IV'
                    elif proc.name() == 'ck3.exe':
                        return 'Crusader Kings III'
                    elif proc.name() == 'CK2game.exe':
                        return 'Crusader Kings II'
                    elif proc.name() == 'hoi4.exe':
                        return 'Hearts of Iron IV'
                    elif proc.name() == 'imperator.exe':
                        return 'Imperator'
                    elif proc.name() == 'victoria2.exe' or proc.name() == 'v2game.exe':
                        return 'Victoria II'
                    continue
                except psutil.AccessDenied as e:
                    print('Access denied to process (PID={}), skipping...'.format(e.pid))
                    next(iter)
                    continue

            # Occurs once all processes have been checked (i.e. after "except StopIteration:")
            print('All processes checked, no supported game found...')
            print('Please launch a supported game!')
            return ''
        except:
            print('Unspecified issue detecting the current game, trying again.')
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
        elif game == 'Crusader Kings III':
            return '.ck3'
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
