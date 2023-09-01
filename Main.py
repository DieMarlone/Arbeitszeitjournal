import configparser
import csv
import datetime
import os.path
from datetime import date
from datetime import datetime
from datetime import timedelta
import os
import time
from Settings import SettingsClass
from UserProfile import UserProfileClass
from datetime import datetime


fieldnames = ['Date', 'Start', 'End', 'Over_hours', 'Pause', 'Extra_minutes']
Settingsfile = "config/settings.ini"
UserProfileFile = "config/userProfile.ini"
today = date.today()
today = today.strftime("%d.%m.%Y")


def createcsv(Settings):

    with open(Settings._dataBase, "w", encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

def readSettings():
    sections = config.sections()
    for section in sections:
        Arbeitszeit = config.get(section, "arbeitszeit")
        JornalAblageort = config.get(section, "datenbank")
        AblageOrtCookie = config.get(section, "printout")
        Arbeitstage = config.get(section, "arbeitstage")
        Arbeitstage = Arbeitstage.split(", ")
        defaultPause = config.get(section, "defaultPause")
    Settings = SettingsClass(Arbeitszeit, Arbeitstage, JornalAblageort, AblageOrtCookie, defaultPause)
    return Settings

def readUserProfile():
    userConfig = configparser.ConfigParser()
    userConfig.read(UserProfileFile)
    sections = userConfig.sections()
    for section in sections:
        firstName = userConfig.get(section, "firstName")
        lastName = userConfig.get(section, "lastName")
        email = userConfig.get(section, "email")
        adress = userConfig.get(section, "adress")
        postalCode = userConfig.get(section, "postalCode")
        telephone = userConfig.get(section, "telephone")
        city = userConfig.get(section, "city")
    UserProfile = UserProfileClass(firstName, lastName, email, adress, postalCode, telephone, city)
    return UserProfile


def calculate_over_hours(weekday, start: str, end: str, pause: str, extra_minutes: int = 0, previous_over_hours: str = "00:00"):
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    pause_time = timedelta(minutes=int(pause))
    extra_time = timedelta(minutes=int(extra_minutes))

    duration = end_time - start_time - pause_time + extra_time
    if weekday not in Settings._workingDays:
        workingTime = 0
    else:
        workingTime = Settings._workingTime
    daily_working_hours = timedelta(hours=workingTime)

    daily_over_hours = duration - daily_working_hours

    # Add previous day's over_hours
    over_hours_parts = previous_over_hours.split(":")
    previous_over_hours_delta = timedelta(hours=int(over_hours_parts[0]), minutes=int(over_hours_parts[1]))
    daily_over_hours += previous_over_hours_delta

    # convert total_over_hours into hours and minutes, handling negative durations as well
    total_minutes = int(daily_over_hours.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    # format hours and minutes with leading zeros
    return f"{hours:02d}:{minutes:02d}"



def today_logging(date):
    date_as_date_objekt = datetime.strptime(date, "%d.%m.%Y")
    Weekday = date_as_date_objekt.strftime('%A')
    # Input is like start = 08:30 end = 18:00
    start = input(f"When did you start on {Weekday} HH:MM: ")
    end = input("When did you stop HH:MM: ")
    
    pause = input(f"How long was your break Minutes(default = {Settings._defaultPause} min): ")
    extra_minutes = input("Did you work extra minutes? Minutes (Default = 0): ")
    if pause == "":
        pause = Settings._defaultPause
    if extra_minutes == "":
        extra_minutes = 0
    else:
        extra_minutes = int(extra_minutes)
    
    database = Settings._dataBase
    if not os.path.isfile(database):
        print("No Database found")
        createcsv(Settings)

    rows = []
    with open(database, 'r', encoding='UTF8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Get the over_hours of the last logged day
    if len(rows) > 1:
        previous_over_hours = rows[-1]['Over_hours']
    else:
        previous_over_hours = "00:00"

    over_hours = calculate_over_hours(Weekday, start, end, pause, extra_minutes, previous_over_hours)
    
    new_row = {
        'Date': date,
        'Start': start,
        'End': end,
        'Over_hours': over_hours,
        'Pause': pause,
        'Extra_minutes': extra_minutes
    }
    
    updatet = False
    # find the row that is already logged for today and update it
    for row in rows:
        if row['Date'] == new_row['Date']:
            print(f"Updating row with date {date} from {row['Start']} to {start} and from {row['End']} to {end}")
            time.sleep(3)
            row.update(new_row)
            updatet = True
            break
    if not updatet:
        rows.append(new_row)
    if rows:
        # Sort rows by Date
        rows.sort(key=lambda row: datetime.strptime(row['Date'], '%d.%m.%Y'))

        fieldnames = ['Date', 'Start', 'End', 'Over_hours', 'Pause', 'Extra_minutes']
        with open(database, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    

#Log extra hours worked on a day
def addExtra(date: str, extra_minutes: int):

    if not os.path.isfile(Settings._dataBase):
        print("No Database found")
        exit(RuntimeError)

    date_as_date_objekt = datetime.strptime(date, "%d.%m.%Y")
    Weekday = date_as_date_objekt.strftime('%A')
    rows = []
    with open(Settings._dataBase, 'r', encoding='UTF8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # find the row with the specified date and update its over_hours and extra_minutes
    for i, row in enumerate(rows):
        if row['Date'] == date:
            row['Extra_minutes'] = extra_minutes
            if i > 0:
                previous_over_hours = rows[i-1]['Over_hours']
            else:
                previous_over_hours = "00:00"
            row['Over_hours'] = calculate_over_hours(Weekday, row['Start'], row['End'], row['Pause'], extra_minutes, previous_over_hours)
            break

    # update over_hours for the following days
    for i in range(rows.index(row) + 1, len(rows)):
        previous_over_hours = rows[i-1]['Over_hours']
        rows[i]['Over_hours'] = calculate_over_hours(Weekday, rows[i]['Start'], rows[i]['End'], rows[i]['Pause'], Settings, int(rows[i]['Extra_minutes']), previous_over_hours)

    fieldnames = ['Date', 'Start', 'End', 'Over_hours', 'Pause', 'Extra_minutes']

    with open(Settings._dataBase, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def recalculate_over_hours():
    
    if not os.path.isfile(Settings._dataBase):
        print("No Database found")
        exit(RuntimeError)

    rows = []
    with open(Settings._dataBase, 'r', encoding='UTF8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Initialize previous_over_hours to 0 for the first day
    previous_over_hours = "00:00"

    # Recalculate over_hours for all days
    for i, row in enumerate(rows):
        date_as_date_objekt = datetime.strptime(row["Date"], "%d.%m.%Y")
        Weekday = date_as_date_objekt.strftime('%A')
        if i > 0:
            previous_over_hours = rows[i-1]['Over_hours']
        row['Over_hours'] = calculate_over_hours(Weekday, row['Start'], row['End'], row['Pause'], int(row['Extra_minutes']), previous_over_hours)

    fieldnames = ['Date', 'Start', 'End', 'Over_hours', 'Pause', 'Extra_minutes']

    with open(Settings._dataBase, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def get_first_date_from_csv(csv_file):
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Überspringen der Kopfzeile
        first_row = next(reader)  # Lesen der ersten Datenzeile
        first_date = first_row[0]  # Das Datum befindet sich in der ersten Spalte
    return first_date


def get_last_date_from_csv(file_path):
    if not os.path.isfile(file_path):
        print("No Database found")
        exit(RuntimeError)

    with open(file_path, 'r', encoding='UTF8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Get the last date
    if len(rows) > 0:
        last_date = rows[-1]['Date']
        return last_date
    else:
        print("CSV file is empty.")
        return None

def get_date_range_from_csv(csv_file):
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Überspringen der Kopfzeile
        dates = [datetime.strptime(row[0], '%d.%m.%Y') for row in reader]  # Datumsliste aus der CSV-Datei
        first_date = min(dates)  # Kleinste Datum ermitteln
        last_date = max(dates)  # Größtes Datum ermitteln
        num_days = (last_date - first_date).days + 1  # Anzahl der Tage berechnen (inklusive des letzten Tages)
    return num_days

def print_logfile(num_days=None, start_date=None):

    if num_days is None:
        num_days = get_date_range_from_csv(Settings._dataBase)
    if start_date is None:
        start_date = get_first_date_from_csv(Settings._dataBase)
    
    start_date = datetime.strptime(start_date, "%d.%m.%Y")


    # Calculate end date and create list of dates to be displayed
    end_date = start_date + timedelta(days=num_days)
    dates_to_display = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    dates_to_display = [(date.strftime('%d.%m.%Y'), date.isocalendar()[1], date.strftime('%A')) for date in dates_to_display]

    # Read data from CSV file and sort by date
    with open(Settings._dataBase, 'r') as file:
        data = csv.reader(file)
        next(data)  # Skip header row
        data = sorted(data, key=lambda row: datetime.strptime(row[0], "%d.%m.%Y"))


    # Prepare the repeated string parts
    delimiter_line = "-"*118
    week_num_old = None
    week_start_date = None

    if not os.path.isfile(Settings._printout):
        os.mkdir("printout")

    # Write selected data to output file
    with open(Settings._printout, "w") as output_file:
        for date_str, week_num, weekday in dates_to_display:
            # If new week, print week header
            if week_num != week_num_old:
                if week_num_old is not None:
                    output_file.write(f"<{delimiter_line}>\n\n")
                    
                output_file.write(f"<-----------------------------------------------------------Week {week_num}---------------------------------------------------->\n")
                week_num_old = week_num

            
            # Find corresponding entry in data
            for day in data:
                if day[0] == date_str:
                    output_file.write(f"|Date: {day[0]}: {weekday:>9} | Start time: {day[1]:>5} to {day[2]:>5} | Total overtime: {day[3]:>5} | Pause: {day[4]:>3} Min | Extra minutes: {day[5]:>3}|\n")
                    break  # Go to next date after finding matching entry

        output_file.write(f"<{delimiter_line}>\n\n")
        last_date = get_last_date_from_csv(Settings._dataBase)
        output_file.write(f"Total overtime: {get_over_hours_for_date(last_date, Settings)}\n")
    print("Logfile has been printed.")
def create_graph(num_days=None, start_date=None):
    import matplotlib.pyplot as plt
    import csv
    from datetime import datetime, timedelta

    if num_days is None:
        num_days = get_date_range_from_csv(Settings._dataBase)
    if start_date is None:
        start_date = get_first_date_from_csv(Settings._dataBase)
    start_date = datetime.strptime(start_date, "%d.%m.%Y")
    
    # Calculate end date and create list of dates to be displayed
    end_date = start_date + timedelta(days=num_days)
    dates_to_display = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    dates_to_display = [(date.strftime('%d.%m.%Y'), date.isocalendar()[1], date.strftime('%A')) for date in dates_to_display]

    # Read data from CSV file and sort by date
    with open(Settings._dataBase, 'r') as file:
        data = csv.reader(file)
        next(data)  # Skip header row
        data = sorted(data, key=lambda row: datetime.strptime(row[0], "%d.%m.%Y"))
        x = []
        y = []
        counter = 0
        for row in data:
            time_str = row[3]
            time_float = 0.0
            if time_str != '-':
                if time_str.startswith('-'):
                    time_str = time_str[1:]  # Remove the leading '-' character
                    negative_sign = -1  # Set negative sign for negative hours
                else:
                    negative_sign = 1

                hours, minutes = time_str.split(':')
                time_float = float(hours) + float(minutes[:-1]) / 60.0
                time_float *= negative_sign

            x.append(counter)
            y.append(time_float)
            counter += 1
        plt.plot(x, y)
        plt.xlabel('Date')
        plt.ylabel('Over Hours')
        plt.title('Over Hours over Time')
        plt.savefig('graph.png')


    
def get_over_hours_for_date(date: str, Settings: SettingsClass):
    # Convert date to datetime object for comparison
    date_object = datetime.strptime(date, "%d.%m.%Y")

    over_hours_for_date = None
    with open(Settings._dataBase, 'r') as file:
            database = csv.DictReader(file)
            for row in database:
                row_date = datetime.strptime(row['Date'], "%d.%m.%Y")
                if row_date == date_object:
                    over_hours_for_date = row['Over_hours']
                    break
    if over_hours_for_date is None:
        print("No entry found for this date please book your working time.")

    return over_hours_for_date


def setSetting():
    Arbeitszeit = input("Working hours per day: ")
    Arbeitstage = input("On which days you work in a week (Monday, Tuesday, Wednesday,...) Default Mon-Fri: ")
    if Arbeitstage == "":
        Arbeitstage = "Monday, Tuesday, Wednesday, Thursday, Friday"
    else:
        Arbeitstage = Arbeitstage.split(", ")
    
    defaultPause = input("Default pause in minutes: ")
    database = "config/Database.csv"
    printout = input("What should your digital work time journal be named (Default Journal.txt): ")

    
    # Check if printout ends with .txt
    if printout == "":
        printout = "Journal.txt"
    elif printout[-4:] != ".txt":
        printout = printout + ".txt"
    printout = f"printout/{printout}"
    
    Settings = SettingsClass(Arbeitszeit, Arbeitstage, database, printout, defaultPause)
    Settings.createSettingsfile()
    return Settings

def createUserProfile():
    firstName = input("First name: ")
    lastName = input("Last name: ")

    email = input("Email: ")
    while "@" not in email:
        print("Please enter a valid email address\n")
        email = input("Email: ")
    
    adress = input("Adress: ")
    postalCode = input("Postal code: ")
    telephone = input("Telephone: ")
    city = input("City: ")

    UserProfile: UserProfileClass = UserProfileClass(firstName, lastName, email, adress, postalCode, telephone, city)
    UserProfile.createProfile()
    return UserProfile

def createPDF():
    import PyPDF2
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    pdfFileName = "Worktime_journal.pdf"
    doc = SimpleDocTemplate(pdfFileName, pagesize=letter)
    story = []

    # Füge Benutzerdaten zum Story-Container hinzu
    styles = getSampleStyleSheet()
    Name = f"""{userProfile.firstName} {userProfile.lastName}"""
    Adresse = f"""{userProfile.adress}"""
    PostalCode = userProfile.postalCode + " " + userProfile.city
    Tel = f"Tel: {userProfile.telephone}"
    Mail = f"Mail: {userProfile.email}\n\n"

    story.append(Paragraph("Work Time List", styles["Title"]))
    story.append(Paragraph(Name, styles["Normal"]))
    story.append(Paragraph(Adresse, styles["Normal"]))
    story.append(Paragraph(PostalCode, styles["Normal"]))
    story.append(Paragraph(Tel, styles["Normal"]))
    story.append(Paragraph(Mail, styles["Normal"]))
    story.append(Paragraph(" ", styles["Normal"]))

    data = [fieldnames]  # Überschrift hinzufügen
    
    # Read data from CSV file and sort by date
    with open(Settings._dataBase, 'r') as file:
        readData = csv.reader(file)
        next(readData)  # Skip header row
        readData = sorted(readData, key=lambda row: datetime.strptime(row[0], "%d.%m.%Y"))
   
        data.extend(readData)  # Arbeitszeitdaten hinzufügen
    
    table = Table(data, colWidths=[100, 100, 100, 100, 50, 100])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    story.append(table)

    # Erstelle das PDF-Dokument mit dem Inhalt aus dem Story-Container
    doc.build(story)

    print(f"Das Arbeitszeitjournal wurde als '{pdfFileName}' gespeichert.")


config = configparser.ConfigParser()
config.read(Settingsfile)
Settings = None
while True:
    if not os.path.isfile(Settingsfile) or not os.path.isfile(UserProfileFile):
        print("""
        1.Set Settings and create a user Profile
        2.Exit/Quit
        """)
        Option = input("What would you like to do? ")
        
        if Option == "1":
            Settings: SettingsClass = setSetting()
            userProfile: UserProfileClass = createUserProfile()
        elif Option == "2":
            exit(1)
        else:
            print("wrong input try again")
    else:
        userProfile: UserProfileClass = readUserProfile()
        if not Settings:
            Settings: SettingsClass = readSettings()
        if os.path.isfile(Settings._dataBase):
            recalculate_over_hours()
        
        print("""
        1.Change Settings
        2.Log today
        3.Log extra time
        4.Log a hole week
        5.Print the log in a file for spezific dates
        6.Print all logged data in the log
        7.Log a specific day
        8.Print over hours left
        9.Print over hours for a specific date
        10.Exit/Quit
        11.Create a graph
        12.Create a user Profile for a personalises work time
        13.Create a PDF	
        """)
        Option = input("What would you like to do? ")
        if Option == "1":
            setSetting()
        elif Option == "2":
            date = today
            today_logging(date)
        elif Option == "3":
            date = input("Welches Datum soll ergänzt werden? DD.MM.YYYY: ")
            extra_minutes = int(input("Wie viele Minuten sollen ergänzt werden? "))
            addExtra(date, extra_minutes)
        elif Option == "4":
            date_str = input("Which Week? (Automatically the first working day of the week will be selected) DD.MM.YYYY: ")
            date = datetime.strptime(date_str, "%d.%m.%Y")
            
            # Ermittle den Wochentag als Zahl (Montag = 0, Dienstag = 1, Mittwoch = 2, ...)
            weekday = date.weekday()
            
            # Berechne die Anzahl der Tage, um zum ersten Arbeitstag zurückzugehen
            days_to_subtract = (weekday) % len(Settings._workingDays)
            
            # Gehe entsprechend viele Tage zurück, um den ersten Arbeitstag zu erhalten
            date -= timedelta(days=days_to_subtract)
            
            # Logging für jeden Arbeitstag der Woche durchführen

            for i in range(len(Settings.workingDays)):
                date_str = date.strftime("%d.%m.%Y")
                today_logging(date_str)
                date += timedelta(days=1)
        elif Option == "5":
            start_date = input("Starting date (DD.MM.YYYY): ")

            num_days = int(input("How many consecutive days should be displayed? "))
            print_logfile(num_days, start_date)
        elif Option == "6":
            print_logfile()
        elif Option == "7":
            date = input("Welches Datum soll gellogt werden? DD.MM.YYYY: ")
            today_logging(date)
        elif Option == "8":
            date = get_last_date_from_csv(Settings._dataBase)
            over_hours_for_date = get_over_hours_for_date(date, Settings)
            print(f"Over hours for {date}: {over_hours_for_date}")
            time.sleep(5)
            
        elif Option == "9":
            date = input("Welches Datum soll ausgegeben werden? DD.MM.YYYY: ")
            over_hours_for_date = get_over_hours_for_date(date, Settings)
            if over_hours_for_date is not None:
                print(f"Over hours for {date}: {over_hours_for_date}")
            time.sleep(5)

        elif Option == "10":
            exit(1)
        elif Option == "11":
            create_graph()
        elif Option == "12":
            userProfile = createUserProfile()
        elif Option == "13":
            createPDF()
       # elif Option == "14":
       #     dateToBeLogged = input("Which date should be logged? DD.MM.YYYY (Default Todday): ")
       #     if dateToBeLogged == '':
       #         dateToBeLogged = today
       #     oldSetting = Settings.workingTime
       #     
       #     workingHours = input("Changed Working Hours: ")
       #     Settings.workingTime = int(workingHours)
       #
       #     today_logging(dateToBeLogged)
       #     Settings.workingTime = oldSetting
        else:
            print("wrong input try again")
            time.sleep(10)




#todo halbtagsarbeit muss auch möglich sein