from tkinter import Tk, messagebox, IntVar, Toplevel,\
                    Checkbutton, ttk, Button, Entry, Label, StringVar,\
                    Menu, END, Frame, Scrollbar, RIGHT, CENTER,\
                    Y, X, YES, Radiobutton, BOTH, BOTTOM
from tkinter.filedialog import askopenfile
from tkcalendar import DateEntry
from xlsxwriter.workbook import Workbook
from datetime import datetime
from functools import cache, lru_cache
import os
import time
import re
try:
    from Encrypt import Internet
except ImportError:
    raise

class Functions:
    """Main functions"""

    def InsertInEntryes(self, entryes=tuple(), dell=int()):
        """Insenrting values in entryes
           if some values already there
           delete previous values and insert new
           Вставляет значения в поля ввода
           если до этого были какие-то значения
           удаляет предыдущие, вставляет текущие
        """
        try:
            if dell == 1:
                [__i.delete(0, END) for __i in entryes]
            else:
                [[__i.delete(0, END), __i.insert(0, __d)] for __i, __d in entryes]
        except TypeError as err:
            messagebox.showinfo("Ошибка", err)

    @cache
    def Sort(self, ReceivedData=tuple()):
        """Sorting incoming messages
           Сортирует входящие сообщения
        """
        try:
            __dataMessage = ReceivedData.split('#^')
            __ReceivedMsg = (__s.split('^') for __s in __dataMessage)
            __ReceivedMsg = (__x for __x in __ReceivedMsg if __x != ('',))
        except (AttributeError, TypeError) as err:
            messagebox.showinfo("Ошибка", err)
        else:
            return __ReceivedMsg

    def MainFN(self):
        """Function send query to server
           and returns todays records
           Функция посылает запрос на сервер
           и возвращает сегодняшние заявки
        """
        try:
            __now = datetime.now()
            __d_strg = __now.strftime("%d.%m.%Y")
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            try:
                # Connect to server, query today's records
                # Соединение с сервером, запрос заявок на сегодня
                __Received = Internet().IntoNetwork(data='^'.join(["CURQUERY",__d_strg]))
                if __Received == 'No':
                    time.sleep(0.2)
                    Functions.mainroot = Root()
                    Root.isfull_label.configure(text="На сегодня заявок нет")
                else:
                    __Sorted = self.Sort(ReceivedData=__Received)
                    time.sleep(0.2)
                    Functions.mainroot = Root(__Sorted)
                    Root.isfull_label.configure(text="Заявки на сегодня:")
            except Exception as exc:
                messagebox.showinfo("Ошибка:", exc)

class Table(Frame):
    """Table for records"""

    def __init__(self, Parent=None, headings=tuple(), rows=tuple()):
        super().__init__(Parent)

        __style = ttk.Style()
        __style.configure(".", font=('Times New Roman', 12), foreground="gray1")
        __style.configure("Treeview.Heading",\
                          font=('Times New Roman', 12), foreground="gray1")

        __style.map('my.Treeview', background=[('selected', 'sky blue')],\
                    foreground=[('selected', 'gray1')])

        self.__tree = ttk.Treeview(self, style='my.Treeview',\
                                   show="headings", selectmode="browse")

        self.__tree["columns"] = headings
        self.__tree["displaycolumns"] = headings

        [(self.__tree.heading(__head, text=__head,\
          anchor=CENTER, command=lambda __lhead=__head :\
          self.__treeview_sort_column(self.__tree, __lhead, False)),\
          self.__tree.column(__head, anchor=CENTER, width=240))\
          for __head in headings]

        [self.__tree.insert('', END, values=__row) for __row in rows]

        __scrolltabley = Scrollbar(self, command=self.__tree.yview)
        __scrolltablex = Scrollbar(self, orient="horizontal",\
                                   command=self.__tree.xview)
        self.__tree.configure(yscrollcommand=__scrolltabley.set,\
                              xscrollcommand=__scrolltablex.set)
        __scrolltabley.pack(side=RIGHT, fill=Y)
        __scrolltablex.pack(side=BOTTOM, fill=X)
        self.__tree.pack(expand=YES, fill=BOTH)
        self.__tree.bind("<Double-Button-1>", self.__OnEvents)
        self.__tree.bind('<Return>', self.__OnEvents)

    def __treeview_sort_column(self, tv, col, reverse):
        """Sorts table values by columns
           Сортировка значений в таблице
           по столбцам
        """
        try: 
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)

            [tv.move(k, '', index) for index, (val, k) in enumerate(l)]

            tv.heading(col,\
                       command=lambda: self.__treeview_sort_column(tv, col, not reverse))
        except (TypeError, AttributeError) as err:
            messagebox.showinfo("Ошибка", err)

    @lru_cache(typed=True)
    def __OnEvents(self, rt):
        """Insert data from line in the table
           into entryes for correction
           Вставляет данные из строки в таблице
           в поля ввода для корректировки
        """
        try:
            __RT = Functions.mainroot
            __item = self.__tree.focus()
        except (UnboundLocalError, TypeError) as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            try:
                if __item:
                    __data = self.__tree.item(__item)['values']
                    __data = list(map(str, __data))
                    __data_list = list(zip(__RT.entryes_tuple, __data[1:8]))
                    Functions().InsertInEntryes(entryes=__data_list)
                    __RT.r_var.set(__data[8]), __RT.Category.set(__data[9]),\
                    __RT.Date.set(__data[0]), __RT.RegDate.set(__data[11])
                else:
                    messagebox.showinfo("Внимание", "Выберите строку в таблице")
            except (Exception, IndexError,\
                    UnboundLocalError, TypeError) as exc:
                messagebox.showinfo("Ошибка:", exc)

    def Export(self, heading=tuple()):
        """Export data from table in excel
           Экспорт заявок с таблице в excel
        """
        file = askopenfile(mode='w+', filetypes=[('Excel', '*.xlsx')])
        if file:
            try:
                workbook = Workbook(file.name)
                worksheet = workbook.add_worksheet()
                [worksheet.write(0, col_n, data) for col_n, data in enumerate(heading)]
                __data = [self.__tree.item(__child)['values']\
                          for __child in self.__tree.get_children()]

                for row_num, row_data in enumerate(__data):
                    for col_num, col_data in enumerate(row_data):
                        worksheet.write(row_num+1, col_num, col_data)
                        worksheet.set_column(col_num, 5, 40)
            except Exception as err:
                messagebox.showinfo("Ошибка", err)
            else:
                workbook.close()
                messagebox.showinfo("Внимание", "Экспортировано успешно")

    def UpdateTable(self, rs=tuple()):
        """Delete data from table and
           insert new data
           Удалить данные с таблицы и
           вставить новые данные
        """
        try:
            [self.__tree.delete(__i) for __i in self.__tree.get_children()]
            [self.__tree.insert('', END, values=__row) for __row in rs]
        except TypeError as err:
            messagebox.showinfo("Error", err)

    def SearchQuery(self, trigger=str()):
        """Searching in the table for values
           that correspond to specified values
           Поиск в таблице значений, которые
           соответствуют указанным критериям
        """
        try:
            __selections = [__child for __child in self.__tree.get_children()\
                            if trigger in self.__tree.item(__child)['values']]
            if __selections:
                [self.__tree.delete(__child) for __child in self.__tree.get_children()\
                 if trigger not in self.__tree.item(__child)['values']]
                Root.isfull_label.configure(text="Сортированные заявки")
                #self.__tree.selection_set(__selections)
            else:
                messagebox.showinfo("Внимание",\
                                    "Таких данных в таблице нет либо нужно обновить таблицу\
                                    \nЧто-бы обновить таблицу выберите \n'Таблица' -> 'Все заявки/Обновить'")
        except TypeError as err:
            messagebox.showinfo("Error", err)

    def RenewQuery(self, trigger=str(), entry=tuple()):
        """Renew changed line
           Обновляет измененную строку
        """
        try:
            __kek = [__child for __child in self.__tree.get_children()\
                     if trigger in self.__tree.item(__child)['values']]
            if __kek:
                self.__tree.delete(__kek)
                [self.__tree.insert('', END, values=__row) for __row in entry]
        except TypeError as err:
            messagebox.showinfo("Error", err)

    def AddQuery(self, entry=tuple()):
        """Adds record to the table
           Добавляет строку в таблицу
        """
        try:
            [self.__tree.insert('', END, values=__row) for __row in entry]
        except TypeError as err:
            messagebox.showinfo("Error", err)

    def DeleteQuery(self, adr, regdate):
        """Deleting record by address
           Удаляет заявку по адрессу
        """
        try:
            [self.__tree.delete(__child) for __child in self.__tree.get_children()\
             if adr in self.__tree.item(__child)['values'] and\
                regdate in self.__tree.item(__child)['values']]
        except TypeError as err:
            messagebox.showinfo("Error", err)

class Registration(Toplevel):
    """Administration window for users"""

    def __init__(self, Parent, data=tuple()):
        super().__init__(Parent)

        Registration.ID, Registration.Login,\
        Registration.Password, Registration.FIO_empl =\
                                                      StringVar(), StringVar(), StringVar(), StringVar()
        self.title("Администрирование:")

        MyLeftPos = (self.winfo_screenwidth() - 800) / 2
        myTopPos = (self.winfo_screenheight() - 300) / 2

        self.geometry( "%dx%d+%d+%d" % (800, 300, MyLeftPos, myTopPos))

        self.__id_label = Label(self, bg="gray10", fg="white",\
                                font=("Times New Roman", 12), text="ID:")
        self.__login_reg_label = Label(self, bg="gray10", fg="white",\
                                       font=("Times New Roman", 12), text="Логин:")
        self.__password_reg_label = Label(self, bg="gray10", fg="white",\
                                          font=("Times New Roman", 12), text="Пароль:")
        self.__fio_reg_label = Label(self, bg="gray10", fg="white",\
                                     font=("Times New Roman", 12), text="ФИО:")

        self.__id_entry = Entry(self, textvariable=Registration.ID, width=40)
        self.__login_reg_entry = Entry(self,\
                                       textvariable=Registration.Login, width=40)
        self.__password_reg_entry = Entry(self,\
                                          textvariable=Registration.Password, width=40)
        self.__fio_reg_entry = Entry(self,\
                                     textvariable=Registration.FIO_empl, width=40)

        self.__reg_button = Button(self, font=("Times New Roman", 12),\
                                   fg="gray1", text="Зарегистрировать",\
                                   width=15, command=lambda: self.__NewUser())
        self.__del_button = Button(self, font=("Times New Roman", 12),\
                                   fg="gray1", text="Удалить по ID",\
                                   width=15, command=lambda: self.__DeleteUser())

        Registration.table = Table(self,\
                                   headings=('ID', 'Login', 'Password', 'FIO'), rows=data)

        # Расположение полей ввода и т.д.
        # Place entryes on needed position etc, etc.
        self.__id_entry.place(relwidth=0.08,\
                              relheight=0.08, relx=0.14, rely=0.70)
        self.__login_reg_entry.place(relwidth=0.15,\
                                     relheight=0.08, relx=0.36, rely=0.70)
        self.__password_reg_entry.place(relwidth=0.15,\
                                        relheight=0.08, relx=0.64, rely=0.70)
        self.__fio_reg_entry.place(relwidth=0.20,\
                                   relheight=0.08, relx=0.17, rely=0.85)

        self.__id_label.place(relwidth=0.05,\
                              relheight=0.08, relx=0.10, rely=0.70)
        self.__login_reg_label.place(relwidth=0.08,\
                                     relheight=0.08, relx=0.28, rely=0.70)
        self.__password_reg_label.place(relwidth=0.08,\
                                        relheight=0.08, relx=0.56, rely=0.70)
        self.__fio_reg_label.place(relwidth=0.06,\
                                   relheight=0.08, relx=0.11, rely=0.85)

        Registration.table.place(relwidth=0.90,\
                                 relheight=0.50, relx=0.05, rely=0.05)

        self.__reg_button.place(relwidth=0.20,\
                                relheight=0.10, relx=0.65, rely=0.85)
        self.__del_button.place(relwidth=0.20,\
                                relheight=0.10, relx=0.40, rely=0.85)

        # Lock on changing window size
        # Запрет на иземение размера окна
        self.resizable(width=False, height=False)

        self['bg'] = "gray10"

    def __NewUser(self):
        try:
            reg_tuple = (Registration.ID.get(), Registration.Login.get(),\
                         Registration.Password.get(), Registration.FIO_empl.get())
            check_ = [x for x in reg_tuple if x == ""]
            if check_:
                messagebox.showinfo("Ошибка:", "Заполните все поля")
        except Exception:
            raise
        else:
            try:
                __ToAuth = "^".join(("REGISTER", *reg_tuple))
                __msg = Internet().IntoNetwork(data=__ToAuth)
            except Exception:
                raise
            else:
                if __msg == "Reg":
                    add_user = (reg_tuple)
                    Registration.table.AddQuery(entry=add_user)
                else:
                    pass

    def __DeleteUser(self):
        try:
            id_ = Registration.ID.get()
            if id_ == "":
                messagebox.showinfo("Ошибка", "Введите ID пользователя")
            else:
                __ToDel = "^".join(("DELETEUSER", id_))
                __msg = Internet().IntoNetwork(data=__ToDel)
        except Exception:
            raise
        else:
            if __msg == "OK":
                __data = Internet().IntoNetwork(data="USERQUERY")
                __sorted_data = Functions().Sort(ReceivedData=__data)
                Registration.table.UpdateTable(rs=__sorted_data)
            else:
                pass

class Authentication(Tk):

    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.__close)

        Authentication.__Login, Authentication.__Password,\
        Authentication.FIO_employee = StringVar(), StringVar(), StringVar()
        Authentication.__ent = IntVar()

        self.title("Авторизация:")

        MyLeftPos = (self.winfo_screenwidth() - 400) / 2
        myTopPos = (self.winfo_screenheight() - 200) / 2

        self.geometry("%dx%d+%d+%d" % (400, 200, MyLeftPos, myTopPos))

        self.__login_label = Label(self, bg="gray10",\
                                   fg="white", font=("Times New Roman", 12),\
                                   text="Введите Логин:")
        self.__password_label = Label(self, bg="gray10",\
                                      fg="white", font=("Times New Roman", 12),\
                                      text="Введите пароль:")

        self.__login_entry = Entry(self,\
                                   font=("Times New Roman", 12), fg='gray1',\
                                   textvariable=Authentication.__Login, width=40)
        self.__password_entry = Entry(self,\
                                      font=("Times New Roman", 12), fg='gray1',\
                                      textvariable=Authentication.__Password, width=40, show="*")

        self.__entr_button = Button(self, font=("Times New Roman", 12),\
                                    fg="gray1", text="Войти", width=15,\
                                    command=lambda: self.__MainWindow())

        self.__entr_button.bind('<Return>', lambda x: self.__MainWindow())
        self.__password_entry.bind('<Return>', lambda x: self.__MainWindow())

        self.__chkbtn = Checkbutton(self, activeforeground='White',\
                                    activebackground='gray10', bg="gray10",\
                                    font=("Times New Roman", 12), fg='White',\
                                    text="Показать пароль", selectcolor='gray10',\
                                    variable=Authentication.__ent, onvalue=1, offvalue=0,\
                                    command=lambda: self.__ShowPas())

        self.__entr_button.place(relwidth=0.30,\
                                 relheight=0.16, relx=0.10, rely=0.75)
        self.__login_entry.place(relwidth=0.40,\
                                 relheight=0.12, relx=0.45, rely=0.30)
        self.__password_entry.place(relwidth=0.40,\
                                    relheight=0.12, relx=0.45, rely=0.50)
        self.__login_label.place(relwidth=0.30,\
                                 relheight=0.12, relx=0.10, rely=0.30)
        self.__password_label.place(relwidth=0.30,\
                                    relheight=0.12, relx=0.10, rely=0.50)
        self.__chkbtn.place(relwidth=0.35,\
                            relheight=0.12, relx=0.06, rely=0.07)

        self.resizable(width=False, height=False)
        self['bg'] = "gray10"

    def __close(self):
        try:
            self.destroy()
            os._exit(0)
        except (OSError, Exception) as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __ShowPas(self):
        try:
            if Authentication.__ent.get():
                self.__password_entry.config(show="")
            else:
                self.__password_entry.config(show="*")
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __MainWindow(self):
        """If Authentication is complete
           destroys Authentication window
           and calls Root
           Если авторизация прошла успешно
           вызывает self.destroy() и запускает
           главное окно
        """
        try:
            __TupleAuth = (Authentication.__Login.get(), Authentication.__Password.get())
            __kek = [__x for __x in __TupleAuth if __x == '' or len(__x) > 30]
            if __kek:
                messagebox.showinfo("Ошибка", "Поля заполнены некорректно")
        except (UnboundLocalError, TypeError) as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            try:
                __ToAuth = "^".join(("ENTER", *__TupleAuth))
                __msg = Internet().IntoNetwork(data=__ToAuth)
            except Exception as exc:
                messagebox.showinfo("Ошибка", exc)
            else:
                try:
                    if __msg:
                        __msg = __msg.split("^")
                        if __msg[0] == "GO":
                            Authentication.FIO_employee = __msg[1]
                            self.destroy()
                            time.sleep(0.5)
                            Functions().MainFN()
                        elif __msg[0] == "NOLOG":
                            messagebox.showinfo("Ошибка", "Нет такого пользователя!")
                        elif __msg[0] == "Fail":
                            messagebox.showinfo("Ошибка", "Неправильный пароль!")
                        else:
                            messagebox.showinfo("Ошибка", "Ошибка сервера!")
                    else:
                        messagebox.showinfo("Ошибка", "Ошибка при покдлючении!")
                except (Exception, IndexError) as exc:
                    messagebox.showinfo("Ошибка", exc)

class Root(Tk):
    """Main window class, inherites Tk class"""

    def __init__(self, data=tuple()):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.__confirm_exit)

        Root.Date, Root.FIO, Root.address, Root.telephone,\
        Root.reason, Root.information, Root.for_master,\
        Root.master, Root.r_var, Root.Category, Root.RegDate =\
                                                              StringVar(), StringVar(), StringVar(), StringVar(),\
                                                              StringVar(), StringVar(), StringVar(), StringVar(),\
                                                              StringVar(), StringVar(), StringVar()
        Root.r_var.set('Открыта')
        
        self.__variables =(Root.FIO.get(), Root.address.get(),\
                           Root.telephone.get(), Root.reason.get(),\
                           Root.information.get(), Root.for_master.get(),\
                           Root.master.get(), Root.r_var.get(),\
                           Root.Category.get())
        self.title(Authentication.FIO_employee)

        MyLeftPos = (self.winfo_screenwidth() - 1200) / 2
        myTopPos = (self.winfo_screenheight() - 600) / 2

        self.geometry("%dx%d+%d+%d" % (1200, 600, MyLeftPos, myTopPos))

        Root.table = Table(self, headings=('Дата выполнения заявки', 'ФИО', 'Адрес',\
                                           'Телефон', 'Причина', 'Время выполнения',\
                                           'Для Мастера', 'Мастер', 'Состояние заявки', 'Категория',\
                                           'ФИО сотрудника', 'Дата регистрации'), rows=data)

        self.FIO_entry = Entry(self, selectforeground='gray1',\
                               selectbackground='sky blue', font=("Times New Roman", 12),\
                               textvariable=Root.FIO, width=18)
        self.address_entry = Entry(self, selectforeground='gray1',\
                                   selectbackground='sky blue', font=("Times New Roman", 12),\
                                   textvariable=Root.address, width=18)
        self.telephone_entry = Entry(self, selectforeground='gray1',\
                                     selectbackground='sky blue', font=("Times New Roman", 12),\
                                     textvariable=Root.telephone, width=18)
        self.reason_entry = Entry(self, selectforeground='gray1',\
                                  selectbackground='sky blue', font=("Times New Roman", 12),\
                                  textvariable=Root.reason, width=18)
        self.information_entry = Entry(self, selectforeground='gray1',\
                                       selectbackground='sky blue', font=("Times New Roman", 12),\
                                       textvariable=Root.information, width=18)
        self.for_master_entry = Entry(self, selectforeground='gray1',\
                                      selectbackground='sky blue', font=("Times New Roman", 12),\
                                      textvariable=Root.for_master, width=18)
        self.master_entry = Entry(self, selectforeground='gray1',\
                                  selectbackground='sky blue', font=("Times New Roman", 12),\
                                  textvariable=Root.master, width=18)
        Root.entryes_tuple = (self.FIO_entry, self.address_entry,\
                              self.telephone_entry, self.reason_entry,\
                              self.information_entry, self.for_master_entry,\
                              self.master_entry)

        self.__monthchoosen = ttk.Combobox(self, font=("Times New Roman", 12),\
                                           width=18, textvariable=Root.Category)

        self.__monthchoosen['values'] = ('Телевидение', 'Интернет', 'Пакет')

        self.__monthchoosen.current()

        __now = datetime.now()
        __y_string = __now.strftime("%Y")
        __d_string = __now.strftime("%d-%m-%Y")
        __k_str = ': '.join(('Сегодня', __d_string))

        self.__cal = DateEntry(self, font=("Times New Roman", 12),\
                               textvariable=Root.Date, width=18,\
                               foreground='white', borderwidth=2,\
                               year=int(__y_string), date_pattern='dd.MM.yyyy')

        self.__category_label = Label(self, bg="gray10",\
                                      fg="white", font=("Times New Roman", 12),\
                                      text="Выберите категорию:")
        self.__FIO_label = Label(self, bg="gray10",\
                                 fg="white", font=("Times New Roman", 12),\
                                 text="Введите ФИО:")
        self.__address_label = Label(self, bg="gray10", \
                                     fg="white", font=("Times New Roman", 12),\
                                     text="Введите адресс:")
        self.__telephone_label = Label(self, bg="gray10", \
                                       fg="white", font=("Times New Roman", 12),\
                                       text="Введите телефон:")
        self.__reason_label = Label(self, bg="gray10", \
                                    fg="white", font=("Times New Roman", 12),\
                                    text="Введите причину:")
        self.__information_label = Label(self, bg="gray10", \
                                         fg="white", font=("Times New Roman", 12),\
                                         text="Время выполнения заявки:")
        self.__for_master_label = Label(self, bg="gray10",\
                                        fg="white", font=("Times New Roman", 12),\
                                        text="Пометка для мастера:")
        self.__master_label = Label(self, bg="gray10",\
                                    fg="white", font=("Times New Roman", 12), \
                                    text="Выполняет мастер:") 
        self.__record_value_label = Label(self, bg="gray10",\
                                          fg="white", font=("Times New Roman", 12),\
                                          text="Информация по заявке:")
        self.__data_label = Label(self, bg="gray10",\
                                  fg="white", font=("Times New Roman", 12),\
                                  text="Выберите дату:")
        self.__clock = Label(self, bg="gray10",\
                             fg="white", font=("Times New Roman", 12))
        self.__curdate = Label(self, bg="gray10",\
                               fg="white", font=("Times New Roman", 12), text=__k_str)
        Root.isfull_label = Label(self, bg="gray10",\
                                  fg="white", font=("Times New Roman", 12))

        self.__tick()

        self.__r1 = Radiobutton(self, activeforeground='White',\
                                activebackground='gray10', bg="gray10",\
                                font=("Times New Roman", 12), fg='White',\
                                text='Открыта', selectcolor='gray10',\
                                variable=self.r_var, value='Открыта')

        self.__r2 = Radiobutton(self, activeforeground='White',\
                                activebackground='gray10', bg="gray10",\
                                font=("Times New Roman", 12), fg='White',\
                                text='Закрыта', selectcolor='gray10',\
                                variable=self.r_var, value='Закрыта')

        self.__delete_button = Button(self, font=("Times New Roman", 12),\
                                      fg="gray1", text="Удалить Запись",\
                                      width=15, command=self.Delete_record)

        self.__add_button = Button(self, font=("Times New Roman", 12),\
                                   fg="gray1", text="Добавить Запись",\
                                   width=15, command=self.Insert_into)

        self.__srch_button = Button(self, font=("Times New Roman", 12),\
                                    fg="gray1", text="Поиск по дате",\
                                    width=15, command=lambda: self.Search(ID=2))

        self.__update_button = Button(self, font=("Times New Roman", 12),\
                                      fg="gray1", text="Обновить Запись",\
                                      width=15, command=self.Update_record)

        self.__clear_button = Button(self, font=("Times New Roman", 12),\
                                     fg="gray1", text="Очистить Поля Ввода", width=15,\
                                     command=lambda: Functions().InsertInEntryes(entryes=Root.entryes_tuple, dell=1))
        root_tuple = (self.__category_label, self.__FIO_label,\
                      self.__address_label, self.__telephone_label,\
                      self.__reason_label, self.__information_label,\
                      self.__for_master_label, self.__master_label, self.__record_value_label,\
                      self.__data_label, *Root.entryes_tuple, self.__r1,\
                      self.__r2, self.__cal, self.__monthchoosen,\
                      self.__delete_button, self.__add_button, self.__srch_button,\
                      self.__update_button, self.__clear_button)

        self.__menu_visibility = True
        self.bind("<Control-Key-o>",\
                                    lambda x: self.__HideMenu(widg= \
                                                                    root_tuple if self.__menu_visibility else self.__ShowMenu()))

        __m = Menu(self)
        __m_edit = Menu(__m, font=("Times New Roman", 11), tearoff=0)
        __m.add_cascade(menu=__m_edit, label="Меню")
        __m_edit.add_command(label="Скрыть меню",\
                             command=lambda: self.__HideMenu(widg=root_tuple))
        __m_edit.add_command(label="Показать меню", command=self.__ShowMenu)
        __m_edit.add_separator()
        __m_edit.add_command(label="Экспорт в Excel",\
                             command=lambda: Root.table.Export(heading=('Дата выполнения заявки', 'ФИО', 'Адрес', 'Телефон',\
                                                                        'Причина', 'Время выполнения', 'Для Мастера',\
                                                                        'Мастер', 'Состояние заявки', 'Категория',\
                                                                        'ФИО сотрудника', 'Дата регистрации')))

        __m_search = Menu(__m, font=("Times New Roman", 11), tearoff=0)
        __m.add_cascade(menu=__m_search, label="Поиск")
        __m_search.add_command(label="По категории",\
                               command=lambda: self.Search(ID=1))
        __m_search.add_command(label="По дате",\
                               command=lambda: self.Search(ID=2))
        __m_search.add_command(label="По ФИО",\
                               command=lambda: self.Search(ID=3))

        __m_table = Menu(__m, font=("Times New Roman", 11), tearoff=0)
        __m.add_cascade(menu=__m_table, label="Таблица")
        __m_table.add_command(label="Все заявки/Обновить",\
                              command=self.Query_all)
        __m_table.add_command(label="Добавить запись",\
                              command=self.Insert_into)
        __m.add_command(label="О программе")
        __m.add_command(label="Выйти", command=self.__confirm_exit)
        try:
            if Authentication.FIO_employee == 'Андрющенко Егор Валерьевич' or\
               Authentication.FIO_employee == 'Соболь Владислав Николаевич' or\
               Authentication.FIO_employee == 'Кравцов Виктор Сергеевич':
                __m.add_command(label="Администрирование", command=self.__RegWindow)
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

        self.columnconfigure(1, weight=1)
        self['menu'] = __m
        self['bg'] = "gray10"
        self.__ShowMenu()

    def Query_all(self):
        """Queries all records from server
           Запрашивает все заявки с сервера
        """
        try:
            __Received = Internet().IntoNetwork(data="ALLQUERY")
            __Sorted = Functions().Sort(ReceivedData=__Received)
            Root.table.UpdateTable(rs=__Sorted)
            Root.isfull_label.configure(text="Все заявки")
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)
        finally:
            messagebox.showinfo("Внимание", "Таблица успешно обновлена!")

    def Insert_into(self):
        """Sending records to server with
           keyword to trigger INSERT query
           in db on remote TCP server
           Посылает запрос на сервер
           с ключевым словом INSERT
           чтобы добавить заявку в БД
        """
        try:
            __now = datetime.now()
            __d_string = __now.strftime("%d-%m-%Y")
            __variables = (*self.__variables, Authentication.FIO_employee, __d_string, Root.Date.get())
            __pattern = r'[A-Za-z]'
            __kek = [__z for __z in __variables if __z == ''\
                     or len(__z) > 100 or re.findall(__pattern, __z)]
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            try:
                if __kek:
                    messagebox.showinfo("Ошибка", "Ошибка в тексте!")
                else:
                    __request = "^".join(("INSERT", *__variables))

                    __ReceivedData = Internet().IntoNetwork(data=__request)
                    Root.isfull_label.configure(text="")
                    messagebox.showinfo("Data:", __ReceivedData)

                    __list_for_table = [[__variables[11], *__variables[0:10]]]
                    Root.table.AddQuery(entry=__list_for_table)
            except (IndexError, Exception, TypeError) as exc:
                messagebox.showinfo("Ошибка:", exc)

    def Search(self, ID=int()):
        """Searching in our table for
           record, with parameters which
           correspond to the requested
           Ищем в нашей таблице запись,
           чьи параметры соответсвуют запрошенным
        """
        try:
            __pattern = r'[A-Za-z]'
            if ID == 1:
                __CAT = Root.Category.get()
                if __CAT == '' or re.findall(__pattern, __CAT):
                    messagebox.showinfo("Ошибка", "Заполните поле категории корректно!")
                else:
                    Root.table.SearchQuery(trigger=__CAT)
            elif ID == 2:
                __DATE = Root.Date.get()
                if __DATE == '' or re.findall(__pattern, __DATE):
                    messagebox.showinfo("Ошибка", "Выберите дату корректно!")
                else:
                    Root.table.SearchQuery(trigger=__DATE)
            elif ID == 3:
                __FIO = Root.FIO.get()
                if __FIO == '' or re.findall(__pattern, __FIO):
                    messagebox.showinfo("Ошибка", "Заполните поле ФИО корректно!")
                else:
                    Root.table.SearchQuery(trigger=__FIO)
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

    def Delete_record(self):
        """Sending address of the client
           with keyword DELETE, wich triggers
           DELETE query in DB on our server
           and deletes record wich correspond
           to this address
           Отправляет адресс заявки клиента
           с ключевым словом DELETE, которое
           вызывает запрос удалить
           в нашей БД на сервере
        """
        def Connect(adr, date):
            __request = "^".join(("DELETE", adr, date))
            __ReceivedData = Internet().IntoNetwork(data=__request)
            messagebox.showinfo("Data:", __ReceivedData)
            Root.table.DeleteQuery(adr=adr, regdate=date)

        message = "Вы уверены, что хотите удалить заявку?"
        result = messagebox.askyesno(message=message, parent=self)
        if result:
            try:
                __pattern = r'[A-Za-z]'
                __DADR, __RegDate = Root.address.get(), Root.RegDate.get()
            except (Exception, UnboundLocalError) as exc:
                messagebox.showinfo("Ошибка:", exc)
            else:
                try:
                    if __DADR == '' or re.findall(__pattern, __DADR):
                        messagebox.showinfo("Ошибка", "Заполните адресс корректно")
                    elif Root.r_var.get() == "Открыта":
                        message = "Заявка в открытом состоянии,\
                                   \nвы уверены что хотите удалить заявку?"
                        result = messagebox.askyesno(message=message, parent=self)
                        if result:
                                Connect(__DADR, __RegDate)
                        else:
                            pass
                    else:
                        Connect(__DADR, __RegDate)
                except Exception as exc:
                    messagebox.showinfo("Ошибка:", exc)
        else:
            pass

    def Update_record(self):
        """Sending data from record
           to our server with keyword UPDATE
           wich triggers UPDATE command in our DB
           and updating the record that corresponds
           to address of that client
           Отправляет данные с заявки на сервер
           с ключевым словом UPDATE, которое
           вызывает UPDATE запрос в нашу БД
           и обновляет заявку с нужным адрессом
        """
        try:
            __variables = (self.__variables, Root.Date.get())

            __pattern = r'[A-Za-z]'
            __kek = [__z for __z in __variables\
                     if __z == '' or len(__z) > 100 or re.findall(__pattern, __z)]
        except (TypeError, Exception, UnboundLocalError) as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            try:
                if __kek:
                    messagebox.showinfo("Ошибка", "Ошибка в тексте!")
                else:
                    message = "Вы уверены, что хотите обновить заявку?"
                    result = messagebox.askyesno(message=message, parent=self)
                    if result:
                        __request = "^".join(("UPDATE", *__variables))
                        __ReceivedData = Internet().IntoNetwork(data=__request)
                        messagebox.showinfo("Data:", __ReceivedData)

                        __gr_var = [[__variables[9], *__variables[0:8]]]
                        Root.table.RenewQuery(trigger=__variables[0], entry=__gr_var)
                    else:
                        pass
            except (Exception, IndexError) as exc:
                messagebox.showinfo("Ошибка:", exc)

    # Функция вызова окна регистрации
    def __RegWindow(self):
        """Sending keyword USERQUERY to our server
           wich triggers QUERY ALL command
           in db on server from user table
           Отправляет ключевое слово USERQUERY
           на сервер, которые вызывает QUERY ALL
           запрос в БД из нашей таблицы с пользователями
        """
        try:
            __RCVD = Internet().IntoNetwork(data="USERQUERY^")
            __srt = Functions().Sort(ReceivedData=__RCVD)
            Registration(self, __srt)
        except (Exception, UnboundLocalError) as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __confirm_exit(self):
        """To confirm is user
           want to exit our programm
           Спрашивает, хочет ли пользователь
           выйти из нашей программы
        """
        try:
            message = "Закончить работу с программой?"
            if messagebox.askyesno(message=message, parent=self):
                self.destroy()
                os._exit(0)
        except (OSError, Exception) as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __tick(self):
        """Calculates current system time
           Вычисляет текущее время
        """
        try:
            __time_string = time.strftime('%H:%M:%S')
            self.__clock.config(text=__time_string)
            self.__clock.after(200, self.__tick)
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __HideMenu(self, widg=tuple()):
        """Hides our menu with place_forget
           and makes our table with records
           more visible
           Прячет наше меню с place_forget
           и делает нашу таблицу с заявками
           более видимой
        """
        try:
            time.sleep(0.2)
            self.update_idletasks()
            [__i.place_forget() for __i in widg]
            Root.table.place(relwidth=0.98,\
                             relheight=0.90, relx=0.01, rely=0.05)
            self.__curdate.place(relwidth=0.13,\
                                 relheight=0.03, relx=0.01, rely=0.01)
            Root.isfull_label.place(relwidth=0.15,\
                                    relheight=0.03, relx=0.43, rely=0.01)
            time.sleep(0.2)
            self.__menu_visibility = False
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __ShowMenu(self):
        """Show hidden menu
           and putting table with
           records in it's place
           Показывает спрятанное меню
           и возвращает таблицу с заявками
           на место
        """
        time.sleep(0.2)
        self.update_idletasks()
        self.__category_label.place(relwidth=0.15,\
                                    relheight=0.03, relx=0.01, rely=0.05)
        self.__FIO_label.place(relwidth=0.15,\
                               relheight=0.03, relx=0.01, rely=0.10)
        self.__address_label.place(relwidth=0.15,\
                                   relheight=0.03, relx=0.01, rely=0.15)
        self.__telephone_label.place(relwidth=0.15,\
                                     relheight=0.03, relx=0.01, rely=0.20)
        self.__reason_label.place(relwidth=0.15,\
                                  relheight=0.03, relx=0.01, rely=0.25)
        self.__information_label.place(relwidth=0.15,\
                                       relheight=0.03, relx=0.01, rely=0.30)
        self.__for_master_label.place(relwidth=0.15,\
                                      relheight=0.03, relx=0.01, rely=0.35)
        self.__master_label.place(relwidth=0.15,\
                                  relheight=0.03, relx=0.01, rely=0.40)
        self.__record_value_label.place(relwidth=0.15,\
                                        relheight=0.03, relx=0.01, rely=0.57)
        self.__data_label.place(relwidth=0.15,\
                                relheight=0.03, relx=0.01, rely=0.46)
        Root.isfull_label.place(relwidth=0.15,\
                                relheight=0.03, relx=0.63, rely=0.01)

        self.FIO_entry.place(relwidth=0.18,\
                             relheight=0.04, relx=0.18, rely=0.10)
        self.address_entry.place(relwidth=0.18,\
                                 relheight=0.04, relx=0.18, rely=0.15)
        self.telephone_entry.place(relwidth=0.18,\
                                   relheight=0.04, relx=0.18, rely=0.20)
        self.reason_entry.place(relwidth=0.18,\
                                relheight=0.04, relx=0.18, rely=0.25)
        self.information_entry.place(relwidth=0.18,\
                                     relheight=0.04, relx=0.18, rely=0.30)
        self.for_master_entry.place(relwidth=0.18,\
                                    relheight=0.04, relx=0.18, rely=0.35)
        self.master_entry.place(relwidth=0.18,\
                                relheight=0.04, relx=0.18, rely=0.40)

        self.__r1.place(relwidth=0.08,\
                        relheight=0.03, relx=0.18, rely=0.57)
        self.__r2.place(relwidth=0.08,\
                        relheight=0.03, relx=0.28, rely=0.57)

        Root.table.place(relwidth=0.60,\
                         relheight=0.90, relx=0.38, rely=0.05)
        self.__monthchoosen.place(relwidth=0.18,\
                                  relheight=0.04, relx=0.18, rely=0.05)
        self.__cal.place(relwidth=0.18,\
                         relheight=0.05, relx=0.18, rely=0.45)

        self.__add_button.place(relwidth=0.16,\
                                relheight=0.05, relx=0.01, rely=0.65)
        self.__srch_button.place(relwidth=0.16,\
                                 relheight=0.05, relx=0.01, rely=0.90)
        self.__update_button.place(relwidth=0.16,\
                                   relheight=0.05, relx=0.20, rely=0.65)
        self.__clear_button.place(relwidth=0.16,\
                                  relheight=0.05, relx=0.20, rely=0.90)

        self.__clock.place(relwidth=0.05,\
                           relheight=0.03, relx=0.93, rely=0.01)
        self.__curdate.place(relwidth=0.13,\
                             relheight=0.03, relx=0.38, rely=0.01)
        time.sleep(0.2)
        self.__menu_visibility = True
        # if username is equal to administrator username
        # show administration panel
        # если имя пользователя соответствует имени админа
        # в меню добавляется панель администратора
        try:
            if Authentication.FIO_employee == 'Андрющенко Егор Валерьевич' or\
               Authentication.FIO_employee == 'Соболь Владислав Николаевич' or\
               Authentication.FIO_employee == 'Кравцов Виктор Сергеевич':
                    self.__delete_button.place(relwidth=0.16,\
                                               relheight=0.05, relx=0.10, rely=0.75)
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

if __name__ == '__main__':
    # Run Authentication window 
    # when programm starts running
    # Запускаем окно авторизации
    # когда программа запускается
    try:
        App = Authentication()
        App.mainloop()
    except Exception:
        raise