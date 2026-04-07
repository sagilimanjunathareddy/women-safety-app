# main.py
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# utils (keep your existing implementations)
from utils.audio_capture import record_audio
from utils.scream_detector import ScreamDetector
from utils.camera_capture import capture_photo
from utils.location_tracker import get_location
from utils.alert_sender import send_alert
from utils.siren_player import play_siren
from utils.trusted_contacts import add_contact, load_contacts, save_contacts, edit_contact, delete_contact
from utils.history_manager import log_alert, load_history

# MapView imports - attempt import, but app will still run if unavailable
try:
    from kivy_garden.mapview import MapMarker
    MAPVIEW_AVAILABLE = True
except Exception:
    MAPVIEW_AVAILABLE = False

KV_FILE = "womensafety.kv"


class SafetyScreen(Screen):
    location_text = StringProperty("📍 Location: Unknown")
    monitoring = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.detector = ScreamDetector()
        except Exception as e:
            self.detector = None
            print("⚠️ Warning: could not initialize ScreamDetector:", e)

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.ids.status.text = "🔴 Monitoring..."
            Clock.schedule_interval(self.detect_scream, 8)
            Clock.schedule_interval(self.update_location, 15)
            # do immediate location update on start
            self.update_location()

    def stop_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            self.ids.status.text = "🟢 Idle"
            try:
                Clock.unschedule(self.detect_scream)
            except Exception:
                pass
            try:
                Clock.unschedule(self.update_location)
            except Exception:
                pass

    def detect_scream(self, dt):
        if self.detector is None:
            print("⚠️ No detector available; skipping detection.")
            return

        record_audio("assets/audio.wav", duration=4)
        try:
            result = self.detector.predict("assets/audio.wav")
        except Exception as e:
            print("⚠️ Detector error:", e)
            result = 0

        if result == 1:
            self.ids.status.text = "🚨 Scream Detected!"
            play_siren()
            capture_photo("assets/photo.jpg")
            location = get_location()
            try:
                send_alert("assets/audio.wav", "assets/photo.jpg", location)
            except Exception as e:
                print("❌ Error sending alert:", e)
            try:
                log_alert("scream", location)
            except Exception:
                pass
        else:
            self.ids.status.text = "🟢 All Clear"

    def record_emergency_voice(self):
        self.ids.status.text = "🎤 Recording Emergency Voice..."
        record_audio("assets/emergency_audio.wav", duration=10)
        self.ids.status.text = "✅ Emergency Voice Recorded!"
        capture_photo("assets/emergency_photo.jpg")
        location = get_location()
        try:
            send_alert("assets/emergency_audio.wav", "assets/emergency_photo.jpg", location)
        except Exception as e:
            print("❌ Error sending alert:", e)
        try:
            log_alert("manual_voice", location)
        except Exception:
            pass

    def play_manual_siren(self):
        play_siren()
        self.ids.status.text = "🚨 Siren Activated!"

    def update_location(self, dt=None):
        """
        - Fetch location using your existing get_location()
        - Update label text (root.location_text)
        - If MapView is present, center map & update user marker
        """
        location = get_location()
        lat = location.get("latitude", "0")
        lon = location.get("longitude", "0")
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except Exception:
            lat_f = 0.0
            lon_f = 0.0

        addr = location.get("address", "Unavailable")
        self.location_text = f"📍 {addr} ({lat_f:.5f}, {lon_f:.5f})"

        # Map integration: center and update marker
        try:
            root = App.get_running_app().root
            if not root:
                return
            # ScreenManager-based app: get map screen by name
            if hasattr(root, "get_screen"):
                map_screen = root.get_screen("map")
            else:
                map_screen = None

            if map_screen and "mapview" in map_screen.ids:
                map_widget = map_screen.ids.mapview
                # center map
                try:
                    map_widget.center_on(lat_f, lon_f)
                except Exception as e:
                    # mapview operations may fail if widget not fully initialized
                    print("⚠️ Map center_on failed:", e)

                # create/update marker
                try:
                    # place/update user_marker attribute on map_screen
                    if hasattr(map_screen, "user_marker") and map_screen.user_marker is not None:
                        map_screen.user_marker.lat = lat_f
                        map_screen.user_marker.lon = lon_f
                    else:
                        if MAPVIEW_AVAILABLE:
                            # MapMarker will be imported earlier if available
                            map_screen.user_marker = MapMarker(lat=lat_f, lon=lon_f, source="")
                            map_widget.add_widget(map_screen.user_marker)
                        else:
                            # MapView not installed; ignore
                            pass
                except Exception as e:
                    print("⚠️ Map marker update failed:", e)
        except Exception:
            # don't crash application if map update fails
            pass


class ContactsScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh_contacts_list()

    def refresh_contacts_list(self):
        self.ids.contacts_box.clear_widgets()
        contacts = load_contacts()
        if not contacts:
            self.ids.contacts_box.add_widget(Label(text="No contacts saved.", color=(1, 1, 1, 0.7), size_hint_y=None, height=40))
            return

        for idx, c in enumerate(contacts):
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=90, spacing=6, padding=6)
            info = f"[b]{c.get('name','Unnamed')}[/b]\n"
            if c.get("phone"):
                info += f"📱 {c.get('phone')}  "
            if c.get("whatsapp"):
                info += f"🟢 {c.get('whatsapp')}  "
            if c.get("email"):
                info += f"\n📧 {c.get('email')}"
            lbl = Label(text=info, markup=True, halign="left", valign="middle", text_size=(self.width * 0.6, None))
            row.add_widget(lbl)

            btn_edit = Button(text="Edit", size_hint_x=None, width=80)
            btn_edit.bind(on_release=lambda bt, i=idx: self.open_edit_popup(i))
            btn_del = Button(text="Delete", size_hint_x=None, width=80, background_color=(1, 0.2, 0.2, 1))
            btn_del.bind(on_release=lambda bt, i=idx: self.confirm_delete(i))

            row.add_widget(btn_edit)
            row.add_widget(btn_del)
            self.ids.contacts_box.add_widget(row)

    def open_add_contact(self):
        content = BoxLayout(orientation="vertical", spacing=8, padding=8)
        inp_name = TextInput(hint_text="Name", multiline=False)
        inp_email = TextInput(hint_text="Email", multiline=False)
        inp_phone = TextInput(hint_text="Phone (+91...)", multiline=False)
        inp_whatsapp = TextInput(hint_text="WhatsApp (whatsapp:+91...)", multiline=False)
        content.add_widget(Label(text="Add Trusted Contact"))
        content.add_widget(inp_name)
        content.add_widget(inp_email)
        content.add_widget(inp_phone)
        content.add_widget(inp_whatsapp)
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=8)
        btn_save = Button(text="Save")
        btn_cancel = Button(text="Cancel")
        btn_box.add_widget(btn_save)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(title="Add Contact", content=content, size_hint=(0.9, 0.7))
        btn_cancel.bind(on_release=popup.dismiss)

        def do_save(*args):
            name = inp_name.text.strip()
            email = inp_email.text.strip()
            phone = inp_phone.text.strip()
            whatsapp = inp_whatsapp.text.strip()
            if not name:
                inp_name.hint_text = "Name (required)"
                return
            add_contact(name, email, phone, whatsapp)
            popup.dismiss()
            self.refresh_contacts_list()

        btn_save.bind(on_release=do_save)
        popup.open()

    def open_edit_popup(self, index):
        contacts = load_contacts()
        if index < 0 or index >= len(contacts):
            return
        c = contacts[index]
        content = BoxLayout(orientation="vertical", spacing=8, padding=8)
        inp_name = TextInput(text=c.get("name", ""), multiline=False)
        inp_email = TextInput(text=c.get("email", ""), multiline=False)
        inp_phone = TextInput(text=c.get("phone", ""), multiline=False)
        inp_whatsapp = TextInput(text=c.get("whatsapp", ""), multiline=False)
        content.add_widget(Label(text="Edit Contact"))
        content.add_widget(inp_name)
        content.add_widget(inp_email)
        content.add_widget(inp_phone)
        content.add_widget(inp_whatsapp)
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=8)
        btn_save = Button(text="Save")
        btn_cancel = Button(text="Cancel")
        btn_box.add_widget(btn_save)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(title="Edit Contact", content=content, size_hint=(0.9, 0.7))
        btn_cancel.bind(on_release=popup.dismiss)

        def do_save(*args):
            new_data = {
                "name": inp_name.text.strip(),
                "email": inp_email.text.strip(),
                "phone": inp_phone.text.strip(),
                "whatsapp": inp_whatsapp.text.strip()
            }
            try:
                edit_contact(index, new_data)
            except TypeError:
                contacts[index].update(new_data)
                save_contacts(contacts)
            popup.dismiss()
            self.refresh_contacts_list()

        btn_save.bind(on_release=do_save)
        popup.open()

    def confirm_delete(self, index):
        contacts = load_contacts()
        if index < 0 or index >= len(contacts):
            return
        name = contacts[index].get("name", "Contact")
        content = BoxLayout(orientation="vertical", spacing=8, padding=8)
        content.add_widget(Label(text=f"Delete {name}?"))
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=8)
        btn_yes = Button(text="Yes", background_color=(1, 0.2, 0.2, 1))
        btn_no = Button(text="No")
        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)
        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.6, 0.35))
        btn_no.bind(on_release=popup.dismiss)

        def do_delete(*args):
            try:
                delete_contact(index)
            except Exception:
                contacts = load_contacts()
                contacts.pop(index)
                save_contacts(contacts)
            popup.dismiss()
            self.refresh_contacts_list()

        btn_yes.bind(on_release=do_delete)
        popup.open()


class MapScreen(Screen):
    pass


class HistoryScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh_history()

    def refresh_history(self):
        self.ids.history_box.clear_widgets()
        try:
            items = load_history()
        except Exception:
            items = []
        if not items:
            self.ids.history_box.add_widget(Label(text="No alerts yet.", color=(1, 1, 1, 0.8)))
            return
        for h in reversed(items):
            txt = f"[b]{h.get('type','ALERT').upper()}[/b]\n{h.get('time')}\n{h.get('address')}\nLat: {h.get('latitude')}, Lon: {h.get('longitude')}"
            lbl = Label(text=txt, markup=True, size_hint_y=None, height=90, color=(1, 1, 1, 0.9))
            self.ids.history_box.add_widget(lbl)


class WomenSafetyApp(App):
    def build(self):
        if not os.path.exists(KV_FILE):
            raise FileNotFoundError(f"{KV_FILE} not found")
        return Builder.load_file(KV_FILE)


if __name__ == "__main__":
    WomenSafetyApp().run()