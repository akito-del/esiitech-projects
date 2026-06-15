import sys, os, time, multiprocessing

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)
except Exception:
    BASE_DIR = os.getcwd()

os.environ['PYTHONIOENCODING'] = 'utf-8'

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QPalette

try:
    import pygame
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    PYGAME_OK = True
except Exception:
    PYGAME_OK = False

try:
    import pyttsx3
    PYTTSX3_OK = True
except Exception:
    PYTTSX3_OK = False

# ── Couleurs dans l'interface ──────────────────────────────
BG       = "#0D1826"   # fond général
CARD     = "#122030"   # fond carte centrale
SKY      = "#7EC8E3"   # bleu ciel — couleur principale
SKY_MED  = "#4A9AB5"   # bleu moyen — boutons actifs
SKY_DIM  = "#1E4A66"   # bleu sombre — bordures
G100     = "#F0F5FA"   # blanc cassé — texte principal
G400     = "#7A9AB0"   # gris moyen — texte secondaire
G700     = "#243545"   # gris sombre — fond bouton inactif
G800     = "#182535"   # gris très sombre — fond cases inactives

# ── Styles Qt stylesheet ─────────────────────────────────────────────────────
BTN_BASE = f"""
    QPushButton {{
        background: {G700}; color: {G100}; border: 1px solid {SKY_DIM};
        border-radius: 8px; font: bold 11px 'Segoe UI'; padding: 6px 16px;
    }}
    QPushButton:hover {{ background: {SKY_DIM}; border-color: {SKY_MED}; color: white; }}
    QPushButton:disabled {{ background: {G800}; color: {G700}; border-color: {G700}; }}
"""
BTN_ACTIVE = f"""
    QPushButton {{
        background: {SKY_MED}; color: white; border: 1px solid {SKY};
        border-radius: 8px; font: bold 11px 'Segoe UI'; padding: 6px 16px;
    }}
    QPushButton:hover {{ background: {SKY}; color: {BG}; }}
    QPushButton:disabled {{ background: {G800}; color: {G700}; border-color: {G700}; }}
"""
BTN_SMALL = f"""
    QPushButton {{
        background: {G700}; color: {G400}; border: 1px solid {G700};
        border-radius: 6px; font: bold 10px 'Segoe UI'; padding: 3px;
    }}
    QPushButton:hover {{ background: {SKY_DIM}; color: {G100}; border-color: {SKY_MED}; }}
    QPushButton:disabled {{ opacity: 0.3; }}
"""
BTN_SMALL_ACTIVE = f"""
    QPushButton {{
        background: {SKY_MED}; color: white; border: 1px solid {SKY};
        border-radius: 6px; font: bold 10px 'Segoe UI'; padding: 3px;
    }}
"""

# ── Données linguistiques ────────────────────────────────────────────────────
langues = {
    "fang":   {"nom":"Fang",   "prononcer":"Fant",   "nombres":{
        1:{"ecrit":"Fo","audio":"audio/fang/1.mp3"},
        2:{"ecrit":"Bein","audio":"audio/fang/2.mp3"},
        3:{"ecrit":"Lâ","audio":"audio/fang/3.mp3"},
        4:{"ecrit":"Nii","audio":"audio/fang/4.mp3"},
        5:{"ecrit":"Tan","audio":"audio/fang/5.mp3"},
        6:{"ecrit":"Samane","audio":"audio/fang/6.mp3"},
        7:{"ecrit":"Sambwa","audio":"audio/fang/7.mp3"},
        8:{"ecrit":"Môme","audio":"audio/fang/8.mp3"},
        9:{"ecrit":"Ebû","audio":"audio/fang/9.mp3"},
        10:{"ecrit":"Awôm","audio":"audio/fang/10.mp3"},
    }},
    "punu":   {"nom":"Punu",   "prononcer":"Pounou", "nombres":{
        1:{"ecrit":"Imossi","audio":"audio/punu/1.mp3"},
        2:{"ecrit":"Bibédji","audio":"audio/punu/2.mp3"},
        3:{"ecrit":"Birriéwou","audio":"audio/punu/3.mp3"},
        4:{"ecrit":"Bine","audio":"audio/punu/4.mp3"},
        5:{"ecrit":"Biranou","audio":"audio/punu/5.mp3"},
        6:{"ecrit":"Bissiaamounou","audio":"audio/punu/6.mp3"},
        7:{"ecrit":"Issambouali","audio":"audio/punu/7.mp3"},
        8:{"ecrit":"Inane","audio":"audio/punu/8.mp3"},
        9:{"ecrit":"Ifou","audio":"audio/punu/9.mp3"},
        10:{"ecrit":"Diwoumi","audio":"audio/punu/10.mp3"},
    }},
    "nzebi":  {"nom":"Nzebi",  "prononcer":"Zébi",   "nombres":{
        1:{"ecrit":"Mô","audio":"audio/nzebi/1.mp3"},
        2:{"ecrit":"Biôli","audio":"audio/nzebi/2.mp3"},
        3:{"ecrit":"Bitate","audio":"audio/nzebi/3.mp3"},
        4:{"ecrit":"Bina","audio":"audio/nzebi/4.mp3"},
        5:{"ecrit":"Bitane","audio":"audio/nzebi/5.mp3"},
        6:{"ecrit":"Bisamne","audio":"audio/nzebi/6.mp3"},
        7:{"ecrit":"Tsambe","audio":"audio/nzebi/7.mp3"},
        8:{"ecrit":"Pômbô","audio":"audio/nzebi/8.mp3"},
        9:{"ecrit":"L'bwa","audio":"audio/nzebi/9.mp3"},
        10:{"ecrit":"L'kumi","audio":"audio/nzebi/10.mp3"},
    }},
    "obamba": {"nom":"Obamba", "prononcer":"Obamba",  "nombres":{
        1:{"ecrit":"Omon","audio":"audio/obamba/1.mp3"},
        2:{"ecrit":"Vouèlè","audio":"audio/obamba/2.mp3"},
        3:{"ecrit":"Tari","audio":"audio/obamba/3.mp3"},
        4:{"ecrit":"Nah","audio":"audio/obamba/4.mp3"},
        5:{"ecrit":"Tani","audio":"audio/obamba/5.mp3"},
        6:{"ecrit":"Siami","audio":"audio/obamba/6.mp3"},
        7:{"ecrit":"Ntchami","audio":"audio/obamba/7.mp3"},
        8:{"ecrit":"Mfouomoh","audio":"audio/obamba/8.mp3"},
        9:{"ecrit":"Wa","audio":"audio/obamba/9.mp3"},
        10:{"ecrit":"Koumi","audio":"audio/obamba/10.mp3"},
    }},
}
chiffres_fr = {1:"Un",2:"Deux",3:"Trois",4:"Quatre",5:"Cinq",
               6:"Six",7:"Sept",8:"Huit",9:"Neuf",10:"Dix"}

# ── TTS dans processus séparé ─────────────────────────────────────────────────
def _parler_process(texte):
    if not PYTTSX3_OK: return
    try:
        m = pyttsx3.init()
        for v in m.getProperty('voices'):
            if 'FR' in v.id.upper() or 'fr' in v.id.lower() or 'Hortense' in v.name:
                m.setProperty('voice', v.id); break
        m.setProperty('rate', 145)
        m.say(texte); m.runAndWait(); m.stop()
    except Exception: pass

# ── Worker QThread ────────────────────────────────────────────────────────────
class ComptageWorker(QThread):
    sig_maj       = pyqtSignal(int, str, str, str)
    sig_statut    = pyqtSignal(str)
    sig_prog_done = pyqtSignal()
    sig_fin       = pyqtSignal()

    def __init__(self, codes, langue_unique, limite_fin=10):
        super().__init__()
        self.codes      = codes
        self.limite_fin = max(1, min(10, limite_fin))
        self._stop  = False
        self._pause = False
        self._saut  = None
        self._proc  = None

    def stop(self):
        self._stop = True; self._pause = False
        self._kill_vocal(); self._audio_stop()

    def toggle_pause(self): self._pause = not self._pause
    def sauter(self, n):    self._saut = n; self._pause = False

    def _audio_stop(self):
        if not PYGAME_OK: return
        try: pygame.mixer.music.stop()
        except Exception: pass

    def _audio_play(self, chemin):
        if not PYGAME_OK: return False
        p = os.path.join(BASE_DIR, chemin)
        if not os.path.exists(p): return False
        try: pygame.mixer.music.load(p); pygame.mixer.music.play(); return True
        except Exception: return False

    def _wait_audio(self):
        if not PYGAME_OK: return
        while True:
            if self._stop or self._saut is not None: self._audio_stop(); return
            if self._pause:
                try: pygame.mixer.music.pause()
                except Exception: pass
                while self._pause and not self._stop and self._saut is None: time.sleep(0.05)
                if self._stop or self._saut is not None: self._audio_stop(); return
                try: pygame.mixer.music.unpause()
                except Exception: pass
            if not pygame.mixer.music.get_busy(): break
            time.sleep(0.05)

    def _kill_vocal(self):
        if self._proc and self._proc.is_alive():
            self._proc.terminate(); self._proc.join(timeout=0.5)
        self._proc = None

    def _dire(self, texte):
        self._kill_vocal()
        if not PYTTSX3_OK or self._stop: return
        self._proc = multiprocessing.Process(target=_parler_process, args=(texte,), daemon=True)
        self._proc.start()
        while self._proc and self._proc.is_alive():
            if self._stop: self._kill_vocal(); return
            time.sleep(0.05)
        self._proc = None

    def _compter(self, code):
        if self._stop: return
        langue = langues[code]
        self.sig_statut.emit(f"Comptage en {langue['nom']}...")
        self._dire(f"En {langue['prononcer']}")
        if self._stop: return
        n = 1
        while n <= self.limite_fin:
            if self._stop: break
            if self._saut is not None:
                n = self._saut; self._saut = None
                info = langue["nombres"][n]
                self.sig_maj.emit(n, info["ecrit"], chiffres_fr[n], code)
                if self._audio_play(info["audio"]): self._wait_audio()
                if self._stop: break
                while self._pause and not self._stop and self._saut is None: time.sleep(0.05)
                if self._saut is not None: continue
                if self._stop: break
                n += 1; continue
            info = langue["nombres"][n]
            self.sig_maj.emit(n, info["ecrit"], chiffres_fr[n], code)
            if self._audio_play(info["audio"]):
                self._wait_audio()
            else:
                w = 0
                while w < 15 and not self._stop and self._saut is None:
                    if not self._pause: w += 1
                    time.sleep(0.07)
            if self._stop: break
            w = 0
            while w < 8 and not self._stop and self._saut is None:
                if not self._pause: w += 1
                time.sleep(0.1)
            n += 1
        if not self._stop:
            self.sig_prog_done.emit()
            self._dire(f"Fin du comptage en {langue['prononcer']}")
            time.sleep(0.3)

    def run(self):
        intro = (f"Comptons de 1 à {self.limite_fin} en Fant, Pounou, Zébi et Obamba"
                 if len(self.codes) > 1
                 else f"Comptons de 1 à {self.limite_fin} en {langues[self.codes[0]]['prononcer']}")
        self._dire(intro)
        if self._stop: self.sig_fin.emit(); return
        time.sleep(0.3)
        for code in self.codes:
            if self._stop: break
            self._compter(code)
            if not self._stop: time.sleep(0.8)
        if not self._stop:
            self._dire("Fin du programme. Bravo !")
            self.sig_statut.emit("✅  Terminé — Bravo !")
        self.sig_fin.emit()


# ── Fenêtre principale ────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Langues du Gabon — ESIITECH")
        self.setFixedSize(720, 580)
        self.setStyleSheet(f"QMainWindow, QWidget {{ background: {BG}; }}")
        self.langue_actuelle = None
        self.worker     = None
        self.en_cours   = False
        self.en_pause   = False
        self.limite_fin = 10
        self._build()

    def _build(self):
        root = QWidget(); self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(28, 18, 28, 18)
        lay.setSpacing(14)

        # ── En-tête ───────────────────────────────────────────────────────────
        lbl_h = QLabel("ESIITECH")
        lbl_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_h.setStyleSheet(f"color:{SKY}; font:bold 15px 'Segoe UI'; letter-spacing:4px;")
        lay.addWidget(lbl_h)

        self.lbl_titre = QLabel("Comptage de 1 à 10")
        self.lbl_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_titre.setStyleSheet(f"color:{G100}; font:bold 22px 'Segoe UI';")
        lay.addWidget(self.lbl_titre)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{SKY_DIM}; background:{SKY_DIM}; max-height:1px;")
        lay.addWidget(sep)

        # ── Boutons langue ────────────────────────────────────────────────────
        lg_row = QHBoxLayout(); lg_row.setSpacing(10)
        self.btn_lg = {}
        for code, data in langues.items():
            b = QPushButton(data["nom"])
            b.setFixedHeight(38)
            b.setStyleSheet(BTN_BASE)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, c=code: self.sel_langue(c))
            self.btn_lg[code] = b
            lg_row.addWidget(b)
        lay.addLayout(lg_row)

        # ── Sélecteur de limite ───────────────────────────────────────────────
        lim_row = QHBoxLayout(); lim_row.setSpacing(5)
        lim_row.addStretch()
        lim_row.addWidget(QLabel("Compter jusqu'à :") )
        lim_row.itemAt(1).widget().setStyleSheet(f"color:{G400}; font:10px 'Segoe UI';")
        lim_row.addSpacing(6)
        self.btn_lim = {}
        for n in range(1, 11):
            b = QPushButton(str(n))
            b.setFixedSize(34, 26)
            b.setStyleSheet(BTN_SMALL_ACTIVE if n == 10 else BTN_SMALL)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, v=n: self.set_limite(v))
            self.btn_lim[n] = b
            lim_row.addWidget(b)
        lim_row.addStretch()
        lay.addLayout(lim_row)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color:{SKY_DIM}; background:{SKY_DIM}; max-height:1px;")
        lay.addWidget(sep2)

        # ── Bouton Lancer ─────────────────────────────────────────────────────
        lancer_row = QHBoxLayout()
        lancer_row.addStretch()
        self.btn_lancer = QPushButton("▶   Lancer")
        self.btn_lancer.setFixedSize(160, 40)
        self.btn_lancer.setStyleSheet(BTN_ACTIVE)
        self.btn_lancer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lancer.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_lancer.clicked.connect(self.lancer)
        lancer_row.addWidget(self.btn_lancer)
        lancer_row.addStretch()
        lay.addLayout(lancer_row)

        # ── Carte centrale ────────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {CARD}; border: 1px solid {SKY_DIM};
                border-radius: 14px;
            }}
        """)
        card.setFixedHeight(150)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(20, 10, 20, 10)
        card_lay.setSpacing(4)

        self.lbl_langue_card = QLabel("")
        self.lbl_langue_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_langue_card.setStyleSheet(f"color:{SKY}; font:bold 11px 'Segoe UI'; letter-spacing:3px; background:transparent; border:none;")
        card_lay.addWidget(self.lbl_langue_card)

        self.lbl_chiffre = QLabel("")
        self.lbl_chiffre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_chiffre.setStyleSheet(f"color:{G100}; font:bold 52px 'Segoe UI'; background:transparent; border:none;")
        card_lay.addWidget(self.lbl_chiffre)

        bot_row = QHBoxLayout(); bot_row.setSpacing(12)
        self.lbl_mot = QLabel("")
        self.lbl_mot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mot.setStyleSheet(f"color:{SKY}; font:bold 22px 'Segoe UI'; background:transparent; border:none;")
        self.lbl_fr = QLabel("")
        self.lbl_fr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_fr.setStyleSheet(f"color:{G400}; font:italic 12px 'Segoe UI'; background:transparent; border:none;")
        bot_row.addWidget(self.lbl_mot)
        bot_row.addWidget(self.lbl_fr)
        card_lay.addLayout(bot_row)
        lay.addWidget(card)

        # ── Cases de progression ──────────────────────────────────────────────
        prog_row = QHBoxLayout(); prog_row.setSpacing(6)
        prog_row.addStretch()
        self.cases = []
        for i in range(10):
            b = QPushButton(str(i + 1))
            b.setFixedSize(52, 38)
            b.setStyleSheet(BTN_SMALL)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, n=i+1: self.clic_chiffre(n))
            self.cases.append(b)
            prog_row.addWidget(b)
        prog_row.addStretch()
        lay.addLayout(prog_row)

        sep3 = QFrame(); sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet(f"color:{SKY_DIM}; background:{SKY_DIM}; max-height:1px;")
        lay.addWidget(sep3)

        # ── Contrôles ─────────────────────────────────────────────────────────
        ctrl_row = QHBoxLayout(); ctrl_row.setSpacing(14)
        ctrl_row.addStretch()
        self.btn_pause = QPushButton("⏸   Pause")
        self.btn_pause.setFixedSize(150, 36)
        self.btn_pause.setStyleSheet(BTN_BASE)
        self.btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_stop = QPushButton("⏹   Stop")
        self.btn_stop.setFixedSize(150, 36)
        self.btn_stop.setStyleSheet(BTN_BASE)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.stop)
        ctrl_row.addWidget(self.btn_pause)
        ctrl_row.addWidget(self.btn_stop)
        ctrl_row.addStretch()
        lay.addLayout(ctrl_row)

        # ── Statut ────────────────────────────────────────────────────────────
        self.lbl_statut = QLabel("Sélectionnez une langue ou lancez toutes les langues.")
        self.lbl_statut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_statut.setStyleSheet(f"color:{G400}; font:10px 'Segoe UI';")
        lay.addWidget(self.lbl_statut)

        self._set_ctrl(False)
        self._reset_cases()

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _set_ctrl(self, on):
        self.btn_pause.setEnabled(on)
        self.btn_stop.setEnabled(on)

    def _reset_cases(self):
        for c in self.cases:
            n = c.text()
            if int(n) > self.limite_fin:
                c.setStyleSheet(BTN_SMALL + " QPushButton { opacity:0.3; color:" + G700 + "; }")
                c.setEnabled(False)
            else:
                c.setStyleSheet(BTN_SMALL)
                c.setEnabled(True)

    def _set_case(self, actif):
        for c in self.cases:
            n = int(c.text())
            if n > self.limite_fin:
                c.setStyleSheet(BTN_SMALL); c.setEnabled(False)
            elif n < actif:
                c.setStyleSheet(f"QPushButton {{ background:{SKY_DIM}; color:{SKY}; border:1px solid {SKY_DIM}; border-radius:6px; font:bold 10px 'Segoe UI'; }}")
                c.setEnabled(True)
            elif n == actif:
                c.setStyleSheet(f"QPushButton {{ background:{SKY_MED}; color:white; border:1px solid {SKY}; border-radius:6px; font:bold 10px 'Segoe UI'; }}")
                c.setEnabled(True)
            else:
                c.setStyleSheet(BTN_SMALL); c.setEnabled(True)

    def _cases_done(self):
        for c in self.cases:
            if int(c.text()) <= self.limite_fin:
                c.setStyleSheet(f"QPushButton {{ background:{SKY_DIM}; color:{SKY}; border:1px solid {SKY_DIM}; border-radius:6px; font:bold 10px 'Segoe UI'; }}")

    def _maj(self, n, mot, fr_txt, code):
        self.lbl_langue_card.setText(f"EN  {langues[code]['nom'].upper()}")
        self.lbl_chiffre.setText(str(n))
        self.lbl_mot.setText(mot)
        self.lbl_fr.setText(f"({fr_txt} en français)")
        self._set_case(n)

    def _reset_ecran(self, garde_langue=False):
        self._reset_cases()
        self.lbl_chiffre.setText(""); self.lbl_mot.setText(""); self.lbl_fr.setText("")
        self.btn_pause.setText("⏸   Pause"); self.en_pause = False
        self._set_ctrl(False); self.btn_lancer.setEnabled(True)
        if not garde_langue:
            self.lbl_langue_card.setText("")
            for b in self.btn_lg.values(): b.setStyleSheet(BTN_BASE)

    # ── Sélecteur de limite ───────────────────────────────────────────────────
    def set_limite(self, n):
        if self.en_cours: return
        self.limite_fin = n
        for v, b in self.btn_lim.items():
            b.setStyleSheet(BTN_SMALL_ACTIVE if v == n else BTN_SMALL)
        self.lbl_titre.setText(f"Comptage de 1 à {n}")
        self.lbl_statut.setText(f"Limite : {n} — Sélectionnez une langue ou lancez.")
        self._reset_cases()

    # ── Sélection langue ──────────────────────────────────────────────────────
    def sel_langue(self, code):
        if self.langue_actuelle == code and not self.en_cours:
            self.langue_actuelle = None
            for b in self.btn_lg.values(): b.setStyleSheet(BTN_BASE)
            self.lbl_langue_card.setText("")
            self.lbl_statut.setText("Sélectionnez une langue ou lancez toutes les langues.")
            return
        self._stop_worker()
        self.langue_actuelle = code
        self._reset_ecran(garde_langue=True)
        for c, b in self.btn_lg.items():
            b.setStyleSheet(BTN_ACTIVE if c == code else BTN_BASE)
        self.lbl_langue_card.setText(f"EN  {langues[code]['nom'].upper()}")
        self.lbl_statut.setText(f"{langues[code]['nom']} sélectionné — Lancez ou cliquez sur un chiffre.")

    # ── Clic case chiffre ─────────────────────────────────────────────────────
    def clic_chiffre(self, n):
        if not self.langue_actuelle:
            self.lbl_statut.setText("⚠  Sélectionnez d'abord une langue."); return
        if self.en_cours and self.worker:
            self.worker.sauter(n)
            self.en_pause = True; self.btn_pause.setText("▶   Reprendre")
            self.lbl_statut.setText("En pause — cliquez Reprendre pour continuer.")
        else:
            code = self.langue_actuelle
            info = langues[code]["nombres"][n]
            self._maj(n, info["ecrit"], chiffres_fr[n], code)
            self.lbl_statut.setText(f"🔊  {langues[code]['nom']} — {chiffres_fr[n]} : {info['ecrit']}")
            if PYGAME_OK:
                path = os.path.join(BASE_DIR, info["audio"])
                if os.path.exists(path):
                    try: pygame.mixer.music.load(path); pygame.mixer.music.play()
                    except Exception: pass

    # ── Contrôles ─────────────────────────────────────────────────────────────
    def toggle_pause(self):
        if not self.en_cours or not self.worker: return
        self.en_pause = not self.en_pause
        self.worker.toggle_pause()
        if self.en_pause:
            self.btn_pause.setText("▶   Reprendre")
            self.lbl_statut.setText("En pause")
        else:
            self.btn_pause.setText("⏸   Pause")
            self.lbl_statut.setText(f"Comptage en {langues[self.langue_actuelle]['nom']}...")

    def stop(self):
        self._stop_worker()
        self.langue_actuelle = None
        self._reset_ecran(garde_langue=False)
        self.lbl_statut.setText("Sélectionnez une langue ou lancez toutes les langues.")

    def _stop_worker(self):
        if self.worker:
            self.worker.stop(); self.worker.wait(2000); self.worker = None
        self.en_cours = False; self.en_pause = False
        for b in self.btn_lim.values(): b.setEnabled(True)

    # ── Lancer ────────────────────────────────────────────────────────────────
    def lancer(self):
        if self.en_cours: return
        codes = [self.langue_actuelle] if self.langue_actuelle else list(langues.keys())
        self._reset_ecran(garde_langue=self.langue_actuelle is not None)
        if self.langue_actuelle:
            for c, b in self.btn_lg.items():
                b.setStyleSheet(BTN_ACTIVE if c == self.langue_actuelle else BTN_BASE)
        self.en_cours = True
        self.btn_lancer.setEnabled(False)
        self._set_ctrl(True)
        for b in self.btn_lim.values(): b.setEnabled(False)
        self.worker = ComptageWorker(codes, self.langue_actuelle, self.limite_fin)
        self.worker.sig_maj.connect(self._maj)
        self.worker.sig_statut.connect(self.lbl_statut.setText)
        self.worker.sig_prog_done.connect(self._cases_done)
        self.worker.sig_fin.connect(self._on_fin)
        self.worker.start()

    def _on_fin(self):
        self.en_cours = False; self.worker = None
        self.lbl_chiffre.setText("✓")
        self.btn_lancer.setEnabled(True)
        self._set_ctrl(False)
        self.btn_pause.setText("⏸   Pause"); self.en_pause = False
        for b in self.btn_lim.values(): b.setEnabled(True)

    def closeEvent(self, e):
        self._stop_worker()
        if PYGAME_OK:
            try: pygame.mixer.quit()
            except Exception: pass
        super().closeEvent(e)


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,     QColor(BG))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(G100))
    pal.setColor(QPalette.ColorRole.Button,     QColor(G700))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(G100))
    pal.setColor(QPalette.ColorRole.Highlight,  QColor(SKY_MED))
    app.setPalette(pal)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())