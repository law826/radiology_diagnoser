"""
question_generator.py
"""
import kivy
kivy.require('1.0.7')
from functools import partial
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.screenmanager import ScreenManager, Screen

from random import choice
import cPickle, getpass, os, sys, nltk

class SaveData:
        pass

class Database:
    def __init__(self):
        self.sd = SaveData()
        username = getpass.getuser()
        maindir = '/Users/%s/Dropbox/question_generator/' %username
        self.out_file = maindir + os.sep + 'output.txt'
        self.in_file = maindir + os.sep + 'input.txt'
        self.open_and_parse_input()

        try:
            self.sd = cPickle.load(open('savedata.p', 'rb')) # Pickle with dict of current directory mapped with save directories.
            self.sd.sentence_counter
        except (IOError, NameError):
            self.sd.sentence_counter = 0

    def Save(self):
        cPickle.dump(self.sd, open('savedata.p', 'wb'))

    def Append(self, string):
        self.sd.dbdict[self.sd.theme].append(string)
        self.Save()

    def open_and_parse_input(self):
        with open(self.in_file, 'r') as f:
            raw = f.read()
            self.st = nltk.sent_tokenize(raw)

# Create database instance.
db = Database()

##################### Start of GUI:
Builder.load_string("""

#:import label kivy.uix.label
#:import la kivy.adapters.listadapter
#:import listview kivy.uix.listview
#:import ListItemButton kivy.uix.listview.ListItemButton

<MainScreen>:
    settings_screen: self
    sentence_box: sentence_box_id
    question_box: question_box_id
    answer_box: answer_box_id
    next_sentence: next_sentence_id

    BoxLayout:
        orientation: 'vertical'
        padding: [2,2,2,2]

        Label:
            text: root.counter
        TextInput:
            id: sentence_box_id
            multiline: True
            on_text_validate: root.AddTerm(self.text); self.text= ''; self.focus= True
            focus: True
        TextInput:
            id: question_box_id
        TextInput:
            id: answer_box_id
        BoxLayout:
            orientation: 'horizontal'
            Button: 
                id: next_sentence_id
                text: 'Next Sentence'
                on_press: root.NextSentence(sentence_box_id.text); self.focus= True
            Button:
                text: 'Go Back'
                on_press:root.GoBack()
            Button:
                text: 'Insert What'
                on_press: root.InsertWhat()
            Button:
                text: 'Insert Blank'
                on_press: root.InsertBlank()
            Button: 
                text: 'Submit as Card'
                on_press: root.SubmitCard()
            Button:
                text: 'Reset Counter'
                on_press: root.reset_counter()
""")

## Declaration of screens.

# Initialize screen will only show up the first time.

class MainScreen(Screen):
    next_sentence = ObjectProperty(None)
    sentence_box = ObjectProperty(None)
    question_box = ObjectProperty(None)
    answer_box = ObjectProperty(None)
    counter = StringProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        #self.list_view.adapter.bind(on_selection_change=self.selection_changed)
        self.cm = False # This will manage the change_theme function later.

    def NextSentence(self, strat):
        if db.sd.sentence_counter+1 < len(db.st):
            self.ClearAllBoxes()
            db.sd.sentence_counter += 1
            sentence = db.st[db.sd.sentence_counter]
            ss.sentence_box.insert_text(sentence)
            self.counter = str(db.sd.sentence_counter+1)+'/'+str(len(db.st))
            db.Save()

    def InsertWhat(self):
        if self.sentence_box.focus == True:
            ss.sentence_box.select_text(0, ss.sentence_box.cursor_index())
            self.first_q_stem = ss.sentence_box.selection_text
            self.sentence_box.cancel_selection()
            ss.sentence_box.insert_text('what? ')
            ss.sentence_box.select_text(0, ss.sentence_box.cursor_index())
            ss.question_box.insert_text(ss.sentence_box.selection_text)
            start_of_answer = ss.sentence_box.cursor_index()
            ss.sentence_box.do_cursor_movement('cursor_pgdown')
            ss.sentence_box.do_cursor_movement('cursor_end')
            ss.sentence_box.select_text(start_of_answer, ss.sentence_box.cursor_index()) 
            ss.answer_box.insert_text(ss.sentence_box.selection_text)
            ss.sentence_box.cancel_selection()
        elif self.answer_box.focus == True:
            # Process second answer.
            self.second_q_clause = ss.answer_box.selection_text
            self.second_q_clause_coord = (ss.answer_box.selection_from, ss.answer_box.selection_to)
            self.answer_box.delete_selection()
            self.answer_box.insert_text('\n\n')

            #Insert second question.
            self.question_box.focus = True
            self.question_box.do_cursor_movement('cursor_end')
            self.question_box.insert_text('\n\n%s%s what?' %(self.first_q_stem, self.second_q_clause))

    def InsertBlank(self):
        if self.sentence_box.focus == True:
            if self.sentence_box.selection_text != '':
                self.question_box.select_all()
                self.question_box.delete_selection()
                answer_phrase = self.sentence_box.selection_text
                self.sentence_box.delete_selection()
                self.sentence_box.insert_text('**BLANK**')
                self.question_box.insert_text(self.sentence_box.text)
                if self.answer_box.text == '':
                    self.answer_box.insert_text(answer_phrase)
                else:
                    self.answer_box.do_cursor_movement('cursor_end')
                    self.answer_box.insert_text('; %s' %answer_phrase)

    def SubmitCard(self):
        q_list = ss.question_box.text.split('\n')
        a_list = ss.answer_box.text.split('\n')

        with open(db.out_file, 'a') as f:
            username = getpass.getuser()
            for i, question in enumerate(q_list):
                if question != '':
                    anki_line = question+'\t'+a_list[i]+'\n'
                    f.write(anki_line)

        self.ClearAllBoxes()

    def GoBack(self):
        if db.sd.sentence_counter > 0:
            self.ClearAllBoxes()
            db.sd.sentence_counter -= 1
            sentence = db.st[db.sd.sentence_counter]
            ss.sentence_box.insert_text(sentence)
            self.counter = str(db.sd.sentence_counter+1)+'/'+str(len(db.st))
            db.Save()

    def ClearAllBoxes(self):
        ss.sentence_box.select_all()
        ss.sentence_box.delete_selection()
        ss.question_box.select_all()
        ss.question_box.delete_selection()
        ss.answer_box.select_all()
        ss.answer_box.delete_selection()

    def reset_counter(self):
        db.sd.sentence_counter = 0
        self.counter = str(db.sd.sentence_counter+1)+'/'+str(len(db.st))
        sentence = db.st[db.sd.sentence_counter]
        ss.sentence_box.insert_text(sentence)

class MyPopup(Popup):
    def __init__(self, **kwargs):
        super(MyPopup, self).__init__(**kwargs)


#####

# Create the manager
sm = ScreenManager()
# Set up functionality to set up the key of the dictionary when the program first launches.
ss = MainScreen(name='MainScreen')
sm.add_widget(ss)
#####

# The main app:
class QuestGenApp(App):
    def build(self):
        return sm
#####

# Running the app:
if __name__ == '__main__':
    QuestGenApp().run()
#####

