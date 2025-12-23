# Antigravity Auto-Permission Tool

Portable desktop application that automatically approves/denies Antigravity permission dialogs.

## How to Use

1. **Double-click** `AntigravityAutoPermit.exe` to run
2. Select **Option 1** for auto-monitor mode
3. The app will watch for permission dialogs and click buttons automatically

## Configuration

Edit `config.json` to change settings:

```json
"file_read": "approve",    // Auto-click Accept/Confirm
"file_write": "skip",      // Do nothing (manual)
"file_delete": "deny",     // Auto-click Deny/Reject
```

## Button Images

The `assets` folder contains button images for detection.
You can add more button screenshots there if needed.

## Hotkeys (in Hotkey Mode)

- `Ctrl+Shift+Y` = Approve
- `Ctrl+Shift+N` = Deny
- `Ctrl+Shift+Q` = Quit
