#!/usr/bin/env python3
"""
Plays a sound at a given time.
Usage: python alarmclock.py <time> [<soundfile.ext>]

Time formats accepted (examples):
  7:00 AM
  07:00 AM
  7:00
  07:00
  10:00 PM
  22:00

If not provided, defaults are used:
  DEFAULT_TIME = "7:00 AM"
  DEFAULT_SOUND = "alarm.aif"
"""

from datetime import datetime, timedelta
import time, sys, os, subprocess

# Constants
DEFAULT_TIME = "7:00 AM"
DEFAULT_SOUND = "alarm.aif"

# How often to check the clock
INTERVAL_SECONDS = 1

def parse_target_time(timestr: str) -> datetime.time:
    """
    Parse a user time string into a time object.
    Accepts 12-hour with AM/PM or 24-hour formats.
    Raises ValueError if parsing fails.
    """

    timestr = timestr.strip()
    parse_formats = ["%I:%M %p", "%I:%M%p", "%H:%M", "%H%M", "%I %p", "%I%M %p"]
    last_exc = None

    for fmt in parse_formats:
        try:
            dt = datetime.strptime(timestr, fmt)
            return dt.time()
        
        except Exception as e:
            last_exc = e

    raise ValueError(f"Unrecognized time format: '{timestr}'") from last_exc

def play_sound(soundfile: str):
    """
    Play a sound file. Tries playsound module first, then platform fallbacks.
    This function blocks until the sound playback command returns.
    """

    soundfile = os.path.expanduser(soundfile)
    if not os.path.isfile(soundfile):
        raise FileNotFoundError(f"Sound file not found: {soundfile}")

    # Try playsound (pure Python)
    try:
        from playsound import playsound
        playsound(soundfile)
        return
    
    except Exception:
        pass

    # macOS: afplay
    if sys.platform == "darwin":
        try:
            subprocess.run(["afplay", soundfile], check=True)
            return
        except Exception:
            pass

    # Linux: paplay, aplay, or ffplay
    if sys.platform.startswith("linux"):
        for cmd in (["paplay", soundfile], ["aplay", soundfile], ["ffplay", "-nodisp", "-autoexit", soundfile]):
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                continue

    # Windows: powershell or wmplayer (powershell is more reliable)
    if sys.platform.startswith("win"):

        # Use PowerShell to play sound
        ps_cmd = (
            f"[console]::beep(750,300);"
            f"(New-Object Media.SoundPlayer '{soundfile}').PlaySync();"
        )
        try:
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            return
        except Exception:
            pass

    # If none of the above succeeded, raise an error
    raise RuntimeError("No available method to play sound on this system. Install 'playsound' or ensure a command-line player is available.")

def confirm_target_today(target_time):
    """
    Return a datetime for the next occurrence of target_time.
    If the target time today is later than now, use today; otherwise use tomorrow.
    """
    now = datetime.now()
    candidate = datetime.combine(now.date(), target_time)
    if candidate <= now:

        # Schedule for tomorrow
        candidate = candidate + timedelta(days=1)
    return candidate

def main():

    # Read command-line args
    args = sys.argv[1:]
    if len(args) == 0:
        target_str = DEFAULT_TIME
        soundfile = DEFAULT_SOUND

    elif len(args) == 1:
        target_str = args[0]
        soundfile = DEFAULT_SOUND

    else:
        target_str = args[0]
        soundfile = args[1]

    # Parse target time
    try:
        target_time = parse_target_time(target_str)
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Accepted formats: 7:00 AM, 07:00, 10:00 PM, 22:00, etc.")
        sys.exit(2)

    # Resolve next occurrence (today or tomorrow)
    alarm_dt = confirm_target_today(target_time)
    alarm_str = alarm_dt.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Alarm set for: {alarm_str}")
    print(f"Sound file: {soundfile}")

    try:
        while True:
            now = datetime.now()

            if now >= alarm_dt:

                print("Alarm time reached. Playing sound...")

                try:
                    play_sound(soundfile)

                except Exception as e:
                    print(f"Failed to play sound: {e}")
                    sys.exit(3)

                print("Done.")

                # Terminate after playing.
                return
            
            # Sleep a short interval to avoid busy loop; check seconds
            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nAlarm cancelled by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
