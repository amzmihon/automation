# Antigravity Auto-Permission Tool

🤖 Automatically approve or deny Antigravity permission prompts based on your configured rules.

## Features

- ✅ **Configurable Permissions** - Choose which permission types to auto-approve
- 🎛️ **Interactive Configuration** - Easy menu to set up your preferences  
- 📝 **Action Logging** - Keep track of all permission decisions
- 🔔 **Sound Alerts** - Get notified when manual approval is needed
- 💾 **Persistent Config** - Your settings are saved automatically

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) For OCR text detection, install Tesseract:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH

## Usage

1. Run the script:
   ```bash
   python antigravity_auto_permit.py
   ```

2. Choose from the menu:
   - **Option 1**: Start monitoring with current settings
   - **Option 2**: Configure which permissions to auto-approve
   - **Option 3**: View current settings
   - **Option 4**: Exit

3. Press `Ctrl+C` to stop monitoring

## Permission Categories

| Category | Description |
|----------|-------------|
| `file_read` | Reading files, fetching config |
| `file_write` | Writing or modifying files |
| `file_delete` | Deleting files |
| `javascript_execute` | Executing JavaScript code |
| `python_execute` | Executing Python code |
| `shell_command` | Running terminal commands |
| `browser_navigate` | Navigating to URLs |
| `browser_click` | Clicking page elements |
| `browser_type` | Typing in input fields |
| `fetch_request` | API/fetch requests |
| `button_click` | Clicking buttons |
| `form_submit` | Submitting forms |
| `database_operation` | Database operations |
| `install_package` | Installing packages |

## Configuration File

Your settings are saved to `config.json` in the same directory. You can also edit this file directly:

```json
{
  "permissions": {
    "file_read": true,
    "file_write": false,
    "javascript_execute": true
  }
}
```

## Button Detection (Advanced)

For better button detection, you can add screenshots of the Confirm and Deny buttons:

1. Create an `assets` folder
2. Take screenshots of the buttons
3. Save as:
   - `assets/confirm_button.png`
   - `assets/deny_button.png`

## Logs

All actions are logged to `permission_log.txt` in the same directory.

## ⚠️ Safety Warning

Be careful when enabling auto-approve for:
- `file_write` - Could overwrite important files
- `file_delete` - Could delete files
- `shell_command` - Could execute dangerous commands
- `install_package` - Could install unwanted packages

Always review what categories you enable!

## Troubleshooting

**Button not detected:**
- Try adding button screenshots to the assets folder
- Make sure the Antigravity window is visible and not minimized

**OCR not working:**
- Install Tesseract OCR
- Add Tesseract to your system PATH

**Script not finding window:**
- Check if the window title matches the patterns in config
