# ==============================================================================
# 1. OMGEVINGSVARIABELEN (Moeten absoluut bovenaan staan!)
# ==============================================================================
import os
os.environ["KIVY_WINDOW"] = "sdl2"
os.environ["KIVY_TEXT"]   = "sdl2"
os.environ["KIVY_IMAGE"]  = "imageio"

# ==============================================================================
# 2. ALGEMENE IMPORTS & LOGGING CONFIGURATIE
# ==============================================================================
import hashlib
import webbrowser
import requests
import logging

# Koppel aan de standaard Kivy logger
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
from plyer import notification, vibrator

import storage

# ==============================================================================
# 4. CONFIGURATIE & APP LOGICA
# ==============================================================================
GEHASHDE_PIN = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
is_locked = True

class VeiligThuis(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.timer_event = None
        self.resterende_tijd = 3
        self.ververs_scherm()

    def ververs_scherm(self):
        self.clear_widgets()
        
        if is_locked:
            self.add_widget(Label(text="🔒 Veilige Ruimte\nVoer uw pincode in:", font_size='18sp', halign='center', size_hint_y=None, height=80))
            self.pin_input = TextInput(password=True, multiline=False, size_hint_y=None, height=60, halign='center', font_size='22sp')
            self.add_widget(self.pin_input)
            
            btn = Button(text="Ontgrendelen", size_hint_y=None, height=60, background_color=(0.2, 0.8, 0.2, 1), bold=True)
            btn.bind(on_release=self.check_pin)
            self.add_widget(btn)
        
        else:
            self.sos_btn = Button(text="🚨 NOOD / HULP INSCHAKELEN", background_color=(1, 0, 0, 1), bold=True, font_size='20sp', size_hint_y=None, height=90)
            self.sos_btn.bind(on_release=self.start_nood_bevestiging)
            self.add_widget(self.sos_btn)

            self.add_widget(Label(text="📝 Gecentreerd Logboek (AES-256 Gecodeerd):", font_size='14sp', size_hint_y=None, height=30, halign='left'))
            
            notitie_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
            self.notitie_input = TextInput(hint_text="Typ een discrete notitie...", multiline=False, font_size='14sp')
            opslaan_btn = Button(text="Opslaan", size_hint_x=None, width=100, background_color=(0, 0.8, 0.5, 1), bold=True)
            opslaan_btn.bind(on_release=self.notitie_opslaan_actie)
            
            notitie_box.add_widget(self.notitie_input)
            notitie_box.add_widget(opslaan_btn)
            self.add_widget(notitie_box)

            scroll = ScrollView(size_hint=(1, 1))
            self.lijst_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
            self.lijst_layout.bind(minimum_height=self.lijst_layout.setter('height'))
            
            self.laad_notities_in_scherm()
            scroll.add_widget(self.lijst_layout)
            self.add_widget(scroll)

            self.hulp_btn = Button(text="Informatie & Hulpbronnen", background_color=(0, 0, 1, 1), size_hint_y=None, height=50, bold=True)
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
            self.lijst_layout.add_widget(Label(text="Geen eerdere notities gevonden.", font_size='13sp', size_hint_y=None, height=30, color=(0.7,0.7,0.7,1)))
        
        for n in notities:
            notitie_regel = Label(
                text=f"• {n} ({n[:16]})", 
                font_size='14sp', 
                size_hint_y=None, 
                height=30, 
                halign='left',
                valign='middle'
            )
            notitie_regel.bind(size=notitie_regel.setter('text_size'))
            self.lijst_layout.add_widget(notitie_regel)

    # --- SOS Systeem met de nieuwe Logger ---
    def start_nood_bevestiging(self, _):
        if self.timer_event: return
        self.resterende_tijd = 3
        self.sos_btn.text = f"⚠️ ALARM GAAT AF IN {self.resterende_tijd}...\n[KLIK HIER OM TE ANNULLEREN]"
        self.sos_btn.background_color = (1, 0.5, 0, 1)
        self.sos_btn.unbind(on_release=self.start_nood_bevestiging)
        self.sos_btn.bind(on_release=self.annuleer_nood)
        self.timer_event = Clock.schedule_interval(self.tel_af, 1.0)

    def tel_af(self, dt):
        self.resterende_tijd -= 1
        
        # Verbeterde logging/vibratie check
        if platform == "android":
            try: vibrator.vibrate(time=0.1)
            except Exception as e: logger.warning(f"Vibratie mislukt op Android: {e}")
        else:
            logger.debug("Vibratie overgeslagen (geen Android platform)")

        if self.resterende_tijd <= 0:
            Clock.unschedule(self.timer_event)
            self.timer_event = None
            self.voer_echt_alarm_uit()
        else:
            self.sos_btn.text = f"⚠️ ALARM GAAT AF IN {self.resterende_tijd}...\n[KLIK HIER OM TE ANNULLEREN]"

    def annuleer_nood(self, _):
        if self.timer_event:
            Clock.unschedule(self.timer_event)
            self.timer_event = None
        self.sos_btn.text = "🚨 NOOD / HULP INSCHAKELEN"
        self.sos_btn.background_color = (1, 0, 0, 1)
        self.sos_btn.unbind(on_release=self.annuleer_nood)
        self.sos_btn.bind(on_release=self.start_nood_bevestiging)

    def voer_echt_alarm_uit(self):
        self.annuleer_nood(None)
        
        if platform == "android":
            try: vibrator.vibrate(time=1.0)
            except: pass
            
        try: notification.notify(title="🚨 Alarm geactiveerd", message="De noodoproep wordt gestart.", timeout=5)
        except: pass
        
        webbrowser.open("tel:+310800113")

        try: requests.post("http://127.0.0.1:8000", json={"user_hash": "anoniem_mobiel"}, timeout=3)
        except Exception as e: logger.error(f"Backend server onbereikbaar: {e}")

    def toon_hulpbronnen(self, *_):
        from kivy.uix.popup import Popup
        txt = ("🚨 ACUTE SPOED: 112\n\n"
               "🔹 Veilig Thuis: 0800-0432\n"
               "  (Huiselijk geweld & kindermishandeling)\n\n"
               "🔹 113 Zelfmoordpreventie: 0800-0113\n\n"
               "🔹 Slachtofferhulp: 0900-0101\n\n"
               "🔹 De Kindertelefoon: 0800-0432")
        popup = Popup(title="Belangrijke Hulpbronnen", content=Label(text=txt, halign='left', valign='middle', font_size='15sp', line_height=1.2), size_hint=(0.95, 0.75))
        popup.content.bind(size=popup.content.setter('text_size'))
        popup.open()

class VeiligApp(App):
    def build(self):
        return VeiligThuis()

if __name__ == '__main__':
    VeiligApp().run()
