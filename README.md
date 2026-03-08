# PadSpectrum v0.0.1

Turn your Novation Launchpad S into a live spectral audio visualizer and a YouTube media controller.

---

## Contents

- `INSTALLER.bat`            -> Installation launcher (double-click)
- `install.ps1`              -> PowerShell installation script
- `padspectrum.py`           -> Main script
- `extension/`               -> Chrome extension (PadSpectrum)
- `padspectrum_banner.png`   -> Promotional visual

---

## Installation

1. **Double-click `INSTALLER.bat`**
   - Choose the installation directory (or press Enter for `Program Files`)
   - Python will be installed automatically if missing
   - pip dependencies will be installed automatically
   - A shortcut will be created on the desktop and in the Start menu

2. **Install the Chrome extension** (guided at the end of installation):
   - Chrome opens automatically on `chrome://extensions`
   - Enable Developer mode (top right)
   - Click "Load unpacked extension"
   - Select the `extension/` folder indicated

---

## Requirements

- Windows 10/11
- Launchpad S connected via USB
- Google Chrome
- **Stereo Mix enabled** (see section below)

---

## Enabling Stereo Mix (important)

The script captures Windows system audio via "Stereo Mix".
Without this step, the LEDs will not react to music.

**Steps:**
1. Right-click the sound icon in the taskbar -> **Sounds**
2. **Recording** tab
3. Right-click in the list -> **Show disabled devices**
4. Right-click **Stereo Mix** -> **Enable**
5. Right-click again -> **Set as default device**
6. Click OK

> **Note:** If "Stereo Mix" does not appear, your sound card does not support it
> natively. In that case, install **VB-Cable** (free):
> https://vb-audio.com/Cable/
> Then route Windows audio output to "CABLE Input" in sound settings,
> and the script will detect "CABLE Output" as the source.

---

## Display Modes

Press the **Arm** button to cycle through 4 modes:

| Mode | Description |
|------|-------------|
| 0    | Gradient bars (green bottom -> red top) |
| 1    | Monochrome bars (color by height) |
| 2    | Floating peak dot |
| 3    | Radial display (bass on the outside, treble at the center) |

---

## YouTube Controls

| Button   | Action                        |
|----------|-------------------------------|
| UP       | Volume +                      |
| DOWN     | Volume -                      |
| LEFT     | Previous track (YouTube)      |
| RIGHT    | Next track (YouTube)          |
| Session  | Open YouTube                  |
| User 1   | Repeat                        |
| User 2   | Shuffle                       |
| Mixer    | Mute / Unmute                 |
| Arm      | Change display mode           |

---

## Troubleshooting

| Problem                         | Solution                                               |
|---------------------------------|--------------------------------------------------------|
| LEDs not reacting               | Check that Stereo Mix is enabled and set as default    |
| Launchpad not detected          | Replug USB cable, restart script                       |
| Buttons have no effect on YouTube | Check that Chrome extension is loaded               |
| Error on launch                 | Check that Python is in Windows PATH                  |

---

## Links

- Chrome Web Store: (publication in progress)
- GitHub: https://github.com/Blounet/PadSpectrum
- Privacy policy: https://blounet.github.io/PadSpectrum/privacy-policy.html

---
---

# PadSpectrum v0.0.1 — Instructions d'installation

Transformez votre Novation Launchpad S en visualiseur spectral audio en temps reel
et en telecommande YouTube.

---

## Contenu du dossier

- `INSTALLER.bat`            -> Lanceur de l'installation (double-clic)
- `install.ps1`              -> Script d'installation PowerShell
- `padspectrum.py`           -> Script principal
- `extension/`               -> Extension Chrome (PadSpectrum)
- `padspectrum_banner.png`   -> Visuel promotionnel

---

## Installation

1. **Double-cliquez sur `INSTALLER.bat`**
   - Choisissez le repertoire d'installation (ou Entree pour `Program Files`)
   - Python sera installe automatiquement s'il est absent
   - Les dependances pip seront installees automatiquement
   - Un raccourci sera cree sur le bureau et dans le menu Demarrer

2. **Installez l'extension Chrome** (etape guidee en fin d'installation) :
   - Chrome s'ouvre automatiquement sur `chrome://extensions`
   - Activez le Mode developpeur (en haut a droite)
   - Cliquez "Charger l'extension non empaquetee"
   - Selectionnez le dossier `extension/` indique

---

## Prerequis

- Windows 10/11
- Launchpad S branche en USB
- Google Chrome
- **Mixage stereo active** (voir section ci-dessous)

---

## Activation du Mixage Stereo (important)

Le script capte le son joue par Windows via le "Mixage stereo".
Sans cette etape, les LEDs ne reagiront pas a la musique.

**Etapes :**
1. Clic droit sur l'icone son dans la barre des taches -> **Sons**
2. Onglet **Enregistrement**
3. Clic droit dans la liste -> **Afficher les peripheriques desactives**
4. Clic droit sur **Mixage stereo** -> **Activer**
5. Clic droit a nouveau -> **Definir en tant que peripherique par defaut**
6. Cliquez OK

> **Note :** Si "Mixage stereo" n'apparait pas, votre carte son ne le supporte
> pas nativement. Dans ce cas, installez **VB-Cable** (gratuit) :
> https://vb-audio.com/Cable/
> Puis routez la sortie audio de Windows vers "CABLE Input" dans les
> parametres son, et le script detectera "CABLE Output" comme source.

---

## Modes d'affichage

Appuyez sur le bouton **Arm** pour cycler entre les 4 modes :

| Mode | Description |
|------|-------------|
| 0    | Degrade par position (vert bas -> rouge haut) |
| 1    | Barre monochrome selon hauteur |
| 2    | Point flottant au sommet |
| 3    | Radial (graves en peripherie, aigus au centre) |

---

## Controles YouTube

| Bouton   | Action                        |
|----------|-------------------------------|
| UP       | Volume +                      |
| DOWN     | Volume -                      |
| LEFT     | Piste precedente (YouTube)    |
| RIGHT    | Piste suivante (YouTube)      |
| Session  | Ouvrir YouTube                |
| User 1   | Repetition                    |
| User 2   | Aleatoire                     |
| Mixer    | Mute / Unmute                 |
| Arm      | Changer mode d'affichage      |

---

## Depannage

| Probleme                        | Solution                                               |
|---------------------------------|--------------------------------------------------------|
| LEDs ne reagissent pas          | Verifier que le Mixage stereo est active et par defaut |
| Launchpad non detecte           | Rebrancher le cable USB, relancer le script            |
| Boutons sans effet sur YouTube  | Verifier que l'extension Chrome est bien chargee       |
| Erreur au lancement             | Verifier que Python est dans le PATH Windows           |

---

## Liens

- Extension Chrome Web Store : (en cours de publication)
- GitHub : https://github.com/Blounet/PadSpectrum
- Politique de confidentialite : https://blounet.github.io/PadSpectrum/privacy-policy.html
