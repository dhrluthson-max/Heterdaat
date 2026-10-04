import os
os.environ["KIVY_WINDOW"] = "sdl2"
os.environ["KIVY_TEXT"]   = "sdl2"
os.environ["KIVY_NO_ARGS"] = "1"

import hashlib
import webbrowser
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InAppTerminalHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    def emit(self, record):
        t = datetime.now().strftime('%H:%M:%S')
        self.callback(f"{t} - {record.levelname} - {record.getMessage()}")

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, Rectangle

import storage

GEHASHDE_PIN = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
is_locked = True

class VeiligThuis(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.timer_event = None
        self.resterende_tijd = 3
        logger.addHandler(InAppTerminalHandler(self.append_terminal_log))
        with self.canvas.before:
            Color(rgba=(0.11, 0.11, 0.12, 1))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        self.ververs_scherm()

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def ververs_scherm(self):
        self.clear_widgets()
        if is_locked:
            self.add_widget(Label(text="🔒 System Storage\nAuthentication required:", halign='center', size_hint_y=None, height=80))
            self.pin_input = TextInput(password=True, multiline=False, size_hint_y=None, height=50, halign='center', font_size='20sp', background_color=(0.14, 0.14, 0.15, 1), foreground_color=(0.85, 0.85, 0.85, 1))
            self.add_widget(self.pin_input)
            btn = Button(text="Access", size_hint_y=None, height=50, background_normal='', background_color=(0.18, 0.18, 0.20, 1), color=(0.85, 0.85, 0.85, 1), bold=True)
            btn.bind(on_release=self.check_pin)
            self.add_widget(btn)
            self.add_widget(BoxLayout())
        else:
            self.sos_btn = Button(text="⚡ RUN SYSTEM DIAGNOSTICS (SOS)", background_normal='', background_color=(0.18, 0.18, 0.20, 1), color=(0.85, 0.85, 0.85, 1), font_size='16sp', size_hint_y=None, height=60, bold=True)
            self.sos_btn.bind(on_release=self.start_nood_bevestiging)
            self.add_widget(self.sos_btn)
            
            self.add_widget(Label(text="📝 Local Notes Log:", font_size='13sp', color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=20, halign='left'))
            notitie_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
            self.notitie_input = TextInput(hint_text="Enter new discrete log entry...", multiline=False, background_color=(0.14, 0.14, 0.15, 1), foreground_color=(0.85, 0.85, 0.85, 1))
            opslaan_btn = Button(text="Save", size_hint_x=None, width=80, background_normal='', background_color=(0.3, 0.65, 0.55, 1), bold=True)
            opslaan_btn.bind(on_release=self.notitie_opslaan_actie)
            notitie_box.add_widget(self.notitie_input)
            notitie_box.add_widget(opslaan_btn)
            self.notitie_box = notitie_box
            self.add_widget(notitie_box)

            self.notitie_scroll = ScrollView(size_hint=(1, 0.4))
            self.lijst_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
            self.lijst_layout.bind(minimum_height=self.lijst_layout.setter('height'))
            self.notitie_scroll.add_widget(self.lijst_layout)
            self.add_widget(self.notitie_scroll)
            self.laad_notities_in_scherm()

            self.add_widget(Label(text="💻 System Live Terminal Log:", font_size='13sp', color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=20, halign='left'))
            self.terminal_scroll = ScrollView(size_hint=(1, 0.4))
            self.terminal_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=4, padding=10)
            self.terminal_layout.bind(minimum_height=self.terminal_layout.setter('height'))
            self.terminal_scroll.add_widget(self.terminal_layout)
            self.add_widget(self.terminal_scroll)
            logger.info("DASHBOARD SECURE SUBSYSTEM INITIALIZED.")

    def append_terminal_log(self, text):
        if hasattr(self, 'terminal_layout'):
            log_line = Label(text=f"> {text}", font_size='11sp', color=(0.2, 0.8, 0.2, 1), size_hint_y=None, height=20, halign='left', valign='middle')
            log_line.bind(size=log_line.setter('text_size'))
            self.terminal_layout.add_widget(log_line)

    def check_pin(self, _):
        global is_locked
        if hashlib.sha256(self.pin_input.text.encode()).hexdigest() == GEHASHDE_PIN:
            is_locked = False
            self.ververs_scherm()
        else:
            self.pin_input.text = ""

    def notitie_opslaan_actie(self, _):
        tekst = self.notitie_input.text.strip()
        if tekst and storage.sla_notitie_op(tekst):
            logger.info("Log entry successfully encrypted and saved.")
            self.notitie_input.text = ""
            self.laad_notities_in_scherm()

    def laad_notities_in_scherm(self):
        self.lijst_layout.clear_widgets()
        for n in storage.haal_notities_op():
            notitie_regel = Label(text=f"• {n}", font_size='13sp', color=(0.85, 0.85, 0.85, 1), size_hint_y=None, height=25, halign='left', valign='middle')
            notitie_regel.bind(size=notitie_regel.setter('text_size'))
            self.lijst_layout.add_widget(notitie_regel)

    def start_nood_bevestiging(self, _):
        if self.timer_event: return
        self.resterende_tijd = 3
        logger.warning("CRITICAL PROCESS INITIATED. COUNTDOWN STARTING.")
        self.sos_btn.text = f"⚠️ CRITICAL FAULT IN {self.resterende_tijd}...\n[CLICK TO ABORT PROCESS]"
        self.sos_btn.background_color = (0.7, 0.4, 0.1, 1)
        self.sos_btn.unbind(on_release=self.start_nood_bevestiging)
        self.sos_btn.bind(on_release=self.annuleer_nood)
        self.timer_event = Clock.schedule_interval(self.tel_af, 1.0)

    def annuleer_nood(self, _):
        if self.timer_event:
            Clock.unschedule(self.timer_event)
            self.timer_event = None
        logger.info("PROCESS ABORTED BY USER. SYSTEM STABILIZED.")
        self.reset_sos_knop()

    def reset_sos_knop(self):
        self.sos_btn.text = "⚡ RUN SYSTEM DIAGNOSTICS (SOS)"
        self.sos_btn.background_color = (0.18, 0.18, 0.20, 1)
        self.sos_btn.unbind(on_release=self.annuleer_nood)
        if not self.timer_event:
            self.sos_btn.bind(on_release=self.start_nood_bevestiging)

    def tel_af(self, dt):
        self.resterende_tijd -= 1
        logger.info(f"COUNTDOWN ACTIVE: T-MINUS {self.resterende_tijd} SECONDS.")
        if self.resterende_tijd <= 0:
            if self.timer_event:
                Clock.unschedule(self.timer_event)
                self.timer_event = None
            self.reset_sos_knop()
            self.voer_echt_alarm_uit()
            return False
        else:
            self.sos_btn.text = f"⚠️ CRITICAL FAULT IN {self.resterende_tijd}...\n[CLICK TO ABORT PROCESS]"

    def voer_echt_alarm_uit(self):
        logger.critical("EMERGENCY SIGNAL TRIGGERED. CONNECTING TO CRISIS LINE.")
        url = "http://127.0.0.1"
        try:
            resp = requests.post(url, json={"user_hash": "anoniem_mobiel"}, timeout=3)
            logger.info(f"Backend gaf respons: {resp.status_code}")
        except Exception as exc:
            logger.error(f"Geen backend verbinding mogelijk: {exc}")
        
        try:
            webbrowser.open("tel:113")
        except Exception:
            webbrowser.open("https://113.nl")

class MainApp(App):
    def build(self):
        self.title = "System Dashboard"
        return VeiligThuis()

if __name__ == '__main__':
    MainApp().run()
