#!/usr/bin/env kivy
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
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.screenmanager import ScreenManager, Screen


from random import choice
import cPickle, getpass, os, sys, nltk, string, re

class SaveData:
        pass

class Database:
    def __init__(self):
        self.sd = SaveData()
        username = getpass.getuser()
        maindir = '/Users/%s/Dropbox/question_generator/' %username
        self.out_file = maindir + os.sep + 'output1.txt'
        self.in_file = maindir + os.sep + 'input1.txt'
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
            raw = raw.replace('\n', '')
            raw = filter(lambda x: x in string.printable, raw)
            self.pre_st = nltk.sent_tokenize(raw)
            self.st = []
            import pdb; pdb.set_trace()
            for presentence in self.pre_st:

                # Compile an expression that further splits into sentences alphabetical characters followed by a period.
                regex = re.compile(r'([A-Za-z]\.[0-9]+ |\?)')
                pre_split = regex.split(presentence) 
                split = []

                # If there is not splitting, then just skip all the mess below and just add the item. 
                if len(pre_split) == 1:
                    split.append(pre_split)
                else:
                    for i, element in enumerate(pre_split):
                        # The instances to consider are periods followed by numbers and question marks not followed by spaces.
                        # Make sure we can index the below.
                        try:
                            element[1]
                            if (len(element) < 6 and element[1] == "."):
                                del split[-1]
                                split.append(pre_split[i-1]+element[:2])
                            # If the sentence ends in a question mark:
                            elif element == '?':
                                # Get rid of the previous so that we can combined these two.
                                del split[-1] 

                                # Combine the two previous but now combine the whole question mark.
                                split.append(pre_split[i-1]+element) 

                            else:
                                # If nothing needs to be done to the sentence.
                                split.append(element)
                        except IndexError:
                            pass

                    # Append to the final output which will be self.st.
                    self.st.append(split)
            import pdb; pdb.set_trace()

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
            size_hint: (1,0.3)
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
            orientation: 'vertical'
            BoxLayout:
                orientation: 'horizontal'
                Button:
                    text: 'Go Back'
                    on_press:root.GoBack()
                    background_color: [0.7, 0, 0, 0.9]
                    size_hint: (0.5, 1)
                Button: 
                    id: next_sentence_id
                    text: 'Next Sentence'
                    on_press: root.NextSentence(sentence_box_id.text); self.focus= True
                    background_color: [0, 0.9, 0, 0.9]
                Button:
                    text: 'Insert What'
                    on_press: root.InsertWhat()
                    background_color: [0.9, 0.7, 0, 0.9]
                Button:
                    text: 'Insert Blank'
                    on_press: root.InsertBlank()
                    background_color: [0, 0, 0.5, 0.9]
            BoxLayout:
                orientation: 'horizontal'
                Button:
                    text: 'Reset Counter'
                    on_press: root.reset_counter()
                    size_hint: (0.5, 1)
                Button:
                    text: 'Set New Topic'
                    on_press: root.NewTopic()
                Button:
                    text: root.topic
                    halign: 'center'
                    on_press: root.InsertNewTopic()
                Button: 
                    text: 'Submit as Card'
                    on_press: root.SubmitCard()
                    background_color: [0, 0.9, 0, 0.9]
""")

## Declaration of screens.

# Initialize screen will only show up the first time.

class MainScreen(Screen):
    next_sentence = ObjectProperty(None)
    sentence_box = ObjectProperty(None)
    question_box = ObjectProperty(None)
    answer_box = ObjectProperty(None)
    counter = StringProperty('Welcome! Click Next Sentence to get started.')
    topic = StringProperty('Insert Current topic:\nNone')

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        #self.list_view.adapter.bind(on_selection_change=self.selection_changed)
        self.cm = False # This will manage the change_theme function later.

    def NextSentence(self, strat):
        if db.sd.sentence_counter+1 < len(db.st):
            self.ClearAllBoxes()
            db.sd.sentence_counter += 1
            sentence = db.st[db.sd.sentence_counter]
            self.sentence_box.insert_text(sentence)
            self.counter = str(db.sd.sentence_counter+1)+'/'+str(len(db.st))
            db.Save()

    def InsertWhat(self):
        if self.sentence_box.focus == True:
            self.sentence_box.select_text(0, ss.sentence_box.cursor_index())
            self.first_q_stem = ss.sentence_box.selection_text
            self.sentence_box.cancel_selection()
            self.sentence_box.insert_text('what? ')
            self.sentence_box.select_text(0, ss.sentence_box.cursor_index())
            self.question_box.insert_text(ss.sentence_box.selection_text)
            start_of_answer = ss.sentence_box.cursor_index()
            self.sentence_box.do_cursor_movement('cursor_pgdown')
            self.sentence_box.do_cursor_movement('cursor_end')
            self.sentence_box.select_text(start_of_answer, ss.sentence_box.cursor_index()) 
            self.answer_box.insert_text(ss.sentence_box.selection_text)
            self.sentence_box.cancel_selection()
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
        self.sentence_box.select_all()
        self.sentence_box.delete_selection()
        self.sentence_box.select_text(0,0)
        self.question_box.select_all()
        self.question_box.delete_selection()
        self.question_box.select_text(0,0)
        self.answer_box.select_all()
        self.answer_box.delete_selection()
        self.answer_box.select_text(0,0)

    def SetNewTopic(instance, value):
        ss.topic = 'Insert Current topic:\n%s' %(value.text)
        ss.topic_raw = value.text
        ss.popup.dismiss()

    def NewTopic(self):
        if self.sentence_box.selection_text == '':
            textinput = TextInput(multiline=False, focus=True)
            textinput.bind(on_text_validate=self.SetNewTopic)

            self.popup = Popup(title='Please enter the current topic.',
                            content=textinput,
                            size_hint=(.5, .5))
            self.popup.open()
        else:
            self.topic = 'Insert Current topic:\n%s' %(self.sentence_box.selection_text)
            self.topic_raw = self.sentence_box.selection_text

    def InsertNewTopic(self):
        self.question_box.do_cursor_movement('cursor_home')
        try:
            self.question_box.insert_text('For %s, ' %self.topic_raw)
        except AttributeError:
            pass

    def reset_counter(self):
        db.sd.sentence_counter = 0
        self.counter = str(db.sd.sentence_counter+1)+'/'+str(len(db.st))
        sentence = db.st[db.sd.sentence_counter]
        self.sentence_box.insert_text(sentence)

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

