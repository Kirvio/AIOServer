from tkinter import END

def InsertInEntryes(entryes = tuple(), dell = int()):
    if dell == 1:
        [__i.delete(0, END) for __i in entryes]
    else:
        [[__i.delete(0, END), __i.insert(0, __d)] for __i, __d in entryes]
      
def center(win):

    win.update_idletasks()
    __width = win.winfo_width()

    __frm_width = win.winfo_rootx() - win.winfo_x()
    __win_width = __width + 2 * __frm_width

    __height = win.winfo_height()
    __titlebar_height = win.winfo_rooty() - win.winfo_y()

    __win_height = __height + __titlebar_height + __frm_width

    __x = win.winfo_screenwidth() // 2 - __win_width // 2
    __y = win.winfo_screenheight() // 2 - __win_height // 2

    win.geometry('{}x{}+{}+{}'.format(__width, __height, __x, __y))
    win.deiconify()  