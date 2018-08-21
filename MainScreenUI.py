# coding: utf-8

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
import threading
from AppControl import AppControl
from kivy.lang import Observable
from os.path import join, dirname
import gettext

# a class that supports multilanguage apps
class Lang(Observable):
    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Lang, self).__init__()
        self.ugettext = None
        self.lang = defaultlang
        self.switch_lang(self.lang)

    def _(self, text):
        return self.ugettext(text)

    def fbind(self, name, func, args, **kwargs):
        if name == "_":
            self.observers.append((func, args, kwargs))
        else:
            return super(Lang, self).fbind(name, func, *largs, **kwargs)

    def funbind(self, name, func, args, **kwargs):
        if name == "_":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Lang, self).funbind(name, func, *args, **kwargs)

    def switch_lang(self, lang):
        # get the right locales directory, and instanciate a gettext
        locale_dir = join(dirname(__file__), 'data', 'locales')
        locales = gettext.translation('langapp', locale_dir, languages=[lang])
        self.ugettext = locales.gettext
        self.lang = lang

        # update all the kv rules attached to this text
        for func, largs, kwargs in self.observers:
            func(largs, None, None)

class MainScreen(FloatLayout):

    btn = ObjectProperty()
    label = ObjectProperty()
    txt_input = ObjectProperty()
    scrollable_label = ScrollView()
    flag = 0  # flag that indicates whether cancel button is pressed (1 when it's pressed)

    # plays the textToSpeech file that contains the response to the user's question
    def play_sound(self):
        self.sound = SoundLoader.load('textToSpeech.mp3')
        if self.sound:
            self.sound.play()
    
    # It runs in the background (not in the main thread), creates an AppControl object and calls its start_rec function to start recording
    def btn_start(self):
        self.app = AppControl()
        self.app.start_rec()

    # It runs in the background, converts speech to text and calls the method process_input that returns a response to the user's question
    def btn_stop(self):
        self.app.convert_to_text()
        text = self.app.process_input(tr.lang)
        if (self.flag==0):
            self.scrollable_label.mylabel.text = text
            self.play_sound()
        else:
            self.scrollable_label.mylabel.text = ""

    # Calls app with the text that is in the TextInput as a parameter
    def call_app(self):
        self.app = AppControl()
        text = self.app.process_input(tr.lang, text = self.txt_input.text)
        if (self.flag==0):
            self.scrollable_label.mylabel.text = text
            self.play_sound()
        else:
            self.scrollable_label.mylabel.text = ""

    # This method is called when button1 is pressed. It changes the GUI's state and calls the corresponding functions
    def btn1_pressed(self):
        if (self.btn.background_color==[0.22, 0.72, 0.2, 1]):
            self.flag = 0
            self.btn.text = tr._('Stop')
            self.label.text = tr._('Press the Stop button when you finish your question')
            self.btn.background_color = 0.88, 0.09, 0.09, 1
            self.scrollable_label.mylabel.text = ''
            t1 = threading.Thread(target=self.btn_start)  # create a thread that calls btn_start()
            t1.start()  # start thread
        else:
            self.btn.text = tr._('Start')
            self.label.text = tr._('Press the button to ask a question')
            self.btn.background_color =  0.22, 0.72, 0.2, 1
            self.scrollable_label.mylabel.text = tr._('Please wait')
            self.app.stop_rec()  # stop recording
            self.app.initialize_STT(tr.lang)  # it can't work in any other but the main thread
            t2 = threading.Thread(target=self.btn_stop)  # create a thread that calls btn_stop()
            t2.start()

    def btn2_pressed(self):
        self.flag = 0
        self.scrollable_label.mylabel.text = tr._('Please wait')
        #print(self.txt_input.text)
        t3 = threading.Thread(target=self.call_app)
        t3.start()

    # "Cancels" current process. If cancel button is pressed, the response is not displayed to the user.
    def cancel(self):
        self.flag = 1

    # If mute button is pressed, any sound that is played stops
    def mute(self):
        if (self.sound.state=='play'):
            self.sound.stop()

class PersonalAssistantApp(App):
    
    lang = StringProperty('el')

    def on_lang(self, instance, lang):
        tr.switch_lang(lang)

    def build(self):
        return MainScreen()

if __name__ == '__main__':
    tr = Lang("el")
    PersonalAssistantApp().run()
