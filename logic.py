import ctypes
import time
from ctypes import POINTER
import win32gui
import win32con
import win32api
import win32process
import keyboard


AZERTY_TO_SCAN = {
    "a": 16,
    "z": 17,
    "e": 18,
    "r": 19,
    "t": 20,
    "y": 21,
    "u": 22,
    "i": 23,
    "o": 24,
    "p": 25,
    "q": 30,
    "s": 31,
    "d": 32,
    "f": 33,
    "g": 34,
    "h": 35,
    "j": 36,
    "k": 37,
    "l": 38,
    "m": 39,
    "w": 44,
    "x": 45,
    "c": 46,
    "v": 47,
    "b": 48,
    "n": 49,
    "1": 2,
    "2": 3,
    "3": 4,
    "4": 5,
    "5": 6,
    "6": 7,
    "7": 8,
    "8": 9,
    "9": 10,
    "0": 11,
    "f1": 59,
    "f2": 60,
    "f3": 61,
    "f4": 62,
    "f5": 63,
    "f6": 64,
    "f7": 65,
    "f8": 66,
    "f9": 67,
    "f10": 68,
    "f11": 87,
    "f12": 88,
    "tab": 15,
    "enter": 28,
    "space": 57,
    "esc": 1,
    "backspace": 14,
    "²": 41,
    "&": 2,
    "é": 3,
    '"': 4,
    "'": 5,
    "(": 6,
    "-": 7,
    "è": 8,
    "_": 9,
    "ç": 10,
    "à": 11,
    ")": 12,
    "=": 13,
    "num 1": 79,
    "num 2": 80,
    "num 3": 81,
    "num 4": 75,
    "num 5": 76,
    "num 6": 77,
    "num 7": 71,
    "num 8": 72,
    "num 9": 73,
    "num 0": 82,
}


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("_input",)
    _fields_ = [("type", ctypes.c_ulong), ("_input", _INPUT_UNION)]


def screen_to_norm(x, y):
    sw = ctypes.windll.user32.GetSystemMetrics(78)
    sh = ctypes.windll.user32.GetSystemMetrics(79)
    ox = ctypes.windll.user32.GetSystemMetrics(76)
    oy = ctypes.windll.user32.GetSystemMetrics(77)
    return int((x - ox) * 65535 / sw), int((y - oy) * 65535 / sh)


class DofusLogic:
    def __init__(self, config):
        self.config = config
        self.all_accounts = []
        self.leader_hwnd = None
        self.error_callback = None

    def set_error_callback(self, callback):
        self.error_callback = callback

    def _notify_error(self, msg):
        if self.error_callback:
            self.error_callback(msg)

    def scan_slots(self):
        windows_trouvees = []

        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                if win32gui.GetClassName(hwnd) == "UnityWndClass":
                    titre = win32gui.GetWindowText(hwnd)
                    if titre.strip():
                        windows_trouvees.append((hwnd, titre))
            return True

        win32gui.EnumWindows(enum_windows_callback, None)

        nouveaux_comptes = []
        for hwnd, titre in windows_trouvees:
            titre_clean = titre.strip()
            if titre_clean.lower().startswith("dofus") or not titre_clean:
                continue
            parts = titre_clean.split(" - ")
            pseudo = parts[0].strip()
            classe = parts[1].strip() if len(parts) > 1 else "Inconnu"
            self.config.data["classes"][pseudo] = classe
            etat_actif = self.config.data["accounts_state"].get(pseudo, True)
            equipe = self.config.data["accounts_team"].get(pseudo, "Team 1")
            nouveaux_comptes.append(
                {
                    "name": pseudo,
                    "hwnd": hwnd,
                    "active": etat_actif,
                    "team": equipe,
                    "classe": classe,
                }
            )

        custom_order = self.config.data.get("custom_order", [])
        for acc in nouveaux_comptes:
            if acc["name"] not in custom_order:
                custom_order.append(acc["name"])

        if len(custom_order) > 50:
            active_names = [acc["name"] for acc in nouveaux_comptes]
            inactive = [n for n in custom_order if n not in active_names]
            while len(custom_order) > 50 and inactive:
                to_remove = inactive.pop(0)
                if to_remove in custom_order:
                    custom_order.remove(to_remove)

        self.config.data["custom_order"] = custom_order
        self.config.save()
        self.all_accounts = sorted(
            nouveaux_comptes, key=lambda x: custom_order.index(x["name"])
        )

        self.leader_hwnd = None
        leader_name = self.config.data.get("leader_name", "")
        for acc in self.all_accounts:
            if acc["name"] == leader_name:
                self.leader_hwnd = acc["hwnd"]

        return self.all_accounts

    def get_cycle_list(self):
        mode = self.config.data.get("current_mode", "ALL")
        valid_accounts = []
        for acc in self.all_accounts:
            if (
                win32gui.IsWindow(acc["hwnd"])
                and acc["active"]
                and (mode == "ALL" or acc["team"] == mode)
            ):
                valid_accounts.append(acc)
        return valid_accounts

    def _update_global_order_from_active(self, active_accs):
        order = self.config.data.get("custom_order", [])
        indices = []
        valid_names = []
        for acc in active_accs:
            if acc["name"] in order:
                indices.append(order.index(acc["name"]))
                valid_names.append(acc["name"])
        indices.sort()
        for i, name in zip(indices, valid_names):
            order[i] = name
        self.config.data["custom_order"] = order
        self.config.save()
        self.all_accounts.sort(key=lambda x: order.index(x["name"]))

    def set_account_position(self, name, new_index):
        active_accs = self.get_cycle_list()
        names = [a["name"] for a in active_accs]
        if name not in names:
            return
        idx = names.index(name)
        acc_to_move = active_accs.pop(idx)
        active_accs.insert(new_index, acc_to_move)
        self._update_global_order_from_active(active_accs)

    def move_account(self, name, direction):
        active_accs = self.get_cycle_list()
        names = [a["name"] for a in active_accs]
        if name not in names:
            return
        idx = names.index(name)
        new_idx = idx + direction
        if 0 <= new_idx < len(names):
            active_accs[idx], active_accs[new_idx] = (
                active_accs[new_idx],
                active_accs[idx],
            )
            self._update_global_order_from_active(active_accs)

    def toggle_account(self, name, is_active):
        for acc in self.all_accounts:
            if acc["name"] == name:
                acc["active"] = is_active
        self.config.data["accounts_state"][name] = is_active
        self.config.save()

    def execute_advanced_bind(self, source, identifier):

        active_list = self.get_cycle_list()
        if not active_list:
            return -1

        target_hwnd = None
        new_global_idx = -1

        if source == "cycle":
            row_index = int(identifier)
            if row_index < len(active_list):
                target_hwnd = active_list[row_index]["hwnd"]
                new_global_idx = row_index

        elif source == "bind":
            target_pseudo = str(identifier)
            for index, acc in enumerate(active_list):
                if acc["name"] == target_pseudo:
                    target_hwnd = acc["hwnd"]
                    new_global_idx = index
                    break

        if target_hwnd:
            self.focus_window(target_hwnd)
            return new_global_idx
        else:
            self._notify_error(f"⚠️ Personnage '{identifier}' non trouvé.")
            return -1

    def change_team(self, name, new_team):
        for acc in self.all_accounts:
            if acc["name"] == name:
                acc["team"] = new_team
        self.config.data["accounts_team"][name] = new_team
        self.config.save()

    def set_mode(self, mode):
        self.config.data["current_mode"] = mode
        self.config.save()

    def set_leader(self, name):
        self.leader_hwnd = None
        self.config.data["leader_name"] = name
        self.config.save()
        for acc in self.all_accounts:
            if acc["name"] == name:
                self.leader_hwnd = acc["hwnd"]

    def close_account_window(self, name):
        for acc in self.all_accounts:
            if acc["name"] == name:
                hwnd = acc["hwnd"]
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
                    ctypes.windll.kernel32.TerminateProcess(handle, 0)
                    ctypes.windll.kernel32.CloseHandle(handle)
                except Exception:
                    pass
                break

    def close_all_active_accounts(self):
        active_accs = self.get_cycle_list()
        for acc in active_accs:
            hwnd = acc["hwnd"]
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
                ctypes.windll.kernel32.TerminateProcess(handle, 0)
                ctypes.windll.kernel32.CloseHandle(handle)
            except:
                pass

    def focus_window(self, hwnd):
        if not hwnd:
            return
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            ctypes.windll.user32.AllowSetForegroundWindow(pid)
            ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
            win32gui.SetForegroundWindow(hwnd)

            timeout = 10
            while win32gui.GetForegroundWindow() != hwnd and timeout > 0:
                time.sleep(0.03)
                timeout -= 1
        except:
            pass

    def get_relative_ratio_pos(self, hwnd=None):
        x_screen, y_screen = win32gui.GetCursorPos()
        target_hwnd = hwnd if hwnd else self.leader_hwnd
        if target_hwnd:
            try:
                client_pt = win32gui.ScreenToClient(target_hwnd, (x_screen, y_screen))
                rect = win32gui.GetClientRect(target_hwnd)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                if w > 0 and h > 0:
                    return (client_pt[0] / float(w), client_pt[1] / float(h))
            except:
                pass
        return (0.0, 0.0)

    def get_screen_coords_from_saved(self, hwnd, saved_pos):
        if not saved_pos or len(saved_pos) != 2:
            return None
        x, y = saved_pos

        if isinstance(x, float) and isinstance(y, float) and x <= 1.0 and y <= 1.0:
            try:
                rect = win32gui.GetClientRect(hwnd)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                if w == 0 or h == 0:
                    return None
                client_x = int(x * w)
                client_y = int(y * h)
                return win32gui.ClientToScreen(hwnd, (client_x, client_y))
            except:
                return None
        else:
            try:
                return win32gui.ClientToScreen(hwnd, (int(x), int(y)))
            except:
                return None

    def _hardware_key(self, scan_code):
        i_down = INPUT()
        i_down.type = 1
        i_down.ki.wScan = scan_code
        i_down.ki.dwFlags = 0x0008

        i_up = INPUT()
        i_up.type = 1
        i_up.ki.wScan = scan_code
        i_up.ki.dwFlags = 0x0008 | 0x0002

        ctypes.windll.user32.SendInput(1, ctypes.byref(i_down), ctypes.sizeof(INPUT))
        time.sleep(0.01)
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_up), ctypes.sizeof(INPUT))

    def _hardware_click(self, x, y):
        nx, ny = screen_to_norm(x, y)
        i_move = INPUT()
        i_move.type = 0
        i_move.mi.dx = nx
        i_move.mi.dy = ny
        i_move.mi.dwFlags = 0x0001 | 0x8000 | 0x4000
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_move), ctypes.sizeof(INPUT))
        time.sleep(0.03)

        i_down = INPUT()
        i_down.type = 0
        i_down.mi.dx = nx
        i_down.mi.dy = ny
        i_down.mi.dwFlags = 0x0002 | 0x8000 | 0x4000
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_down), ctypes.sizeof(INPUT))
        time.sleep(0.04)

        i_up = INPUT()
        i_up.type = 0
        i_up.mi.dx = nx
        i_up.mi.dy = ny
        i_up.mi.dwFlags = 0x0004 | 0x8000 | 0x4000
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_up), ctypes.sizeof(INPUT))

    def _fast_hardware_click(self, x, y):
        nx, ny = screen_to_norm(x, y)
        i_move = INPUT()
        i_move.type = 0
        i_move.mi.dx = nx
        i_move.mi.dy = ny
        i_move.mi.dwFlags = 0x0001 | 0x8000 | 0x4000
        i_down = INPUT()
        i_down.type = 0
        i_down.mi.dx = nx
        i_down.mi.dy = ny
        i_down.mi.dwFlags = 0x0002 | 0x8000 | 0x4000
        i_up = INPUT()
        i_up.type = 0
        i_up.mi.dx = nx
        i_up.mi.dy = ny
        i_up.mi.dwFlags = 0x0004 | 0x8000 | 0x4000

        speed = self.config.data.get("click_speed", "Rapide")

        delay_press = (
            0.01 if speed == "Rapide" else (0.04 if speed == "Moyen" else 0.06)
        )
        delay_after = 0.0 if speed == "Rapide" else (0.09 if speed == "Moyen" else 0.18)

        ctypes.windll.user32.SendInput(1, ctypes.byref(i_move), ctypes.sizeof(INPUT))
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_down), ctypes.sizeof(INPUT))
        time.sleep(delay_press)
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_up), ctypes.sizeof(INPUT))

        if delay_after > 0:
            time.sleep(delay_after)

    def _fast_hardware_right_click(self, x, y):
        nx, ny = screen_to_norm(x, y)
        i_move = INPUT()
        i_move.type = 0
        i_move.mi.dx = nx
        i_move.mi.dy = ny
        i_move.mi.dwFlags = 0x0001 | 0x8000 | 0x4000
        i_down = INPUT()
        i_down.type = 0
        i_down.mi.dx = nx
        i_down.mi.dy = ny
        i_down.mi.dwFlags = 0x0008 | 0x8000 | 0x4000
        i_up = INPUT()
        i_up.type = 0
        i_up.mi.dx = nx
        i_up.mi.dy = ny
        i_up.mi.dwFlags = 0x0010 | 0x8000 | 0x4000

        speed = self.config.data.get("click_speed", "Rapide")

        delay_press = (
            0.01 if speed == "Rapide" else (0.04 if speed == "Moyen" else 0.06)
        )
        delay_after = 0.0 if speed == "Rapide" else (0.09 if speed == "Moyen" else 0.18)

        ctypes.windll.user32.SendInput(1, ctypes.byref(i_move), ctypes.sizeof(INPUT))
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_down), ctypes.sizeof(INPUT))
        time.sleep(delay_press)
        ctypes.windll.user32.SendInput(1, ctypes.byref(i_up), ctypes.sizeof(INPUT))

        if delay_after > 0:
            time.sleep(delay_after)

    def broadcast_key(self, key_name):
        time.sleep(0.1)
        active_accs = self.get_cycle_list()
        if not active_accs:
            return
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass
        current_hwnd = win32gui.GetForegroundWindow()

        scan_code = AZERTY_TO_SCAN.get(key_name.lower())

        try:
            for acc in active_accs:
                self.focus_window(acc["hwnd"])
                time.sleep(0.1)
                if scan_code:
                    self._hardware_key(scan_code)
                else:
                    keyboard.send(key_name)
                time.sleep(0.02)
            if self.config.data.get("return_to_leader", True) and self.leader_hwnd:
                self.focus_window(self.leader_hwnd)
            else:
                self.focus_window(current_hwnd)
        except:
            pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def execute_paste_enter(self):
        time.sleep(0.1)
        active_accs = self.get_cycle_list()
        if not active_accs:
            return
        original_fg_hwnd = win32gui.GetForegroundWindow()
        time.sleep(0.15)
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

        try:
            for acc in active_accs:
                self.focus_window(acc["hwnd"])
                time.sleep(0.1)
                keyboard.send("ctrl+v")
                time.sleep(0.02)
                keyboard.send("enter")
                time.sleep(0.02)
            if self.config.data.get("return_to_leader", True) and self.leader_hwnd:
                self.focus_window(self.leader_hwnd)
            else:
                self.focus_window(original_fg_hwnd)
        except:
            pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def execute_auto_zaap(self):
        active_accs = self.get_cycle_list()
        zaaps_pos = self.config.data["macro_positions"].get("zaaps", {})
        haven_key = self.config.data.get("game_haven_key", "h")

        if not active_accs:
            return
        for acc in active_accs:
            if acc["name"] not in zaaps_pos:
                self._notify_error(f"Votre Zaap ({acc['name']}) n'est pas calibré.")
                return

        original_fg_hwnd = win32gui.GetForegroundWindow()
        time.sleep(0.15)
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

        haven_scan = AZERTY_TO_SCAN.get(haven_key.lower())

        try:
            for acc in active_accs:
                self.focus_window(acc["hwnd"])
                time.sleep(0.15)
                if haven_scan:
                    self._hardware_key(haven_scan)
                else:
                    keyboard.send(haven_key)
                time.sleep(0.02)

            try:
                delai = float(self.config.data.get("zaap_delay", "1.8"))
            except ValueError:
                delai = 1.8

            time.sleep(delai)

            click_order = (
                active_accs[1:] + [active_accs[0]]
                if len(active_accs) > 1
                else active_accs
            )

            for index, acc in enumerate(click_order):
                coords = self.get_screen_coords_from_saved(
                    acc["hwnd"], zaaps_pos.get(acc["name"])
                )
                if not coords:
                    continue
                x_c, y_c = coords

                self.focus_window(acc["hwnd"])
                time.sleep(0.15)
                win32api.SetCursorPos((x_c, y_c))
                time.sleep(0.05)

                self._hardware_click(x_c, y_c)
                time.sleep(0.05)

            if self.config.data.get("return_to_leader", True) and self.leader_hwnd:
                self.focus_window(self.leader_hwnd)
            else:
                self.focus_window(original_fg_hwnd)
        except:
            pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def sync_click_all(self):
        active_accs = self.get_cycle_list()
        if not active_accs:
            return
        current_x, current_y = win32api.GetCursorPos()
        hwnd_under_mouse = win32gui.WindowFromPoint((current_x, current_y))
        root_hwnd = win32gui.GetAncestor(hwnd_under_mouse, win32con.GA_ROOT)

        is_dofus = any(acc["hwnd"] == root_hwnd for acc in self.all_accounts)
        reference_hwnd = (
            root_hwnd
            if is_dofus
            else (self.leader_hwnd if self.leader_hwnd else active_accs[0]["hwnd"])
        )

        try:
            rel_x, rel_y = win32gui.ScreenToClient(
                reference_hwnd, (current_x, current_y)
            )
            ref_rect = win32gui.GetClientRect(reference_hwnd)
            ref_w, ref_h = ref_rect[2] - ref_rect[0], ref_rect[3] - ref_rect[1]
            if ref_w == 0 or ref_h == 0:
                return
            ratio_x, ratio_y = rel_x / float(ref_w), rel_y / float(ref_h)
        except:
            return

        original_fg_hwnd = win32gui.GetForegroundWindow()
        time.sleep(0.15)
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

        try:
            for acc in active_accs:
                hwnd = acc["hwnd"]
                try:
                    target_rect = win32gui.GetClientRect(hwnd)
                    t_w, t_h = (
                        target_rect[2] - target_rect[0],
                        target_rect[3] - target_rect[1],
                    )
                    if t_w == 0 or t_h == 0:
                        continue
                    client_x, client_y = int(ratio_x * t_w), int(ratio_y * t_h)
                    target_x, target_y = win32gui.ClientToScreen(
                        hwnd, (client_x, client_y)
                    )

                    self.focus_window(hwnd)
                    win32api.SetCursorPos((target_x, target_y))
                    self._fast_hardware_click(target_x, target_y)
                except:
                    pass

            if self.config.data.get("return_to_leader", True) and self.leader_hwnd:
                self.focus_window(self.leader_hwnd)
            else:
                self.focus_window(original_fg_hwnd)
            try:
                win32api.SetCursorPos((current_x, current_y))
            except:
                pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def sync_right_click_all(self):
        active_accs = self.get_cycle_list()
        if not active_accs:
            return
        current_x, current_y = win32api.GetCursorPos()
        hwnd_under_mouse = win32gui.WindowFromPoint((current_x, current_y))
        root_hwnd = win32gui.GetAncestor(hwnd_under_mouse, win32con.GA_ROOT)

        is_dofus = any(acc["hwnd"] == root_hwnd for acc in self.all_accounts)
        reference_hwnd = (
            root_hwnd
            if is_dofus
            else (self.leader_hwnd if self.leader_hwnd else active_accs[0]["hwnd"])
        )

        try:
            rel_x, rel_y = win32gui.ScreenToClient(
                reference_hwnd, (current_x, current_y)
            )
            ref_rect = win32gui.GetClientRect(reference_hwnd)
            ref_w, ref_h = ref_rect[2] - ref_rect[0], ref_rect[3] - ref_rect[1]
            if ref_w == 0 or ref_h == 0:
                return
            ratio_x, ratio_y = rel_x / float(ref_w), rel_y / float(ref_h)
        except:
            return

        original_fg_hwnd = win32gui.GetForegroundWindow()
        time.sleep(0.15)
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

        try:
            for acc in active_accs:
                hwnd = acc["hwnd"]
                try:
                    target_rect = win32gui.GetClientRect(hwnd)
                    t_w, t_h = (
                        target_rect[2] - target_rect[0],
                        target_rect[3] - target_rect[1],
                    )
                    if t_w == 0 or t_h == 0:
                        continue
                    client_x, client_y = int(ratio_x * t_w), int(ratio_y * t_h)
                    target_x, target_y = win32gui.ClientToScreen(
                        hwnd, (client_x, client_y)
                    )

                    self.focus_window(hwnd)
                    win32api.SetCursorPos((target_x, target_y))
                    self._fast_hardware_right_click(target_x, target_y)
                except:
                    pass

            if self.config.data.get("return_to_leader", True) and self.leader_hwnd:
                self.focus_window(self.leader_hwnd)
            else:
                self.focus_window(original_fg_hwnd)
            try:
                win32api.SetCursorPos((current_x, current_y))
            except:
                pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def execute_group_invite(self):
        leader = self.config.data.get("leader_name")
        chat_pos = self.config.data["macro_positions"].get("chat_position")

        if not self.leader_hwnd or not leader:
            self._notify_error("Décidez d'un chef pour inviter !")
            return
        if not chat_pos:
            self._notify_error("Votre Chat n'est pas calibré.")
            return

        coords = self.get_screen_coords_from_saved(self.leader_hwnd, chat_pos)
        if not coords:
            return
        x_c, y_c = coords

        active_accs = self.get_cycle_list()
        time.sleep(0.1)
        self.focus_window(self.leader_hwnd)
        time.sleep(0.2)

        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass
        try:
            win32api.SetCursorPos((x_c, y_c))
            time.sleep(0.05)
            self._hardware_click(x_c, y_c)
            time.sleep(0.15)

            keyboard.send("ctrl+a")
            time.sleep(0.05)
            keyboard.send("backspace")
            time.sleep(0.1)

            for acc in active_accs:
                if acc["name"] == leader:
                    continue
                keyboard.write(f"/invite {acc['name']}")
                time.sleep(0.1)
                keyboard.send("enter")
                time.sleep(0.1)
        except:
            pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def execute_treasure_hunt(self):
        chat_pos = self.config.data["macro_positions"].get("chat_position")
        if not chat_pos:
            self._notify_error("Votre Chat n'est pas calibré.")
            return

        current_hwnd = win32gui.GetForegroundWindow()
        known_hwnds = [acc["hwnd"] for acc in self.all_accounts]
        target_hwnd = current_hwnd
        if target_hwnd not in known_hwnds:
            if self.leader_hwnd:
                target_hwnd = self.leader_hwnd
                self.focus_window(target_hwnd)
                time.sleep(0.2)
            else:
                return

        coords = self.get_screen_coords_from_saved(target_hwnd, chat_pos)
        if not coords:
            return
        x_c, y_c = coords

        time.sleep(0.1)
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass
        try:
            win32api.SetCursorPos((x_c, y_c))
            time.sleep(0.05)
            self._hardware_click(x_c, y_c)
            time.sleep(0.15)

            keyboard.send("ctrl+v")
            time.sleep(0.05)
            keyboard.send("enter")
            time.sleep(0.20)
            keyboard.send("enter")
        except:
            pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def execute_swap_xp_drop(self):
        pos = self.config.data["macro_positions"].get("xp_drop_button")
        if not pos:
            self._notify_error("Votre XP/Drop n'est pas calibré.")
            return

        active_accs = self.get_cycle_list()
        if not active_accs:
            return

        time.sleep(0.1)
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass
        try:
            for acc in active_accs:
                hwnd = acc["hwnd"]
                coords = self.get_screen_coords_from_saved(hwnd, pos)
                if not coords:
                    continue
                x_c, y_c = coords

                self.focus_window(hwnd)
                time.sleep(0.2)
                win32api.SetCursorPos((x_c, y_c))
                time.sleep(0.03)
                self._hardware_click(x_c, y_c)

            if self.config.data.get("return_to_leader", True) and self.leader_hwnd:
                self.focus_window(self.leader_hwnd)
        except:
            pass
        finally:
            try:
                ctypes.windll.user32.BlockInput(False)
            except:
                pass

    def sort_taskbar(self):
        active_accs = self.get_cycle_list()
        if not active_accs:
            return
        try:
            for acc in active_accs:
                win32gui.ShowWindow(acc["hwnd"], win32con.SW_HIDE)
            time.sleep(0.2)
            for acc in active_accs:
                win32gui.ShowWindow(acc["hwnd"], win32con.SW_SHOW)
                time.sleep(0.05)
            if self.leader_hwnd:
                self.focus_window(self.leader_hwnd)
        except Exception:
            pass
