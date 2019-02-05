from Tkconstants import *
from Tkinter import Button, Frame


class Menu(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid_columnconfigure(0, weight=1)

        self.first = Button(self, text="Grayscale", command=self.gray_scale)
        self.first.grid(row=0, column=0, sticky=W + E, padx=20, pady=5)

        self.second = Button(self, text="second", command=self.command)
        self.second.grid(row=1, column=0, sticky=W + E, padx=20, pady=5)

        self.grid(row=0, column=0, rowspan=4, sticky=N + W + E + S)

    def command(self):
        print "do command"

    def gray_scale(self):
        print "asd"
