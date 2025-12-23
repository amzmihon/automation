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
    
    def scan_and_act(self) -> Optional[str]:
        """
        Scan for all configured buttons and perform their configured action.
        Returns the button name that was acted upon, or None.
        """
        buttons = self.config.get("buttons", {})
        
        for btn_name, btn_config in buttons.items():
            image = btn_config.get("image", "")
            action = btn_config.get("action", "skip")
            
            # Try to find this button on screen
            coords = self.find_button(image)
            
            if coords:
                x, y = coords
                
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
        self.running = False
        self.stats = {"approved": 0, "denied": 0, "skipped": 0}
        self.check_interval = config.get("settings", {}).get("check_interval", 0.5)
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        self.running = True
        
        print("\n" + "=" * 60)
        print("  🔍 AUTO-MONITOR MODE (Per-Button Control)")
        print("=" * 60)
        print("\n  Watching for buttons...")
        print("  Each button acts according to config.json")
        print("\n  Press Ctrl+C to stop.\n")
        
        # Show current button settings
        print("  Current Button Settings:")
        print("  " + "-" * 50)
        for btn_name, btn_config in self.config.get("buttons", {}).items():
            action = btn_config.get("action", "skip")
            icons = {"approve": "✅", "deny": "❌", "skip": "⏸️"}
            icon = icons.get(action, "❓")
            print(f"    {btn_name:<25} {icon} {action.upper()}")
        print("  " + "-" * 50 + "\n")
        
        log("Started per-button monitoring", self.config)
        
        try:
            while self.running:
                result = self.button_finder.scan_and_act()
                
                if result:
                    if "APPROVED" in result:
                        self.stats["approved"] += 1
                    elif "DENIED" in result:
                        self.stats["denied"] += 1
                    elif "SKIPPED" in result:
                        self.stats["skipped"] += 1
                
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

def main():
    """Main menu."""
    config = load_config()
    
    while True:
        print("\n" + "=" * 60)
        print("  🤖 ANTIGRAVITY AUTO-PERMISSION TOOL")
        print("      (Per-Button Control)")
        print("=" * 60)
        print("\n  1 │ 🔍 Start Auto-Monitor")
        print("  2 │ 🎹 Start Hotkey Mode")
        print("  3 │ 📋 View Button Settings")
        print("  4 │ ⚙️  Configure Buttons")
        print("  5 │ ➕ Add New Button")
        print("  6 │ 📸 Capture Button Image")
        print("  7 │ 📂 Open config.json")
        print("  8 │ 🚪 Exit")
        print("\n" + "-" * 60)
        
        choice = input("  Select (1-8): ").strip()
        
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
            try:
                os.startfile(CONFIG_FILE)
            except:
                print(f"\n  📂 Open: {CONFIG_FILE}")
        elif choice == "8":
            print("\n  👋 Goodbye!\n")
            break
        else:
            print("  ❌ Invalid option")

if __name__ == "__main__":
    main()
