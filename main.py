# ==============================================================================
# 1. OMGEVINGSVARIABELEN (Moeten absoluut bovenaan staan!)
# ==============================================================================
import os
os.environ["KIVY_WINDOW"] = "sdl2"
os.environ["KIVY_TEXT"]   = "sdl2"
os.environ["KIVY_IMAGE"]  = "imageio"

# ==============================================================================
# 2. ALGEMENE IMPORTS & LOGGING
# ==============================================================================
import hashlib
import webbrowser
import requests
import logging

logger = logging.getLogger(__name__)

# ==============================================================================
# 3. KIVY & PLYER IMPORTS
# ==============================================================================
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label  import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, Rectangle, RoundedRectangle
from plyer import notification, vibrator

import storage

# ==============================================================================
# 4. STEALTH KLEURENPALET (Gedempt & OLED-vriendelijk)
# ==============================================================================
BG_COLOR     = (0.11, 0.11, 0.12, 1)  # Zeer donkergrijs, bijna zwart
CARD_COLOR   = (0.18, 0.18, 0.20, 1)  # Iets lichter grijs voor containers
INPUT_COLOR  = (0.14, 0.14, 0.15, 1)  # Donkere achtergrond voor invoervelden
ACCENT_COLOR = (0.30, 0.65, 0.55, 1)  # Matte, gedempte teal (onopvallend)
TEXT_COLOR   = (0.85, 0.85, 0.85, 1)  # Zacht wit (geen eye-strain)
DIM_TEXT     = (0.50, 0.50, 0.50, 1)  # Neutraal grijs voor secundaire info

# ==============================================================================
# 5. APP LOGICA
# ==============================================================================
GEHASHDE_PIN = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
is_locked = True

class VeiligThuis(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.timer_event = None
        self.resterende_tijd = 3
        
        # Teken de donkere hoofd-achtergrond
        with self.canvas.before:
            Color(rgba=BG_COLOR)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        self.ververs_scherm()

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def ververs_scherm(self):
        self.clear_widgets()
        
        # 1. DISCREET SLOT SCHERM (Lijkt op een systeem-wachtwoord prompt) -----
        if is_locked:
            self.add_widget(Label(
                text="🔒 System Storage\nAuthentication required:", 
                font_size='16sp', color=DIM_TEXT, halign='center', size_hint_y=None, height=80
            ))
            
            self.pin_input = TextInput(
                password=True, multiline=False, size_hint_y=None, height=50, 
                halign='center', font_size='20sp', background_color=INPUT_COLOR, 
                foreground_color=TEXT_COLOR, cursor_color=ACCENT_COLOR
            )
            self.add_widget(self.pin_input)
            
            btn = Button(
                text="Access", size_hint_y=None, height=50, 
                background_normal='', background_color=CARD_COLOR, color=TEXT_COLOR, bold=True
            )
            btn.bind(on_release=self.check_pin)
            self.add_widget(btn)
            self.add_widget(BoxLayout()) # Spacer
        
        # 2. VEILIG HOOFDSCHERM ("System Notes" Dummy Masker) ------------------
        else:
            # SOS Knop (Gecamoufleerd als "Systeem Diagnostiek" om opvallen te voorkomen)
            self.sos_btn = Button(
                text="⚡ RUN SYSTEM DIAGNOSTICS (SOS)", 
                background_normal='', background_color=CARD_COLOR, 
                color=TEXT_COLOR, font_size='16sp', size_hint_y=None, height=70, bold=True
            )
            self.sos_btn.bind(on_release=self.start_nood_bevestiging)
            self.add_widget(self.sos_btn)

            # Discrete notitie-titel
            self.add_widget(Label(
                text="📝 Local Notes Log (AES-256):", 
                font_size='13sp', color=DIM_TEXT, size_hint_y=None, height=25, halign='left'
            ))
            
            # Invoer-box
            notitie_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
            self.notitie_input = TextInput(
                hint_text="Enter discrete log entry...", multiline=False, font_size='14sp',
                background_color=INPUT_COLOR, foreground_color=TEXT_COLOR, cursor_color=ACCENT_COLOR
            )
            opslaan_btn = Button(
                text="Save", size_hint_x=None, width=80, 
                background_normal='', background_color=ACCENT_COLOR, color=BG_COLOR, bold=True
            )
            opslaan_btn.bind(on_release=self.notitie_opslaan_actie)
            
            notitie_box.add_widget(self.notitie_input)
            notitie_box.add_widget(opslaan_btn)
            self.add_widget(notitie_box)

            # Scrollbaar discreet overzicht van eerdere notities
            scroll = ScrollView(size_hint=(1, 1))
            self.lijst_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
            self.lijst_layout.bind(minimum_height=self.lijst_layout.setter('height'))
            
            self.laad_notities_in_scherm()
            scroll.add_widget(self.lijst_layout)
            self.add_widget(scroll)

            # Info knop gecamoufleerd
            self.hulp_btn = Button(
                text="System Readme & Resources", 
                background_normal='', background_color=INPUT_COLOR, color=DIM_TEXT, size_hint_y=None, height=40
            )
            self.hulp_btn.bind(on_release=self.toon_hulpbronnen)
            self.add_widget(self.hulp_btn)

    def check_pin(self, _):
        global is_locked
        if hashlib.sha256(self.pin_input.text.encode()).hexdigest() == GEHASHDE_PIN:
            is_locked = False
            self.ververs_scherm()
        else:
            self.pin_input.text = ""

    def notitie_opslaan_actie(self, _):
        tekst = self.notitie_input.text.strip()
        if tekst:
            if storage.sla_notitie_op(tekst):
                self.notitie_input.text = ""
                self.laad_notities_in_scherm()

    def laad_notities_in_scherm(self):
        self.lijst_layout.clear_widgets()
        notities = storage.haal_notities_op()
        
        if not notities:
            self.lijst_layout.add_widget(Label(
                text="No index data found.", font_size='13sp', 
                size_hint_y=None, height=30, color=DIM_TEXT
            ))
        
        for n in notities:
            notitie_regel = Label(
                text=f"• {n} ({n[:16]})", 
                font_size='13sp', color=TEXT_COLOR, size_hint_y=None, height=25, 
                halign='left', valign='middle'
            )
            notitie_regel.bind(size=notitie_regel.setter('text_size'))
            self.lijst_layout.add_widget(notitie_regel)

    # --- SOS Systeem met Discrete bewoordingen ---
    def start_nood_bevestiging(self, _):
        if self.timer_event: return
        self.resterende_tijd = 3
        self.sos_btn.text = f"⚠️ CRITICAL FAULT IN {self.resterende_tijd}...\n[CLICK TO ABORT PROCESS]"
        self.sos_btn.background_color = (0.7, 0.4, 0.1, 1) # Gedempt oranje
        self.sos_btn.unbind(on_release=self.start_nood_bevestiging)
        self.sos_btn.bind(on_release=self.annuleer_nood)
        self.timer_event = Clock.schedule_interval(self.tel_af, 1.0)

    def tel_af(self, dt):
        self.resterende_tijd -= 1
        
        if platform == "android":
            try: vibrator.vibrate(time=0.1)
            except Exception as e: logger.warning(f"Vibratie fout: {e}")
        else:
            logger.debug("Vibratie overgeslagen (geen Android platform)")

        if self.resterende_tijd <= 0:
            Clock.unschedule(self.timer_event)
            self.timer_event = None
            self.voer_echt_alarm_uit()
        else:
            self.sos_btn.text = f"⚠️ CRITICAL FAULT IN {self.resterende_tijd}...\n[CLICK TO ABORT PROCESS]"

    def annuleer_nood(self, _):
        if self.timer_event:
            Clock.unschedule(self.timer_event)
            self.timer_event = None
        self.sos_btn.text = "⚡ RUN SYSTEM DIAGNOSTICS (SOS)"
        self.sos_btn.background_color = CARD_COLOR
        self.sos_btn.unbind(on_release=self.annuleer_nood)
        self.sos_btn.bind(on_release=self.start_nood_bevestiging)

    def voer_echt_alarm_uit(self):
        self.annuleer_nood(None)
        
        if platform == "android":
            try: vibrator.vibrate(time=1.0)
            except: pass
            
        try: notification.notify(title="System Alert", message="Diagnostics protocol initialized.", timeout=5)
        except: pass
        
        webbrowser.open("tel:+310800113")

        try: requests.post("http://127.0.0.1:8000", json={"user_hash": "anoniem_mobiel"}, timeout=3)
        except Exception as e: logger.error(f"Network error: {e}")

    def toon_hulpbronnen(self, *_):
        from kivy.uix.popup import Popup
        txt = ("🚨 EMERGENCY CODE: 112\n\n"
               "🔹 Support Line A: 0800-0432\n"
               "  (Secure counseling line)\n\n"
               "🔹 Support Line B: 0800-0113\n\n"
               "🔹 Support Line C: 0900-0101")
        popup = Popup(
            title="System Documentation", 
