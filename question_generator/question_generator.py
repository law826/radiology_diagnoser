"""
question_generator.py
"""
import kivy
from random import choice
import cPickle
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

class SaveData:
        pass

class Database:
    def __init__(self):
        try: 
            self.sd = cPickle.load(open('savedata.p', 'rb')) # Pickle with dict of current directory mapped with save directories.
        except (IOError, cPickle.UnpicklingError):
            self.sd = SaveData()
            self.sd.dbdict = {}
            self.sd.theme = 'Setup'
            self.sd.dbdict[self.sd.theme] = []
            self.Save()

    def Save(self):
        cPickle.dump(self.sd, open('savedata.p', 'wb'))

    def Append(self, string):
        self.sd.dbdict[self.sd.theme].append(string)
        self.Save()

# Create database instance.
db = Database()


##################### Start of GUI:
Builder.load_string("""

#:import label kivy.uix.label
#:import la kivy.adapters.listadapter
#:import listview kivy.uix.listview
#:import ListItemButton kivy.uix.listview.ListItemButton

<InitializeScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Welcome! Please enter the name of your first theme.'
        TextInput:
            id: txti
            multiline: False
            on_text_validate: root.SetInitialMode(self.text); root.manager.current = 'main'
            focus: True


<MainScreen>:
    label: main_label

    BoxLayout:
        orientation: 'vertical'
        padding: [4,4,4,4]

        Label:
            text: 'Welcome'
            id: main_label
        BoxLayout:
            orientation: 'horizontal'
            Button:
                text: 'Next Term'
                on_press: root.NewTerm()
            Button:
                text: 'Settings'
                on_press: root.manager.current = 'settings'
            Button:
                text: 'Quit'
                on_press: root.Exit()

<SettingsScreen>:
    settings_screen: self
    text_input: text_input_id
    question_box: question_box_id
    answer_box: answer_box_id
    on_pre_enter: root.initiate_label()
    add_button: add_button_id

    BoxLayout:
        orientation: 'vertical'
        padding: [2,2,2,2]

        TextInput:
            id: text_input_id
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
                id: add_button_id
                text: 'Next Sentence'
                on_press: root.NextSentence(text_input_id.text); self.focus= True
            Button:
                text: 'Insert What'
                on_press: root.InsertWhat()
            Button: 
                text: 'Submit as Anki Card'
                on_press: root.SubmitCard()
            Button:
                text: 'Back to Main'
                on_press: root.manager.current = 'main'
""")

## Declaration of screens.

# Initialize screen will only show up the first time.

class InitializeScreen(Screen):
    def SetInitialMode(self, text):
        db.sd.dbdict[text] = []
        db.sd.theme = text


class MainScreen(Screen):
    # Set the initial display term. 
    label = ObjectProperty(None)

    def InitiateTerm(self):
        self.label.text = "Welcome"

    def NewTerm(self):
        self.label.text = choice(db.sd.dbdict[db.sd.theme])

    def Exit(self):
        import sys; sys.exit()

class SettingsScreen(Screen):
    list_contents = ListProperty(db.sd.dbdict[db.sd.theme])
    add_button = ObjectProperty(None)
    question_box = ObjectProperty(None)
    answer_box = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        #self.list_view.adapter.bind(on_selection_change=self.selection_changed)
        self.cm = False # This will manage the change_theme function later.

    def initiate_label(self):
        self.theme = db.sd.theme

    def NextSentence(self, strat):
        ss.text_input.insert_text('The differential diagnosis of COP includes bronchiolalveolar cell carcinoma, lymphoma, vasculitis, sarcoidosis, chronic eosinophilic pneumonia, and infectious pneumonia.')

    def InsertWhat(self):
        ss.text_input.insert_text('what? ')
        ss.text_input.select_text(0, ss.text_input.cursor_index())
        ss.question_box.insert_text(ss.text_input.selection_text)
        start_of_answer = ss.text_input.cursor_index()
        ss.text_input.do_cursor_movement('cursor_pgdown')
        ss.text_input.do_cursor_movement('cursor_end')
        ss.text_input.select_text(start_of_answer, ss.text_input.cursor_index()) 
        ss.answer_box.insert_text(ss.text_input.selection_text)

    def SubmitCard(self):
        anki_line = ss.question_box.text+'\t'+ss.answer_box.text+'\n'
        with open('/Users/law826/Desktop/test.txt', 'a') as f:
            f.write(anki_line)


class MyPopup(Popup):
    def __init__(self, **kwargs):
        super(MyPopup, self).__init__(**kwargs)


#####

# Create the manager
sm = ScreenManager()
# Set up functionality to set up the key of the dictionary when the program first launches.
if db.sd.theme == 'Setup':
    sm.add_widget(InitializeScreen(name='initialize'))
ms = MainScreen(name='main')
ss = SettingsScreen(name='settings')
sm.add_widget(ms)
sm.add_widget(ss)
#####

# The main app:
class ProbSolApp(App):
    def build(self):
        return sm
#####

# Running the app:
if __name__ == '__main__':
    ProbSolApp().run()
#####

