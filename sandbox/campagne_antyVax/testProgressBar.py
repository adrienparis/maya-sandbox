from tkinter import *
from tkinter.ttk import *
import time

ws = Tk()
ws.title('Searching Files')
# ws.geometry('400x250+1000+300')

def step():
    for i in range(200):
        ws.update_idletasks()
        pb1['value'] += 1
        percent.set("{} %".format(i))
        time.sleep(0.01)

pb1 = Progressbar(ws, orient=HORIZONTAL,  mode='indeterminate')
pb1.pack(expand=True)
percent = StringVar()
statusLabel = Label(ws, textvariable=percent).pack()

Button(ws, text='Start', command=step).pack()

ws.mainloop()