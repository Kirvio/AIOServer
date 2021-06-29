from tkinter import Tk, messagebox, IntVar, Toplevel,\
                    Checkbutton, ttk, Button, Entry, Label, StringVar,\
                    Menu, END, Frame, Scrollbar, RIGHT, CENTER,\
                    Y, X, YES, Radiobutton, BOTH, BOTTOM
from tkinter.filedialog import askopenfile
from tkinter.font import BOLD
from tkcalendar import DateEntry
from xlsxwriter.workbook import Workbook
from datetime import datetime
from weakref import ref
from functools import lru_cache
import os
import time
import re
try:
    from Encrypt import Internet
except ImportError:
    raise

class Table(Frame):

    def __init__(self, Parent=None, headings=tuple(), rows=list(), counter=0):
        super().__init__(Parent)

        self.Parent = Parent
        self.counter = counter

        __style = ttk.Style()
        __style.configure(".", font=('Times New Roman', 12),
                               foreground="gray1")
        __style.configure("Treeview.Heading", font=('Times New Roman', 14, BOLD),
                                              foreground="gray1")

        __style.map('my.Treeview', background=[('selected', 'sky blue')],
                                   foreground=[('selected', 'gray1')])

        self.__tree = ttk.Treeview(self, style='my.Treeview',
                                         show="headings", selectmode="browse")

        self.__tree["columns"] = headings
        self.__tree["displaycolumns"] = headings

        [(self.__tree.heading(__head, text=__head,
                                      anchor=CENTER, command=lambda __lhead=__head :\
                                      self.__treeview_sort_column(self.__tree, __lhead, False)),
          self.__tree.column(__head, anchor=CENTER, width=240))\
                                                               for __head in headings]

        [self.__tree.insert('', END, values=__row) for __row in rows]

        __scrolltabley = Scrollbar(self, command=self.__tree.yview)
        __scrolltablex = Scrollbar(self, orient="horizontal",
                                         command=self.__tree.xview)
        self.__tree.configure(yscrollcommand=__scrolltabley.set,
                              xscrollcommand=__scrolltablex.set)
        __scrolltabley.pack(side=RIGHT, fill=Y)
        __scrolltablex.pack(side=BOTTOM, fill=X)
        self.__tree.pack(expand=YES, fill=BOTH)
        self.__tree.bind("<Double-Button-1>", self.__double_click)
        self.__tree.bind('<Return>', self.__double_click)
        if counter == 0:
            self.t_m = Menu(self,
                                 font=("Inter Medium", 9),
                                 activebackground='sky blue',
                                 activeforeground='gray1', tearoff=0)
            self.t_m.add_command(label="Обновить таблицу", command=Parent.query_all)
            self.t_m.add_command(label="Скрыть меню", command=Parent.hide_menu)
            self.t_m.add_command(label="Показать меню", command=Parent.show_menu)
            self.t_m.add_command(label="Поиск по дате", command=lambda: Parent.search(ID=2))
            self.t_m.add_separator()
            self.t_m.add_command(label="Экспорт в Excel", command=lambda: self.Export(heading=headings))

            self.__tree.bind('<Button-3>', self.__do_popup)
        elif counter == 2:
            self.t_m = Menu(self,
                                 font=("Inter Medium", 9),
                                 activebackground='sky blue',
                                 activeforeground='gray1', tearoff=0)
            self.t_m.add_command(label="Обновить таблицу", command=Parent.query_all)
            self.t_m.add_separator()
            self.t_m.add_command(label="Экспорт в Excel", command=lambda: self.Export(heading=headings))
            self.__tree.bind('<Button-3>', self.__do_popup)

    def __treeview_sort_column(self, tv, col, reverse):
        """Sorts table values by columns
           Сортировка значений в таблице
           по столбцам
        """
        try: 
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)

            [tv.move(k, '', index) for index, (val, k) in enumerate(l)]

            tv.heading(col,
                           command=lambda: self.__treeview_sort_column(tv, col, not reverse))
        except (TypeError, AttributeError) as err:
            messagebox.showinfo("Ошибка", err, parent=self.Parent)

    @lru_cache(typed=True)
    def __double_click(self, rt):
        """Insert data from line in the table
           into entryes for correction
           Вставляет данные из строки в таблице
           в поля ввода для корректировки
        """
        try:
            __item = self.__tree.focus()
        except (UnboundLocalError, TypeError) as exc:
            messagebox.showinfo("Ошибка:", exc, parent=self.Parent)
        else:
            if __item:
                if self.counter == 1:
                    try:
                        __reg_vars = ref(Root.reg_window)
                        __weak_ref_var = __reg_vars()
                        __data = self.__tree.item(__item)['values']
                        __data = list(map(str, __data))
                        __data_list = list(zip(__weak_ref_var.reg_entryes_tuple, __data))
                        Root.insert_in_entryes(entryes=__data_list)
                    except (Exception, IndexError,\
                            UnboundLocalError, TypeError) as exc:
                        messagebox.showinfo("Ошибка:", exc, parent=self.Parent)
                else:
                    try:
                        __root_vars = ref(Authentication.mainroot)
                        __weak_ref_var = __root_vars()
                        __data = self.__tree.item(__item)['values']
                        __data = list(map(str, __data))
                        __data_list = list(zip(__weak_ref_var.entryes_tuple, __data[1:9]))

                        Root.insert_in_entryes(entryes=__data_list)

                        __weak_ref_var.r_var.set(__data[9]),\
                        __weak_ref_var.Category.set(__data[10]),\
                        __weak_ref_var.Date.set(__data[0]),\
                        __weak_ref_var.RegDate.set(__data[12])
                    except (Exception, IndexError,\
                            UnboundLocalError, TypeError) as exc:
                        messagebox.showinfo("Ошибка:", exc, parent=self.Parent)
            else:
                messagebox.showinfo("Внимание", "Выберите строку в таблице",
                                                                            parent=self.Parent)

    def __do_popup(self, event):
        try:
            self.t_m.tk_popup(event.x_root, event.y_root)
        finally:
            self.t_m.grab_release()

    def Export(self, heading=tuple()):
        """Export data from table in excel
           Экспорт заявок с таблице в excel
        """
        file = askopenfile(mode='w+', filetypes=[('Excel', '*.xlsx')],
                                                                      parent=self.Parent)
        if file:
            try:
                workbook = Workbook(file.name)
                worksheet = workbook.add_worksheet()
                [worksheet.write(0, col_n, data) for col_n, data in enumerate(heading)]
                __data = [self.__tree.item(__child)['values'] \
                                                              for __child in self.__tree.get_children()]

                [[worksheet.write(row_num+1, col_num, col_data), \
                  worksheet.set_column(col_num, 5, 40)] \
                                                        for row_num, row_data in enumerate(__data)\
                                                        for col_num, col_data in enumerate(row_data)]
            except Exception as err:
                messagebox.showinfo("Ошибка", err, parent=self.Parent)
            else:
                workbook.close()
                messagebox.showinfo("Внимание", "Экспортировано успешно",
                                                                         parent=self.Parent)

    def update_table(self, rs=tuple()):
        """Delete data from table and
           insert new data
           Удалить данные с таблицы и
           вставить новые данные
        """
        try:
            [self.__tree.delete(__i) for __i in self.__tree.get_children()]
            [self.__tree.insert('', END, values=__row) for __row in rs]
        except TypeError as err:
            messagebox.showinfo("Error", err, parent=self.Parent)
    
    def search_sort(self, val):
        val = [__child \
                       for __child in self.__tree.get_children() \
                       for __item in self.__tree.item(__child)['values'] \
                                                                         if type(__item) == str \
                                                                         if val in __item]
        yield list(val)

    def search_query(self, trigger):
        """searching in the table for values
           that correspond to specified values
           Поиск в таблице значений, которые
           соответствуют указанным критериям
        """
        if self.counter == 0:
            try:
                __selections = [__child for __child in self.__tree.get_children() \
                                                                                  if trigger in self.__tree.item(__child)['values']]
                if __selections:
                    [self.__tree.delete(__child) for __child in self.__tree.get_children() \
                                                                                           if __child not in __selections]
                    Root.isfull_label.configure(text="Сортированные заявки")
                    #self.__tree.selection_set(__selections)
                else:
                    messagebox.showinfo("Внимание",\
                                        "Таких данных в таблице нет, попробуйте обновить таблицу\
                                        \nЧто-бы обновить таблицу выберите \n'Таблица' -> 'Все заявки/Обновить'",
                                                                                                                 parent=self.Parent)
            except TypeError as err:
                messagebox.showinfo("Error", err, parent=self.Parent)
        else:
            try:
                __selections1 = next(self.search_sort(trigger[0]))
                __selections2 = next(self.search_sort(trigger[1]))
                __selections3 = next(self.search_sort(trigger[2]))
                __selections4 = next(self.search_sort(trigger[3]))
                common_ones = list(set(__selections1) & set(__selections2)\
                                   & set(__selections3) & set(__selections4))
                if common_ones == []:
                    messagebox.showinfo("Внимание",\
                                        "Таких данных в таблице нет, попробуйте обновить таблицу",
                                                                                                  parent=self.Parent)
                else:
                    [self.__tree.delete(__child) for __child in self.__tree.get_children() \
                                                                                           if __child not in common_ones]
            except (TypeError, IndexError) as err:
                messagebox.showinfo("Error", err, parent=self.Parent)

    def change_record(self, trigger, entry=list()):
        """Renew changed line
           Обновляет измененную строку
        """
        try:
            self.remove_record(trigger)
            [self.__tree.insert('', END, values=__row) for __row in entry]
        except (TypeError, IndexError) as err:
            messagebox.showinfo("Error", err, parent=self.Parent)

    def add_record(self, entry=tuple()):
        """Adds record to the table
           Добавляет строку в таблицу
        """
        try:
            [self.__tree.insert('', END, values=__row) for __row in entry]
        except TypeError as err:
            messagebox.showinfo("Error", err, parent=self.Parent)

    def remove_record(self, trigger):
        """Deleting record by address
           Удаляет заявку по адрессу
        """
        try:
            [self.__tree.delete(__child) for __child in self.__tree.get_children() \
                                                                                   if trigger[0] in self.__tree.item(__child)['values'] and \
                                                                                      trigger[1] in self.__tree.item(__child)['values'] and \
                                                                                      trigger[2] in self.__tree.item(__child)['values'] and \
                                                                                      trigger[3] in self.__tree.item(__child)['values']]
        except (TypeError, IndexError) as err:
            messagebox.showinfo("Error", err, parent=self.Parent)

class Registration(Toplevel):
    """Administration window for users"""

    def __init__(self, Parent, data=tuple()):
        super().__init__(Parent)

        self.__variables = [self.ID, self.Login,
                            self.Password, self.FIO_empl] = \
                                                            StringVar(), StringVar(), StringVar(), StringVar()
        self.title("Администрирование:")

        MyLeftPos = (self.winfo_screenwidth() - 1200) / 2
        myTopPos = (self.winfo_screenheight() - 500) / 2

        self.geometry( "%dx%d+%d+%d" % (1200, 500, MyLeftPos, myTopPos))

        self.__id_label = Label(self, bg="gray10", fg="white",
                                      font=("Times New Roman", 12), text="ID:")
        self.__login_reg_label = Label(self, bg="gray10", fg="white",
                                             font=("Times New Roman", 12), text="Логин:")
        self.__password_reg_label = Label(self, bg="gray10", fg="white",
                                                font=("Times New Roman", 12), text="Пароль:")
        self.__fio_reg_label = Label(self, bg="gray10", fg="white",
                                           font=("Times New Roman", 12), text="ФИО:")

        self.__id_entry = Entry(self, font=("Times New Roman", 12), fg='gray1',
                                      selectforeground='gray1', selectbackground='sky blue',
                                      textvariable=self.ID, width=40)
        self.__login_reg_entry = Entry(self, font=("Times New Roman", 12), fg='gray1',
                                             selectforeground='gray1', selectbackground='sky blue',
                                             textvariable=self.Login, width=40)
        self.__password_reg_entry = Entry(self, font=("Times New Roman", 12), fg='gray1',
                                                selectforeground='gray1', selectbackground='sky blue',
                                                textvariable=self.Password, width=40)
        self.__fio_reg_entry = Entry(self, font=("Times New Roman", 12), fg='gray1',
                                           selectforeground='gray1', selectbackground='sky blue',
                                           textvariable=self.FIO_empl, width=40)

        self.reg_entryes_tuple = (self.__id_entry, self.__login_reg_entry,
                                  self.__password_reg_entry, self.__fio_reg_entry)

        self.__reg_button = Button(self, font=("Times New Roman", 12),
                                         background='White', activebackground='sky blue',
                                         fg="gray1", text="Зарегистрировать",
                                         width=15, command=lambda: self.__new_user())
        self.__del_button = Button(self, font=("Times New Roman", 12),
                                         background='White', activebackground='sky blue',
                                         fg="gray1", text="Удалить по ID",
                                         width=15, command=lambda: self.__delete_user())
        self.__clear_button = Button(self, font=("Times New Roman", 12),
                                           background='White', activebackground='sky blue',
                                           fg="gray1", text="Очистить Поля Ввода",
                                           width=15, command=lambda: Root.insert_in_entryes(\
                                                                                            entryes=self.reg_entryes_tuple, dell=1))
        self.__change_usr = Button(self, font=("Times New Roman", 12),
                                         background='White', activebackground='sky blue',
                                         fg="gray1", text="Изменить",
                                         width=15, command=lambda: self.__change_user())

        self.table = Table(self,
                                headings=('ID', 'Login', 'Password', 'FIO'), rows=data, counter=1)

        # Расположение полей ввода и т.д.
        # Place entryes on needed position etc, etc.
        self.__id_entry.place(relwidth=0.08,
                              relheight=0.05, relx=0.10, rely=0.70)
        self.__login_reg_entry.place(relwidth=0.15,
                                     relheight=0.05, relx=0.24, rely=0.70)
        self.__password_reg_entry.place(relwidth=0.15,
                                        relheight=0.05, relx=0.45, rely=0.70)
        self.__fio_reg_entry.place(relwidth=0.20,
                                   relheight=0.05, relx=0.66, rely=0.70)

        self.__id_label.place(relwidth=0.05,
                              relheight=0.05, relx=0.06, rely=0.70)
        self.__login_reg_label.place(relwidth=0.08,
                                     relheight=0.05, relx=0.17, rely=0.70)
        self.__password_reg_label.place(relwidth=0.08,
                                        relheight=0.05, relx=0.38, rely=0.70)
        self.__fio_reg_label.place(relwidth=0.06,
                                   relheight=0.05, relx=0.60, rely=0.70)

        self.table.place(relwidth=0.90,
                         relheight=0.50, relx=0.05, rely=0.05)

        self.__reg_button.place(relwidth=0.14,
                                relheight=0.06, relx=0.20, rely=0.85)
        self.__del_button.place(relwidth=0.14,
                                relheight=0.06, relx=0.35, rely=0.85)
        self.__clear_button.place(relwidth=0.14,
                                  relheight=0.06, relx=0.50, rely=0.85)
        self.__change_usr.place(relwidth=0.14,
                                relheight=0.06, relx=0.65, rely=0.85)

        # Lock on changing window size
        # Запрет на иземение размера окна
        self.resizable(width=False, height=False)

        self['bg'] = "gray10"

    def __new_user(self):
        try:
            list_ = [i.get() for i in self.__variables]
            check_ = [x for x in list_ \
                                       if x == ""]
        except Exception as exc:
            messagebox.showinfo("Ошибка", exc, parent=self)
        else:
            if check_:
                messagebox.showinfo("Ошибка:", "Заполните все поля", parent=self)
            else:
                message = "Добавить пользователя?"
                result = messagebox.askyesno(message=message, parent=self)
                if result:
                    try:
                        __request = "^".join(("REGISTER", *list_))
                        __received_data = Internet().IntoNetwork(data=__request)
                    except Exception as exc:
                        messagebox.showinfo("Ошибка", exc, parent=self)
                    else:
                        if __received_data == "Reg":
                            messagebox.showinfo("Внимание", "Пользователь успешно добавлен", parent=self)
                            new_user = [list_]
                            self.table.add_record(entry=new_user)
                        else:
                            messagebox.showinfo('Ошибка', 'Пользователь не добавлен', parent=self)
                else:
                    pass

    def __delete_user(self):
        try:
            id_ = self.ID.get()
        except Exception as exc:
            messagebox.showinfo("Ошибка", exc, parent=self)
        else:
            try:
                if id_ == "":
                    messagebox.showinfo("Ошибка", "Введите ID пользователя", parent=self)
                else:
                    message = "Удалить пользователя?"
                    result = messagebox.askyesno(message=message, parent=self)
                    if result:
                        __request = "^".join(("DELETEUSER", id_))
                        __received_data = Internet().IntoNetwork(data=__request)
                        if __received_data == "OK":
                            messagebox.showinfo("Внимание", "Пользователь удален из системы", parent=self)
                            self.table.remove_record(adr=self.Password.get(), regdate=self.FIO_empl.get())
                        else:
                            messagebox.showinfo('Ошибка', 'Пользователь не удален', parent=self)
                    else:
                        pass
            except Exception as exc:
                messagebox.showinfo("Ошибка", exc, parent=self)

    def __change_user(self):
        try:
            list_ = [i.get() for i in self.__variables]
            check_ = [x for x in list_ \
                                       if x == ""]
        except Exception as exc:
            messagebox.showinfo("Ошибка", exc, parent=self)
        else:
            if check_:
                messagebox.showinfo("Ошибка:", "Заполните все поля", parent=self)
            else:
                message = "Изменить пользователя?"
                result = messagebox.askyesno(message=message, parent=self)
                if result:
                    try:
                        __request = "^".join(("CHANGEUSER", *list_))
                        __received_data = Internet().IntoNetwork(data=__request)
                    except Exception as exc:
                        messagebox.showinfo("Ошибка", exc, parent=self)
                    else:
                        if __received_data == 'OK':
                            messagebox.showinfo("Внимание", f"Пользователь {list_[1]} изменён", parent=self)
                            self.table.change_record(trigger=list_[2], entry=[list_])
                        else:
                            messagebox.showinfo("Ошибка", "Пользователь не изменён", parent=self)
                else:
                    pass

class Search(Toplevel):

    def __init__(self, Parent, data=tuple()):
        super().__init__(Parent)


        self.__month_date, self.__employee,\
        self.__category, self.__year_date = \
                                            StringVar(), StringVar(), StringVar(), StringVar()

        MyLeftPos = (self.winfo_screenwidth() - 1200) / 2
        myTopPos = (self.winfo_screenheight() - 500) / 2

        self.geometry( "%dx%d+%d+%d" % (1200, 500, MyLeftPos, myTopPos))

        self.__date_search__label = Label(self, bg="gray10", fg="white",
                                                font=("Times New Roman", 12), text="Выберите месяц:")
        self.__year_search_label = Label(self, bg="gray10", fg="white",
                                               font=("Times New Roman", 12), text="Выберите год:")
        self.__employee_search_label = Label(self, bg="gray10", fg="white",
                                                   font=("Times New Roman", 12), text="ФИО Сотрудника:")
        self.__category_search_label = Label(self, bg="gray10", fg="white",
                                                   font=("Times New Roman", 12), text="Выберите категорию:")

        self.__employee_search_box = ttk.Combobox(self,
                                                       font=("Times New Roman", 12), style='my.TCombobox',
                                                       width=18, textvariable=self.__employee)

        self.__employee_search_box['values'] = ('Андрющенко Егор Валерьевич',
                                                'Кравцов Виктор Сергеевич',
                                                'Соболь Владислав Николаевич')

        self.__category_box = ttk.Combobox(self,
                                                font=("Times New Roman", 12), style='my.TCombobox',
                                                width=18, textvariable=self.__category)

        self.__category_box['values'] = ('Телевидение', 'Интернет', 'Пакет')

        self.__month_box = ttk.Combobox(self,
                                             font=("Times New Roman", 12), style='my.TCombobox',
                                             width=18, textvariable=self.__month_date)

        __month_dict = {'Январь': '.01.', 'Февраль': '.02.',
                        'Март': '.03.', 'Апрель': '.04.', 'Май': '.05.',
                        'Июнь': '.06.', 'Июль': '.07.', 'Август': '.08.',
                        'Сентябрь': '.09.', 'Октябрь': '.10.',
                        'Ноябрь': '.11.', 'Декабрь': '.12.', '': ''}

        self.__month_box['values'] = list(__month_dict.keys())[0:12]

        self.__year_box = ttk.Combobox(self,
                                            font=("Times New Roman", 12), style='my.TCombobox',
                                            width=18, textvariable=self.__year_date)

        self.__year_box['values'] = ('2021', '2022', '2023', '2024', '2025',\
                                     '2026', '2027', '2028', '2029', '2030')

        self.__table = Table(self, headings=('Дата выполнения заявки', 'ФИО', 'Адрес',
                                             'Телефон', 'Причина', 'Текущий ТП', 'Время выполнения',
                                             'Для Мастера', 'Мастер', 'Состояние заявки', 'Категория',
                                             'ФИО сотрудника', 'Дата регистрации'), rows=data, counter=2)

        entryes_tuple = (self.__category_box, self.__employee_search_box,
                         self.__month_box, self.__year_box)

        self.__search_button = Button(self, font=("Times New Roman", 12),
                                            background='White', activebackground='sky blue',
                                            fg="gray1", text="Найти",
                                            width=15, command=lambda: \
                                                                      self.__table.search_query(\
                                                                                                trigger=(__month_dict[self.__month_box.get()],
                                                                                                         self.__year_date.get(),
                                                                                                         self.__employee.get(),
                                                                                                         self.__category.get())))

        self.__clear_button = Button(self, font=("Times New Roman", 12),
                                           background='White', activebackground='sky blue',
                                           fg="gray1", text="Очистить поля",
                                           width=15, command=lambda: \
                                                                     Root.insert_in_entryes(entryes=entryes_tuple, dell=1))

        self.__update_button = Button(self, font=("Times New Roman", 12),
                                            background='White', activebackground='sky blue',
                                            fg="gray1", text="Обновить таблицу",
                                            width=15, command=self.query_all)

        self.__month_box.place(relwidth=0.15,
                               relheight=0.05, relx=0.31, rely=0.04)
        self.__year_box.place(relwidth=0.15,
                              relheight=0.05, relx=0.60, rely=0.04)
        self.__employee_search_box.place(relwidth=0.15,
                                         relheight=0.05, relx=0.31, rely=0.11)
        self.__category_box.place(relwidth=0.15,
                                  relheight=0.05, relx=0.60, rely=0.11)

        self.__date_search__label.place(relwidth=0.14,
                                        relheight=0.04, relx=0.19, rely=0.04)
        self.__year_search_label.place(relwidth=0.11,
                                       relheight=0.04, relx=0.50, rely=0.04)
        self.__employee_search_label.place(relwidth=0.15,
                                           relheight=0.04, relx=0.18, rely=0.11)
        self.__category_search_label.place(relwidth=0.15,
                                           relheight=0.04, relx=0.46, rely=0.11)

        self.__search_button.place(relwidth=0.15,
                                   relheight=0.06, relx=0.20, rely=0.20)
        self.__clear_button.place(relwidth=0.15,
                                  relheight=0.06, relx=0.40, rely=0.20)
        self.__update_button.place(relwidth=0.15,
                                   relheight=0.06, relx=0.60, rely=0.20)

        self.__table.place(relwidth=0.96,
                           relheight=0.65, relx=0.02, rely=0.30)

        self.resizable(width=False, height=False)

        self['bg'] = "gray10"

    def query_all(self):
        """Queries all records from server
           Запрашивает все заявки с сервера
        """
        try:
            __received_data = Internet().IntoNetwork(data="ALLQUERY")
            __sorted_data = next(Root.sorting_(received_data=__received_data))
            self.__table.update_table(rs=__sorted_data)
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc, parent=self)
        else:
            messagebox.showinfo("Внимание", "Таблица успешно обновлена!", parent=self)

class Authentication(Tk):

    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.__close)

        self.auth_list = [__Login, __Password,
                          Authentication.FIO_employee] = \
                                                         StringVar(), StringVar(), StringVar()
        self.__switch = IntVar()

        self.title("Авторизация:")

        MyLeftPos = (self.winfo_screenwidth() - 400) / 2
        myTopPos = (self.winfo_screenheight() - 200) / 2

        self.geometry("%dx%d+%d+%d" % (400, 200, MyLeftPos, myTopPos))

        self.__login_label = Label(self, bg="gray10",
                                         fg="white", font=("Times New Roman", 12),
                                         text="Введите Логин:")
        self.__password_label = Label(self, bg="gray10",
                                            fg="white", font=("Times New Roman", 12),
                                            text="Введите пароль:")

        self.__login_entry = Entry(self, selectforeground='gray1', selectbackground='sky blue',
                                         font=("Times New Roman", 12), fg='gray1',
                                         textvariable=__Login, width=40)
        self.__password_entry = Entry(self, selectforeground='gray1', selectbackground='sky blue',
                                            font=("Times New Roman", 12), fg='gray1',
                                            textvariable=__Password, width=40, show="*")

        self.__entr_button = Button(self, font=("Times New Roman", 12),
                                          background='White', activebackground='sky blue',
                                          fg="gray1", text="Войти", width=15,
                                          command=lambda: self.__main_window())

        self.__entr_button.bind('<Return>', lambda x: self.__main_window())
        self.__password_entry.bind('<Return>', lambda x: self.__main_window())

        self.__chkbtn = Checkbutton(self, activeforeground='White',
                                          activebackground='gray10', bg="gray10",
                                          font=("Times New Roman", 12), fg='White',
                                          text="Показать пароль", selectcolor='gray10',
                                          variable=self.__switch, onvalue=1, offvalue=0,
                                          command=lambda: self.__show_pas())

        self.__entr_button.place(relwidth=0.30,
                                 relheight=0.16, relx=0.10, rely=0.75)
        self.__login_entry.place(relwidth=0.40,
                                 relheight=0.12, relx=0.45, rely=0.30)
        self.__password_entry.place(relwidth=0.40,
                                    relheight=0.12, relx=0.45, rely=0.50)
        self.__login_label.place(relwidth=0.30,
                                 relheight=0.12, relx=0.10, rely=0.30)
        self.__password_label.place(relwidth=0.30,
                                    relheight=0.12, relx=0.10, rely=0.50)
        self.__chkbtn.place(relwidth=0.35,
                            relheight=0.12, relx=0.06, rely=0.07)

        self.resizable(width=False, height=False)
        self['bg'] = "gray10"

    def __close(self):
        try:
            self.destroy()
            os._exit(0)
        except (OSError, Exception) as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __show_pas(self):
        try:
            if self.__switch.get():
                self.__password_entry.config(show="")
            else:
                self.__password_entry.config(show="*")
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

    def __main_window(self):
        """If Authentication is complete
           destroys Authentication window
           and calls Root
           Если авторизация прошла успешно
           вызывает self.destroy() и запускает
           главное окно
        """
        try:
            list_ = [i.get() for i in self.auth_list]
            __check = [__x for __x in list_[0:2] \
                                                 if __x == '' or len(__x) > 30]
        except (UnboundLocalError, TypeError) as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            if __check:
                messagebox.showinfo("Ошибка", "Поля заполнены некорректно")
            else:
                try:
                    __request = "^".join(("ENTER", *list_[0:2]))
                    __received_data = Internet().IntoNetwork(data=__request)
                except Exception as exc:
                    messagebox.showinfo("Ошибка", exc)
                else:
                    try:
                        if __received_data:
                            __data_message = __received_data.split("^")
                            if __data_message[0] == "GO":
                                Authentication.FIO_employee = __data_message[1]
                                self.destroy()
                                time.sleep(0.5)
                                self.main_function()
                            elif __data_message[0] == "NOLOG":
                                messagebox.showinfo("Ошибка", "Нет такого пользователя!")
                            elif __data_message[0] == "Fail":
                                messagebox.showinfo("Ошибка", "Неправильный пароль!")
                            else:
                                messagebox.showinfo("Ошибка", "Ошибка сервера!")
                        else:
                            messagebox.showinfo("Ошибка", "Ошибка при покдлючении!")
                    except (Exception, IndexError) as exc:
                        messagebox.showinfo("Ошибка", exc)

    def main_function(self):
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
                __received_data = Internet().IntoNetwork(data='^'.join(["CURQUERY",__d_strg]))
                if __received_data == 'No':
                    time.sleep(0.2)
                    Authentication.mainroot = Root()
                    Root.isfull_label.configure(text="На сегодня заявок нет")
                else:
                    __sorted_data = next(Root.sorting_(received_data=__received_data))
                    time.sleep(0.2)
                    Authentication.mainroot = Root(__sorted_data)
                    Root.isfull_label.configure(text="Заявки на сегодня:")
            except Exception as exc:
                messagebox.showinfo("Ошибка:", exc)

class Root(Tk):
    """Main window class, inherites Tk class"""

    def __init__(self, data=list()):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.__confirm_exit)

        self.__variables = [self.Date, self.FIO, self.address, self.telephone,
                            self.reason, self.tariff, self.information, self.for_master,
                            Root.master, Root.r_var, self.Category, self.RegDate] = \
                                                                                    StringVar(), StringVar(), StringVar(), StringVar(),\
                                                                                    StringVar(), StringVar(), StringVar(), StringVar(),\
                                                                                    StringVar(), StringVar(), StringVar(), StringVar()
        Root.r_var.set('Открыта')
        self.user = Authentication.FIO_employee
        self.title(self.user)

        MyLeftPos = (self.winfo_screenwidth() - 1200) / 2
        myTopPos = (self.winfo_screenheight() - 600) / 2

        self.geometry("%dx%d+%d+%d" % (1200, 600, MyLeftPos, myTopPos))

        Root.table = Table(self, headings=('Дата выполнения заявки', 'ФИО', 'Адрес',
                                           'Телефон', 'Причина', 'Текущий ТП', 'Время выполнения',
                                           'Для Мастера', 'Мастер', 'Состояние заявки', 'Категория',
                                           'ФИО сотрудника', 'Дата регистрации'), rows=data)

        style = ttk.Style()

        style.configure('my.DateEntry',
                                       selectforeground='gray1',
                                       selectbackground='sky blue')
        style.configure('my.TCombobox',
                                       selectforeground='gray1',
                                       selectbackground='sky blue')

        __now = datetime.now()
        __y_string = __now.strftime("%Y")
        __d_string = __now.strftime("%d-%m-%Y")
        __k_str = ': '.join(('Сегодня', __d_string))

        self.FIO_entry = Entry(self, selectforeground='gray1',
                                     selectbackground='sky blue', font=("Times New Roman", 12),
                                     textvariable=self.__variables[1], width=18)
        self.address_entry = Entry(self, selectforeground='gray1',
                                         selectbackground='sky blue', font=("Times New Roman", 12),
                                         textvariable=self.__variables[2], width=18)
        self.telephone_entry = Entry(self, selectforeground='gray1',
                                           selectbackground='sky blue', font=("Times New Roman", 12),
                                           textvariable=self.__variables[3], width=18)
        self.reason_entry = Entry(self, selectforeground='gray1',
                                        selectbackground='sky blue', font=("Times New Roman", 12),
                                        textvariable=self.__variables[4], width=18)
        self.tariff_entry = Entry(self, selectforeground='gray1',
                                        selectbackground='sky blue', font=("Times New Roman", 12),
                                        textvariable=self.__variables[5], width=18)
        self.information_entry = Entry(self, selectforeground='gray1',
                                             selectbackground='sky blue', font=("Times New Roman", 12),
                                             textvariable=self.__variables[6], width=18)
        self.for_master_entry = Entry(self, selectforeground='gray1',
                                            selectbackground='sky blue', font=("Times New Roman", 12),
                                            textvariable=self.__variables[7], width=18)
        self.master_entry = Entry(self, selectforeground='gray1',
                                        selectbackground='sky blue', font=("Times New Roman", 12),
                                        textvariable=self.__variables[8], width=18)

        self.__cal = DateEntry(self,
                                    font=("Times New Roman", 12), style='my.DateEntry',
                                    textvariable=self.__variables[0], width=18,
                                    borderwidth=2, year=int(__y_string),
                                    date_pattern='dd.MM.yyyy')

        self.__monthchoosen = ttk.Combobox(self,
                                                font=("Times New Roman", 12), style='my.TCombobox',
                                                width=18, textvariable=self.__variables[10])

        self.__monthchoosen['values'] = ('Телевидение', 'Интернет', 'Пакет')

        self.entryes_tuple = (self.FIO_entry, self.address_entry,
                              self.telephone_entry, self.reason_entry,
                              self.tariff_entry, self.information_entry,
                              self.for_master_entry, self.master_entry,
                              self.__monthchoosen,  self.__cal)

        self.__category_label = Label(self,
                                           bg="gray10", fg="white",
                                           font=("Times New Roman", 12),
                                           text="Выберите категорию:")
        self.__FIO_label = Label(self,
                                      bg="gray10", fg="white",
                                      font=("Times New Roman", 12),
                                      text="Введите ФИО:")
        self.__address_label = Label(self,
                                          bg="gray10", fg="white",
                                          font=("Times New Roman", 12),
                                          text="Введите адресс:")
        self.__telephone_label = Label(self,
                                            bg="gray10", fg="white",
                                            font=("Times New Roman", 12),
                                            text="Введите телефон:")
        self.__reason_label = Label(self,
                                         bg="gray10", fg="white",
                                         font=("Times New Roman", 12),
                                         text="Введите причину:")
        self.__tariff_label = Label(self,
                                         bg="gray10", fg="white",
                                         font=("Times New Roman", 12),
                                         text="Введите текущий ТП:")
        self.__information_label = Label(self,
                                              bg="gray10", fg="white",
                                              font=("Times New Roman", 12),
                                              text="Время выполнения заявки:")
        self.__for_master_label = Label(self,
                                             bg="gray10", fg="white",
                                             font=("Times New Roman", 12),
                                             text="Пометка для мастера:")
        self.__master_label = Label(self,
                                         bg="gray10", fg="white",
                                         font=("Times New Roman", 12),
                                         text="Выполняет мастер:") 
        self.__record_value_label = Label(self,
                                               bg="gray10", fg="white",
                                               font=("Times New Roman", 12),
                                               text="Информация по заявке:")
        self.__data_label = Label(self,
                                       bg="gray10", fg="white",
                                       font=("Times New Roman", 12),
                                       text="Выберите дату:")
        self.__clock = Label(self,
                                  bg="gray10", fg="white",
                                  font=("Times New Roman", 12))
        self.__curdate = Label(self,
                                    bg="gray10", fg="white",
                                    font=("Times New Roman", 12), text=__k_str)
        Root.isfull_label = Label(self,
                                       bg="gray10", fg="white",
                                       font=("Times New Roman", 12))

        self.__tick()

        self.__r1 = Radiobutton(self, activeforeground='White',
                                      activebackground='gray10', bg="gray10",
                                      font=("Times New Roman", 12), fg='White',
                                      text='Открыта', selectcolor='gray10',
                                      variable=self.r_var, value='Открыта')

        self.__r2 = Radiobutton(self, activeforeground='White',
                                      activebackground='gray10', bg="gray10",
                                      font=("Times New Roman", 12), fg='White',
                                      text='Закрыта', selectcolor='gray10',
                                      variable=self.r_var, value='Закрыта')

        self.__delete_button = Button(self, font=("Times New Roman", 12),
                                            background='White', activebackground='sky blue',
                                            fg="gray1", text="Удалить запись",
                                            width=15, command=lambda: self.delete_record(trigger=[self.RegDate.get(),\
                                                                                                  self.Date.get(),\
                                                                                                  self.address.get(),\
                                                                                                  self.FIO.get()]))

        self.__add_button = Button(self, font=("Times New Roman", 12),
                                         background='White', activebackground='sky blue',
                                         fg="gray1", text="Сохранить запись",
                                         width=15, command=self.insert_into)

        self.__srch_button = Button(self, font=("Times New Roman", 12),
                                          background='White', activebackground='sky blue',
                                          fg="gray1", text="Поиск",
                                          width=15, command=self.search_window)

        self.__update_button = Button(self, font=("Times New Roman", 12),
                                            background='White', activebackground='sky blue',
                                            fg="gray1", text="Изменить запись",
                                            width=15, command=self.change_record)

        self.__clear_button = Button(self, font=("Times New Roman", 12),
                                           background='White', activebackground='sky blue',
                                           fg="gray1", text="Очистить поля", width=15,
                                           command=lambda: self.insert_in_entryes(\
                                                                                  entryes=self.entryes_tuple, dell=1))

        self.root_tuple = (self.__category_label, self.__FIO_label,
                           self.__address_label, self.__telephone_label,
                           self.__reason_label, self.tariff_entry,
                           self.__information_label, self.__for_master_label,
                           self.__master_label, self.__record_value_label,
                           self.__data_label, *self.entryes_tuple, self.__r1,
                           self.__r2, self.__cal, self.__monthchoosen,
                           self.__delete_button, self.__add_button, self.__srch_button,
                           self.__update_button, self.__clear_button, self.__tariff_label)

        self.__menu_visibility = True
        self.bind("<Control-Key-o>",
                                    lambda x: self.hide_menu() if self.__menu_visibility \
                                                               else self.show_menu())

        __m = Menu(self)
        __m_edit = Menu(__m, font=("Times New Roman", 11),
                             activebackground='sky blue',
                             activeforeground='gray1',
                             tearoff=0)
        __m.add_cascade(menu=__m_edit, label="Меню")
        __m_edit.add_command(label="Скрыть меню",
                             command=self.hide_menu)
        __m_edit.add_command(label="Показать меню", command=self.show_menu)
        __m_edit.add_separator()
        __m_edit.add_command(label="Экспорт в Excel",
                             command=lambda: self.table.Export(heading=('Дата выполнения заявки', 'ФИО', 'Адрес', 'Телефон',
                                                                        'Причина', 'Текущий ТП', 'Время выполнения',
                                                                        'Для Мастера', 'Мастер', 'Состояние заявки',
                                                                        'Категория', 'ФИО сотрудника', 'Дата регистрации')))

        __m_search = Menu(__m, font=("Times New Roman", 11),
                               activebackground='sky blue',
                               activeforeground='gray1',
                               tearoff=0)
        __m.add_cascade(menu=__m_search, label="Быстрый поиск")
        __m_search.add_command(label="По категории",
                               command=lambda: self.search(ID=1))
        __m_search.add_command(label="По дате",
                               command=lambda: self.search(ID=2))
        __m_search.add_command(label="По ФИО",
                               command=lambda: self.search(ID=3))

        __m_table = Menu(__m, font=("Times New Roman", 11),
                              activebackground='sky blue',
                              activeforeground='gray1',
                              tearoff=0)
        __m.add_cascade(menu=__m_table, label="Таблица")
        __m_table.add_command(label="Все заявки/Обновить",
                              command=self.query_all)
        __m_table.add_command(label="Добавить запись",
                              command=self.insert_into)

        __m_about = Menu(__m, font=("Times New Roman", 11),
                              activebackground='sky blue',
                              activeforeground='gray1',
                              tearoff=0)
        __m.add_cascade(menu=__m_about, label="О программе")
        __m_about.add_command(label="Инструкция пользователя", command=self.instruction)

        __m.add_command(label="Выйти", command=self.__confirm_exit)

        try:
            if self.user == 'Андрющенко Егор Валерьевич' or\
               self.user == 'Соболь Владислав Николаевич' or\
               self.user == 'Кравцов Виктор Сергеевич':
                   __m.add_command(label="Администрирование", command=self.registration_window)
        except (Exception, TypeError) as exc:
            messagebox.showinfo("Ошибка:", exc)

        self.columnconfigure(1, weight=1)
        self['menu'] = __m
        self['bg'] = "gray10"
        self.show_menu()

    @staticmethod
    def insert_in_entryes(entryes=list(), dell=int()):
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

    @staticmethod
    def sorting_(received_data=list()):
        """Sorting incoming messages
           Сортирует входящие сообщения
        """
        try:
            __data_message = received_data.split('#^')
            __received_msg = (__s.split('^') for __s in __data_message)
            __received_msg = (__x for __x in __received_msg \
                                                            if __x != ('',))
        except (AttributeError, TypeError) as err:
            messagebox.showinfo("Ошибка", err)
        else:
            yield __received_msg

    def instruction(self):
        """This function purpose is to open file
           on local share(Instruction)
        """
        share_dir = r'\\172.20.20.3\share\3. Документы\Инструкция(Заявки)\index.html'
        os.startfile(share_dir)

    def query_all(self):
        """Queries all records from server
           Запрашивает все заявки с сервера
        """
        try:
            __received_data = Internet().IntoNetwork(data="ALLQUERY")
            __sorted_data = next(self.sorting_(received_data=__received_data))
            self.table.update_table(rs=__sorted_data)
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            messagebox.showinfo("Внимание", "Таблица успешно обновлена!")

    def insert_into(self):
        """Sending records to server with
           keyword to trigger INSERT query
           in db on remote TCP server
           Посылает запрос на сервер
           с ключевым словом INSERT
           чтобы добавить заявку в БД
        """
        message = "       Вы уверены?"
        result = messagebox.askyesno(message=message, parent=self)
        if result:
            try:
                __now = datetime.now()
                __d_string = __now.strftime("%d-%m-%Y")
                list_ = [i.get() for i in self.__variables]
                __variables = [*list_[1:5], *list_[6:11], self.user,
                               __d_string, list_[0], list_[5]]
                __pattern = r'[A-Za-z]'
                __check = [__z for __z in __variables \
                                                      if __z == '' \
                                                                   or len(__z) > 100 \
                                                                   or re.findall(__pattern, __z)]
            except Exception as exc:
                messagebox.showinfo("Ошибка:", exc)
            else:
                try:
                    if __check:
                        messagebox.showinfo("Ошибка", "Ошибка в тексте!")
                    else:
                        if self.r_var.get() == 'Закрыта':
                            messagebox.showinfo("Внимание", "Заявка в закрытом состоянии")
                        else:
                            __request = "^".join(("INSERT", *__variables))

                            __received_data = Internet().IntoNetwork(data=__request)
                            self.isfull_label.configure(text="")
                            messagebox.showinfo("Data:", __received_data)
                            __list_for_table = [[__variables[11], *__variables[0:4],
                                                 __variables[12], *__variables[4:11]]]
                            self.table.add_record(entry=__list_for_table)
                except (IndexError, Exception, TypeError) as exc:
                    messagebox.showinfo("Ошибка:", exc)
        else:
            pass

    def search(self, ID):
        """searching in our table for
           record, with parameters which
           correspond to the requested
           Ищем в нашей таблице запись,
           чьи параметры соответсвуют запрошенным
        """
        try:
            __pattern = r'[A-Za-z]'
            if ID == 1:
                __CAT = self.Category.get()
                if __CAT == '' or re.findall(__pattern, __CAT):
                    messagebox.showinfo("Ошибка", "Заполните поле категории корректно!")
                else:
                    self.table.search_query(trigger=__CAT)
            elif ID == 2:
                __DATE = self.Date.get()
                if __DATE == '' or re.findall(__pattern, __DATE):
                    messagebox.showinfo("Ошибка", "Выберите дату корректно!")
                else:
                    self.table.search_query(trigger=__DATE)
            elif ID == 3:
                __FIO = self.FIO.get()
                if __FIO == '' or re.findall(__pattern, __FIO):
                    messagebox.showinfo("Ошибка", "Заполните поле ФИО корректно!")
                else:
                    self.table.search_query(trigger=__FIO)
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

    def connect(self, trigger):
        __request = "^".join(("DELETE", *trigger))
        __received_data = Internet().IntoNetwork(data=__request)
        messagebox.showinfo("Data:", __received_data)
        self.table.remove_record(trigger)

    def delete_record(self, trigger):
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

        message = "Вы уверены, что хотите удалить заявку?"
        result = messagebox.askyesno(message=message, parent=self)
        if result:
            try:
                if self.r_var.get() == "Открыта":
                    message = "Заявка в открытом состоянии,\
                               \nвы уверены что хотите удалить заявку?"
                    result = messagebox.askyesno(message=message, parent=self)
                    if result:
                        self.connect(trigger)
                    else:
                        pass
                else:
                    self.connect(trigger)
            except Exception as exc:
                messagebox.showinfo("Ошибка:", exc)
        else:
            pass

    def change_record(self):
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
            list_ = [i.get() for i in self.__variables]
            __variables = [*list_[1:5], *list_[6:12], list_[0], list_[5]]
            __pattern = r'[A-Za-z]'
            __check = [__z for __z in __variables \
                                                  if __z == '' or len(__z) > 100 \
                                                                                 or re.findall(__pattern, __z)]
        except (TypeError, Exception, UnboundLocalError) as exc:
            messagebox.showinfo("Ошибка:", exc)
        else:
            try:
                if __check:
                    messagebox.showinfo("Ошибка", "Ошибка в тексте!")
                else:
                    message = "Вы уверены, что хотите изменить заявку?"
                    result = messagebox.askyesno(message=message, parent=self)
                    __gr_var = [[__variables[10], *__variables[0:4], __variables[11],
                                 *__variables[4:9], 'User', __variables[9]]]
                    if result:
                        __request = "^".join(("UPDATE", *__variables))
                        __received_data = Internet().IntoNetwork(data=__request)
                        messagebox.showinfo("Data:", __received_data)
                        self.table.change_record(trigger=[__variables[9], __variables[0],\
                                                          __variables[10], __variables[1]], entry=__gr_var)
                    else:
                        pass
            except (Exception, IndexError) as exc:
                messagebox.showinfo("Ошибка:", exc)

    def registration_window(self):
        """Sending keyword USERQUERY to our server
           wich triggers QUERY ALL command
           in db on server from user table
           Отправляет ключевое слово USERQUERY
           на сервер, которые вызывает QUERY ALL
           запрос в БД из нашей таблицы с пользователями
        """
        try:
            __received_data = Internet().IntoNetwork(data="USERQUERY^")
            __sorted_data = next(self.sorting_(received_data=__received_data))
            Root.reg_window = Registration(self, __sorted_data)
        except (Exception, UnboundLocalError) as exc:
            messagebox.showinfo("Ошибка:", exc)
            raise

    def search_window(self):
        """Open window for search"""
        try:
            __received_data = Internet().IntoNetwork(data="ALLQUERY^")
            __sorted_data = next(self.sorting_(received_data=__received_data))
            Root.search_window_ = Search(self, data=__sorted_data)
        except (Exception, UnboundLocalError) as exc:
            messagebox.showinfo("Ошибка:", exc)
            raise

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
            os._exit(1)

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

    def hide_menu(self):
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
            [__i.place_forget() for __i in self.root_tuple]
            self.table.place(relwidth=0.98,
                             relheight=0.90, relx=0.01, rely=0.05)
            self.__curdate.place(relwidth=0.13,
                                 relheight=0.03, relx=0.01, rely=0.01)
            self.isfull_label.place(relwidth=0.15,
                                    relheight=0.03, relx=0.43, rely=0.01)
            time.sleep(0.2)
            self.__menu_visibility = False
        except Exception as exc:
            messagebox.showinfo("Ошибка:", exc)

    def show_menu(self):
        """Show hidden menu
           and putting table with
           records in it's place
           Показывает спрятанное меню
           и возвращает таблицу с заявками
           на место
        """
        time.sleep(0.2)
        self.update_idletasks()
        self.__category_label.place(relwidth=0.12,
                                    relheight=0.03, relx=0.05, rely=0.05)
        self.__FIO_label.place(relwidth=0.10,
                               relheight=0.03, relx=0.08, rely=0.10)
        self.__address_label.place(relwidth=0.09,
                                   relheight=0.03, relx=0.08, rely=0.15)
        self.__telephone_label.place(relwidth=0.12,
                                     relheight=0.03, relx=0.06, rely=0.20)
        self.__reason_label.place(relwidth=0.12,
                                  relheight=0.03, relx=0.06, rely=0.25)
        self.__tariff_label.place(relwidth=0.12,
                                  relheight=0.03, relx=0.05, rely=0.30)
        self.__information_label.place(relwidth=0.15,
                                       relheight=0.03, relx=0.02, rely=0.35)
        self.__for_master_label.place(relwidth=0.12,
                                      relheight=0.03, relx=0.05, rely=0.40)
        self.__master_label.place(relwidth=0.11,
                                  relheight=0.03, relx=0.06, rely=0.45)
        self.__record_value_label.place(relwidth=0.15,
                                        relheight=0.03, relx=0.03, rely=0.61)
        self.__data_label.place(relwidth=0.09,
                                relheight=0.03, relx=0.08, rely=0.52)
        self.isfull_label.place(relwidth=0.15,
                                relheight=0.03, relx=0.63, rely=0.01)

        self.FIO_entry.place(relwidth=0.18,
                             relheight=0.04, relx=0.18, rely=0.10)
        self.address_entry.place(relwidth=0.18,
                                 relheight=0.04, relx=0.18, rely=0.15)
        self.telephone_entry.place(relwidth=0.18,
                                   relheight=0.04, relx=0.18, rely=0.20)
        self.reason_entry.place(relwidth=0.18,
                                relheight=0.04, relx=0.18, rely=0.25)
        self.tariff_entry.place(relwidth=0.18,
                                relheight=0.04, relx=0.18, rely=0.30)
        self.information_entry.place(relwidth=0.18,
                                     relheight=0.04, relx=0.18, rely=0.35)
        self.for_master_entry.place(relwidth=0.18,
                                    relheight=0.04, relx=0.18, rely=0.40)
        self.master_entry.place(relwidth=0.18,
                                relheight=0.04, relx=0.18, rely=0.45)

        self.__r1.place(relwidth=0.08,
                        relheight=0.03, relx=0.18, rely=0.61)
        self.__r2.place(relwidth=0.08,
                        relheight=0.03, relx=0.28, rely=0.61)

        self.table.place(relwidth=0.60,
                         relheight=0.90, relx=0.38, rely=0.05)
        self.__monthchoosen.place(relwidth=0.18,
                                  relheight=0.04, relx=0.18, rely=0.05)
        self.__cal.place(relwidth=0.18,
                         relheight=0.05, relx=0.18, rely=0.51)

        self.__add_button.place(relwidth=0.16,
                                relheight=0.05, relx=0.01, rely=0.70)
        self.__srch_button.place(relwidth=0.16,
                                 relheight=0.05, relx=0.01, rely=0.90)
        self.__update_button.place(relwidth=0.16,
                                   relheight=0.05, relx=0.20, rely=0.70)
        self.__clear_button.place(relwidth=0.16,
                                  relheight=0.05, relx=0.20, rely=0.90)

        self.__clock.place(relwidth=0.05,
                           relheight=0.03, relx=0.93, rely=0.01)
        self.__curdate.place(relwidth=0.13,
                             relheight=0.03, relx=0.38, rely=0.01)
        time.sleep(0.2)
        self.__menu_visibility = True
        # if username is equal to administrator username
        # show administration panel
        # если имя пользователя соответствует имени админа
        # в меню добавляется панель администратора
        try:
            if self.user == 'Андрющенко Егор Валерьевич' or\
               self.user == 'Соболь Владислав Николаевич' or\
               self.user == 'Кравцов Виктор Сергеевич':
                    self.__delete_button.place(relwidth=0.16,
                                               relheight=0.05, relx=0.10, rely=0.80)
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