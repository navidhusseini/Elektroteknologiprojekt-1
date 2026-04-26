import mido
import customtkinter as ctk
import pygame
import os
import threading

# --- KONFIGURATION ---
SONG_FOLDER = "./songs"

# Opret mappe hvis den mangler
if not os.path.exists(SONG_FOLDER):
    os.makedirs(SONG_FOLDER)

class DJSoftware(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialiser lyd-motor med 2 kanaler (Decks)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.deck_a = pygame.mixer.Channel(0)
        self.deck_b = pygame.mixer.Channel(1)

        self.title("PSoC 5 Pro DJ - Dual Deck")
        self.geometry("900x650")

        self.songs = [f for f in os.listdir(SONG_FOLDER) if f.endswith('.mp3')]
        if not self.songs:
            self.songs = ["Ingen sange fundet"]

        # Interne værdier
        self.vol_a_val = 0.8
        self.vol_b_val = 0.8
        self.crossfader_val = 0.0 # -1 til 1
        
        self.setup_ui()
        self.setup_midi()

    def setup_ui(self):
        # 1. MIDI Status Lys & Terminal Print Feedback
        self.status_frame = ctk.CTkFrame(self, height=40)
        self.status_frame.pack(fill="x", padx=10, pady=10)
        self.led_indicator = ctk.CTkLabel(self.status_frame, text="●", font=("Arial", 20), text_color="red")
        self.led_indicator.pack(side="left", padx=10)
        self.status_text = ctk.CTkLabel(self.status_frame, text="PSoC DISCONNECTED - Venter på enhed...")
        self.status_text.pack(side="left")

        # 2. Hovedlayout for Decks
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True, fill="both", padx=20)

        # Opret Deck A og Deck B
        self.ui_deck_a = self.create_deck_ui(self.main_frame, "DECK A", self.deck_a)
        self.ui_deck_a['frame'].grid(row=0, column=0, padx=20)
        
        self.ui_deck_b = self.create_deck_ui(self.main_frame, "DECK B", self.deck_b)
        self.ui_deck_b['frame'].grid(row=0, column=1, padx=20)

        # 3. Crossfader i bunden
        self.cf_frame = ctk.CTkFrame(self)
        self.cf_frame.pack(pady=20, padx=50, fill="x")
        ctk.CTkLabel(self.cf_frame, text="CROSSFADER (A <---> B)").pack(pady=5)
        self.crossfader = ctk.CTkSlider(self.cf_frame, from_=-1, to=1, command=self.handle_crossfade)
        self.crossfader.set(0)
        self.crossfader.pack(pady=10, fill="x", padx=20)

    def create_deck_ui(self, parent, title, channel):
        """Hjælpefunktion til at bygge UI for et deck returnerer et dictionary med referencer"""
        frame = ctk.CTkFrame(parent, width=400)
        
        # Titel
        ctk.CTkLabel(frame, text=title, font=("Arial", 20, "bold")).pack(pady=10)
        
        # Sangvælger
        song_var = ctk.StringVar(value=self.songs[0])
        ctk.CTkOptionMenu(frame, variable=song_var, values=self.songs).pack(pady=10)
        
        # Knapper
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="▶ PLAY", width=100, fg_color="green", hover_color="darkgreen", 
                      command=lambda: self.play_deck(channel, song_var.get())).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="⏹ STOP", width=100, fg_color="red", hover_color="darkred", 
                      command=channel.stop).grid(row=0, column=1, padx=5)

        # VOLUME SLIDER (Tilbage igen!)
        ctk.CTkLabel(frame, text="VOLUME").pack(pady=(15,0))
        vol_slider = ctk.CTkSlider(frame, from_=0, to=1, command=lambda v: self.set_deck_volume(channel, v))
        vol_slider.set(0.8)
        vol_slider.pack(pady=10)

        # DUMMY SLIDERS (For PSoC CC mapping)
        ctk.CTkLabel(frame, text="LOW-PASS FILTER (Ingen lyd-effekt i pygame)").pack(pady=(15,0))
        filter_slider = ctk.CTkSlider(frame, from_=0, to=127)
        filter_slider.set(127)
        filter_slider.pack(pady=10)

        ctk.CTkLabel(frame, text="PITCH (Ingen lyd-effekt i pygame)").pack(pady=(15,0))
        pitch_slider = ctk.CTkSlider(frame, from_=0, to=127)
        pitch_slider.set(64)
        pitch_slider.pack(pady=10)

        # Returner referencer, så de kan opdateres via MIDI
        return {'frame': frame, 'vol_slider': vol_slider, 'filter_slider': filter_slider, 'pitch_slider': pitch_slider}

    def setup_midi(self):
        """Sætter MIDI op og lytter i en baggrundstråd"""
        def midi_thread():
            try:
                # 1. Print i terminalen hvad vi finder
                print("--- SØGER EFTER MIDI ENHEDER ---")
                ports = mido.get_input_names()
                print(f"Fundne enheder: {ports}")
                
                port_name = next((n for n in ports if "PSoC" in n or "USB" in n), None)
                
                if port_name:
                    print(f"\n[SUCCES] Forbinder til: {port_name}")
                    with mido.open_input(port_name) as inport:
                        # Opdater UI Lys
                        self.after(0, lambda: self.led_indicator.configure(text_color="green"))
                        self.after(0, lambda: self.status_text.configure(text=f"CONNECTED: {port_name}"))
                        
                        # Lyt efter beskeder i uendelig loop
                        for msg in inport:
                            self.handle_midi_msg(msg)
                else:
                    print("\n[ADVARSEL] Ingen PSoC fundet. Kører software-only mode.")
            except Exception as e:
                print(f"\n[FEJL] MIDI Fejl: {e}")

        threading.Thread(target=midi_thread, daemon=True).start()

    # --- LYD & KONTROL LOGIK ---

    def play_deck(self, channel, song_name):
        if song_name == "Ingen sange fundet": return
        path = os.path.join(SONG_FOLDER, song_name)
        try:
            sound = pygame.mixer.Sound(path)
            channel.play(sound)
            # Opdater volumen ud fra både deck-slider og crossfader
            self.update_actual_volumes()
        except Exception as e:
            print(f"Kunne ikke loade sang: {e}")

    def set_deck_volume(self, channel, val):
        """Kaldes når man rykker på deckets egen volume slider"""
        if channel == self.deck_a:
            self.vol_a_val = float(val)
        else:
            self.vol_b_val = float(val)
        self.update_actual_volumes()

    def handle_crossfade(self, val):
        """Kaldes når man rykker crossfaderen"""
        self.crossfader_val = float(val)
        self.update_actual_volumes()

    def update_actual_volumes(self):
        """Beregner den rigtige volumen (Deck Vol * Crossfader dæmpning)"""
        # Crossfader logik: -1 = Kun A, 0 = Begge, 1 = Kun B
        cf = self.crossfader_val
        cf_a_multiplier = max(0, 1 - max(0, cf)) # Hvis cf > 0, dæmp A
        cf_b_multiplier = max(0, 1 + min(0, cf)) # Hvis cf < 0, dæmp B

        final_vol_a = self.vol_a_val * cf_a_multiplier
        final_vol_b = self.vol_b_val * cf_b_multiplier

        self.deck_a.set_volume(final_vol_a)
        self.deck_b.set_volume(final_vol_b)

    def handle_midi_msg(self, msg):
        """Her oversættes PSoC beskeder til UI handlinger"""
        if msg.type == 'control_change':
            # Eksempel: CC 7 er Deck A Volume
            if msg.control == 7:
                val = msg.value / 127.0
                self.after(0, lambda: self.ui_deck_a['vol_slider'].set(val))
                self.set_deck_volume(self.deck_a, val)
            
            # Eksempel: CC 8 er Deck B Volume
            elif msg.control == 8:
                val = msg.value / 127.0
                self.after(0, lambda: self.ui_deck_b['vol_slider'].set(val))
                self.set_deck_volume(self.deck_b, val)

            # Eksempel: CC 10 er Crossfader
            elif msg.control == 10:
                val = (msg.value / 63.5) - 1 # Omregn 0-127 til -1 til 1
                self.after(0, lambda: self.crossfader.set(val))
                self.handle_crossfade(val)

if __name__ == "__main__":
    app = DJSoftware()
    app.mainloop()