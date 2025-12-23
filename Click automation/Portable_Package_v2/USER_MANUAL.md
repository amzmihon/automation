# 📖 Antigravity Auto-Permission Tool v2.0
## User Manual - Per-Button Control

> Configure each button independently - Confirm, Accept, Deny, Reject can each have different actions!

---

## 🚀 Quick Start

1. **Double-click** `AntigravityAutoPermit.exe`
2. Type **1** and press Enter to start auto-monitoring
3. Each button acts according to your `config.json` settings

---

## 🆕 What's New in v2.0

- **Per-Button Control**: Each button type has its own action
- **Independent Settings**: Confirm can auto-approve while Accept stays manual
- **Add New Buttons**: Easily add more button types
- **Capture Tool**: Take screenshots of new buttons

---

## 📋 config.json Structure

```json
{
  "buttons": {
    "confirm": {
      "image": "confirm.png",
      "action": "approve"     ← Auto-click this button
    },
    "accept": {
      "image": "accept.png",
      "action": "skip"        ← Ignore this button (manual)
    },
    "deny": {
      "image": "deny.png",
      "action": "skip"        ← Ignore
    },
    "reject": {
      "image": "reject.png",
      "action": "skip"        ← Ignore
    }
  }
}
```

---

## 🎯 Action Types

| Action | What Happens |
|--------|--------------|
| `"approve"` | Auto-click this button when found |
| `"deny"` | Auto-click this button when found |
| `"skip"` | Ignore - do nothing (manual decision) |

---

## 📋 Menu Options

| Option | Description |
|--------|-------------|
| **1** | 🔍 Start Auto-Monitor - watches screen, clicks buttons |
| **2** | 🎹 Hotkey Mode - manual control with keyboard |
| **3** | 📋 View Settings - see current button configurations |
| **4** | ⚙️ Configure - change button actions interactively |
| **5** | ➕ Add Button - add a new button type |
| **6** | 📸 Capture - take screenshot of a button |
| **7** | 📂 Open config.json |
| **8** | 🚪 Exit |

---

## 💡 Example Configurations

### Auto-approve all confirmations, skip everything else:
```json
"confirm": {"action": "approve"},
"deny_confirm_combo": {"action": "approve"},
"accept": {"action": "skip"},
"reject": {"action": "skip"},
"deny": {"action": "skip"}
```

### Auto-approve Accept buttons, but not Confirm:
```json
"accept": {"action": "approve"},
"accept_reject_combo": {"action": "approve"},
"confirm": {"action": "skip"},
"deny": {"action": "skip"}
```

### Auto-deny all deny/reject buttons:
```json
"deny": {"action": "deny"},
"reject": {"action": "deny"}
```

---

## 🎹 Hotkey Mode (Option 2)

| Hotkey | Action |
|--------|--------|
| `Ctrl+Shift+Y` | Send Accept (Alt+Enter) |
| `Ctrl+Shift+N` | Send Deny (Escape) |
| `Ctrl+Shift+Q` | Quit |

---

## ➕ Adding New Buttons (Option 5)

1. Select Option 5
2. Enter button name (e.g., `continue`)
3. Enter image filename (e.g., `continue.png`)
4. Choose action: a=approve, d=deny, s=skip
5. Use Option 6 to capture the button image

---

## 📸 Capturing Button Images (Option 6)

1. Make the button visible on screen
2. Select Option 6
3. Enter filename (e.g., `mybutton.png`)
4. Position cursor over the button
5. Wait 3 seconds for capture
6. Enter button dimensions

---

## ⚙️ Settings in config.json

```json
"settings": {
  "check_interval": 0.5,      ← How often to scan (seconds)
  "action_delay": 0.3,        ← Delay before clicking
  "cooldown": 2.0,            ← Time between clicks
  "confidence": 0.8,          ← Image matching accuracy (0-1)
  "sound_alert_on_skip": true ← Beep when skipping
}
```

---

## 📁 Files in This Package

```
Portable_Package_v2/
├── AntigravityAutoPermit.exe   ← Main application
├── config.json                  ← Button settings (edit this!)
├── assets/                      ← Button images
│   ├── confirm.png
│   ├── accept.png
│   ├── deny.png
│   ├── reject.png
│   └── ...
└── USER_MANUAL.md               ← This file
```

---

## ⚠️ Important Notes

1. **Button images must match** - If buttons look different on your screen, recapture them
2. **Keep exe and config together** - They must be in the same folder
3. **Run as Administrator** - May be needed for keyboard shortcuts
4. **Don't minimize Antigravity** - Buttons must be visible to be detected

---

*Antigravity Auto-Permission Tool v2.0*
