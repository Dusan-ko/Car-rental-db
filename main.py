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

    def add_data_cars(self,*rows):

        try:
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
                return len(rows)
        except sqlite3.IntegrityError as e:
            return f"Error: Integrity constraint violated - {e}"
        except sqlite3.OperationalError as e:
            return f"Error: Operational issue - {e}"
        except Exception as e:
            return f"Error: Operational issue - {e}"

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

    def add_customer(self, row):
        try:
            with sqlite3.connect(self.database) as connection:
                cursor = connection.cursor()
                car_id = row[3]
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

                    cursor.execute(insert_query,row)

                    customer_id = cursor.lastrowid

                    self.change_renter(car_id, customer_id, cursor, connection)

                    connection.commit()

                    return f'{row[0]} {row[1]} has rented car {car_id}'
        except sqlite3.IntegrityError as e:
            return f"Error: Integrity constraint violated - {e}"

        except sqlite3.OperationalError as e:
            return f"Error: Operational issue - {e}"

        except Exception as e:
            return f"Error: Operational issue - {e}"




    def check_availability(self, car_id, cursor):
            # NEDA SA VOLAT SAMOSTATNE
            query = 'SELECT rented_id FROM Cars WHERE id = ?'
            cursor.execute(query, (car_id,))

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

        add_car_button = tkinter.Button(panel, text='Add Car',fg='green', command=self.add_car_gui)
        add_car_button.pack(fill='both', expand=True)

        add_customer_button = tkinter.Button(panel, text='Add Customer',fg='purple', command=self.add_customer_gui)
        add_customer_button.pack(fill='both', expand=True)





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



    def add_car_gui(self):
        def add_car(object ,make_inp, model_inp, year_inp):
            make = make_inp.get().strip()
            model = model_inp.get().strip()
            year = year_inp.get().strip()
            if len(make) > 2 and len(model) > 1:
                try:
                    if int(year) > 1800:
                        msg = self.databaza.add_data_cars([make,model,year,None])
                        if isinstance(msg, int):
                            msg = f'Added {make} {model} {year} into DB'
                        object.configure(text=f"{msg}", bg='white', fg='black')

                except:
                    object.configure(text='Error, year needs to be Numeric and above 1800 !', bg='white', fg='black')
            else:
                object.configure(text='Error, Make or Model needs to have at least 3 letters', bg='white', fg='black')





        top = tkinter.Toplevel()

        top.title('Adding car')

        # INPUTS HERE ---------------------------------
        input_container = tkinter.LabelFrame(top, background='red')
        input_container.grid(row=0, column=0, sticky='NSEW',padx=0, pady=0)


        make_container = tkinter.LabelFrame(input_container, bg='white')
        make_container.grid(row=0, column=0, columnspan=2, padx=20, pady=5, sticky='w')

        make_entry = tkinter.Entry(make_container, bg='white', fg='black')
        make_entry.grid(row=0, column=1, padx=5, pady=5)
        make_label = tkinter.Label(make_container, text='MAKE*', bg='white', fg='black')
        make_label.grid(row=0, column=0, padx=0, pady=5)


        model_container = tkinter.LabelFrame(input_container, bg='white')
        model_container.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky='w')

        model_entry = tkinter.Entry(model_container, bg='white', fg='black')
        model_entry.grid(row=0, column=1, padx=5, pady=5)
        model_label = tkinter.Label(model_container, text='MODEL*', bg='white', fg='black')
        model_label.grid(row=0, column=0, padx=0, pady=5)


        year_container = tkinter.LabelFrame(input_container, bg='white')
        year_container.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky='w')

        year_entry = tkinter.Entry(year_container, bg='white', fg='black')
        year_entry.grid(row=0, column=1, padx=5, pady=5)
        year_label = tkinter.Label(year_container, text='YEAR* (NUMERIC)', bg='white', fg='black')
        year_label.grid(row=0, column=0, padx=0, pady=5)

        submit_container = tkinter.Frame(input_container, bg='red')
        submit_container.grid(row=3, column=0, padx=5, pady=10, columnspan=2, sticky='ew')
        result = tkinter.Label(input_container, text='', bg='red', fg='white')
        result.grid(row=4, column=0, columnspan=2, pady=5)
        submit = tkinter.Button(submit_container, text='SUBMIT', highlightbackground='red',
                                command=lambda:add_car(result, make_entry, model_entry, year_entry))
        submit.pack()

        # ----------------------------------------------


        top.mainloop()

    def add_customer_gui(self):
        def new_customer(object,fname_inp,lname_inp, age_inp, car_id_inp):
            fname = fname_inp.get().strip()
            lname = lname_inp.get().strip()
            age = age_inp.get().strip()
            car_id = car_id_inp.get().strip()

            if len(fname) > 2 and len(lname) > 2:
                try:
                    if 17 < int(age) and int(age) < 80:
                        msg = self.databaza.add_customer([fname,lname,int(age),int(car_id)])
                        object.configure(text=f"{msg}", bg='white', fg='black')
                    else:
                        object.configure(text='Error, We rent cars only to people who are between 18 to 80!', bg='white', fg='black')


                except:
                    object.configure(text='Error', bg='white', fg='black')
            else:
                object.configure(text='Error, Your firstname and lastname need to have at least 3 letters', bg='white', fg='black')

        top = tkinter.Toplevel()
        top.title('Adding customer')
        # INPUTS HERE ---------------------------------
        input_container = tkinter.LabelFrame(top, background='purple')
        input_container.grid(row=0, column=0, sticky='NSEW',padx=0, pady=0)


        fname_container = tkinter.LabelFrame(input_container, bg='white')
        fname_container.grid(row=0, column=0, columnspan=2, padx=20, pady=5, sticky='w')

        fname_entry = tkinter.Entry(fname_container, bg='white', fg='black')
        fname_entry.grid(row=0, column=1, padx=5, pady=5)
        fname_label = tkinter.Label(fname_container, text='FIRSTANAME*', bg='white', fg='black')
        fname_label.grid(row=0, column=0, padx=0, pady=5)


        lname_container = tkinter.LabelFrame(input_container, bg='white')
        lname_container.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky='w')

        lname_entry = tkinter.Entry(lname_container, bg='white', fg='black')
        lname_entry.grid(row=0, column=1, padx=5, pady=5)
        lname_label = tkinter.Label(lname_container, text='LASTNAME*', bg='white', fg='black')
        lname_label.grid(row=0, column=0, padx=0, pady=5)


        age_container = tkinter.LabelFrame(input_container, bg='white')
        age_container.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky='w')

        age_entry = tkinter.Entry(age_container, bg='white', fg='black')
        age_entry.grid(row=0, column=1, padx=5, pady=5)
        age_label = tkinter.Label(age_container, text='AGE* (NUMERIC)', bg='white', fg='black')
        age_label.grid(row=0, column=0, padx=0, pady=5)


        car_id_container = tkinter.LabelFrame(input_container, bg='white')
        car_id_container.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky='w')

        car_id_entry = tkinter.Entry(car_id_container, bg='white', fg='black')
        car_id_entry.grid(row=0, column=1, padx=5, pady=5)
        car_id_label = tkinter.Label(car_id_container, text='CAR_ID*', bg='white', fg='black')
        car_id_label.grid(row=0, column=0, padx=0, pady=5)

        submit_container = tkinter.Frame(input_container, bg='purple')
        submit_container.grid(row=4, column=0, padx=5, pady=10, columnspan=2, sticky='ew')
        result = tkinter.Label(input_container, text='', bg='purple', fg='white')
        result.grid(row=5, column=0, columnspan=2, pady=5)
        submit = tkinter.Button(submit_container, text='SUBMIT', highlightbackground='purple',
                                command=lambda: new_customer(result, fname_entry, lname_entry, age_entry, car_id_entry))
        submit.pack()

        # ----------------------------------------------

        top.mainloop()










if __name__ == '__main__':
    auta_db = Database()
    # print(auta_db.add_customer(['Cyril', 'Bratislavsky', '20', '15']))
    databaseGUI()
    tkinter.mainloop()



