# Alarm Clock (alarmclock.py)

Plays a sound at a specified time from the command line.

## Usage
```bash
python alarmclock.py <time> [<soundfile.ext>]
```

- If no arguments are provided, defaults are used:
  - **DEFAULT_TIME:** `7:00 AM`
  - **DEFAULT_SOUND:** `alarm.aif`

## Accepted time formats
Examples the script accepts:
- `7:00 AM`
- `07:00 AM`
- `7:00`
- `07:00`
- `10:00 PM`
- `22:00`

The parser accepts these formats (non-exhaustive): `%I:%M %p`, `%I:%M%p`, `%H:%M`, `%H%M`, `%I %p`, `%I%M %p`.

## Behavior
- The script determines the next occurrence of the requested time: if that time today is still in the future it schedules for today, otherwise for tomorrow.
- It checks the clock every second and plays the given sound file when the time is reached.
- After playback, the script exits.

## Sound playback
- The script first attempts to use the Python `playsound` module.
- Platform fallbacks:
  - macOS: `afplay`
  - Linux: `paplay`, `aplay`, or `ffplay` (`ffplay` with `-nodisp -autoexit`)
  - Windows: PowerShell SoundPlayer via `powershell -Command`
- If no playback method is available the script raises an error. Install `playsound` or ensure a command-line audio player is available.

## Exit codes
- `0` — Normal exit (including user-cancelled via Ctrl+C).
- `2` — Invalid time format.
- `3` — Failed to play sound.

## Example
Set an alarm for 6:30 AM with a custom file:
```bash
python alarmclock.py "6:30 AM" ~/sounds/myalarm.wav
```

## Notes
- Provide full or relative path to the sound file; `~` is expanded.
- The script blocks while playing sound (uses synchronous playback).
