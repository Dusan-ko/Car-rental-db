import sqlite3
import tkinter
from tkinter import ttk



class Database:
    def __init__(self):
        self.database = 'carRental.db'

    # Struktura row je nasledovna:
    # (nazov, type, PK, AI)
    def pridat_tabulky(self):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()

            query_auta_table = '''
            CREATE TABLE IF NOT EXISTS Cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER,
                rented_id INTEGER,
                FOREIGN KEY("rented_id") REFERENCES "Customers" ("id")
            );
             '''

            query_zakaznici = '''
            CREATE TABLE IF NOT EXISTS Customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                age INTEGER,
                car_id INTEGER,
                FOREIGN KEY("car_id") REFERENCES "Cars" ("id")
              );
              '''


            cursor.execute(query_auta_table)
            cursor.execute(query_zakaznici)

            connection.commit()

    def pridaj_data_cars(self,*rows):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()

            insert_query = '''
            INSERT INTO Cars (make, model, year, rented_id)
            VALUES (?, ?, ?, ?);
            '''
            if len(rows) == 1:
                cursor.execute(insert_query, rows[0])
            else:
                cursor.executemany(insert_query, rows)
            connection.commit()
            print(f'Inserted {len(rows)}')

    def all_data_customers(self):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            select_query = "SELECT * FROM Customers;"
            cursor.execute(select_query)
            people = cursor.fetchall()

            return people

    def all_data_cars(self):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            select_query = "SELECT * FROM Cars;"
            cursor.execute(select_query)
            house = cursor.fetchall()

            return house

    def change_renter(self,car_id, renter_id, cursor, connection):
            query = 'UPDATE Cars SET rented_id=? where id=?'
            cursor.execute(query, (renter_id, car_id,))
            connection.commit()

    def add_customer(self, firstname, lastname, age, car_id):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            check = self.check_availability(car_id, cursor)
            if check == 2:
                return 'Car doesnt exist'
            elif check == 1:
                return 'Car isnt currently available'
            else:
                insert_query = '''
                INSERT INTO Customers (firstname, lastname, age, car_id)
                VALUES (?, ?, ?, ?); 
                '''

                cursor.execute(insert_query,(firstname,lastname,age,car_id))

                customer_id = cursor.lastrowid

                self.change_renter(car_id, customer_id, cursor, connection)

                connection.commit()

                return f'{firstname} {lastname} has rented car {car_id}'




    def check_availability(self, car_id, cursor):
            # NEDA SA VOLAT SAMOSTATNE
            query = 'SELECT rented_id FROM Cars WHERE id = ?'
            cursor.execute(query, (str(car_id)))

            response = cursor.fetchone()

            if response == None:
                return 2
            elif isinstance(response,tuple):
                if response[0] == None:
                    return 0
                else:
                    return 1



class databaseGUI:
    def __init__(self):
        root = tkinter.Tk()
        self.databaza = Database()
        self.root = root
        root.title('DATABAZA VIEW')
        root.geometry('800x450')
        panel = tkinter.Frame(root)
        panel.pack(fill="both",expand = True)

        view_all_button = tkinter.Button(panel, text='View Cars', fg='blue',bg='gray', command=self.view_cars)
        view_all_button.pack(fill="both",expand=True)

        add_data_button = tkinter.Button(panel, text='Add Data',fg='green')
        add_data_button.pack(fill='both', expand=True)

    # def add_data:

    def zmen(self,tree, insert):
        if insert is not None:
            for item in tree.get_children():
                tree.delete(item)

            for i, car in enumerate(insert):
                if i % 2 == 1:
                    tree.insert('', i,text=car[0], values=car[1:], tags=('evenrow',))
                elif i % 2 == 0:
                    tree.insert('', i,text=car[0], values=car[1:], tags=('oddrow',))
                else:
                    print('0 matches found')


    def view_cars(self):
        # TODO SORTING V TREEVIEW
        def filter(db, input):

            def porovnaj(operator, cislo, stlpec, zapis):
                vysledok = []
                if operator == '>':
                    for item in zapis:
                        if int(item[stlpec]) > cislo:
                            vysledok.append(item)
                elif operator == '<':
                    for item in zapis:
                        if int(item[stlpec]) < cislo:
                            vysledok.append(item)
                else:
                    for item in zapis:
                        if int(item[stlpec]) == cislo:
                            vysledok.append(item)
                return vysledok


            zapis = db
            vrat = []
            input = input.strip()

            operator = None
            for char in '<>=':
                if char in input:
                    operator = char
                    break

            if not operator:
                if input.isnumeric():
                    for item in zapis:
                        if input in str(item[0]) or input in str(item[3]) \
                                or input in str(item[1]) or input in str(item[2]):
                            vrat.append(item)
                else:
                    for item in zapis:
                        if input.lower() in str(item[1]).lower() or input.lower() in str(item[2]).lower():
                            vrat.append(item)
            else:
                parts = input.split(operator)
                first = parts[0].strip().lower()
                second = parts[1].strip().lower()
                if first.strip().lower() == 'year':
                    vrat = porovnaj(operator, int(second), 3,zapis)
                elif first.strip().lower() ==  'id':
                    vrat = porovnaj(operator, int(second), 0,zapis)

                elif second.strip().lower() ==  'year':
                    if operator == '<':
                        operator = '>'
                    elif operator == '>':
                        operator = '<'
                    vrat = porovnaj(operator, int(first), 3,zapis)
                elif second.strip().lower() ==  'id':
                    if operator == '<':
                        operator = '>'
                    elif operator == '>':
                        operator = '<'
                    vrat = porovnaj(operator, int(first), 0,zapis)
                else:
                    print('Wrong input')
            return vrat

        data = self.databaza.all_data_cars()
        # OKNO
        top = tkinter.Toplevel()
        top.title('Car DB Viewer')

        # Filter Bar
        input_container = ttk.LabelFrame(top, text=' DATABAZA AUT ')
        input_container.grid(row=0, column=0, sticky='ew')

        # Filter Entry
        input_entry = ttk.Entry(input_container)
        input_entry.grid(row=0, column=0, padx=5, pady=5)

        # Filter Button
        input_button = ttk.Button(input_container, text='FILTER',command=lambda:self.zmen(cars, filter(data,input_entry.get())))
        input_button.grid(row=0, column=1, padx=5, pady=5)

        # Treeviw
        style = ttk.Style()
        style.theme_use('clam')
        nameplate = ("Make", "Model", "Year", "RENTED BY")
        cars = ttk.Treeview(top,columns=nameplate)
        cars.grid()
        cars.heading("#0", text="ID")
        for col in nameplate:
            cars.heading(col, text=col)


        cars.tag_configure('oddrow', background='dark orange')
        cars.tag_configure('evenrow', background='#FFFFFF', foreground='black')

        for i,car in enumerate(data):
            if i % 2 == 1:
                cars.insert('', i,text=car[0], values=car[1:], tags=('evenrow',))
            else:
                cars.insert('', i,text=car[0], values=car[1:], tags=('oddrow',))









        top.mainloop()











if __name__ == '__main__':
    auta_db = Database()
    # auta_db.pridat_tabulky()
    # auta_db.pridaj_data_cars(('Ferrari','F40', 1989, None),('Mercedes-Benz','C63', 2012, None))
    # auta_db.pridaj_data_customers(('Jozko', 'Mrvicka', 40, 1))
    # print(auta_db.all_data_customers())
    # auta_db.all_data_cars()
    # auta_db.change_renter(1,None)
    # auta_db.add_customer('Michal', 'Pichal', 19, 2)
    # print(auta_db.all_data_customers())
    databaseGUI()
    tkinter.mainloop()



