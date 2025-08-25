# Dropbox Integration Setup Guide

## Overview

The thesis data export system now automatically saves files to both your local `thesis_data/` folder and your Dropbox account. This ensures your research data is safely backed up in the cloud.

## Current Status

✅ **Dropbox Integration Implemented**
- Export button now saves to both local and Dropbox
- Automatic backup of all thesis data files
- Error handling for connection issues
- Status indicator in sidebar

⚠️ **Access Token Needs Update**
- Current token lacks required permissions
- Need to regenerate with proper scopes

## Setting Up Dropbox Access

### Step 1: Create Dropbox App (If Not Done)

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose "Scoped access"
4. Choose "Full Dropbox" access
5. Name your app (e.g., "Thesis Data Exporter")

### Step 2: Configure App Permissions

**IMPORTANT**: Your app needs these permissions:
- `files.content.write` - To upload files
- `files.content.read` - To verify uploads
- `files.metadata.read` - To check file status

To add these permissions:
1. Go to your app in the [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click on the "Permissions" tab
3. Check the boxes for:
   - ✅ `files.content.write`
   - ✅ `files.content.read` 
   - ✅ `files.metadata.read`
4. Click "Submit" to save changes

### Step 3: Generate New Access Token

1. In your app console, go to the "Settings" tab
2. Scroll down to "OAuth 2" section
3. Click "Generate access token"
4. Copy the new token (it will start with `sl.`)

### Step 4: Update secrets.toml

Replace the current `DROPBOX_ACCESS_TOKEN` in `.streamlit/secrets.toml`:

```toml
DROPBOX_ACCESS_TOKEN="your_new_token_here"
```

## File Organization in Dropbox

Your files will be organized in Dropbox as follows:

```
/thesis_exports/
├── sessions/           # Individual session data
│   ├── session_data_123_20240816_143022.json
│   └── session_data_456_20240816_150315.json
├── interactions/       # Interaction logs
│   ├── interactions_123_20240816_143022.json
│   └── interactions_456_20240816_150315.json
├── csv/               # CSV exports
│   ├── interactions_123_20240816_143022.csv
│   └── design_moves_123_20240816_143022.csv
└── comprehensive/     # Full thesis data exports
    ├── interactions_session123.csv
    ├── design_moves_session123.csv
    ├── session_summary_session123.json
    └── full_log_session123.json
```

## How It Works

### Export Process

1. **User clicks Export button** in sidebar
2. **Local files created** in `./thesis_data/` folder
3. **Files uploaded to Dropbox** automatically
4. **Status displayed** showing success/failure for each location

### Export Types

1. **Comprehensive Export** (from InteractionLogger)
   - `interactions_[session_id].csv` - All user interactions
   - `design_moves_[session_id].csv` - Design decision tracking
   - `session_summary_[session_id].json` - Session metadata
   - `full_log_[session_id].json` - Complete interaction log

2. **Session Data Export** (JSON download)
   - Complete session state
   - Messages, analysis results, metadata
   - Available as download + Dropbox backup

### Error Handling

The system gracefully handles various error scenarios:

- **No internet connection**: Files saved locally only
- **Invalid token**: Clear error message with setup instructions
- **Insufficient permissions**: Specific guidance on required scopes
- **Dropbox API errors**: Fallback to local-only export

## Testing the Integration

Run the test script to verify everything works:

```bash
python test_dropbox_integration.py
```

This will test:
- ✅ Dropbox connection
- ✅ File upload capability
- ✅ Session data export
- ✅ CSV export functionality

## Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check that your access token is correct
   - Verify token has required permissions
   - Regenerate token if needed

2. **"App not permitted to access endpoint"**
   - Your app lacks `files.content.write` permission
   - Follow Step 2 above to add required permissions
   - Generate new token after adding permissions

3. **"Dropbox client not initialized"**
   - Check that `DROPBOX_ACCESS_TOKEN` is in secrets.toml
   - Verify the token format (should start with `sl.`)
   - Restart the application after updating token

4. **Files not appearing in Dropbox**
   - Check the `/thesis_exports/` folder in your Dropbox
   - Verify upload success in the app's status messages
   - Check Dropbox app permissions

### Status Indicators

The sidebar shows Dropbox status:
- 🟢 **Connected**: Ready to upload files
- 🟡 **Not connected**: Check token/permissions
- 🔴 **Package not installed**: Run `pip install dropbox`

## Benefits

✅ **Automatic Backup**: All thesis data automatically backed up
✅ **Dual Storage**: Local files + cloud backup for safety
✅ **Organized Structure**: Clean folder organization in Dropbox
✅ **Error Recovery**: Graceful fallback to local-only if needed
✅ **Real-time Status**: Clear feedback on upload success/failure

## Security Notes

- Access tokens are stored securely in `secrets.toml`
- Tokens are not logged or displayed in the UI
- Only your thesis data files are uploaded
- Files are uploaded to your personal Dropbox account

## Next Steps

1. **Update your Dropbox app permissions** (Step 2 above)
2. **Generate new access token** (Step 3 above)
3. **Update secrets.toml** (Step 4 above)
4. **Test the integration** using the test script
5. **Start using the export feature** - it will now save to both locations!

Once set up correctly, every time you click the export button, your thesis data will be safely stored in both your local folder and your Dropbox account.
