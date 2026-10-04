import os
os.environ["KIVY_WINDOW"] = "sdl2"
os.environ["KIVY_TEXT"]   = "sdl2"
os.environ["KIVY_NO_ARGS"] = "1"
import requests, logging, webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding, self.spacing = 30, 20
        self.status_label = Label(text="DASHBOARD SECURE SUBSYSTEM INITIALIZED.", font_size='18sp', bold=True, color=get_color_from_hex("#00FF00"))
        self.add_widget(self.status_label)
        self.timer_label = Label(text="SYSTEM READY", font_size='32sp', bold=True, color=get_color_from_hex("#FFFFFF"))
        self.add_widget(self.timer_label)
        self.action_button = Button(text="TRIGGER EMERGENCY", font_size='20sp', bold=True, background_color=get_color_from_hex("#FF0000"), background_normal='')
        self.action_button.bind(on_press=self.start_countdown)
        self.add_widget(self.action_button)
        self.countdown_event = None
        self.time_left = 3

    def start_countdown(self, instance):
        if self.countdown_event:
            Clock.unschedule(self.countdown_event)
            self.countdown_event = None
            self.time_left = 3
            self.timer_label.text = "SYSTEM STABILIZED"
            self.status_label.text = "PROCESS ABORTED BY USER."
            self.status_label.color = get_color_from_hex("#00FF00")
            self.action_button.text = "TRIGGER EMERGENCY"
            return
        self.status_label.text = "CRITICAL PROCESS INITIATED."
        self.status_label.color = get_color_from_hex("#FFCC00")
        self.action_button.text = "ABORT PROCESS"
        self.time_left = 3
        self.timer_label.text = f"T-MINUS {self.time_left} SECONDS"
        self.countdown_event = Clock.schedule_interval(self.trigger_countdown, 1.0)

    def trigger_countdown(self, dt):
        self.time_left -= 1
        self.timer_label.text = f"T-MINUS {self.time_left} SECONDS"
        if self.time_left <= 0:
            Clock.unschedule(self.countdown_event)
            self.countdown_event = None
            self.voer_echt_alarm_uit()

    def voer_echt_alarm_uit(self):
        logger.critical("EMERGENCY SIGNAL TRIGGERED. CONNECTING TO CRISIS LINE.")
        url = "http://127.0.0"
        
        try:
            resp = requests.post(url, json={"user_hash": "anoniem_mobiel"}, timeout=3)
            logger.info(f"Backend gaf respons: {resp.status_code}")
            if resp.status_code == 200:
                self.status_label.text = "BACKEND CONNECTED: SIGNAL RECEIVED."
                self.status_label.color = get_color_from_hex("#00FF00")
            else:
                self.status_label.text = f"BACKEND ERROR: STATUS {resp.status_code}"
        except Exception as exc:
            logger.error(f"Geen backend verbinding mogelijk: {exc}")
            self.status_label.text = "CONNECTION REFUSED: CHECK BACKEND"
        
        try:
            webbrowser.open("tel:113")
        except Exception:
            webbrowser.open("https://113.nl")

class MainApp(App):
    def build(self):
        self.title = "Heterdaat Secure Dashboard"
        return MainLayout()

if __name__ == '__main__':
    MainApp().run()
