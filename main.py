from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import time
from datetime import datetime
import wave
import threading
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from os.path import join
from kivy.clock import Clock
from audiostream import get_input
import requests
import base64
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout

class WindowManager(ScreenManager):  # class used for transitions between windows
    pass

class ScreenUnderDevelopment(Screen):
    pass

class HomeScreen(Screen):  # class which defines the homescreen layout
    def __init__(self, **kw):
        super(HomeScreen, self).__init__(**kw)
        self.message = self.welcome_message()
        self.user_data_dir = App.get_running_app().user_data_dir
        self.filename = join(self.user_data_dir, "jsonStore.json")
        self.store = JsonStore(self.filename)
        Clock.schedule_once(self.finish_init)

    def finish_init(self, dt):  # kv rules are not applied until the original Widget (HomeScreen) has finished instantiating, so must delay the initialisation which requires access to kv ids
        try:
            self.initial_use = (self.store.get("initialUse")["initial_use"])
            if self.initial_use == "True":
                self.help_info_on()
            else:
                self.help_info_off()
        except:
            self.help_info_on()

    def help_info_on(self):
        self.ids.Help_Arrow_RecyclingLogo.opacity = 1
        self.ids.Help_Text_RecyclingLogo.opacity = 1
        self.ids.Help_Text_BinLogo.opacity = 1
        self.ids.Help_Arrow_BinLogo.opacity = 1

    def help_info_off(self):
        self.ids.Help_Arrow_RecyclingLogo.opacity = 0
        self.ids.Help_Text_RecyclingLogo.opacity = 0
        self.ids.Help_Text_BinLogo.opacity = 0
        self.ids.Help_Arrow_BinLogo.opacity = 0

    def on_press_RecyclingLogo(self):
        self.ids.RecyclingLogo.source = "RecyclingLogo_Darker.png"  # changes the source of the image when 'on_press' is called
        self.ids.RecyclingLogo_Circle.source = "Logo_Circle_Darker.png"

    def on_press_BinLogo(self):
        self.ids.BinLogo.source = "BinLogo_Darker.png"  # changes the source of the image when 'on_press' is called
        self.ids.BinLogo_Circle.source = "Logo_Circle_Darker.png"

    def on_release_RecyclingLogo(self):
        time.sleep(0.1)
        self.ids.RecyclingLogo.source = "RecyclingLogo.png"
        IdentifyItem()

    def on_release_BinLogo(self):
        time.sleep(0.1)
        self.ids.RecyclingLogo.source = "BinLogo.png"

    def help_button(self):
        if self.ids.Help_Arrow_RecyclingLogo.opacity == 0:
            self.help_info_on()
        else:
            self.help_info_off()

    def welcome_message(self):
        self.current_hour = int(datetime.now().hour)
        if 4 < self.current_hour <= 12:
            return "Good Morning"
        elif 12 < self.current_hour <= 17:
            return "Good Afternoon"
        elif 17 < self.current_hour <= 23:
            return "Good Evening"
        else:
            return "Good Night"

class IdentifyItem(Screen):
    Mic_Loading = StringProperty()
    Mic_Listening = StringProperty()
    Mic_Pressed = StringProperty()
    Mic_Static = StringProperty()

    def __init__(self, **kwargs):
        super(IdentifyItem, self).__init__()
        self.Mic_Static = "Mic_Static.png"
        self.Mic_Loading = 'Mic_Loading.zip'
        self.Mic_Listening = "Mic_Listening.zip"
        self.ids.Mic_Image.opacity = 0
        self.ids.Mic_Image.source = self.Mic_Listening
        self.ids.Mic_Image.source = self.Mic_Loading
        self.ids.Mic_Image.source = self.Mic_Static
        self.ids.Mic_Image.opacity = 1
        try:
            self.initial_use = (self.store.get("initialUse")["initial_use"])
            if self.initial_use == "True":
                self.initial_mic_popup()
            else:
                pass
        except:
            self.initial_mic_popup()

    def initial_mic_popup(self):
        self.dialog = MDDialog(
            auto_dismiss=True,
            title="Talk to me!",
            text="Press and hold the microphone icon to tell me what you want to recycle"
        )
        self.dialog.open()

    def on_press_ok(self, instance):
        self.dialog.dismiss()

    def help_button(self):
        self.initial_mic_popup()

    def on_press(self):
        self.initial_use = (self.store.get("initialUse")["initial_use"])
        if self.initial_use == "False":
            self.user_data_dir = App.get_running_app().user_data_dir
            self.filename = join(self.user_data_dir, "jsonStore.json")
            self.audio_to_text = AudioToText()
            self.audio_thread = threading.Thread(target=self.audio_to_text.start, args=(),
                                                 daemon=False)  # initialises an instance of Thread.
            self.ids.Mic_Image.source = self.Mic_Listening
            self.start_time = time.time()  # sets up timer to record how long button pressed for
            self.audio_thread.start()  # starts the Thread instance
        else:
            self.store.put("initialUse", initial_use="False")

    def stop_recording(self):
        self.end_time = time.time()
        if (self.end_time - self.start_time) <= 1:  # if this audio recording is too short, an error message will be returned
            self.audio_to_text.false_stop()
            self.ids.Mic_Image.source = self.Mic_Static
            self.open_snackbar()
            self.dismiss_snackbar_thread = threading.Thread(target=self.dismiss_snackbar, args=(),
                                                            daemon=False)  # initialises an instance of Thread. As 'daemon = True', this thread will run in the background until the program terminates (or until it finishes running).
            self.dismiss_snackbar_thread.start()
        else:
            self.ids.Mic_Image.source = self.Mic_Loading
            self.audio_to_text.stop()

    def open_snackbar(self):
        animation = Animation(pos_hint={"center_x": 0.5, "top": 0.095}, d=0.03)
        animation.start(self.ids.snackbar)

    def dismiss_snackbar(self):
        time.sleep(3.5)
        animation = Animation(pos_hint={"center_x": 0.5, "top": 0}, d=0.03)
        animation.start(self.ids.snackbar)

    def database_API(self, userInput):
        baseURL = "http://recycleappapi.eu-west-2.elasticbeanstalk.com/"
        county = self.store.get("userInput")["county"]
        data = {"input": userInput, "county": county}
        response = requests.post(baseURL + "ReyclingInfo", data)
        self.keywords = response.json()
        current_screen = App.get_running_app().root.get_screen('identify_item')
        current_screen.ids.header.text = self.keywords
        current_screen.ids.Mic_Image.opacity = 0
        try:
            postcode_valid = (self.store.get("userInput")["postcode_valid"])
            if postcode_valid == "True":
                UserLocation().postcode_input_popup(MDApp) #should be pass
            else:
                UserLocation().postcode_input_popup(MDApp)
        except:
            UserLocation().postcode_input_popup(MDApp)

class AudioToText(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.samples_per_second = 60
        self.audio_data = []
        self.mic = get_input(callback=self.mic_callback, rate=8000, source='mic', buffersize=2048)

    def mic_callback(self, buffer):
        self.audio_data.append(buffer)

    def start(self):
        self.audio_data = []
        self.mic.start()
        Clock.schedule_interval(self.readchunk, 1 / self.samples_per_second)

    def readchunk(self, sample_rate):
        self.mic.poll()  # polls 'get_input(callback=self.mic_callback, source='mic', buffersize=2048)', recording audio

    def false_stop(self):
        self.audio_data = []
        Clock.unschedule(self.readchunk, None)
        self.mic.stop()

    def stop(self):
        Clock.unschedule(self.readchunk, None)
        self.mic.stop()
        user_data_dir = App.get_running_app().user_data_dir
        self.filename = join(user_data_dir, "audio.wav")
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(8000)
        wf.writeframes(b''.join(self.audio_data))
        wf.close()
        self.text_thread = threading.Thread(target=self.speech_to_text, args=(), daemon=False)  # initialises an instance of Thread. As 'daemon = True', this thread will run in the background until the program terminates (or until it finishes running).
        self.text_thread.start()

    def speech_to_text(self):
        api_token = '53d86b9ca0254532b9721661db0d3743'
        headers = {'authorization': api_token}
        with open(self.filename, 'rb') as audio_bytes: # read the binary data from a wav file
            data = audio_bytes.read()[44:] # strip off wav headers
        data = base64.b64encode(data) # base64 encode the binary data so it can be included as a JSON parameter
        data = str(data, "utf-8")
        json = {'audio_data': data}
        response = requests.post("https://api.assemblyai.com/v2/stream", json=json, headers=headers) # send the data to the /v2/stream endpoint
        self.results = response.json()["text"]
        IdentifyItem.database_API(self, self.results) #pass self as an argument so that the instance is passed too

class UserLocation_Content(BoxLayout):
    pass

class UserLocation(Screen):
    def postcode_input_popup(self, MDApp):
        self.dialog = MDDialog(
            title="Enter your postcode:",
            auto_dismiss=False,
            type="custom",
            size_hint = (0.8,0.8),
            content_cls=UserLocation_Content(),  # content class
            buttons=[MDFlatButton(text="CANCEL", text_color=((128 / 255), (128 / 255), (128 / 255), 1), on_press = self.on_press_pass),
                     MDRaisedButton(text="CONFIRM", on_press=self.check_postcode)])
        self.dialog.open()

    def check_postcode(self, instance):
        user_data_dir = App.get_running_app().user_data_dir
        self.filename = join(user_data_dir, "jsonStore.json")
        self.store = JsonStore(self.filename)
        for object in self.dialog.content_cls.children:  # iterates through the KV file methods and stores the text of textfield method (which is the users inputted postcode)
            if isinstance(object, MDTextField):
                self.postcode = object.text
                self.postcode_valid, self.county = self.get_location()
                if self.postcode_valid == False:
                    self.store.put("userInput", postcode_valid="False")
                    x_cood = int(instance.pos[0])
                    y_cood = int(instance.pos[1])
                    animation = Animation(pos=((x_cood + 15), y_cood), t="out_quad", d=0.02 / 1)
                    animation += Animation(pos=((x_cood - 15), y_cood), t="out_elastic", d=0.02 / 1)
                    animation += Animation(pos=(x_cood, y_cood), t="out_elastic", d=0.02 / 1)
                    animation.start(instance)
                else:
                    self.store.put("userInput", postcode_valid="True", postcode=object.text, county=self.county)
                    self.dialog.dismiss()
                    UserLocation().postcode_save_popup(MDApp)

    def get_location(self):
        try:
            url = "https://api.postcodes.io/postcodes/" + self.postcode
            r = requests.get(url)
            self.county = r.json()['result']["admin_district"]
            return True, self.county
        except:
            try:
                url = "https://api.postcodes.io/outcodes/" + self.postcode
                r = requests.get(url)
                self.county = r.json()['result']["admin_district"]
                return True, self.county
            except:
                self.county = "Null"
                return False, self.county

    def postcode_save_popup(self, MDApp):
        self.dialog = MDDialog(
            title="Save your postcode for next time?",
            auto_dismiss=False,
            size_hint=(0.8, 0.8),
            buttons=[MDFlatButton(text="I'LL PASS", text_color=((128 / 255), (128 / 255), (128 / 255), 1),
                                  on_press=self.on_press_pass),
                     MDRaisedButton(text="SURE!", on_press=self.on_press_sure)])
        self.dialog.open()

    def on_press_sure(self, instance):
        self.dialog.dismiss()

    def on_press_pass(self, instance):
        self.dialog.dismiss()
        user_data_dir = App.get_running_app().user_data_dir
        self.filename = join(user_data_dir, "jsonStore.json")
        self.store = JsonStore(self.filename)
        self.store.put("userInput")



class MyApp(MDApp):
    def build(self):
        self.filename = join(App.get_running_app().user_data_dir, "jsonStore.json")
        self.store = JsonStore(self.filename)
        self.store.clear()
        self.theme_cls.primary_palette = "Green"
        layout = Builder.load_file("layout.kv")  # loads the kv file
        return layout


if __name__ == "__main__": #if the name of the file is the main program (not a module imported from another file)
    MyApp().run()
