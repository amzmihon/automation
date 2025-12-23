# 🤖 Antigravity Auto-Permission Tool v3.0

## File-Controlled Button Automation

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   � Edit allowed_buttons.txt  ──►  🔍 Tool Reads It  ──►  🖱️ Auto-Click │
│                                                                 │
│   Example: "confirm, accept"   ──►   File Detected   ──►  Buttons Clicked │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Overview

> **Problem**: Antigravity shows permission dialogs. You want SOME buttons auto-clicked, others skipped.
>
> **Solution**: Edit `allowed_buttons.txt` → Only those buttons auto-click!

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           HOW IT WORKS                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐    │
│  │ allowed_buttons │     │   This Tool     │     │   Permission    │    │
│  │     .txt        │────▶│   Reads File    │────▶│   Auto-Clicked  │    │
│  │                 │     │   Every 2 sec   │     │                 │    │
│  │ confirm         │     │   Detects:      │     │   ✅ Confirm    │    │
│  │                 │     │   - confirm     │     │   ⏸️ Accept     │    │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (3 Steps)

```
Step 1                    Step 2                    Step 3
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│                  │     │                  │     │                  │
│  Run the .exe    │────▶│  Press 1 to      │────▶│  Edit the file   │
│                  │     │  Start Monitor   │     │  allowed_buttons │
│                  │     │                  │     │  .txt            │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                         │
                                                         ▼
                                                  ┌──────────────────┐
                                                  │  ✅ Auto-clicks  │
                                                  │  only those      │
                                                  │  buttons!        │
                                                  └──────────────────┘
```

---

## � allowed_buttons.txt

This is the **key file** you edit to control which buttons get auto-clicked.

### File Location
```
Portable_Package_v3/allowed_buttons.txt
```

### How to Edit
1. Open the file in any text editor (Notepad, VS Code, etc.)
2. Write button names (one per line or comma-separated)
3. Save the file
4. The tool picks up changes within 2 seconds!

### Examples

| What You Write | What Happens |
|----------------|--------------|
| `confirm` | ✅ Only Confirm buttons auto-click |
| `confirm, accept` | ✅ Both Confirm AND Accept auto-click |
| `alt + enter` | ✅ Accept buttons auto-click |
| `deny, reject` | ✅ Deny & Reject buttons auto-click |
| *(leave empty)* | ⚙️ Uses config.json default settings |

### Supported Button Names

```
┌──────────────────────────────────────────────────────┐
│  What You Type        │  Buttons That Get Clicked   │
├───────────────────────┼─────────────────────────────┤
│  confirm              │  Confirm, Deny+Confirm combo│
│  accept               │  Accept, Accept+Reject combo│
│  alt + enter          │  Accept buttons             │
│  deny                 │  Deny button                │
│  reject               │  Reject button              │
│  escape / esc         │  Deny, Reject buttons       │
└──────────────────────────────────────────────────────┘
```

---

## 📋 Menu Options

```
╔════════════════════════════════════════════════════════════╗
║  🤖 ANTIGRAVITY AUTO-PERMISSION TOOL                       ║
║      (Chat Mode: 💬 ON)                                    ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  1 │ 🔍 Start Auto-Monitor    ← Main feature!             ║
║  2 │ 🎹 Start Hotkey Mode     ← Manual keyboard control   ║
║  3 │ 📋 View Button Settings  ← See current config        ║
║  4 │ ⚙️  Configure Buttons     ← Change button actions     ║
║  5 │ ➕ Add New Button        ← Add custom buttons        ║
║  6 │ 📸 Capture Button Image  ← Screenshot new buttons    ║
║  7 │ 💬 Toggle File Mode      ← Enable/Disable file ctrl  ║
║  8 │ 📂 Open config.json      ← Edit config file          ║
║  9 │ 🚪 Exit                                               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🔍 Feature 1: Auto-Monitor (Option 1)

The **main feature** - watches your screen and auto-clicks buttons.

```
┌─────────────────────────────────────────────────────────┐
│                    AUTO-MONITOR FLOW                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Reads allowed_buttons.txt every 2 seconds           │
│  2. Scans screen for button images                      │
│  3. Clicks buttons that match file content              │
│                                                         │
│  ┌─────────────────┐                                    │
│  │ Screen Scan     │──▶ Found "Confirm" button          │
│  └─────────────────┘           │                        │
│                                ▼                        │
│  ┌─────────────────┐   ┌──────────────┐   ┌───────────┐ │
│  │ File says:      │──▶│ "confirm"    │──▶│ ✅ CLICK! │ │
│  │ "confirm"       │   │ matches!     │   └───────────┘ │
│  └─────────────────┘   └──────────────┘                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Press Ctrl+C to stop monitoring**

---

## � Package Contents

```
Portable_Package_v3/
│
├── 📦 AntigravityAutoPermit.exe   ← Run this!
│
├── 📄 allowed_buttons.txt          ← EDIT THIS to control buttons!
│
├── 📄 config.json                  ← Settings file
│   ├── buttons: Define button images & default actions
│   ├── settings: Scan interval, cooldown, confidence
│   └── chat_input_mode: File reading settings
│
├── 📖 USER_MANUAL.md               ← You are here!
│
└── 📁 assets/                      ← Button images
    ├── confirm.png
    ├── accept.png
    ├── deny.png
    ├── reject.png
    └── ...
```

---

## ⚙️ config.json Reference

```json
{
  "buttons": {
    "confirm": {
      "image": "confirm.png",     // Image file in assets/
      "action": "approve",        // Default when file is empty
      "description": "Blue Confirm button"
    }
  },
  
  "settings": {
    "check_interval": 0.5,        // Scan every 0.5 seconds
    "action_delay": 0.3,          // Wait before clicking
    "cooldown": 2.0,              // Wait between clicks
    "confidence": 0.8             // Image match accuracy (0-1)
  },
  
  "chat_input_mode": {
    "enabled": true,              // Enable file reading
    "refresh_interval": 2.0,      // Re-read file every 2 sec
    "fallback_to_config": true    // Empty file = use defaults
  }
}
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| File changes not detected | Wait 2 seconds, check file saved |
| Buttons not detected | Recapture images (Option 6) |
| Wrong button clicked | Lower `confidence` in config |
| Too many clicks | Increase `cooldown` value |

---

*Antigravity Auto-Permission Tool v3.0 - File-Controlled Edition* 🚀
