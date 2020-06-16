import sqlite3
import os.path

#Datenbank mit den Tabellen erstellen wenn noch nicht vorhaden
def createDatabaseAndTable():
    if not os.path.exists('noten.db'):
        #Wenn Datenbank "noten.db" nicht vorhanden ist erstellen und Tabelle Note und Modul hinzufügen
        connection=sqlite3.connect('noten.db')
        cursor=connection.cursor()
        cursor.execute('''CREATE TABLE Modul (ModulID INTEGER PRIMARY KEY AUTOINCREMENT,ModulName TEXT)''')
        cursor.execute('''CREATE TABLE Note (Note DOUBLE,ModulID INTEGER,FOREIGN KEY (ModulID) REFERENCES Modul(ModulID))''')
        connection.close()
    else:
        #Wenn Datenbank existiert überprüfen ob Tabelle Note und Modul schon vorhanden sind
        connection=sqlite3.connect('noten.db')
        c=connection.cursor()
        #Befehl auf der Datenbank ausführen
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Modul' ''')

        #Wenn count vom SELECT-Statement 0 ist, Tabelle Modul erstellen
        if c.fetchone()[0]==0 : {
            #Befehl auf der Datenbank ausführen
            c.execute('''CREATE TABLE Modul (ModulID INTEGER PRIMARY KEY AUTOINCREMENT,ModulName TEXT)''')
        }

        #Befehl auf der Datenbank ausführen
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Note' ''')

        #Wenn count vom SELECT-Statement 0 ist, Tabelle Note erstellen
        if c.fetchone()[0]==0 : {
            #Befehl auf der Datenbank ausführen
            c.execute('''CREATE TABLE Note (Note DOUBLE,ModulID INTEGER,FOREIGN KEY (ModulID) REFERENCES Modul(ModulID))''')
        }

#Datenbank und Klassen erstellen wenn noch nicht vorhanden
createDatabaseAndTable()

#Projekt-Loop bis 'Q' gedrückt wird
while True:
    try:
        benutzereingabe = input("Was willst du machen? (N für Note eintragen, M für Modul erstellen, F für Notenübersicht in Textdatei): ")
        if benutzereingabe == "N" or benutzereingabe == "n":
            while True:
                try:
                    modul, note = input("Gib der Modulname gefolgt von der Note ein (z.B. M122 5.2): ").split()
                    noteFloat = float(note)

                    #Verbindung zur Datenbank erstellen
                    connection=sqlite3.connect('noten.db')
                    cursor=connection.cursor()
                    
                    #Noten eingabe überprüfen, nur Noten von 1 bis 6 sind erlaubt
                    if noteFloat > 6:
                        print("Noten sind nur von 1.0 bis 6.0 erlaubt")
                        break
                    elif noteFloat < 1:
                        print("Noten sind nur von 1.0 bis 6.0 erlaubt")
                        break

                    #überprüfen ob das eingegebene Modul in der Datenbank existiert
                    cursor.execute("SELECT COUNT(ModulName) FROM modul WHERE ModulName =?", (modul,))
                    existModul = cursor.fetchone()[0]
                    if existModul == 1:
                        modulStr = str(modul) #ModulName in ein String umwandeln für den Datenbank-Befehl
                        cursor.execute("INSERT INTO Note (Note, ModulID) VALUES (?, ?)", (note, modulStr,))
                        connection.commit()
                        print("Die Note "+note+" wurde dem Modul "+modul+" hinzugefügt")
                        connection.close()
                        break
                    else:
                        # Modul nicht vorhanden
                        print("Modul existiert nicht. Bitte zuerst mit 'M' erstellen")
                        break
                    connection.close()
                except ValueError:
                    print("Vorgaben beachten: <Modulname Note> (z.B. M123 4.0)")
                    break
        elif benutzereingabe == "M" or benutzereingabe == "m":
            while True:
                try:
                    modul = input("Gib ein Modulname ein (z.B. M123): ")
                    #Verbindung zur Datenbank erstellen
                    connection=sqlite3.connect('noten.db')
                    cursor=connection.cursor()

                    #überprüfen ob eingegebenes Modul bereits existiert
                    cursor.execute("SELECT COUNT(ModulName) FROM modul WHERE ModulName =?", (modul,))
                    modulExist = cursor.fetchone()[0] #

                    #überprüfen ob Modulname aus mehreren Wörtern besteht
                    if len(modul.split()) > 1:
                        print("Modulname darf aus nur einem Word bestehen!")
                        break
                    #überprüfen ob Modul bereits existiert oder nicht
                    elif modulExist > 1:
                        print('Dieses Modul existiert bereits! Du kannst es mit Notel befüllen "N"')
                        break
                    else:
                        modulStr = str(modul) #ModulName in ein String umwandeln für den Datenbank-Befehl
                        cursor.execute("INSERT INTO Modul (ModulName) VALUES (?)", (modulStr,))
                        connection.commit()
                        print("Das Modul "+modul+" wurde hinzugefügt und kann ab sofort Noten (mit 'N') aufnehmen.")
                        break
                    connection.close()
                except ValueError:
                    print('Vorgaben beachten: <Modulname> (M123)')
                    break
        elif benutzereingabe == 'F' or benutzereingabe == 'f':
            #Verbindung zur Datenbank erstellen
            connection=sqlite3.connect('noten.db')
            cursor=connection.cursor()

            cursor.execute('SELECT * FROM Modul')
            moduls = cursor.fetchall() #ganzes Resultat in moduls speichern

            #Datei <Modulnote.txt> erstellen
            f = open('Modulnoten.txt','w')

            #for-loop durch alle Module die in der Datenbank existieren
            for modul in moduls:
                modulStr = str(modul[1])
                f.write(modulStr + '\n') #Modulname in die Datei schreiben
                cursor.execute('SELECT Note FROM Note where ModulID = ?;', (modulStr,))
                noten = cursor.fetchall() #ganzes Resultat in noten speichern

                #for-loop durch alle Noten pro Modul die in der Datenbank existeren
                for note in noten:
                    noteStr = str(note[0])
                    f.write(noteStr + '\n') #Noten in die Datei schreiben
                cursor.execute('SELECT ROUND(AVG(Note),2) FROM Note WHERE ModulID = ?;', (modulStr,))
                average = cursor.fetchone()[0] #nächste Zeile der Abfrage
                averageStr = str(average) #average in ein String umwandeln
                f.write('Durchschnitt: ')
                f.write(averageStr) #Durchschnitt der Module ausgeben
                f.write('\n') #Leerzeile schreiben
                f.write('\n') #Leerzeile schreiben
            
            cursor.execute('SELECT count(*) FROM Note')
            existModul = cursor.fetchone()[0] #ganzes Resultat in moduls speichern

            if existModul > 0:
                #Notendurchschnitt über alle Module
                cursor.execute('SELECT ROUND(AVG(Note),2) FROM Note')
                averageAll = cursor.fetchone()[0] #nächste Zeile der Abfrage
                averageAllStr = str(averageAll)
                f.write('Durchschnittsnote aller Module: ')
                f.write(averageAllStr)
            else:
                f.write('Es befinden sich keine Noten in der Datenbank')

            connection.close()
            print('Eine Datei "Modulnoten.txt" mit allen Noten und Modulen wurde erstellt.')
            break
        elif benutzereingabe == 'Q' or benutzereingabe == 'q':
            print("Good bye and see you soon")
            break
        else:
            print('Diese Eingabe ist nicht möglich.')
    except ValueError:
        print("Bitte beachte die Vorgaben...")

