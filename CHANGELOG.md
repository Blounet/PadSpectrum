# Changelog — PadSpectrum

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.0.1] — 2026-03-08 — Alpha

### Added
- Spectral audio visualizer on the Launchpad S 8x8 LED grid
- 4 display modes (gradient bars, monochrome bars, floating peak dot, radial)
- Arm button cycles through display modes
- YouTube playback controls (next, previous, repeat, shuffle, open)
- System volume control (up, down, mute) via Windows multimedia keys
- Chrome extension with WebSocket connection (localhost:8765)
- Auto-launch Chrome on m.youtube.com if closed (Session button)
- ARM_LOCKOUT protection against parasitic MIDI messages
- Anti-bounce filter (DEBOUNCE_MS) on top row buttons
- Noise floor threshold to avoid residual display when no audio
- Automatic loopback device detection (Stereo Mix, VB-Cable, etc.)
- Windows installer (INSTALLER.bat + install.ps1)
- PowerShell script creates desktop and Start menu shortcuts

### Known Issues
- Occasional spurious MIDI messages on LEFT and USER1 buttons (mitigated by ARM_LOCKOUT)
- WebSocket reconnection may trigger phantom commands on track change
