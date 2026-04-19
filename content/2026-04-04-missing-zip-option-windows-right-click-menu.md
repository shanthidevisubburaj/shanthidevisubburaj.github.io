Title: Missing ZIP Option in Windows Right-Click Menu — Here's How to Fix It
Date: 2026-04-11
Category: Windows
Tags: Windows, tips, context-menu, troubleshooting, productivity
Slug: missing-zip-option-windows-right-click-menu

The classic "Send to → Compressed (zipped) folder" option sometimes disappears from the Windows right-click context menu. Here's what causes it and how to get it back in under two minutes.

## What Happened

Windows ships with a built-in ZIP shell extension handled by `zipfldr.dll`. When third-party tools like Git, VLC, or OneDrive add their own context menu entries, they can displace or corrupt the ZIP handler registration — leaving you with a bloated menu but no ZIP option.

## Fix 1 — Check the Send to Submenu

Before anything else, right-click your folder or file and hover over **Send to →**. The "Compressed (zipped) folder" option is sometimes hiding in the submenu even when it's not visible at the top level.

## Fix 2 — Re-register the ZIP Shell Extension

Open Command Prompt as Administrator and run:
```cmd
regsvr32 zipfldr.dll
```

This re-registers the native ZIP handler with Windows Shell. Restart Explorer or reboot after running it.

## Fix 3 — Restart Windows Explorer

Sometimes a stale shell session is all that's causing the issue. Run this in CMD:
```cmd
taskkill /f /im explorer.exe
start explorer.exe
```

## Fix 4 — Verify the Registry Key

Press `Win + R`, type `regedit`, and navigate to:
```
HKEY_CLASSES_ROOT\CompressedFolder
```

If this key is missing or corrupted, the ZIP option will not appear anywhere in the context menu. You may need to restore it from another machine or via a `.reg` export.

## Root Cause

Heavy context menu contributors — Git Bash, Git GUI, VLC, SkyDrive Pro — are visible in the screenshot. Any one of them can push a bad shell extension that breaks ZIP registration as a side effect. Fix 2 resolves this in most cases.