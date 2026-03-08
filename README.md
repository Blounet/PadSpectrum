# PadSpectrum v0.0.1 — Instructions d'installation

Transformez votre Novation Launchpad S en visualiseur spectral audio en temps reel
et en telecommande YouTube.

## Contenu du dossier

- `INSTALLER.bat`            -> Lanceur de l'installation (double-clic)
- `install.ps1`              -> Script d'installation PowerShell
- `launchpad_spectrum.py`    -> Script principal
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
- GitHub : https://github.com/david-36800/padspectrum
- Politique de confidentialite : https://david-36800.github.io/launchpad-s-controller/privacy-policy.html
