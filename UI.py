import os, inspect 
import re
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import * 
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import font
import queue as Queue
import threading
import complaint_handler
from selenium import webdriver
import urllib
from urllib.request import urlopen
import socket
import time

current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0]))


class ComplaintHandlerUI(tk.Tk):
    def __init__(self, queue, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.queue = queue

        self.geometry("400x460")
        self.title("CATSWeb Automation Tool")
        self.iconbitmap('Jnj32.ico')
        self.configure(background="#FFFFFF")

        container = Frame(self)

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginPage, PageOne):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(background="#FFFFFF")

        self.show_frame(LoginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.running = 1
        self.queue = controller.queue
        self.flagQueue = Queue.Queue()
        self.controller = controller

        style = Style()
        #style.configure("BW.TLabel", font = ('Helvetica','10'),foreground="#64B23B")
        #style.configure("BW.TButton", font = ('Helvetica','10'), foreground="#64B23B", background="#FFFFFF")
        style.configure("BW.TEntry", background = "gray90")

        imgFile = '\\\\'.join(os.path.join(current_folder,"jnj.gif").split('\\'))
        img = tk.PhotoImage(file='jnjGIF.gif')      
        self.logo = Label(self, image=img)
        self.logo.image = img

        self.message = Label(self, text="Please enter your login information:")
        self.message.config(font = ('Helvetica','12'), foreground="#638213", background="#FFFFFF")
        self.loginStatusMsg = Label(self, text='', font = ('Helvetica','10'), foreground="black", background="#FFFFFF")
        self.authorName = Label(self, text=u'\u00a9'+" Designed & Developed by Prashanth Kumar & Andrew Jesiah")
        self.authorName.config(font = ('Montserrat','8'),foreground="#112D25", background="#FFFFFF")

        large_font = ('Verdana',17)

        self.UserEntry = Entry(self,style="BW.TEntry", font=large_font,foreground = 'grey')
        self.UserEntry.insert(0, 'Employee ID')
        self.UserEntry.bind('<FocusIn>', self.on_Userentry_click)
        self.UserEntry.bind('<FocusOut>', self.on_Userfocusout)
        self.UserEntry.bind('<Return>', lambda x: self.clicked(self.UserEntry.get(), self.PassEntry.get()))

        self.PassEntry = Entry(self,style="BW.TEntry", font=large_font, foreground = 'grey')
        self.PassEntry.insert(0, 'Password')
        self.PassEntry.bind('<FocusIn>', self.on_Passentry_click)
        self.PassEntry.bind('<FocusOut>', self.on_Passfocusout)
        self.PassEntry.bind('<Return>', lambda x: self.clicked(self.UserEntry.get(), self.PassEntry.get()))
        
        '''
        self.signal = tk.Canvas(self,width=15, height=15)
        self.signal.place(x='470', y='220')
        self.catsWebLabel = Label(self, text='CATSWeb',style='BW.TLabel')
        self.catsWebLabel.place(x='390', y='220')
        '''
        helv36 = font.Font(family='Helvetica', size=11)
        self.btn = tk.Button(self, text="Login", command=lambda: self.clicked(self.UserEntry.get(), self.PassEntry.get()))
        self.btn.config(relief='flat', bg='#737370', fg="#FFFFFF", height=2, width=33)
        self.btn['font'] = helv36

        self.internet = Label(self, text="Checking...")
        self.internet.config(font = ('Helvetica','11'), foreground="black", background="#FFFFFF")

        self.logo.place(x='200', y='50', anchor='center')
        self.message.place(x='200', y='115', anchor="center")
        self.loginStatusMsg.place(x='200', y='170', anchor="center")
        self.UserEntry.place(x='47', y='200')
        self.PassEntry.place(x='47', y='260')
        self.btn.place(x='47', y='325')
        self.authorName.place(x='87', y='442')
        #self.internet.place(x='270', y='400')


    def on_Userentry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.UserEntry.get() == 'Employee ID':
           self.UserEntry.delete(0, "end") # delete all the text in the entry
           self.UserEntry.insert(0, '') #Insert blank for user input
           self.UserEntry.config(foreground = 'black')

    def on_Userfocusout(self, event):
        if self.UserEntry.get() == '':
            self.UserEntry.insert(0, 'Employee ID')
            self.UserEntry.config(foreground = 'grey')

    def on_Passentry_click(self,event): 
        if self.PassEntry.get() == 'Password':
           self.PassEntry.delete(0, "end") # delete all the text in the entry
           self.PassEntry.insert(0, '') #Insert blank for user input
           self.PassEntry.config(show="*",foreground = 'black')

    def on_Passfocusout(self, event):
        if self.PassEntry.get() == '':
            self.PassEntry.insert(0, 'Password')
            self.PassEntry.config(show="",foreground = 'grey')


    def clicked(self, ID, password):
        if ID == 'Employee ID' or len(ID) == 0:
            messagebox.showinfo('Error!', 'Enter Employee ID')
            return
        if password == 'Password' or len(password) == 0:
            messagebox.showinfo('Error!', 'Enter Password')
            return
        
        self.running = 1
        self.message.config(text='')
        self.UserEntry.unbind('<Return>')
        self.PassEntry.unbind('<Return>')
        self.UserEntry.config(state='disabled')
        self.PassEntry.config(state='disabled')
        self.loginStatusMsg.config(text='Logging in... Please wait')
        self.thread1 = threading.Thread(target=self.workerThread1, args=(ID, password))
        self.thread1.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
        self.thread1.start()


    def workerThread1(self, ID, password):
        while self.running:
            self.btn.config(state = 'disabled')
            loginMsg, url, flag = complaint_handler.Login(ID, password)

            if flag:
                self.message.config(text='Please enter your login information:', font = ('Helvetica','11'), foreground="#638213", background="#FFFFFF")
                self.queue.put(url)
                self.controller.show_frame(PageOne)
                print("Logged in!")
                print('---------------------------------------------')

            else:
                self.message.config(text=loginMsg, font = ('Helvetica','11'), foreground="#E26C1B", background="#FFFFFF")
                self.btn.config(state = 'normal')
                self.UserEntry.bind('<Return>', lambda x: self.clicked(self.UserEntry.get(), self.PassEntry.get()))
                self.PassEntry.bind('<Return>', lambda x: self.clicked(self.UserEntry.get(), self.PassEntry.get()))
                print('Invalid login, please try again.')
                print('----------------------------------------')

            self.UserEntry.config(state='normal')
            self.PassEntry.config(state='normal')
            self.PassEntry.delete(0, 'end')
            self.PassEntry.insert(0, 'Password')
            self.PassEntry.config(show="",foreground = 'grey')
            self.running = 0
            self.loginStatusMsg.config(text='')


    
class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.count = 0
        self.running = 1
        self.t1 = time.time()
        self.main_url = ''
        self.treeSelection = ''
        self.queue = controller.queue
        self.infoQueue = Queue.Queue()
        self.CFnumQueue = Queue.Queue()
        self.flagQueue = Queue.Queue()
        self.controller = controller
        
        self.login_page = self.controller.get_page(LoginPage)

        style = Style()
        style.configure("BW.TLabel", font = ('Montserrat','10', 'bold'),foreground="#112D25", background="#DBDDDC")
        style.configure("BW.TButton", font = ('Montserrat','10','bold'), foreground="#112D25", background="#DBDDDC")
        style.configure("BW.TEntry", background="gray90")
        style.configure("BW.TCheck", foreground="#112D25", background="#FFFFFF")
        
        self.CF_number = Label(self, text="Complaint Folder:", style="BW.TLabel")
        self.CF_number.config(font = ('Helvetica','10','bold'), foreground="#112D25", background="#FFFFFF")

        self.CFnum = Entry(self, validate="key", validatecommand=(self.register(self.validate), '%P'))
        #self.CFnum = Entry(self)

        self.msg = Label(self, style="BW.TLabel")
        
        self.authorName = Label(self, text=u'\u00a9'+" Designed & Developed by Prashanth Kumar & Andrew Jesiah")
        self.authorName.config(font = ('Montserrat','8'),foreground="#112D25", background="#FFFFFF")        

        helv36 = font.Font(family='Helvetica', size=9)
    
        self.button1 = tk.Button(self, text="Submit", command=lambda : self.submit(self.CFnum.get(), self.main_url))
        self.button1.config(relief='flat', bg='#737370', fg="#FFFFFF", height=2, width=38)
        self.button1['font'] = helv36

        self.button2 = tk.Button(self, text="Logout", command=lambda: self.logout())
        self.button2.config(relief='flat', bg='#737370', fg="#FFFFFF", height=1, width=10)
        self.button2['font'] = helv36
    
        # Set the treeview
        self.tree = Treeview( self, columns=('CF number', 'Complaint Status'))
        self.tree.heading('#0', text='No', anchor='w')
        self.tree.heading('#1', text='Complaint Folder', anchor='w')
        self.tree.heading('#2', text='Complaint Status')
        self.tree.column('#0', stretch=tk.YES, width=33, anchor='w')
        self.tree.column('#1', stretch=tk.YES, width=100, anchor='w')
        self.tree.column('#2', stretch=tk.YES, width=250, anchor='w')
    
        self.treeview = self.tree
        self.treeview.bind("<ButtonRelease-1>",lambda event :self.tree_select_event(event))

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.internet = Label(self, text="Checking...")
        self.internet.config(font = ('Helvetica','11'), foreground="black", background="#FFFFFF")

        self.delButton = tk.Button(self, text="Delete", command=lambda: self.delete(self.treeSelection))
        self.delButton.config(relief='flat', bg='#737370', fg="#FFFFFF", height=1, width=8)
        self.delButton['font'] = helv36

        self.previewButton = tk.Button(self, text="View", command=lambda: self.viewPreview(self.CFnum.get(), self.treeSelection, self.main_url))
        self.previewButton.config(relief='flat', bg='#737370', fg="#FFFFFF", height=1, width=8)
        self.previewButton['font'] = helv36

        # Initialize the counter
        self.count = 0

        self.CF_number.place(x='35', y='20')
        self.CFnum.place(x='157', y='20')
        self.previewButton.place(x='300', y='20')
        #self.msg.place(x='18', y='40')
        self.button1.place(x='200', y='80', anchor='center')
        self.tree.place(x='0', y='140')
        self.delButton.place(x='4', y='382')
        self.button2.place(x='315', y='385')
        #self.internet.place(x='270', y='420')
        self.authorName.place(x='87', y='442')
        self.vsb.place(x='380', y='140', height=228)
        '''
        self.signal = tk.Canvas(self,width=15, height=15)
        self.signal.place(x='720', y='270')
        self.catsWebLabel = Label(self, text='CATSWeb',style='BW.TLabel')
        self.catsWebLabel.place(x='640', y='270')
        '''

    def tree_select_event(self, event):
        item_iid = self.tree.selection()
        if item_iid:
            self.treeSelection = item_iid[0]

    def viewPreview(self, CFnum, treeSelection, main_url):
        if CFnum:
            self.thread1 = threading.Thread(target=self.workerThread2, args=(CFnum, main_url))
            self.thread1.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
            self.thread1.start()
        elif treeSelection:
            self.thread1 = threading.Thread(target=self.workerThread2, args=(treeSelection, main_url))
            self.thread1.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
            self.thread1.start()
        elif len(CFnum) == 0:
            messagebox.showinfo('Error!', 'Enter a complaint folder number')
            return

    def workerThread2(self,CFnum, main_url):
        sessionFlag, previewFlag, previewMsg = complaint_handler.preview(CFnum, main_url)

        if not sessionFlag:
            messagebox.showinfo('Error!', 'Session Expired. Please login again')
            self.logout()

        elif not previewFlag:
            messagebox.showinfo('Error!', previewMsg)


    def delete(self, treeSelection):
        if 'Ongoing' in self.treeview.item(treeSelection)["tags"]:
            messagebox.showinfo('Error!', 'Complaint folder already in process')
            return
        self.treeview.delete(treeSelection)
        self.treeSelection = ''

    def validate(self, possible_new_value):
        if re.match(r'^[0-9]*$', possible_new_value):
            return True
        return False
    

    def logout(self):
        self.login_page.UserEntry.bind('<Return>', lambda x: self.login_page.clicked(self.login_page.UserEntry.get(), self.login_page.PassEntry.get()))
        self.login_page.PassEntry.bind('<Return>', lambda x: self.login_page.clicked(self.login_page.UserEntry.get(), self.login_page.PassEntry.get()))
        self.login_page.btn.config(state = 'normal')
        self.CFnum.delete(0, "end")
        self.tree.delete(*self.tree.get_children())
        self.controller.show_frame(LoginPage)


    def submit(self, CFnum, main_url):
        if len(CFnum) == 0:
            messagebox.showinfo('Error!', 'Enter a complaint folder number')
            return
        self.running = 1
        self.t1 = time.time()
        print('time: ',time.time() - self.t1)
        # Increment counter
        self.count = len(self.treeview.get_children()) + 1
        
        if CFnum in self.treeview.get_children():
            print(CFnum, self.treeview.item(CFnum)["tags"])
            if 'Ongoing' in self.treeview.item(CFnum)["tags"]:
                messagebox.showinfo('Error!', 'Complaint folder already in process')
                return
            elif any(tag in self.treeview.item(CFnum)["tags"] for tag in ['Error', 'Closed']):
                self.treeview.item(CFnum, values=(self.CFnum.get(),'Processing... Please wait'), tags='Ongoing')

        else:
            self.treeview.insert('', 'end', self.CFnum.get(), text=str(self.count), values=(self.CFnum.get(),'Processing... Please wait'), tags='Ongoing')
            print(CFnum, self.treeview.item(CFnum)["tags"])

        self.treeview.tag_configure('Ongoing', background='')

        ThreadedTask(CFnum, main_url, self.infoQueue,self.CFnumQueue, self.flagQueue, self.controller).start()

    def processQueueIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize( ):
            try:
                self.main_url = self.queue.get(0)
                self.msg.config(text = self.main_url)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def processinfoQueueIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.infoQueue.qsize( ):
            try:
                CFnum = self.CFnumQueue.get(0)
                statusMsg = self.infoQueue.get(0)
                statusFlag = self.flagQueue.get(0)
                if statusFlag:
                    self.treeview.set(CFnum, 'Complaint Status', statusMsg)
                    self.treeview.item(CFnum, tags='Closed')
                    self.treeview.tag_configure('Closed', background='green')
                else:
                    self.treeview.set(CFnum, 'Complaint Status', statusMsg)
                    self.treeview.item(CFnum, tags='Error')
                    self.treeview.tag_configure('Error', background='red')
                # Check contents of message and do whatever is needed. As a
                # simple test, print it in real life, you would
                # suitably update the GUI's display in a richer fashion).
                
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass



class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """

        self.running = 1

        # Create the queue
        self.queue = Queue.Queue( )

        # Set up the GUI part
        self.gui = ComplaintHandlerUI(self.queue)

        self.login_page = self.gui.get_page(LoginPage)
        self.page_one = self.gui.get_page(PageOne)

        self.periodicCall()

        self.gui.mainloop()


    def periodicCall(self):
        self.page_one.processQueueIncoming()
        self.page_one.processinfoQueueIncoming()
        
        #Check every 200 ms if there is an active internet connection
        
        if(self.internet_on()):
            self.login_page.internet.config(text='Internet Connected')
            self.page_one.internet.config(text='Internet Connected')
            self.login_page.btn.config(command=lambda: self.login_page.clicked(self.login_page.UserEntry.get(), self.login_page.PassEntry.get()))
            self.page_one.button1.config(command=lambda: self.page_one.submit(self.page_one.CFnum.get(), self.page_one.main_url))

            '''
            if(self.catsWebconn() == 200):
                self.login_page.signal.config(bg='green')
                self.page_one.signal.config(bg='green')
            else:
                self.login_page.signal.config(bg='red')
                self.page_one.signal.config(bg='red')
            '''
        else:
            self.login_page.internet.config(text='Internet Not Connected')
            self.page_one.internet.config(text='Internet Not Connected')
            self.login_page.btn.config(command=lambda: self.messagebox())
            self.page_one.button1.config(command=lambda: self.messagebox())
            #self.login_page.signal.config(bg='red')
        

        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            self.running = 0
            
        self.gui.after(500, self.periodicCall)

    def messagebox(self):
        messagebox.showinfo('Error!', 'Internet not connected')

    
    def internet_on(self):
        for timeout in [10,15]:
            try:
                socket.setdefaulttimeout(timeout)
                host = socket.gethostbyname("www.google.com")
                s = socket.create_connection((host, 80), 2)
                s.close()
                return True
            except : pass
        return False

    def catsWebconn(self):
        try:
            return (urlopen("http://cwprod/CATSWebNET/").getcode())
        except:
            return False
    

class ThreadedTask(threading.Thread):
    def __init__(self, CFnum, main_url, infoQueue, CFnumQueue, flagQueue, controller):
        threading.Thread.__init__(self)
        self.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
        self.CFnum = CFnum
        self.main_url = main_url
        self.infoQueue = infoQueue
        self.CFnumQueue = CFnumQueue
        self.flagQueue = flagQueue
        self.controller = controller
        self.login_page = self.controller.get_page(LoginPage)
        self.page_one = self.controller.get_page(PageOne)

    def run(self):
        sessionFlag, CF_number, statusMsg, statusFlag = complaint_handler.complaintProcess(self.CFnum, self.main_url)

        if not sessionFlag:
            messagebox.showinfo('Error!', 'Session Expired. Please login again')
            self.page_one.logout()

        else:
            print(statusMsg)

            self.CFnumQueue.put(CF_number)
            self.infoQueue.put(statusMsg)
            self.flagQueue.put(statusFlag)
            


client = ThreadedClient()
