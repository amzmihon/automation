"""
Antigravity Auto-Permission Tool (Per-Button Control)
======================================================
Configure each button individually - Confirm, Accept, Deny, Reject can each
have different actions (approve, deny, skip).

Config (config.json) example:
  "confirm": {"action": "approve"}   ← Auto-click Confirm buttons
  "accept": {"action": "skip"}       ← Ignore Accept buttons (manual)
  "deny": {"action": "skip"}         ← Ignore Deny buttons
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict

# Check dependencies
try:
    import pyautogui
    import pygetwindow as gw
except ImportError:
    print("❌ Missing dependencies! Run:")
    print("   pip install pyautogui pygetwindow")
    sys.exit(1)

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False
    print("⚠️  'keyboard' module not found. Install: pip install keyboard")

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("⚠️  OCR modules not found. Install: pip install pytesseract Pillow")

# Paths
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
LOG_FILE = SCRIPT_DIR / "permission_log.txt"
ASSETS_DIR = SCRIPT_DIR / "assets"

# Ensure assets dir exists
ASSETS_DIR.mkdir(exist_ok=True)

# ============================================================================
# DEFAULT CONFIG
# ============================================================================

DEFAULT_CONFIG = {
    "buttons": {
        "confirm": {"image": "confirm.png", "action": "approve", "description": "Confirm button"},
        "deny": {"image": "deny.png", "action": "skip", "description": "Deny button"},
        "accept": {"image": "accept.png", "action": "skip", "description": "Accept button"},
        "reject": {"image": "reject.png", "action": "skip", "description": "Reject button"},
        "deny_confirm_combo": {"image": "deny_confirm.png", "action": "approve", "description": "Deny/Confirm combo"},
        "accept_reject_combo": {"image": "accept_reject.png", "action": "skip", "description": "Accept/Reject combo"},
    },
    "settings": {
        "check_interval": 0.5,
        "action_delay": 0.3,
        "cooldown": 2.0,
        "log_actions": True,
        "sound_alert_on_skip": True,
        "confidence": 0.8
    },
    "chat_input_mode": {
        "enabled": True,
        "window_title": "Antigravity",
        "input_region": None,  # Will be detected automatically or set manually
        "refresh_interval": 2.0,  # How often to re-read chat (seconds)
        "fallback_to_config": True  # Use config.json when chat is empty
    },
    "hotkeys": {
        "approve": "ctrl+shift+y",
        "deny": "ctrl+shift+n",
        "quit": "ctrl+shift+q"
    },
    "window_titles": ["Antigravity", "Open Agent Manager"]
}

# ============================================================================
# CONFIG MANAGEMENT
# ============================================================================

def load_config() -> Dict:
    """Load config from JSON file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Merge with defaults
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
                return config
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
    
    save_config(DEFAULT_CONFIG)
    print(f"📝 Created default config: {CONFIG_FILE}")
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict):
    """Save config to JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ============================================================================
# LOGGING
# ============================================================================

def log(msg: str, config: Dict = None):
    """Print and log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")
    
    if config and config.get("settings", {}).get("log_actions", True):
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                full_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{full_ts}] {msg}\n")
        except:
            pass

def play_alert():
    """Play alert sound."""
    try:
        import winsound
        winsound.Beep(800, 150)
    except:
        print("\a")

# ============================================================================
# CHAT INPUT READER
# ============================================================================

class ChatInputReader:
    """
    Reads button names from Antigravity chat input field.
    User types comma-separated button names like: "confirm, alt + enter, accept"
    Only those buttons will be auto-processed.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.chat_config = config.get("chat_input_mode", {})
        self.enabled = self.chat_config.get("enabled", True)
        self.window_title = self.chat_config.get("window_title", "Antigravity")
        self.input_region = self.chat_config.get("input_region", None)
        self.last_read_time = 0
        self.refresh_interval = self.chat_config.get("refresh_interval", 2.0)
        self.cached_buttons = []
        self.fallback_to_config = self.chat_config.get("fallback_to_config", True)
        
        # Button name aliases (what user might type -> config button names)
        self.aliases = {
            "alt + enter": ["accept", "accept_reject_combo"],
            "alt+enter": ["accept", "accept_reject_combo"],
            "enter": ["confirm", "deny_confirm_combo"],
            "escape": ["deny", "reject"],
            "esc": ["deny", "reject"],
        }
    
    def find_antigravity_window(self) -> Optional[Tuple[int, int, int, int]]:
        """Find Antigravity window and return its region (x, y, width, height)."""
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
                if win.visible and not win.isMinimized:
                    return (win.left, win.top, win.width, win.height)
        except Exception as e:
            log(f"⚠️ Error finding window: {e}")
        return None
    
    def get_chat_input_region(self, window_region: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Estimate the chat input area region.
        The input box is typically at the bottom of the Antigravity window.
        """
        if self.input_region:
            return tuple(self.input_region)
        
        x, y, w, h = window_region
        # Chat input is usually at the bottom, spanning most of the width
        # Estimate: bottom 50 pixels, leaving some margins
        input_x = x + 50
        input_y = y + h - 70  # 70 pixels from bottom
        input_w = w - 200     # Leave space for buttons on right
        input_h = 40          # Input field height
        
        return (input_x, input_y, input_w, input_h)
    
    def read_chat_text(self) -> str:
        """Read text from the chat input field using OCR."""
        if not HAS_OCR:
            return ""
        
        try:
            window = self.find_antigravity_window()
            if not window:
                return ""
            
            region = self.get_chat_input_region(window)
            
            # Capture screenshot of the input region
            screenshot = pyautogui.screenshot(region=region)
            
            # Use OCR to read text
            text = pytesseract.image_to_string(screenshot, config='--psm 7')
            return text.strip()
            
        except Exception as e:
            log(f"⚠️ OCR error: {e}")
            return ""
    
    def parse_button_names(self, text: str) -> list:
        """
        Parse comma-separated button names from text.
        Returns list of button names that should be auto-processed.
        """
        if not text:
            return []
        
        # Split by comma, clean up each name
        raw_names = [name.strip().lower() for name in text.split(",")]
        
        button_names = []
        for name in raw_names:
            if not name:
                continue
            
            # Check if it's an alias
            if name in self.aliases:
                button_names.extend(self.aliases[name])
            else:
                # Check if it matches a config button name
                for btn_name in self.config.get("buttons", {}).keys():
                    if name in btn_name.lower() or btn_name.lower() in name:
                        button_names.append(btn_name)
                        break
                else:
                    # No match found, add as-is (might match partially later)
                    button_names.append(name)
        
        return list(set(button_names))  # Remove duplicates
    
    def get_allowed_buttons(self) -> list:
        """
        Get list of button names that should be auto-processed.
        Reads from chat if enabled, otherwise returns empty list.
        """
        if not self.enabled:
            return []  # Disabled - use config.json actions
        
        # Check if we need to refresh
        current_time = time.time()
        if current_time - self.last_read_time > self.refresh_interval:
            chat_text = self.read_chat_text()
            self.cached_buttons = self.parse_button_names(chat_text)
            self.last_read_time = current_time
            
            if self.cached_buttons:
                log(f"📝 Chat input detected: {self.cached_buttons}")
        
        return self.cached_buttons
    
    def should_process_button(self, button_name: str, button_action: str) -> bool:
        """
        Determine if a button should be processed.
        
        If chat_input_mode is enabled:
          - Only process buttons listed in chat input
          - If chat is empty and fallback_to_config is True, use config.json action
        
        If chat_input_mode is disabled:
          - Use config.json action normally
        """
        if not self.enabled:
            return True  # Use config.json action
        
        allowed = self.get_allowed_buttons()
        
        if not allowed:
            # Chat is empty
            if self.fallback_to_config:
                return True  # Use config.json action
            else:
                return False  # Skip everything
        
        # Check if this button is in the allowed list
        button_lower = button_name.lower()
        for allowed_btn in allowed:
            if allowed_btn in button_lower or button_lower in allowed_btn:
                return True
        
        return False  # Not in allowed list - skip

# ============================================================================
# BUTTON FINDER
# ============================================================================

class ButtonFinder:
    """Finds buttons on screen and performs configured actions."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.confidence = config.get("settings", {}).get("confidence", 0.8)
        self.last_action_time = 0
        self.cooldown = config.get("settings", {}).get("cooldown", 2.0)
        self.action_delay = config.get("settings", {}).get("action_delay", 0.3)
    
    def can_act(self) -> bool:
        """Check if cooldown has passed."""
        return (time.time() - self.last_action_time) > self.cooldown
    
    def find_button(self, image_name: str) -> Optional[Tuple[int, int]]:
        """Find a button by its image file."""
        image_path = ASSETS_DIR / image_name
        if not image_path.exists():
            return None
        
        try:
            location = pyautogui.locateCenterOnScreen(
                str(image_path),
                confidence=self.confidence
            )
            if location:
                return (location.x, location.y)
        except Exception:
            pass
        return None
    
    def click_at(self, x: int, y: int, button_name: str) -> bool:
        """Click at coordinates."""
        if not self.can_act():
            return False
        
        time.sleep(self.action_delay)
        pyautogui.click(x, y)
        self.last_action_time = time.time()
        log(f"🖱️ Clicked [{button_name}] at ({x}, {y})", self.config)
        return True
    
    def send_keyboard(self, shortcut: str, description: str) -> bool:
        """Send keyboard shortcut."""
        if not self.can_act():
            return False
        
        if HAS_KEYBOARD:
            time.sleep(self.action_delay)
            keyboard.press_and_release(shortcut)
            self.last_action_time = time.time()
            log(f"⌨️ Sent [{shortcut}] for {description}", self.config)
            return True
        return False
    
    def scan_and_act(self, chat_reader: Optional['ChatInputReader'] = None) -> Optional[str]:
        """
        Scan for all configured buttons and perform their configured action.
        
        If chat_reader is provided and enabled:
          - Only process buttons mentioned in the chat input
          - If chat is empty, fallback to config.json behavior
        
        Returns the button name that was acted upon, or None.
        """
        buttons = self.config.get("buttons", {})
        
        for btn_name, btn_config in buttons.items():
            image = btn_config.get("image", "")
            action = btn_config.get("action", "skip")
            
            # Check if this button should be processed based on chat input
            if chat_reader:
                if not chat_reader.should_process_button(btn_name, action):
                    continue  # Skip this button - not in chat input
            
            # Try to find this button on screen
            coords = self.find_button(image)
            
            if coords:
                x, y = coords
                
                # If chat_reader has explicit button list, override action to "approve"
                if chat_reader and chat_reader.enabled and chat_reader.get_allowed_buttons():
                    # User explicitly typed this button in chat - approve it
                    if "confirm" in btn_name.lower() or "accept" in btn_name.lower() or "deny_confirm" in btn_name.lower():
                        if self.click_at(x, y, btn_name):
                            return f"APPROVED: {btn_name} (from chat)"
                    elif "deny" in btn_name.lower() or "reject" in btn_name.lower():
                        if self.click_at(x, y, btn_name):
                            return f"DENIED: {btn_name} (from chat)"
                    else:
                        if self.click_at(x, y, btn_name):
                            return f"CLICKED: {btn_name} (from chat)"
                else:
                    # Use config.json action
                    if action == "approve":
                        # Click the button (for approve buttons like Confirm, Accept)
                        if "confirm" in btn_name.lower() or "accept" in btn_name.lower():
                            if self.click_at(x, y, btn_name):
                                return f"APPROVED: {btn_name}"
                        # Or use keyboard shortcut
                        elif self.send_keyboard("alt+enter", btn_name):
                            return f"APPROVED: {btn_name}"
                            
                    elif action == "deny":
                        # Click deny buttons
                        if "deny" in btn_name.lower() or "reject" in btn_name.lower():
                            if self.click_at(x, y, btn_name):
                                return f"DENIED: {btn_name}"
                        elif self.send_keyboard("escape", btn_name):
                            return f"DENIED: {btn_name}"
                            
                    elif action == "skip":
                        # Do nothing, but notify
                        if self.config.get("settings", {}).get("sound_alert_on_skip", True):
                            play_alert()
                        log(f"⏸️ SKIPPED: {btn_name} (manual required)", self.config)
                        return f"SKIPPED: {btn_name}"
        
        return None

# ============================================================================
# PERMISSION MONITOR
# ============================================================================

class PermissionMonitor:
    """Monitors screen for permission dialogs."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.button_finder = ButtonFinder(config)
        self.chat_reader = ChatInputReader(config)
        self.running = False
        self.stats = {"approved": 0, "denied": 0, "skipped": 0, "clicked": 0}
        self.check_interval = config.get("settings", {}).get("check_interval", 0.5)
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        self.running = True
        
        chat_mode_enabled = self.config.get("chat_input_mode", {}).get("enabled", True)
        
        print("\n" + "=" * 60)
        if chat_mode_enabled:
            print("  🔍 AUTO-MONITOR MODE (Chat-Controlled)")
        else:
            print("  🔍 AUTO-MONITOR MODE (Per-Button Control)")
        print("=" * 60)
        
        if chat_mode_enabled:
            print("\n  📝 CHAT INPUT MODE ACTIVE!")
            print("  ─" * 30)
            print("  Type button names in Antigravity chat to auto-approve:")
            print("    Examples:")
            print("      • 'confirm'           → Only auto-approve Confirm buttons")
            print("      • 'confirm, accept'   → Auto-approve both")
            print("      • 'alt + enter'       → Auto-approve Accept/Alt+Enter")
            print("      • Empty chat          → Use config.json defaults")
            print("  ─" * 30)
        else:
            print("\n  Watching for buttons...")
            print("  Each button acts according to config.json")
        
        print("\n  Press Ctrl+C to stop.\n")
        
        # Show current button settings
        print("  Config.json Button Defaults:")
        print("  " + "-" * 50)
        for btn_name, btn_config in self.config.get("buttons", {}).items():
            action = btn_config.get("action", "skip")
            icons = {"approve": "✅", "deny": "❌", "skip": "⏸️"}
            icon = icons.get(action, "❓")
            print(f"    {btn_name:<25} {icon} {action.upper()}")
        print("  " + "-" * 50 + "\n")
        
        if chat_mode_enabled:
            log("Started CHAT-CONTROLLED monitoring", self.config)
        else:
            log("Started per-button monitoring", self.config)
        
        last_chat_buttons = []
        
        try:
            while self.running:
                # Check for chat input changes (display status)
                if chat_mode_enabled:
                    current_buttons = self.chat_reader.get_allowed_buttons()
                    if current_buttons != last_chat_buttons:
                        if current_buttons:
                            print(f"\n  💬 Active buttons from chat: {', '.join(current_buttons)}")
                        else:
                            print(f"\n  💬 Chat empty - using config.json defaults")
                        last_chat_buttons = current_buttons.copy()
                
                # Scan and act
                result = self.button_finder.scan_and_act(
                    chat_reader=self.chat_reader if chat_mode_enabled else None
                )
                
                if result:
                    if "APPROVED" in result:
                        self.stats["approved"] += 1
                    elif "DENIED" in result:
                        self.stats["denied"] += 1
                    elif "SKIPPED" in result:
                        self.stats["skipped"] += 1
                    elif "CLICKED" in result:
                        self.stats["clicked"] += 1
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopped monitoring.")
        
        self.show_stats()
    
    def show_stats(self):
        """Show session statistics."""
        print("\n" + "=" * 40)
        print("  📊 SESSION STATS")
        print("=" * 40)
        print(f"  ✅ Approved: {self.stats['approved']}")
        print(f"  ❌ Denied:   {self.stats['denied']}")
        print(f"  ⏸️ Skipped:  {self.stats['skipped']}")
        if self.stats['clicked'] > 0:
            print(f"  🖱️ Clicked:  {self.stats['clicked']}")
        print("=" * 40 + "\n")

# ============================================================================
# INTERACTIVE CONFIGURATION
# ============================================================================

def configure_buttons(config: Dict) -> Dict:
    """Interactive button configuration."""
    print("\n" + "=" * 60)
    print("  ⚙️ CONFIGURE BUTTONS")
    print("=" * 60)
    print("\n  For each button, enter:")
    print("    a = Approve (auto-click)")
    print("    d = Deny (auto-click deny)")
    print("    s = Skip (do nothing)")
    print("    Enter = Keep current")
    print("-" * 60)
    
    buttons = config.get("buttons", {})
    
    for btn_name, btn_config in buttons.items():
        current = btn_config.get("action", "skip")
        icons = {"approve": "✅", "deny": "❌", "skip": "⏸️"}
        icon = icons.get(current, "❓")
        desc = btn_config.get("description", "")
        
        choice = input(f"  {btn_name:<20} [{icon} {current}] ({desc}): ").strip().lower()
        
        if choice in ['a', '1', 'approve']:
            buttons[btn_name]["action"] = "approve"
        elif choice in ['d', '2', 'deny']:
            buttons[btn_name]["action"] = "deny"
        elif choice in ['s', '3', 'skip']:
            buttons[btn_name]["action"] = "skip"
    
    config["buttons"] = buttons
    save_config(config)
    print("\n  ✅ Configuration saved!")
    return config

def display_settings(config: Dict):
    """Display current settings."""
    print("\n" + "=" * 60)
    print("  📋 CURRENT BUTTON SETTINGS")
    print("=" * 60)
    
    icons = {"approve": "✅ APPROVE", "deny": "❌ DENY", "skip": "⏸️ SKIP"}
    
    for btn_name, btn_config in config.get("buttons", {}).items():
        action = btn_config.get("action", "skip")
        image = btn_config.get("image", "")
        icon = icons.get(action, "❓")
        print(f"  {btn_name:<20} → {icon:<15} ({image})")
    
    print("\n" + "-" * 60)
    print(f"  📂 Config: {CONFIG_FILE}")
    print("=" * 60)

def hotkey_mode(config: Dict):
    """Manual hotkey mode."""
    if not HAS_KEYBOARD:
        print("\n❌ 'keyboard' module required. Run: pip install keyboard")
        return
    
    stats = {"approved": 0, "denied": 0}
    hotkeys = config.get("hotkeys", DEFAULT_CONFIG["hotkeys"])
    
    print("\n" + "=" * 60)
    print("  🎹 HOTKEY MODE")
    print("=" * 60)
    print(f"\n  {hotkeys['approve']:<20} → Approve (Alt+Enter)")
    print(f"  {hotkeys['deny']:<20} → Deny (Escape)")
    print(f"  {hotkeys['quit']:<20} → Quit")
    print("\n" + "=" * 60 + "\n")
    
    def do_approve():
        keyboard.press_and_release('alt+enter')
        stats["approved"] += 1
        print(f"  ✅ Approved! ({stats['approved']})")
    
    def do_deny():
        keyboard.press_and_release('escape')
        stats["denied"] += 1
        print(f"  ❌ Denied! ({stats['denied']})")
    
    keyboard.add_hotkey(hotkeys['approve'], do_approve)
    keyboard.add_hotkey(hotkeys['deny'], do_deny)
    
    print("  Waiting... Press", hotkeys['quit'], "to quit.\n")
    keyboard.wait(hotkeys['quit'])
    
    print(f"\n  Stats: {stats['approved']} approved, {stats['denied']} denied\n")

def add_button(config: Dict) -> Dict:
    """Add a new button to config."""
    print("\n" + "=" * 60)
    print("  ➕ ADD NEW BUTTON")
    print("=" * 60)
    
    name = input("\n  Button name (e.g., 'continue'): ").strip().lower()
    if not name:
        print("  ❌ Cancelled")
        return config
    
    image = input("  Image filename (e.g., 'continue.png'): ").strip()
    if not image:
        image = f"{name}.png"
    
    print("\n  Action: a=approve, d=deny, s=skip")
    action_input = input("  Select action: ").strip().lower()
    
    if action_input in ['a', 'approve']:
        action = "approve"
    elif action_input in ['d', 'deny']:
        action = "deny"
    else:
        action = "skip"
    
    desc = input("  Description (optional): ").strip()
    
    config["buttons"][name] = {
        "image": image,
        "action": action,
        "description": desc or f"{name} button"
    }
    
    save_config(config)
    print(f"\n  ✅ Added button: {name} → {action}")
    
    # Check if image exists
    if not (ASSETS_DIR / image).exists():
        print(f"  ⚠️ Image not found: {ASSETS_DIR / image}")
        print("     Use Option 5 to capture the button image.")
    
    return config

def capture_button():
    """Capture a button screenshot."""
    print("\n" + "=" * 60)
    print("  📸 CAPTURE BUTTON")
    print("=" * 60)
    print("\n  1. Make sure the button is visible on screen")
    print("  2. Position your cursor over the button")
    print("  3. Enter the filename to save")
    
    filename = input("\n  Save as (e.g., 'mybutton.png'): ").strip()
    if not filename:
        print("  ❌ Cancelled")
        return
    
    if not filename.endswith('.png'):
        filename += '.png'
    
    print("\n  Move cursor to the button center...")
    print("  Capturing in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    x, y = pyautogui.position()
    
    # Capture region around cursor
    width = int(input("  Button width (default 100): ").strip() or "100")
    height = int(input("  Button height (default 30): ").strip() or "30")
    
    region = (x - width//2, y - height//2, width, height)
    screenshot = pyautogui.screenshot(region=region)
    
    filepath = ASSETS_DIR / filename
    screenshot.save(str(filepath))
    print(f"\n  ✅ Saved: {filepath}")

# ============================================================================
# MAIN MENU
# ============================================================================

def toggle_chat_mode(config: Dict) -> Dict:
    """Toggle and configure chat input mode."""
    print("\n" + "=" * 60)
    print("  💬 CHAT INPUT MODE SETTINGS")
    print("=" * 60)
    
    chat_config = config.get("chat_input_mode", {})
    enabled = chat_config.get("enabled", True)
    
    print(f"\n  Current Status: {'🟢 ENABLED' if enabled else '🔴 DISABLED'}")
    print("\n  When ENABLED:")
    print("    • Type button names in Antigravity chat")
    print("    • Only those buttons will be auto-processed")
    print("    • Example: 'confirm, accept' in chat")
    print("\n  When DISABLED:")
    print("    • Uses config.json button actions")
    print("    • Traditional per-button control")
    
    print("\n  Options:")
    print("    1 = Enable chat mode")
    print("    2 = Disable chat mode")
    print("    3 = Configure settings")
    print("    Enter = Keep current")
    
    choice = input("\n  Select: ").strip()
    
    if choice == "1":
        chat_config["enabled"] = True
        print("\n  ✅ Chat mode ENABLED")
    elif choice == "2":
        chat_config["enabled"] = False
        print("\n  ✅ Chat mode DISABLED")
    elif choice == "3":
        print("\n  Configure Chat Mode Settings:")
        print("  " + "-" * 40)
        
        # Window title
        current_title = chat_config.get("window_title", "Antigravity")
        new_title = input(f"    Window title [{current_title}]: ").strip()
        if new_title:
            chat_config["window_title"] = new_title
        
        # Refresh interval
        current_refresh = chat_config.get("refresh_interval", 2.0)
        new_refresh = input(f"    Refresh interval seconds [{current_refresh}]: ").strip()
        if new_refresh:
            try:
                chat_config["refresh_interval"] = float(new_refresh)
            except:
                pass
        
        # Fallback to config
        current_fallback = chat_config.get("fallback_to_config", True)
        fallback_str = "y" if current_fallback else "n"
        new_fallback = input(f"    Use config.json when chat empty? (y/n) [{fallback_str}]: ").strip().lower()
        if new_fallback in ["y", "yes", "true"]:
            chat_config["fallback_to_config"] = True
        elif new_fallback in ["n", "no", "false"]:
            chat_config["fallback_to_config"] = False
        
        print("\n  ✅ Settings updated")
    
    config["chat_input_mode"] = chat_config
    save_config(config)
    return config

def main():
    """Main menu."""
    config = load_config()
    
    while True:
        chat_enabled = config.get("chat_input_mode", {}).get("enabled", True)
        chat_status = "💬 ON" if chat_enabled else "💬 OFF"
        
        print("\n" + "=" * 60)
        print("  🤖 ANTIGRAVITY AUTO-PERMISSION TOOL")
        print(f"      (Chat Mode: {chat_status})")
        print("=" * 60)
        print("\n  1 │ 🔍 Start Auto-Monitor")
        print("  2 │ 🎹 Start Hotkey Mode")
        print("  3 │ 📋 View Button Settings")
        print("  4 │ ⚙️  Configure Buttons")
        print("  5 │ ➕ Add New Button")
        print("  6 │ 📸 Capture Button Image")
        print("  7 │ 💬 Toggle Chat Mode")
        print("  8 │ 📂 Open config.json")
        print("  9 │ 🚪 Exit")
        print("\n" + "-" * 60)
        
        choice = input("  Select (1-9): ").strip()
        
        if choice == "1":
            monitor = PermissionMonitor(config)
            monitor.start_monitoring()
        elif choice == "2":
            hotkey_mode(config)
        elif choice == "3":
            display_settings(config)
            input("\n  Press Enter to continue...")
        elif choice == "4":
            config = configure_buttons(config)
        elif choice == "5":
            config = add_button(config)
        elif choice == "6":
            capture_button()
        elif choice == "7":
            config = toggle_chat_mode(config)
        elif choice == "8":
            try:
                os.startfile(CONFIG_FILE)
            except:
                print(f"\n  📂 Open: {CONFIG_FILE}")
        elif choice == "9":
            print("\n  👋 Goodbye!\n")
            break
        else:
            print("  ❌ Invalid option")

if __name__ == "__main__":
    main()
