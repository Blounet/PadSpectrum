"""
PadSpectrum v0.0.1 — Visualiseur spectral audio (loopback Windows)
============================================================
Boutons du bandeau superieur :
    UP      (CC 104) -- Volume +
    DOWN    (CC 105) -- Volume -
    LEFT    (CC 106) -- Piste precedente (YouTube)
    RIGHT   (CC 107) -- Piste suivante (YouTube)
    Session (CC 108) -- Ouvrir YouTube (lance Chrome si ferme)
    User1   (CC 109) -- Repetition
    User2   (CC 110) -- Aleatoire
    Mixer   (CC 111) -- Mute/Unmute

Colonne droite :
    Arm     (note 120) -- Changer mode d'affichage LED

Modes d'affichage :
    0 -- Degrade par position (vert bas -> rouge haut)
    1 -- Barre monochrome selon hauteur
    2 -- Point flottant au sommet
    3 -- Radial (graves en peripherie, aigus au centre)
"""

import sys
import time
import threading
import queue
import asyncio
import subprocess
import os
import numpy as np
import sounddevice as sd
import mido
import mido.backends.rtmidi  # noqa
import ctypes
import websockets

# ---------------------------------------------
# CONFIG
# ---------------------------------------------
SAMPLE_RATE = 44100
BLOCK_SIZE  = 1024
N_COLS      = 8
N_ROWS      = 8
SMOOTHING   = 0.35   # lissage temporel des niveaux (0=instantane, 1=infini)
GAIN        = 2.5    # amplification du signal avant normalisation

FREQ_BANDS = [
    (20,    80),     # bande 0 -- sub-basses
    (80,   200),     # bande 1 -- basses
    (200,  500),     # bande 2 -- bas-mediums
    (500,  1200),    # bande 3 -- mediums
    (1200, 3000),    # bande 4 -- haut-mediums
    (3000, 6000),    # bande 5 -- presence
    (6000, 12000),   # bande 6 -- brillance
    (12000,20000),   # bande 7 -- air
]

# Boutons bandeau superieur (CC)
BTN_UP      = 104
BTN_DOWN    = 105
BTN_LEFT    = 106
BTN_RIGHT   = 107
BTN_SESSION = 108
BTN_USER1   = 109
BTN_USER2   = 110
BTN_MIXER   = 111

# Bouton colonne droite (note)
BTN_ARM     = 120

# Etat global des modes
DISPLAY_MODE  = 0
N_MODES       = 4
last_arm_time = 0.0
ARM_LOCKOUT   = 0.1  # secondes -- protege contre les faux messages MIDI parasites
                     # qui se declenchent apres un appui sur Arm

# ---------------------------------------------
# MAPPING RADIAL (mode 3)
# La grille 8x8 est divisee en 4 carres de 4x4.
# Chaque lettre correspond a une bande frequentielle :
#
# Carre 1 (cols 0-3, rows 0-3)     Carre 2 (cols 4-7, rows 0-3)
#   a a a a                           e e e e
#   a b b b                           f f f e
#   a b c c                           g g f e
#   a b c d                           h g f e
#
# Carre 3 (cols 0-3, rows 4-7)     Carre 4 (cols 4-7, rows 4-7)
#   i j k l                           p o n m
#   i j k k                           o o n m
#   i j j j                           n n n m
#   i i i i                           m m m m
#
# Mapping bande -> lettres :
#   bande 0 (20-80 Hz)     : a, m  (bord exterieur -- graves)
#   bande 1 (80-200 Hz)    : e, i
#   bande 2 (200-500 Hz)   : b, n
#   bande 3 (500-1200 Hz)  : f, j
#   bande 4 (1200-3000 Hz) : c, o
#   bande 5 (3000-6000 Hz) : g, k
#   bande 6 (6000-12000 Hz): d, p
#   bande 7 (12-20 kHz)    : h, l  (centre -- aigus)
# ---------------------------------------------
_C1 = [
    [0, 0, 0, 0],  # a a a a
    [0, 2, 2, 2],  # a b b b
    [0, 2, 4, 4],  # a b c c
    [0, 2, 4, 6],  # a b c d
]
_C2 = [
    [1, 1, 1, 1],  # e e e e
    [3, 3, 3, 1],  # f f f e
    [5, 5, 3, 1],  # g g f e
    [7, 5, 3, 1],  # h g f e
]
_C3 = [
    [1, 3, 5, 7],  # i j k l
    [1, 3, 5, 5],  # i j k k
    [1, 3, 3, 3],  # i j j j
    [1, 1, 1, 1],  # i i i i
]
_C4 = [
    [6, 4, 2, 0],  # p o n m
    [4, 4, 2, 0],  # o o n m
    [2, 2, 2, 0],  # n n n m
    [0, 0, 0, 0],  # m m m m
]

# Construction du dictionnaire bande -> liste de (col, row)
BAND_CELLS = {i: [] for i in range(8)}
for _row in range(4):
    for _col in range(4):
        BAND_CELLS[_C1[_row][_col]].append((_col,     _row))
        BAND_CELLS[_C2[_row][_col]].append((_col + 4, _row))
        BAND_CELLS[_C3[_row][_col]].append((_col,     _row + 4))
        BAND_CELLS[_C4[_row][_col]].append((_col + 4, _row + 4))

# ---------------------------------------------
# COULEURS
# Launchpad S : velocity = 16*g + r + 12, r et g dans [0, 3]
# ---------------------------------------------
def make_color(r, g):
    return 16 * g + r + 12

COLOR_OFF    = 0
COLOR_ACTIVE = make_color(3, 3)  # jaune vif -- feedback visuel des boutons

# Degrade 8 niveaux : rouge vif (haut/fort) -> vert faible (bas/faible)
GRADIENT = [
    make_color(3, 0),  # row 0 -- rouge vif
    make_color(3, 1),  # row 1 -- orange-rouge
    make_color(3, 2),  # row 2 -- ambre
    make_color(3, 3),  # row 3 -- jaune vif
    make_color(2, 3),  # row 4 -- jaune-vert
    make_color(1, 3),  # row 5 -- vert-jaune vif
    make_color(0, 2),  # row 6 -- vert moyen
    make_color(0, 1),  # row 7 -- vert faible
]

def row_color(row):
    """Mode 0 -- couleur selon la position dans la barre (0=haut, 7=bas)."""
    return GRADIENT[row]

def height_color(filled_rows):
    """Mode 1/2 -- couleur selon la hauteur globale de la barre."""
    if filled_rows == 0:
        return COLOR_OFF
    return GRADIENT[N_ROWS - filled_rows]

def level_color(level):
    """Mode 3 -- couleur selon un niveau normalise 0.0-1.0."""
    if level < 0.05:
        return COLOR_OFF
    idx = int((1.0 - level) * (len(GRADIENT) - 1))
    return GRADIENT[max(0, min(len(GRADIENT) - 1, idx))]

# ---------------------------------------------
# VOLUME WINDOWS
# Utilise ctypes pour simuler les touches multimedia
# (pycaw abandonnee -- erreur d'activation AudioDevice)
# ---------------------------------------------
def volume_up():
    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)

def volume_down():
    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)

def volume_mute():
    ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)

# ---------------------------------------------
# CHROME
# ---------------------------------------------
def is_chrome_running():
    """Verifie si Chrome est en cours d'execution via tasklist."""
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq chrome.exe'],
        capture_output=True, text=True
    )
    return 'chrome.exe' in result.stdout

def open_chrome_youtube():
    """Lance Chrome sur m.youtube.com -- cherche dans les emplacements standards."""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            subprocess.Popen([path, "https://m.youtube.com"])
            return

# ---------------------------------------------
# LAUNCHPAD S -- MIDI
# Note grille    : note = row * 16 + col
# Bandeau sup.   : CC 104-111
# Colonne droite : note = row * 16 + 8 (Arm = note 120)
# ---------------------------------------------
def find_launchpad_output():
    for name in mido.get_output_names():
        if "launchpad" in name.lower():
            return name
    return None

def find_launchpad_input():
    for name in mido.get_input_names():
        if "launchpad" in name.lower():
            return name
    return None

def note_for_cell(col, row):
    return row * 16 + col

def led_on(port, col, row, color):
    port.send(mido.Message('note_on', note=note_for_cell(col, row), velocity=color))

def led_off(port, col, row):
    port.send(mido.Message('note_on', note=note_for_cell(col, row), velocity=COLOR_OFF))

def top_btn_led(port, cc, color):
    port.send(mido.Message('control_change', control=cc, value=color))

def side_btn_led(port, note, color):
    port.send(mido.Message('note_on', note=note, velocity=color))

def clear_all(port):
    """Eteint toutes les LEDs de la grille et des boutons."""
    port.send(mido.Message('sysex', data=[0x00, 0x20, 0x29, 0x02, 0x0A, 0x14, 0x00]))
    for r in range(N_ROWS):
        for c in range(N_COLS):
            led_off(port, c, r)
    for cc in [BTN_UP, BTN_DOWN, BTN_LEFT, BTN_RIGHT,
               BTN_SESSION, BTN_USER1, BTN_USER2, BTN_MIXER]:
        top_btn_led(port, cc, COLOR_OFF)
    side_btn_led(port, BTN_ARM, COLOR_OFF)

# ---------------------------------------------
# AUDIO -- LOOPBACK
# Necessite "Mixage stereo" active dans les
# parametres d'enregistrement Windows
# ---------------------------------------------
def find_loopback_device():
    """Detecte automatiquement le peripherique loopback."""
    keywords = ["stereo mix", "mixage", "loopback", "what u hear",
                "vb-audio", "vb-cable", "cable output", "wave out mix"]
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            for kw in keywords:
                if kw in d['name'].lower():
                    return i
    return None

def list_input_devices():
    print("\nPeripheriques d'entree disponibles :")
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            print(f"  [{i:2d}] {d['name']}")
    print()

# ---------------------------------------------
# ANALYSE SPECTRALE
# FFT avec fenetre de Hanning, decoupage en
# bandes logarithmiques, normalisation et seuil
# ---------------------------------------------
def compute_band_levels(audio_block, sample_rate):
    mono     = audio_block.mean(axis=1) if audio_block.ndim > 1 else audio_block
    windowed = mono * np.hanning(len(mono))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs    = np.fft.rfftfreq(len(mono), d=1.0 / sample_rate)

    levels = np.zeros(N_COLS)
    for i, (f_low, f_high) in enumerate(FREQ_BANDS):
        mask = (freqs >= f_low) & (freqs < f_high)
        if mask.any():
            levels[i] = np.sqrt(np.mean(spectrum[mask] ** 2))

    levels  = np.log1p(levels * GAIN)
    max_val = levels.max()

    # Seuil absolu : ignore le bruit de fond (valeur pre-normalisation)
    if max_val < 0.01:
        return np.zeros(N_COLS)

    levels /= max_val
    return np.clip(levels, 0.0, 1.0)

# ---------------------------------------------
# WEBSOCKET
# Serveur local sur localhost:8765
# Reçoit les connexions de l'extension Chrome
# ---------------------------------------------
ws_command_queue = queue.Queue()
ws_client = None

async def ws_handler(websocket):
    global ws_client
    ws_client = websocket
    try:
        await websocket.wait_closed()
    finally:
        ws_client = None

async def ws_dispatcher():
    """Consomme la queue de commandes et les envoie au client WebSocket."""
    while True:
        try:
            cmd = ws_command_queue.get_nowait()
            if ws_client:
                await ws_client.send(cmd)
        except queue.Empty:
            pass
        await asyncio.sleep(0.05)

async def ws_main():
    async with websockets.serve(ws_handler, "localhost", 8765):
        await ws_dispatcher()

def start_ws_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws_main())

# ---------------------------------------------
# LISTENER MIDI INPUT
# Tourne dans un thread dedie (bloquant)
# Gere les boutons bandeau et le bouton Arm
# ---------------------------------------------
def midi_input_listener(input_name, lp_out, stop_event):
    global DISPLAY_MODE, last_arm_time

    # Anti-rebond : ignore les appuis trop rapproches sur un meme CC
    last_cc_time = {}
    DEBOUNCE_MS  = 500

    with mido.open_input(input_name) as lp_in:
        for msg in lp_in:
            if stop_event.is_set():
                break

            # --- Boutons bandeau superieur (CC, value=127 = appui) ---
            if msg.type == 'control_change' and msg.value == 127:
                cc  = msg.control
                now = time.time() * 1000

                # Filtre anti-rebond
                if now - last_cc_time.get(cc, 0) < DEBOUNCE_MS:
                    continue
                last_cc_time[cc] = now

                if cc == BTN_UP:
                    volume_up()
                    top_btn_led(lp_out, BTN_UP, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_UP, COLOR_OFF)).start()

                elif cc == BTN_DOWN:
                    volume_down()
                    top_btn_led(lp_out, BTN_DOWN, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_DOWN, COLOR_OFF)).start()

                elif cc == BTN_LEFT:
                    # ARM_LOCKOUT : protege contre les faux messages parasites
                    if time.time() - last_arm_time > ARM_LOCKOUT:
                        ws_command_queue.put("prev_track")
                    top_btn_led(lp_out, BTN_LEFT, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_LEFT, COLOR_OFF)).start()

                elif cc == BTN_RIGHT:
                    if time.time() - last_arm_time > ARM_LOCKOUT:
                        ws_command_queue.put("next_track")
                    top_btn_led(lp_out, BTN_RIGHT, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_RIGHT, COLOR_OFF)).start()

                elif cc == BTN_SESSION:
                    # Lance Chrome si ferme, sinon ouvre YouTube dans l'onglet existant
                    if time.time() - last_arm_time > ARM_LOCKOUT:
                        if is_chrome_running():
                            ws_command_queue.put("open_youtube")
                        else:
                            threading.Thread(target=open_chrome_youtube, daemon=True).start()
                    top_btn_led(lp_out, BTN_SESSION, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_SESSION, COLOR_OFF)).start()

                elif cc == BTN_USER1:
                    if time.time() - last_arm_time > ARM_LOCKOUT:
                        ws_command_queue.put("toggle_repeat")
                    top_btn_led(lp_out, BTN_USER1, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_USER1, COLOR_OFF)).start()

                elif cc == BTN_USER2:
                    if time.time() - last_arm_time > ARM_LOCKOUT:
                        ws_command_queue.put("toggle_shuffle")
                    top_btn_led(lp_out, BTN_USER2, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_USER2, COLOR_OFF)).start()

                elif cc == BTN_MIXER:
                    volume_mute()
                    top_btn_led(lp_out, BTN_MIXER, COLOR_ACTIVE)
                    threading.Timer(0.1, lambda: top_btn_led(lp_out, BTN_MIXER, COLOR_OFF)).start()

            # --- Bouton Arm (note 120) -- cycle entre les modes d'affichage ---
            elif msg.type == 'note_on' and msg.note == BTN_ARM and msg.velocity == 127:
                last_arm_time = time.time()
                DISPLAY_MODE  = (DISPLAY_MODE + 1) % N_MODES
                side_btn_led(lp_out, BTN_ARM, COLOR_ACTIVE)
                threading.Timer(0.1, lambda: side_btn_led(lp_out, BTN_ARM, COLOR_OFF)).start()

# ---------------------------------------------
# BOUCLE PRINCIPALE
# 3 threads : audio (callback), MIDI input, WebSocket
# ---------------------------------------------
def main():
    global DISPLAY_MODE

    lp_out_name = find_launchpad_output()
    lp_in_name  = find_launchpad_input()
    if not lp_out_name:
        print("Launchpad S non trouve.")
        sys.exit(1)

    device_id = find_loopback_device()
    if device_id is None:
        list_input_devices()
        try:
            device_id = int(input("Entrez l'index du peripherique loopback : "))
        except ValueError:
            sys.exit(1)

    smoothed   = np.zeros(N_COLS)
    prev_grid  = np.full((N_COLS, N_ROWS), -1, dtype=int)
    stop_event = threading.Event()

    # Demarrage du serveur WebSocket dans un thread dedie
    ws_thread = threading.Thread(target=start_ws_server, daemon=True)
    ws_thread.start()

    with mido.open_output(lp_out_name) as lp_out:
        clear_all(lp_out)
        time.sleep(0.1)

        # Demarrage du listener MIDI dans un thread dedie
        if lp_in_name:
            t = threading.Thread(
                target=midi_input_listener,
                args=(lp_in_name, lp_out, stop_event),
                daemon=True
            )
            t.start()

        def audio_callback(indata, frames, time_info, status):
            nonlocal smoothed, prev_grid
            levels   = compute_band_levels(indata, SAMPLE_RATE)
            smoothed = SMOOTHING * smoothed + (1.0 - SMOOTHING) * levels

            # Seuil bas : evite l'affichage residuel quand aucun son ne passe
            smoothed[smoothed < 0.02] = 0.0

            if DISPLAY_MODE == 3:
                # Mode radial : chaque bande frequentielle colore ses LEDs
                for band, cells in BAND_CELLS.items():
                    color = level_color(smoothed[band])
                    for (col, row) in cells:
                        if prev_grid[col, row] != color:
                            if color == COLOR_OFF:
                                led_off(lp_out, col, row)
                            else:
                                led_on(lp_out, col, row, color)
                            prev_grid[col, row] = color
            else:
                # Modes 0, 1, 2 : affichage en barres verticales
                for col in range(N_COLS):
                    filled_rows = int(smoothed[col] * N_ROWS)

                    for row in range(N_ROWS):
                        lit = filled_rows > 0 and row >= N_ROWS - filled_rows

                        if DISPLAY_MODE == 0:
                            # Degrade par position dans la barre
                            color = row_color(row) if lit else COLOR_OFF
                        elif DISPLAY_MODE == 1:
                            # Barre monochrome selon hauteur globale
                            color = height_color(filled_rows) if lit else COLOR_OFF
                        else:
                            # Point flottant : seulement la LED du sommet
                            color = height_color(filled_rows) if (lit and row == N_ROWS - filled_rows) else COLOR_OFF

                        if prev_grid[col, row] != color:
                            if color == COLOR_OFF:
                                led_off(lp_out, col, row)
                            else:
                                led_on(lp_out, col, row, color)
                            prev_grid[col, row] = color

        with sd.InputStream(
            device=device_id,
            channels=2,
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            callback=audio_callback,
        ):
            try:
                while True:
                    time.sleep(0.01)
            except KeyboardInterrupt:
                stop_event.set()
                clear_all(lp_out)

if __name__ == "__main__":
    main()
