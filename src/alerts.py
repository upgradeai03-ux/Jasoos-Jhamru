"""
WasteGuard AI - Audio & Visual Alert Engine
Provides real audio alert mechanism with cooldown timer, toggle controls,
graceful audio hardware fallback, and visual warning state indicators.
"""

import time
import os
import platform
from typing import Dict, Any, Tuple

# Optional sound engine imports
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class AlertEngine:
    def __init__(self, cooldown_seconds: float = 5.0, enabled: bool = True):
        self.cooldown_seconds = cooldown_seconds
        self.enabled = enabled
        self.last_alert_time: float = 0.0
        self.total_alerts_triggered: int = 0
        self.audio_system_working: bool = True

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"[WARN] Pygame audio init failed: {e}. Falling back to winsound/visual alerts.")
                self.audio_system_working = False

    def trigger_violation_alert(
        self,
        detected_class: str,
        selected_bin: str
    ) -> Dict[str, Any]:
        """
        Triggers an audio alert if enabled and cooldown time has elapsed.

        Returns:
            Dict status containing:
            {
                "alert_played": bool,
                "reason": str,
                "cooldown_remaining": float,
                "visual_warning": bool
            }
        """
        now = time.time()
        elapsed = now - self.last_alert_time

        if not self.enabled:
            return {
                "alert_played": False,
                "reason": "Alert system is disabled.",
                "cooldown_remaining": 0.0,
                "visual_warning": True
            }

        if elapsed < self.cooldown_seconds:
            cooldown_rem = round(self.cooldown_seconds - elapsed, 1)
            return {
                "alert_played": False,
                "reason": f"Alert cooldown active ({cooldown_rem}s remaining).",
                "cooldown_remaining": cooldown_rem,
                "visual_warning": True
            }

        # Cooldown passed -> Play real audio alert
        played = self._play_sound_alert()
        self.last_alert_time = time.time()
        self.total_alerts_triggered += 1

        return {
            "alert_played": played,
            "reason": "Audio alert triggered!" if played else "Audio playback failed; visual alert activated.",
            "cooldown_remaining": self.cooldown_seconds,
            "visual_warning": True
        }

    def _play_sound_alert(self) -> bool:
        """Plays real system beep or sound tone cross-platform."""
        played = False

        # Attempt Winsound beep on Windows
        if WINSOUND_AVAILABLE and platform.system() == "Windows":
            try:
                # 1000 Hz frequency, 300 ms duration
                winsound.Beep(1000, 300)
                played = True
            except Exception as e:
                print(f"[WARN] Winsound playback failed: {e}")

        # Fallback to Pygame tone if winsound fails
        if not played and PYGAME_AVAILABLE:
            try:
                # Generate simple sine wave tone buffer if no audio file is present
                sample_rate = 44100
                duration = 0.3  # seconds
                n_samples = int(sample_rate * duration)
                buf = np.sin(2 * np.pi * np.arange(n_samples) * 880 / sample_rate).astype(np.float32)
                sound = pygame.sndarray.make_sound((buf * 32767).astype(np.int16))
                sound.play()
                played = True
            except Exception as e:
                print(f"[WARN] Pygame synth sound failed: {e}")

        return played

    def reset_cooldown(self) -> None:
        """Resets the alert cooldown timer immediately."""
        self.last_alert_time = 0.0
