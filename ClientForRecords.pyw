from tkinter import Tk, messagebox, font, IntVar, Checkbutton, ttk, Button, Entry, Label, StringVar, Menu, W, E, END, Frame, Scrollbar, RIGHT, CENTER, Y, X, YES, Radiobutton, BOTH, BOTTOM, TOP, FALSE
from tkinter.filedialog import askopenfile
from tkcalendar import DateEntry
from xlsxwriter.workbook import Workbook
from socket import AF_INET, socket, SOCK_STREAM, error
import os
import time
import re
from datetime import datetime
from Encrypt import decrypt_message, encrypt_message
from MainFunctions import InsertInEntryes, center

# Класс для соединения с сервером
class ToServer(object):
         
    # Функция подключения к серверу
    def InitConnection(self, host, port, data=str()):
        __HEADER = 64
        try:
            __sock = socket(AF_INET, SOCK_STREAM)
        except error as __err:
            messagebox.showinfo('Ошибка', __err)
        else:
            try: 
                __sock.connect((host, port))
                __query = encrypt_message(data)                               # Зашифровываем данные перед отправкой
                __query_length = len(__query)                                 # Вычисляем длину ссообщения
                __send_length = str(__query_length).encode('utf8')            # Кодируем длину в нужный формат
                __send_length += b' ' * (__HEADER - len(__send_length))       # Кодируем полученную длину в байты и отправляем
                time.sleep(0.2)
                __sock.sendall(__send_length)                                 # Сначала длину
                __sock.sendall(__query)                                       # Затем само зашифрованное сообщение
                __msg_length = __sock.recv(__HEADER).decode('utf8')
                if __msg_length:
                    __msg_length = int(__msg_length)
                    time.sleep(0.2)
                    __msg = __sock.recv(__msg_length)
                    __ready = decrypt_message(__msg)                          # Расшифровываем данные с сервера
                    return __ready
                else:
                    messagebox.showinfo("Ошибка", "Какая-то ошибка")
            except (UnicodeDecodeError, error, ValueError, OSError) as __err:
                messagebox.showinfo("Ошибка", __err)
                return False
        finally:
            __sock.close()

    # Сортируем данные с сервера
    def Sort(self, ReceivedData=tuple()):
        try:
            __dataMessage = ReceivedData.split('#')
            __ReceivedMsg = [tuple(__s.split('^')) for __s in __dataMessage]
            __ReceivedMsg = [__x for __x in __ReceivedMsg if __x != ('',)]
            return __ReceivedMsg
        except AttributeError as err:
            messagebox.showinfo("Ошибка", err)

    # Функция запрашивает данные
    def Query_all(self):
        __Received = self.InitConnection(host = "localhost", port = 43333, data = "ALLQUERY")
        __Sorted = self.Sort(ReceivedData = __Received)
        Root.table.UpdateTable(rs = __Sorted)
        Root.isfull_label.configure(text = "Все заявки")
        messagebox.showinfo("Внимание", "Таблица успешно обновлена!")

    # Функция отправляет полученные данные на сервер с ключевым словом и разделителями 
    def Insert_into(self):
        __now = datetime.now()
        __d_string = __now.strftime("%d-%m-%Y")
        __variables = [Root.FIO.get(), Root.address.get(), Root.telephone.get(), Root.reason.get(), Root.information.get(), \
        Root.for_master.get(), Root.master.get(), Root.r_var.get(), Root.Category.get(), Authorization.FIO_employee, __d_string, Root.Date.get()]
        __pattern = r'[A-Za-z]'
        __kek = [__z for __z in __variables if __z == '' or len(__z) > 100 or re.findall(__pattern, __z)]

        # If length of the query more then 50 or contents engl letters or empty, call nessagebox
        if __kek:
            messagebox.showinfo("Ошибка", "Ошибка в тексте!")
        else:
            __request = "^".join(["INSERT", *__variables])
                  
            __ReceivedData = self.InitConnection(host = "localhost", port = 43333, data = __request)
            Root.isfull_label.configure(text = "")
            messagebox.showinfo("Data:", __ReceivedData)

            __tuple_for_table = [[__variables[11], __variables[0], __variables[1], __variables[2], __variables[3], __variables[4], \
            __variables[5], __variables[6], __variables[7], __variables[8]]]
            Root.table.AddQuery(entry = (__tuple_for_table))        
      
    # Функция ищет данные в таблице
    def Search(self, ID = int()):
        __pattern = r'[A-Za-z]'
        if ID == 1:
            __CAT = Root.Category.get()
            if __CAT == '' or re.findall(__pattern, __CAT):
                messagebox.showinfo("Ошибка", "Введите категорию корректно!")
            else:
                Root.table.SearchQuery(trigger = __CAT)
        elif ID == 2:
            __DATE = Root.Date.get()
            if __DATE == '' or re.findall(__pattern, __DATE):
                messagebox.showinfo("Ошибка", "Выберите дату корректно!")
            else:
                Root.table.SearchQuery(trigger = __DATE)
        elif ID == 3:
            __FIO = Root.FIO.get()
            if __FIO == '' or re.findall(__pattern, __FIO):
                messagebox.showinfo("Ошибка", "Заполните поле ФИО корректно!")
            else:
                Root.table.SearchQuery(trigger = __FIO)
                    
    # Функция отправляет на сервер запрос на удаление заявки
    def Delete_by_address(self):      
        __pattern = r'[A-Za-z]'
        __DADR = Root.address.get()
        if __DADR == '' or re.findall(__pattern, __DADR):
            messagebox.showinfo("Ошибка", "Заполните адресс корректно")
        elif Root.r_var.get() == "Открыта":
            messagebox.showinfo("Ошибка", "Заявка в открытом состоянии \
            \nЗакройте заявку перед тем как удалить")
        else:
            __request = "^".join(["DELETE", __DADR])
            __ReceivedData = self.InitConnection(host = "localhost", port = 43333, data = __request)
            messagebox.showinfo("Data:", __ReceivedData)
            # Для Таблицы
            Root.table.DeleteQuery(adr = __DADR)
      
    # Функция отправляет запрос на сервер с ключевым словом обновить
    def Update_data(self):
        __variables = [Root.FIO.get(), Root.address.get(), Root.telephone.get(), Root.reason.get(), Root.information.get(), Root.for_master.get(),\
        Root.master.get(), Root.r_var.get(), Root.Category.get(), Root.Date.get()]

        __pattern = r'[A-Za-z]'
        __kek = [__z for __z in __variables if __z == '' or len(__z) > 100 or re.findall(__pattern, __z)]
        if __kek:
            messagebox.showinfo("Ошибка", "Ошибка в тексте!")
        else:
            __request = "^".join(["UPDATE", *__variables])
            __ReceivedData = self.InitConnection(host = "localhost", port = 43333, data = __request) 
            messagebox.showinfo("Data:", __ReceivedData)
                
            __gr_var = [[__variables[9], __variables[0], __variables[1], __variables[2], __variables[3], __variables[4], \
            __variables[5], __variables[6], __variables[7], __variables[8]]]
            Root.table.RenewQuery(trigger = __variables[0], entry = __gr_var)

"""GUI Part"""
# Класс для работы с таблицей
class Table(Frame):

    # Инициирует функцию с таблицей в фрейме
    def __init__(self, Parent = None, headings = tuple(), rows = tuple()):
        super().__init__()
        
        __style = ttk.Style()
        __style.configure(".", font = ('Times New Roman', 12), foreground = "gray1")
        __style.configure("Treeview.Heading", font = ('Times New Roman', 12), foreground = "gray1")
        __style.map('my.Treeview', background = [('selected', 'sky blue')], foreground = [('selected', 'gray1')])
        self.__tree = ttk.Treeview(self, style = 'my.Treeview', show = "headings", selectmode = "browse") 
        self.__tree["columns"] = headings
        self.__tree["displaycolumns"] = headings
        
        [[self.__tree.heading(__head, text = __head, anchor = CENTER, command = lambda __lhead = __head : \
        self.__treeview_sort_column(self.__tree, __lhead, False)), \
        self.__tree.column(__head, anchor = CENTER, width = 240)] for __head in headings]

        [self.__tree.insert('', END, values = __row) for __row in rows]

        __scrolltabley = Scrollbar(self, command = self.__tree.yview)
        __scrolltablex = Scrollbar(self, orient = "horizontal", command = self.__tree.xview)
        self.__tree.configure(yscrollcommand = __scrolltabley.set, xscrollcommand = __scrolltablex.set)
        __scrolltabley.pack(side = RIGHT, fill = Y)
        __scrolltablex.pack(side = BOTTOM, fill = X)
        self.__tree.pack(expand = YES, fill = BOTH)
        self.__tree.bind("<Double-Button-1>", self.__OnEvents)
        self.__tree.bind('<Return>', self.__OnEvents)

    # Функция сортировки по столбцам
    def __treeview_sort_column(self, tv, col, reverse):
        print('sorting %s!' % col)
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse = reverse)

        [tv.move(k, '', index) for index, (val, k) in enumerate(l)]

        tv.heading(col, command = lambda: self.__treeview_sort_column(tv, col, not reverse))

    # Функция двойного щелчка
    def __OnEvents(self, rt):
        __RT = Main.mainroot
        __item = self.__tree.focus() 
        if __item:
            __data = self.__tree.item(__item)['values']
            try:
                InsertInEntryes(entryes = ((__RT.FIO_entry,str(__data[1])), (__RT.address_entry,str(__data[2])), (__RT.telephone_entry,str(__data[3])), (__RT.reason_entry,str(__data[4])), 
                (__RT.information_entry,str(__data[5])), (__RT.for_master_entry,str(__data[6])), (__RT.master_entry,str(__data[7]))))
                __RT.r_var.set(str(__data[8])), __RT.Category.set(str(__data[9])), __RT.Date.set(str(__data[0]))
            except IndexError as err:
                print(err)
                messagebox.showinfo("Ошибка", "Выберите строку в таблице")
        else:
            messagebox.showinfo("Внимание", "Выберите строку в таблице")
      
    def Export(self):
        file = askopenfile(mode ='w+', filetypes =[('Excel', '*.xlsx')])
        if file:
            try:
                workbook = Workbook(file.name)
                worksheet = workbook.add_worksheet()
                __data = [self.__tree.item(__child)['values'] for __child in self.__tree.get_children()]
                for row_num, row_data in enumerate(__data):
                    for col_num, col_data in enumerate(row_data):
                        worksheet.write(row_num, col_num, col_data)
                        worksheet.set_column(col_num, 5, 40)
            except Exception as exc:
                messagebox.showinfo("Ошибка", exc)
            else:
                workbook.close()
                os.startfile(r'C:/ПО Заявки/Export.xlsx')

    # Обновить данные в таблице
    def UpdateTable(self, rs = tuple()):
        [self.__tree.delete(__i) for __i in self.__tree.get_children()]       # получаем строки из treeview и удаляем, дабы исключить повторения содержимого
        [self.__tree.insert('', END, values = __row) for __row in rs]

    # Функция поиска
    def SearchQuery(self, trigger = str()):
        __selections = [__child for __child in self.__tree.get_children() if trigger in self.__tree.item(__child)['values']]
        if __selections:
            [self.__tree.delete(__child) for __child in self.__tree.get_children() if trigger not in self.__tree.item(__child)['values']]
            Root.isfull_label.configure(text = "Сортированные заявки")
            #self.__tree.selection_set(__selections)                  
        else:
            messagebox.showinfo("Внимание", "Таких данных в таблице нет либо нужно обновить таблицу \
            \nЧто-бы обновить таблицу выберите \n'Таблица' -> 'Все заявки/Обновить'")

    # Функция обновления строк
    def RenewQuery(self, trigger = str(), entry = tuple()):
        __kek = [__child for __child in self.__tree.get_children() if trigger in self.__tree.item(__child)['values']]
        if __kek:
            self.__tree.delete(__kek)
            [self.__tree.insert('', END, values = __row) for __row in entry]
        
    # Функция данных в таблицу
    def AddQuery(self, entry=tuple()):
        [self.__tree.insert('', END, values = __row) for __row in entry]
        
    # Функция удаления строк с таблицы
    def DeleteQuery(self, adr=()):
        [self.__tree.delete(__child) for __child in self.__tree.get_children() if adr in self.__tree.item(__child)['values']]
        print('deleted')

# Окно Регистрации
class Registration(Tk):

    def __init__(self):
        super().__init__()

        # Нужные переменные    
        Registration.ID, Registration.Login, Registration.Password, Registration.FIO_empl = StringVar(), StringVar(), StringVar(), StringVar()
        
        self.title("Регистрация:")
        self.geometry("400x300")
        center(self) 
                
        # Описание для полей ввода
        self.__ID_LABEL = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "ID:")
        self.__LOGIN_REG_LABEL = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Логин:")
        self.__PASSWORD_REG_LABEL = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Пароль:")
        self.__FIO_REG_LABEL = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "ФИО:")

        # Поля ввода
        self.__ID_ENTRY = Entry(textvariable = Registration.ID, width = 40)
        self.__LOGIN_REG_ENTRY = Entry(textvariable = Registration.Login, width = 40)
        self.__PASSWORD_REG_ENTRY = Entry(textvariable = Registration.Password, width = 40)
        self.__FIO_REG_ENTRY = Entry(textvariable = Registration.FIO_empl, width = 40)

        self.__reg_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Зарегистрироваться", width = 15, command = lambda: self.__NewUser())
        
        # Расположение полей ввода и т.д.
        self.__ID_ENTRY.place(relwidth = 0.40, relheight = 0.08, relx = 0.38, rely = 0.15)
        self.__LOGIN_REG_ENTRY.place(relwidth = 0.40, relheight = 0.08, relx = 0.38, rely = 0.30)
        self.__PASSWORD_REG_ENTRY.place(relwidth = 0.40, relheight = 0.08, relx = 0.38, rely = 0.45)
        self.__FIO_REG_ENTRY.place(relwidth = 0.40, relheight = 0.08, relx = 0.38, rely = 0.60)

        self.__ID_LABEL.place(relwidth = 0.30, relheight = 0.08, relx = 0.12, rely = 0.15)
        self.__LOGIN_REG_LABEL.place(relwidth = 0.30, relheight = 0.08, relx = 0.12, rely = 0.30)
        self.__PASSWORD_REG_LABEL.place(relwidth = 0.30, relheight = 0.08, relx = 0.12, rely = 0.45)
        self.__FIO_REG_LABEL.place(relwidth = 0.30, relheight = 0.08, relx = 0.12, rely = 0.60)
        
        self.__reg_button.place(relwidth = 0.40, relheight = 0.10, relx = 0.38, rely = 0.78)

        # Запрет на иземение размера окна
        self.resizable(width = False, height = False)
        center(self)

        self['bg'] = "gray10"


    def __NewUser(self):
        __ToAuth = "^".join(["REGISTER", Registration.ID.get(), Registration.Login.get(), Registration.Password.get(), Registration.FIO_empl.get()])
        __msg = ToServer().InitConnection(host = "localhost", port = 43333, data = __ToAuth)
        print(__msg)
        if __msg == "Reg":
            messagebox.showinfo("Успех:", "Регистрация прошла успешно!")
            self.destroy()
            time.sleep(0.5)
            Main()
        elif __msg == "EX":
            messagebox.showinfo("Внимание", "Пользователь уже существует!") 
        else:
            messagebox.showinfo("Error:", "Ошибка при подключении!")



# Окно авторизации
class Authorization(Tk):

    def __init__(self):
        super().__init__()

        # Нужные переменные    
        Authorization.__Login, Authorization.__Password, Authorization.FIO_employee = StringVar(), StringVar(), StringVar()
        Authorization.__ent, Authorization.__pas = IntVar(), IntVar()

        self.title("Авторизация:")
        self.geometry("400x200") 
        
        # Описание для полей ввода
        self.__login_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Введите Логин:")
        self.__password_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Введите пароль:")
        #self.__forerver_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Введите :")

        # Поля ввода
        self.__login_entry = Entry(font = ("Times New Roman", 12), fg = 'gray1', textvariable = Authorization.__Login, width = 40)
        self.__password_entry = Entry(font = ("Times New Roman", 12), fg = 'gray1', textvariable = Authorization.__Password, width = 40, show = "*")

        self.__entr_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Войти", width = 15, command = lambda: self.__MainWindow())

        self.__reg_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Регистрация", width = 15, command = lambda: self.__RegWindow())

        self.__chkbtn = Checkbutton(self, activeforeground = 'White', activebackground = 'gray10', bg = "gray10", font = ("Times New Roman", 12), fg = 'White', \
        text = "Показать пароль", selectcolor = 'gray10', variable = Authorization.__ent, onvalue=1, offvalue=0, command = lambda: self.__ShowPas())

        #self.__chkbtn = Checkbutton(self, text = "Сохранить пароль", variable = Authorization.__pas, onvalue=1, offvalue=0, command = lambda: self.__RememberPas())
        
        #(relwidth = 0.16, relheight = 0.05, relx = 0.01, rely = 0.80)
        # Расположение полей ввода и т.д.
        self.__entr_button.place(relwidth = 0.30, relheight = 0.16, relx = 0.10, rely = 0.75)
        self.__reg_button.place(relwidth = 0.30, relheight = 0.16, relx = 0.55, rely = 0.75)
        self.__login_entry.place(relwidth = 0.40, relheight = 0.12, relx = 0.45, rely = 0.30)
        self.__password_entry.place(relwidth = 0.40, relheight = 0.12, relx = 0.45, rely = 0.50)
        self.__login_label.place(relwidth = 0.30, relheight = 0.12, relx = 0.10, rely = 0.30)
        self.__password_label.place(relwidth = 0.30, relheight = 0.12, relx = 0.10, rely = 0.50)

        self.__chkbtn.place(relwidth = 0.35, relheight = 0.12, relx = 0.06, rely = 0.07)
        
        # Запрет на иземение размера окна
        self.resizable(width = False, height = False)
        self['bg'] = "gray10"
    
    def __ShowPas(self):
        if Authorization.__ent.get():
            self.__password_entry.config(show = "")
        else:
            self.__password_entry.config(show = "*")

    #def __RememberPas(self):

    #           if Authorization.__ent.get():

    #                self.__password_entry.config(show = "*")

        #         else:

        #              self.__password_entry.config(show = "")

    
    # Функция вызова окна регистрации
    def __RegWindow(self):
            self.destroy()
            time.sleep(0.2)
            __RegWin = Registration()  

    # Функция авторизации 
    def __MainWindow(self):
        __TupleAuth = [Authorization.__Login.get(), Authorization.__Password.get()]
        __kek = [__x for __x in __TupleAuth if __x == '' or len(__x) > 30]
        if __kek:
            messagebox.showinfo("Ошибка", "Поля заполнены некорректно")
        else:
            __ToAuth = "^".join(["ENTER", *__TupleAuth])   
            __msg = ToServer().InitConnection(host = "localhost", port = 43333, data = __ToAuth)
            if __msg:
                __msg = __msg.split("^")
                print(__msg[0])
                if __msg[0] == "GO":    
                    Authorization.FIO_employee = __msg[1]
                    print(Authorization.FIO_employee)
                    self.destroy()
                    time.sleep(0.5)
                    Main()
                elif __msg[0] == "NOLOG":       
                    messagebox.showinfo("Ошибка", "Нет такого пользователя!")
                elif __msg[0] == "Fail":
                    messagebox.showinfo("Ошибка", "Неправильный пароль!")
                else: 
                    messagebox.showinfo("Ошибка", "Ошибка сервера!")
            else:
                messagebox.showinfo("Ошибка", "Ошибка при покдлючении!")

# Главное окно
class Root(Tk):
      
    # Для обращении к конструкции родительского класса
    def __init__(self, data = tuple()):
        super().__init__()
        
        # self.bind("<Configure>", self.__configure_handler)
        self.protocol("WM_DELETE_WINDOW", self.__confirm_delete)
        self.__TS = ToServer()

        # Переменные
        Root.Date, Root.FIO, Root.address, Root.telephone, Root.reason, Root.information, Root.for_master, Root.master, Root.r_var, Root.Category = \
        StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
        Root.r_var.set('Открыта')
        
        self.title(Authorization.FIO_employee)
        self.geometry("1200x600")
        center(self) 

        Root.table = Table(self, headings = ('Дата выполнения заявки', 'ФИО', 'Адрес', 'Телефон', 'Причина', 'Время выполнения', 'Для Мастера', 'Мастер', 'Состояние заявки', 'Категория', 'ФИО сотрудника', 'Дата регистрации'), rows = data)
        
        # Поля для ввода
        self.FIO_entry = Entry(selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.FIO, width = 18)
        self.address_entry = Entry(selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.address, width = 18)
        self.telephone_entry = Entry(selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.telephone, width = 18)
        self.reason_entry = Entry(selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.reason, width = 18)
        self.information_entry = Entry(selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.information, width = 18)
        self.for_master_entry = Entry(selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.for_master, width = 18)
        self.master_entry = Entry(selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.master, width = 18)

        self.__monthchoosen = ttk.Combobox(self, font = ("Times New Roman", 12), width = 18, textvariable = Root.Category) 

        # Adding combobox drop down list 
        self.__monthchoosen['values'] = ('Телевидение',  
                                'Интернет',
                                'Пакет') 

        self.__monthchoosen.current() 

        __now = datetime.now()
        __y_string = __now.strftime("%Y")
        __d_string = __now.strftime("%d-%m-%Y")
        __k_str = ': '.join(['Сегодня', __d_string])

        self.__cal = DateEntry(self, selectforeground = 'gray1', selectbackground = 'sky blue', font = ("Times New Roman", 12), textvariable = Root.Date, width = 18, background = 'sky blue',
        foreground = 'white', borderwidth = 2, year = int(__y_string))
        
        # Описание полей
        self.__category_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Выберите категорию:")
        self.__FIO_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Введите ФИО:")
        self.__address_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Введите адресс:")
        self.__telephone_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Введите телефон:")
        self.__reason_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Введите причину:")
        self.__information_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Время выполнения заявки:")
        self.__for_master_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Пометка для мастера:")
        self.__master_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Выполняет мастер:") 
        self.__record_value_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Информация по заявке:")
        self.__data_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = "Выберите дату:")
        self.__clock = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12))
        self.__curdate = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12), text = __k_str)
        Root.isfull_label = Label(bg = "gray10", fg = "white", font = ("Times New Roman", 12))
        self.__tick()
        
        # Кнопки
        self.__r1 = Radiobutton(activeforeground = 'White', activebackground = 'gray10', bg = "gray10", font = ("Times New Roman", 12), fg = 'White', text = 'Открыта', selectcolor = 'gray10', variable = self.r_var, value = 'Открыта')
        self.__r2 = Radiobutton(activeforeground = 'White', activebackground = 'gray10', bg = "gray10", font = ("Times New Roman", 12), fg = 'White', text = 'Закрыта', selectcolor = 'gray10', variable = self.r_var, value = 'Закрыта')

        self.__delete_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Удалить Запись", width = 15, command = self.__TS.Delete_by_address)

        self.__add_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Добавить Запись", width = 15, command = self.__TS.Insert_into)

        self.__srch_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Поиск по дате", width = 15, command = lambda: self.__TS.Search(ID = 2))

        self.__update_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Обновить Запись", width = 15, command = self.__TS.Update_data)

        #self.__query_all_button = Button(text="Обновить", width=15, command=self.__TS.Query_all)
        #self.__query_all_button.place(relwidth=0.15, relheight=0.05, relx=0.01, rely=0.60)

        self.__clear_button = Button(font = ("Times New Roman", 12), fg = "gray1", text = "Очистить Поля Ввода", width = 15, command = lambda: InsertInEntryes(entryes = (self.FIO_entry, \
        self.address_entry, self.telephone_entry, self.reason_entry, self.information_entry, self.for_master_entry, self.master_entry), dell = 1))

        # Где они расположены

        __m = Menu(self)
        __m_edit = Menu(__m, font = ("Times New Roman", 11), tearoff = 0)
        __m.add_cascade(menu = __m_edit, label = "Меню")
        __m_edit.add_command(label = "Скрыть меню", command = lambda: self.__HideMenu(widg = [self.__category_label, \
        self.__FIO_label, self.__address_label, self.__telephone_label, self.__reason_label, self.__information_label, self.__for_master_label, self.__master_label,\
        self.__record_value_label, self.__data_label, self.FIO_entry, self.address_entry, self.telephone_entry, self.reason_entry, self.information_entry, self.for_master_entry, \
        self.master_entry, self.__r1, self.__r2, self.__cal, self.__monthchoosen, self.__delete_button, self.__add_button, self.__srch_button, self.__update_button, self.__clear_button]))
        __m_edit.add_command(label = "Показать меню", command = self.__ShowMenu)
        __m_edit.add_separator()
        __m_edit.add_command(label = "Экспорт в Excel", command = lambda : Root.table.Export())

        __m_search = Menu(__m, font = ("Times New Roman", 11), tearoff=0) 
        __m.add_cascade(menu=__m_search, label="Поиск")
        __m_search.add_command(label = "По категории", command = lambda: self.__TS.Search(ID = 1))
        __m_search.add_command(label = "По дате", command = lambda: self.__TS.Search(ID = 2))
        __m_search.add_command(label = "По ФИО", command = lambda: self.__TS.Search(ID = 3))

        __m_table = Menu(__m, font = ("Times New Roman", 11), tearoff=0)
        __m.add_cascade(menu = __m_table, label = "Таблица")
        __m_table.add_command(label = "Все заявки/Обновить", command = self.__TS.Query_all)
        __m_table.add_command(label = "Добавить запись", command = self.__TS.Insert_into)                  

        __m.add_command(label = "О программе")
        __m.add_command(label = "Выйти", command = self.destroy)

        self.columnconfigure(1, weight = 1)
        self['menu'] = __m
        self['bg'] = "gray10"
        self.__ShowMenu()

    #def __configure_handler(self, event):
    #    self.update_idletasks()
    #    time.sleep(0.1)

    def __confirm_delete(self):
        message = "Закончить работу с программой?"
        if messagebox.askyesno(message = message, parent = self):
            self.destroy()

    def __tick(self):
        __time_string = time.strftime('%H:%M:%S')
        self.__clock.config(text = __time_string)
        self.__clock.after(200, self.__tick)

    def __HideMenu(self, widg = tuple()):
        self.update_idletasks()
        [__i.place_forget() for __i in widg]
        Root.table.place(relwidth = 0.98, relheight = 0.90, relx = 0.01, rely = 0.05)
        self.__curdate.place(relwidth = 0.13, relheight = 0.03, relx = 0.01, rely = 0.01)
        Root.isfull_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.43, rely = 0.01)
        time.sleep(0.2)

    def __ShowMenu(self):
        self.update_idletasks()
        self.__category_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.05)
        self.__FIO_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.10)
        self.__address_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.15)
        self.__telephone_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.20)
        self.__reason_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.25)
        self.__information_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.30)
        self.__for_master_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.35)
        self.__master_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.40)
        self.__record_value_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.57)
        self.__data_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.01, rely = 0.46)
        Root.isfull_label.place(relwidth = 0.15, relheight = 0.03, relx = 0.63, rely = 0.01)

        self.FIO_entry.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.10)
        self.address_entry.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.15)
        self.telephone_entry.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.20)
        self.reason_entry.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.25)
        self.information_entry.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.30)
        self.for_master_entry.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.35)
        self.master_entry.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.40)

        self.__r1.place(relwidth = 0.08, relheight = 0.03, relx = 0.18, rely = 0.57)
        self.__r2.place(relwidth = 0.08, relheight = 0.03, relx = 0.28, rely = 0.57)

        Root.table.place(relwidth = 0.60, relheight = 0.90, relx = 0.38, rely = 0.05)
        self.__monthchoosen.place(relwidth = 0.18, relheight = 0.04, relx = 0.18, rely = 0.05)
        self.__cal.place(relwidth = 0.18, relheight = 0.05, relx = 0.18, rely = 0.45)

        self.__delete_button.place(relwidth = 0.16, relheight = 0.05, relx = 0.10, rely = 0.73)
        self.__add_button.place(relwidth = 0.16, relheight = 0.05, relx = 0.01, rely = 0.65)
        self.__srch_button.place(relwidth = 0.16, relheight = 0.05, relx = 0.01, rely = 0.90)
        self.__update_button.place(relwidth = 0.16, relheight = 0.05, relx = 0.20, rely = 0.65)
        self.__clear_button.place(relwidth = 0.16, relheight = 0.05, relx = 0.20, rely = 0.90)

        self.__clock.place(relwidth = 0.05, relheight = 0.03, relx = 0.93, rely = 0.01)
        self.__curdate.place(relwidth = 0.13, relheight = 0.03, relx = 0.38, rely = 0.01)
        time.sleep(0.2)

# Главная функция для взаимодействия с основным окном
def Main():             
    __now = datetime.now()
    __d_strg = __now.strftime("%d.%m.%Y")

    # Первое соединение с сервером, запрос заявок на сегодня 
    __Received = ToServer().InitConnection(host = "localhost", port = 43333, data = '^'.join(["CURQUERY",__d_strg]))
    if __Received == 'None':
        time.sleep(0.2)
        Main.mainroot = Root()
        Root.isfull_label.configure(text = "На сегодня заявок нет")
    else:
        __Sorted = ToServer().Sort(ReceivedData = __Received)
        time.sleep(0.2)
        Main.mainroot = Root(__Sorted)
        Root.isfull_label.configure(text = "Заявки на сегодня:")  

# Запуск программы
if __name__ == '__main__':
    time.sleep(0.5)
    App = Authorization()
    center(App)
    App.mainloop()