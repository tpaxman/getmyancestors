#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import Tk, Frame, Label, Entry, StringVar, Button, IntVar, Checkbutton, filedialog, messagebox
from getmyancestors import Session, Tree
import asyncio
import re


class SignIn(Frame):

    def __init__(self, window, **kwargs):
        super(SignIn, self).__init__(window, **kwargs)
        self.username = StringVar()
        self.password = StringVar()
        label_username = Label(self, text='Username')
        entry_username = Entry(self, textvariable=self.username, width=30)
        label_password = Label(self, text='Password')
        entry_password = Entry(self, show='●', textvariable=self.password, width=30)
        label_username.pack()
        entry_username.pack()
        label_password.pack()
        entry_password.pack()
        entry_username.focus_set()
        entry_username.bind('<Key>', self.enter)
        entry_password.bind('<Key>', self.enter)

    def enter(self, evt):
        if evt.keysym == 'Return':
            self.master.master.login()


class StartIndi(Frame):

    def __init__(self, window, **kwargs):
        super(StartIndi, self).__init__(window, **kwargs)
        self.label_fid = Label(self, text='')
        self.fid = StringVar()
        self.btn_delete = Button(self, text='delete', command=self.delete)
        entry_fid = Entry(self, textvariable=self.fid, width=10)
        entry_fid.bind('<FocusOut>', self.get_data)
        self.label_fid.pack()
        entry_fid.pack()
        self.btn_delete.pack()

    def get_data(self, evt):
        if re.match(r'[A-Z0-9]{4}-[A-Z0-9]{3}', self.fid.get()):
            try:
                fs = self.master.master.master.master.fs
                data = fs.get_url('/platform/tree/persons/%s.json' % self.fid.get())
                self.add_data(data)
            except AttributeError:
                pass

    def add_data(self, data):
        if data and 'persons' in data:
            indi = data['persons'][0]
            self.fid.set(indi['id'])
            if 'names' in data['persons'][0]:
                for name in data['persons'][0]['names']:
                    if name['preferred']:
                        self.label_fid.config(text=name['nameForms'][0]['fullText'])
                        break

    def delete(self):
        self.master.master.start_indis.remove(self)
        self.destroy()


class Options(Frame):
    def __init__(self, window, ordinances=False, **kwargs):
        super(Options, self).__init__(window, **kwargs)
        self.ancestors = IntVar()
        self.ancestors.set(4)
        self.descendants = IntVar()
        self.spouses = IntVar()
        self.ordinances = IntVar()
        self.contributors = IntVar()
        self.start_indis = list()
        self.indis = Frame(self)
        label_ancestors = Label(self, text='Number of generations to ascend')
        entry_ancestors = Entry(self, textvariable=self.ancestors, width=3)
        label_descendants = Label(self, text='Number of generations to descend')
        entry_descendants = Entry(self, textvariable=self.descendants, width=3)
        btn_add_indi = Button(self, text='add', command=self.add_indi)
        btn_spouses = Checkbutton(self, text='Add spouses and couples information', variable=self.spouses)
        btn_ordinances = Checkbutton(self, text='Add temple information', variable=self.ordinances)
        btn_contributors = Checkbutton(self, text='Add list of contributors in notes', variable=self.contributors)
        label_ancestors.pack()
        entry_ancestors.pack()
        label_descendants.pack()
        entry_descendants.pack()
        self.indis.pack()
        btn_add_indi.pack()
        btn_spouses.pack()
        if ordinances:
            btn_ordinances.pack()
        btn_contributors.pack()
        entry_ancestors.focus_set()

    def add_indi(self, data=None):
        new_indi = StartIndi(self.indis)
        self.start_indis.append(new_indi)
        new_indi.add_data(data)
        new_indi.pack()


class Gui(Frame):
    def __init__(self, window, **kwargs):
        super(Gui, self).__init__(window, borderwidth=10, **kwargs)
        self.fs = None
        self.tree = None
        self.filename = None
        self.logfile = open('gui.log', 'w')
        self.info_label = Label(self)
        self.form = Frame(self)
        self.sign_in = SignIn(self.form)
        self.options = Options(self.form, True)
        self.title = Label(self, text='Sign In to FamilySearch')
        buttons = Frame(self)
        self.btn_quit = Button(buttons, text='Quit', command=self.quit)
        self.btn_valid = Button(buttons, text='Sign In', fg='red', command=self.login)
        self.title.pack()
        self.sign_in.pack()
        self.form.pack()
        self.btn_quit.pack(side='left')
        self.btn_valid.pack(side='right')
        self.info_label.pack()
        buttons.pack()
        self.pack()

    def info(self, text):
        self.info_label.config(text=text)
        self.master.update()

    def save(self):
        self.filename = filedialog.asksaveasfilename(title='Save as', filetypes=(('GEDCOM files', '.ged'), ('All files', '*.*')))
        if not self.filename:
            return
        with open(self.filename, 'w') as file:
            self.tree.print(file)

    def login(self):
        self.btn_valid.config(state='disabled')
        self.info('Login to FamilySearch...')
        self.fs = Session(self.sign_in.username.get(), self.sign_in.password.get(), verbose=True, logfile=self.logfile, timeout=1)
        if not self.fs.logged:
            messagebox.showinfo(message='The username or password was incorrect')
            self.btn_valid.config(state='normal')
            self.info('')
            return
        self.tree = Tree(self.fs)
        data = self.fs.get_url('/platform/tree/persons/%s.json' % self.fs.get_userid())
        self.options.add_indi(data)
        self.sign_in.destroy()
        self.title.config(text='Options')
        self.btn_valid.config(command=self.download, state='normal', text='Download')
        self.info('')
        self.options.pack()

    def download(self):
        todo = [start_indi.fid.get() for start_indi in self.options.start_indis]
        for fid in todo:
            if not re.match(r'[A-Z0-9]{4}-[A-Z0-9]{3}', fid):
                messagebox.showinfo(message='Invalid FamilySearch ID: ' + fid)
                return
        self.options.destroy()
        _ = self.fs._
        self.btn_valid.config(state='disabled')
        self.info(_('Download starting individuals...'))
        self.tree.add_indis(todo)
        todo = set(todo)
        done = set()
        for i in range(self.options.ancestors.get()):
            if not todo:
                break
            done |= todo
            self.info(_('Download ') + str(i + 1) + _('th generation of ancestors...'))
            todo = self.tree.add_parents(todo) - done

        todo = set(self.tree.indi.keys())
        done = set()
        for i in range(self.options.descendants.get()):
            if not todo:
                break
            done |= todo
            self.info(_('Download ') + str(i + 1) + _('th generation of descendants...'))
            todo = self.tree.add_children(todo) - done

        if self.options.spouses.get():
            self.info('Download spouses and marriage information...')
            todo = set(self.tree.indi.keys())
            self.tree.add_spouses(todo)
        ordi = self.options.ordinances.get()
        cont = self.options.contributors.get()

        async def download_stuff(loop):
            futures = set()
            for fid, indi in self.tree.indi.items():
                futures.add(loop.run_in_executor(None, indi.get_notes))
                if ordi:
                    futures.add(loop.run_in_executor(None, self.tree.add_ordinances, fid))
                if cont:
                    futures.add(loop.run_in_executor(None, indi.get_contributors))
            for fam in self.tree.fam.values():
                futures.add(loop.run_in_executor(None, fam.get_notes))
                if cont:
                    futures.add(loop.run_in_executor(None, fam.get_contributors))
            for future in futures:
                await future

        loop = asyncio.get_event_loop()
        self.info(_('Download notes') + (((',' if cont else _(' and')) + _(' ordinances')) if ordi else '') + (_(' and contributors') if cont else '') + '...')
        loop.run_until_complete(download_stuff(loop))

        self.tree.reset_num()
        self.btn_valid.config(command=self.save, state='normal', text='Save')
        self.info(text='Success')


window = Tk()
sign_in = Gui(window)
sign_in.mainloop()
