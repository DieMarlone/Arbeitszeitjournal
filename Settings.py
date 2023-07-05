import configparser
import os


class SettingsClass:


    def __init__(self, workingTime: int, workingDays: list, dataBase: str, printout: str, defaultPause: str):
        self._workingTime = int(workingTime)
        self._workingDays = workingDays
        self._dataBase = dataBase
        self._printout = printout
        self._defaultPause = defaultPause
        self.Settingsfile = "config/settings.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.Settingsfile)

    @property
    def workingTime(self):
        return self._workingTime

    @workingTime.setter
    def workingTime(self, value):
        self._workingTime = value

    @property
    def workingDays(self):
        return self._workingDays

    @workingDays.setter
    def workingDays(self, value):
        self._workingDays = value

    @property
    def dataBase(self):
        return self._dataBase

    @dataBase.setter
    def dataBase(self, value):
        self._dataBase = value

    @property
    def printout(self):
        return self._printout

    @printout.setter
    def printout(self, value):
        self._printout = value

    def reconfigureSettings(self):
        self.config.set("PARAMETERS", "Arbeitszeit", self.workingTime)
        self.config.set("PARAMETERS", "Datenbank", self.dataBase)
        self.config.set("PARAMETERS", "printout", self.printout)
        self.config.set("PARAMETERS", "Arbeitstage", self.workingDays)
        self.config.set("PARAMETERS", "defaultPause", self._defaultPause)
        with open(self.Settingsfile, 'w') as configfile:
            self.config.write(configfile)
            configfile.close()
            
    def createSettingsfile(self):
        self.config['PARAMETERS'] = {'Arbeitszeit': self.workingTime,
                                     'Datenbank': self.dataBase,
                                     'printout': self.printout,
                                     'Arbeitstage': self.workingDays,
                                     'defaultPause': self._defaultPause}
        
        # Erstelle das Verzeichnis, falls es nicht existiert
        os.makedirs(os.path.dirname(self.Settingsfile), exist_ok=True)
        with open(self.Settingsfile, 'w') as configfile:
            self.config.write(configfile)
            configfile.close()