# 📖 Antigravity Auto-Permission Tool v3.0
## User Manual - Chat-Controlled Button Actions

> **NEW!** Type button names directly in Antigravity chat to control which buttons are auto-processed!

---

## 🚀 Quick Start

1. **Double-click** `AntigravityAutoPermit.exe`
2. Type **1** and press Enter to start auto-monitoring
3. **Type button names in Antigravity chat** (e.g., `confirm, accept`)
4. Only those buttons will be auto-processed!

---

## 🆕 What's New in v3.0

- **💬 Chat Input Mode**: Type button names in Antigravity chat for real-time control
- **Dynamic Control**: Change which buttons are active without restarting
- **Fallback to Config**: When chat is empty, uses config.json defaults
- **Per-Button Control**: Each button type has its own action
- **Easy Toggle**: Turn chat mode on/off from menu

---

## 💬 Chat Input Mode (NEW!)

### How It Works

1. Start Auto-Monitor (Option 1)
2. Type button names in Antigravity's chat input box
3. Only those buttons will be auto-clicked

### Examples

| What You Type in Chat | What Gets Auto-Processed |
|-----------------------|--------------------------|
| `confirm` | Only Confirm buttons |
| `confirm, accept` | Both Confirm and Accept buttons |
| `alt + enter` | Accept/Alt+Enter buttons |
| `deny, reject` | Deny and Reject buttons |
| *(empty)* | Falls back to config.json settings |

### Aliases

You can type these shortcuts:
- `alt + enter` or `alt+enter` → Accept buttons
- `enter` → Confirm buttons
- `escape` or `esc` → Deny/Reject buttons

---

## 📋 config.json Structure

```json
{
  "buttons": {
    "confirm": {
      "image": "confirm.png",
      "action": "approve"     ← Default when chat is empty
    },
    "accept": {
      "image": "accept.png",
      "action": "skip"        ← Default when chat is empty
    }
  },
  "chat_input_mode": {
    "enabled": true,           ← Turn chat mode on/off
    "window_title": "Antigravity",
    "refresh_interval": 2.0,   ← How often to read chat (seconds)
    "fallback_to_config": true ← Use config.json when chat is empty
  }
}
```

---

## 🎯 Action Types (for config.json defaults)

| Action | What Happens |
|--------|--------------|
| `"approve"` | Auto-click this button when found |
| `"deny"` | Auto-click this button when found |
| `"skip"` | Ignore - do nothing (manual decision) |

---

## 📋 Menu Options

| Option | Description |
|--------|-------------|
| **1** | 🔍 Start Auto-Monitor - watches screen, reads chat |
| **2** | 🎹 Hotkey Mode - manual control with keyboard |
| **3** | 📋 View Settings - see current button configurations |
| **4** | ⚙️ Configure - change button actions interactively |
| **5** | ➕ Add Button - add a new button type |
| **6** | 📸 Capture - take screenshot of a button |
| **7** | � Toggle Chat Mode - enable/disable chat control |
| **8** | �📂 Open config.json |
| **9** | 🚪 Exit |

---

## 💡 Usage Scenarios

### Scenario 1: Only approve Confirm buttons, skip Accept
**In Antigravity chat, type:** `confirm`

### Scenario 2: Approve both Confirm and Accept
**In Antigravity chat, type:** `confirm, accept`

### Scenario 3: Temporarily skip everything
**Clear the chat input** (leave empty with `fallback_to_config: false`)

### Scenario 4: Use traditional config.json mode
**Option 7** → Disable chat mode

---

## 💬 Chat Mode Settings (Option 7)

| Setting | Description |
|---------|-------------|
| `enabled` | Turn chat reading on/off |
| `window_title` | Window name to find Antigravity |
| `refresh_interval` | How often to re-read chat (seconds) |
| `fallback_to_config` | Use config.json when chat is empty |

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
├── config.json                  ← Button & chat mode settings
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

1. **Tesseract OCR Required** - For chat input mode, install Tesseract OCR
2. **Button images must match** - If buttons look different, recapture them
3. **Keep exe and config together** - They must be in the same folder
4. **Run as Administrator** - May be needed for keyboard shortcuts
5. **Don't minimize Antigravity** - Buttons must be visible to be detected

---

## 🔧 Troubleshooting

### Chat mode not reading text?
- Make sure Tesseract OCR is installed
- Check that Antigravity window title matches config
- Try adjusting `refresh_interval` in config.json

### Buttons not being detected?
- Recapture button images using Option 6
- Adjust `confidence` value (lower = more lenient)
- Make sure buttons are visible on screen

---

*Antigravity Auto-Permission Tool v3.0 - Chat-Controlled Edition*
