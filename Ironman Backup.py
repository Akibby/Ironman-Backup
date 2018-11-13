#! python3

import os, shutil, datetime, re, schedule, time, psutil

location = os.path.expanduser('~\\Documents\\Paradox Interactive\\')    # Location of the Paradox Interactive folder
backupLocation = location + 'Ironman Backup\\'                          # Location of backup folder
euSuffix = '_Backup'                                                    # To ignore _Backup eu4 files
hoiTemp = '_temp'                                                       # To ignore _temp hoi4 files
timer = 5                                                               # Enter interval to save in MINUTES
ext = ''                                                                # Initialize variable for extensions

print('Working in directory ' + location)

# Finds game to be saved
def startup():
    game = currentGame()

    if not os.path.isdir(backupLocation+'\\'+game):
        print('making '+backupLocation+game)
        os.makedirs(backupLocation+'\\'+game)

    if game == 'Stellaris':
        stellarisSave()
    elif os.path.exists(location + game + '\\save games'):
        genSave(game)

# Generic save
def genSave(game):
    file = findNew(game)
    ext = getEXT(game)
    file = rmEXT(file, ext)
    if not file.endswith(euSuffix) and not file.endswith(hoiTemp) and ext != '': 
        if not os.path.exists(backupLocation+game+'\\'+file):
            print('making ' + backupLocation+game+'\\'+file)
            os.makedirs(backupLocation+game+'\\'+file)
        shutil.copy(location+game+'\\save games\\'+file+ext,
                    backupLocation+game+'\\'+file+'\\'+file+'-'+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%y %H%M%S')+ext)
        print(file+ext+' copied at ' +
              datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'))

# Save for Stellaris
def stellarisSave():
    folder = findNew('Stellaris')
    if os.path.exists(location+'Stellaris\\save games\\'+folder+'\\ironman.sav'):
        if not os.path.isdir(backupLocation+'Stellaris\\'+folder):
            print('making ' + backupLocation+'Stellaris\\'+folder)
            os.makedirs(backupLocation+'Stellaris\\'+folder)
        shutil.copy(location+'Stellaris\\save games\\'+folder+'\\ironman.sav',
                    backupLocation+'Stellaris\\'+folder+'\\ironman-'+datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%y-%H%M%S') + '.sav')
        print('ironman.sav copied at ' +
              datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'))

# Find what game is currently running
def currentGame():
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
            elif p.name() == 'victoria2.exe' or p.name() == 'v2game.exe':
                return 'Victoria II'
        print('Please launch a game!')
        return ''
    except:
        print('Issue detecting the game, trying again.')
        return currentGame()

# Find most recently updated file
def findNew(game):
    i = 0
    latestUpdateIndex = 0
    latestUpdate = 0.1
    saves = os.listdir(location+game+'\\save games')
    while i < len(saves):
        if not os.path.isdir(location+game+'\\save games\\'+saves[i]):
            update = os.path.getmtime(location+game+'\\save games\\'+saves[i])
            if update > latestUpdate:
                latestUpdate = update
                latestUpdateIndex = i
        i = i + 1
    return saves[latestUpdateIndex]

# Grab return extension
def getEXT(game):
    if game == 'Europa Universalis IV':
        return '.eu4'
    elif game == 'Crusader Kings II':
        return '.ck2'
    elif game == 'Hearts of Iron IV':
        return '.hoi4'
    elif game == 'Victoria II':
        return '.v2'
    else:
        print("I haven't played this game before!")
        return ''

# Remove file extension
def rmEXT(file, ext):
    cut = re.compile(r'(.*)' + ext)
    snip = cut.search(file)
    return snip.group(1)


# Job scheduler
startup()
schedule.every(timer).minutes.do(startup)
while True:
    schedule.run_pending()
    time.sleep(1)
