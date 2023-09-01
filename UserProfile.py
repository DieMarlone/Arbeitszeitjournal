import configparser


class UserProfileClass:
    def __init__(self, firstName: str, lastName: str, email: str, adress: str, postalCode: str, telephone: str, city: str):
        self._firstName = firstName
        self._lastName = lastName
        self._email = email
        self._adress = adress
        self._postalCode = postalCode
        self._telephone = telephone
        self._city = city
        self.userProfile = "config/userProfile.ini"


    @property
    def firstName(self):
        return self._firstName
    
    @firstName.setter
    def firstName(self, value):
        self._firstName = value
    
    @property
    def lastName(self):
        return self._lastName
    
    @lastName.setter
    def lastName(self, value):
        self._lastName = value

    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        self._email = value
    
    @property
    def adress(self):
        return self._adress
    
    @adress.setter
    def adress(self, value):
        self._adress = value
    
    @property
    def postalCode(self):
        return self._postalCode
    
    @postalCode.setter
    def postalCode(self, value):
        self._postalCode = value
    
    @property
    def telephone(self):
        return self._telephone
    
    @telephone.setter
    def telephone(self, value):
        self._telephone = value
    
    @property
    def city(self):
        return self._city
    
    @city.setter
    def city(self, value):
        self._city = value

    def createProfile(self):
        config = configparser.ConfigParser()
        config['USERPROFILE'] = {'firstName': self._firstName,
                                 'lastName': self._lastName,
                                 'email': self._email,
                                 'adress': self._adress,
                                 'postalCode': self._postalCode,
                                 'telephone': self._telephone,
                                 'city': self._city}
        with open(self.userProfile, 'w') as configfile:
            config.write(configfile)
            configfile.close()


    def readProfile(self):
        config = configparser.ConfigParser()
        config.read(self.userProfile)
        return config['USERPROFILE']