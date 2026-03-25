import json
import os


class Config:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.data = {
            "prev_key": "tab",
            "next_key": "²",
            "leader_key": "f1",
            "sync_key": "f3",
            "sync_right_key": "",
            "treasure_key": "",
            "swap_xp_drop_key": "",
            "toggle_app_key": "f10",
            "paste_enter_key": "",
            "auto_zaap_key": "",
            "refresh_key": "f5",
            "calib_key": "f4",
            "sort_taskbar_key": "",
            "invite_group_key": "",
            "zaap_delay": "1.0",
            "game_inv_key": "i",
            "game_char_key": "c",
            "game_spell_key": "s",
            "game_haven_key": "h",
            "radial_menu_active": True,
            "radial_menu_hotkey": "alt+left_click",
            "leader_name": "",
            "accounts_state": {},
            "accounts_team": {},
            "current_mode": "ALL",
            "classes": {},
            "custom_order": [],
            "macro_positions": {
                "chat_position": None,
                "xp_drop_button": None,
                "zaaps": {},
            },
            "advanced_bind_mode": "cycle",
            "persistent_character_binds": {},
            "cycle_row_binds": [
                "ctrl+F1",
                "ctrl+F2",
                "ctrl+F3",
                "ctrl+F4",
                "ctrl+F5",
                "ctrl+F6",
                "ctrl+F7",
                "ctrl+F8",
            ],
            "click_speed": "Lent",
            "toolbar_active": False,
            "spam_click_active": False,
            "return_to_leader": True,
            "show_tooltips": True,
            "toolbar_x": 100,
            "toolbar_y": 100,
            "volume_level": 50,
            "ignore_organizer_warning": False,
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def reset_settings(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        self.__init__(self.filename)
