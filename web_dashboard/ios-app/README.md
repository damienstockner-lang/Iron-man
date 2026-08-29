# Friday Assistant iOS App

Native iOS wrapper for the Friday Assistant web dashboard. Built with Capacitor.

## Features

All Friday Assistant features available offline:
- 📊 Dashboard & Statistics
- ✅ Task Management
- 📝 Notes with Tags
- ⏰ Reminders
- 💰 Expense Tracking
- 👟 Step Counter
- 😊 Mood Tracker
- 📺 TV Control with Google Voice Mode
- 👤 Contacts
- 📤 Data Export
- 🌐 Open Instagram, Snapchat, YouTube, Google, and more
- 🗣️ Text-to-Speech
- 🌍 Translation
- 📷 Vision / Image Analysis
- ❓ Ask Questions
- 🎨 Design Anything
- 🦾 Iron Man Helmet Mode
- 🌤️ Weather
- 📞 Call & Message People
- 📅 Schedule & Appointments

## Prerequisites

- macOS with Xcode 14.0+
- Node.js 16+
- npm or yarn
- CocoaPods (for Capacitor iOS dependencies)

## Quick Setup

### 1. Install Dependencies

```bash
cd web_dashboard/ios-app
npm install
```

### 2. Add iOS Platform

```bash
npx cap add ios
```

### 3. Sync Web Assets

```bash
npm run sync
```

### 4. Open in Xcode

```bash
npm run open
```

### 5. Build & Run

In Xcode:
1. Select your target device (iPhone or simulator)
2. Click the Run button (▶️)
3. The app will launch on your device

## Building for App Store

### Local Build

```bash
# Update team ID in ExportOptions.plist and Info.plist first
npm run build:ipa
```

The IPA will be in `ios/App/build/`.

### Codemagic CI/CD

The included `codemagic.yaml` is configured for automated builds:

1. Push this repo to GitHub/GitLab
2. Connect Codemagic to your repo
3. Set the `APPLE_TEAM_ID` environment variable
4. Codemagic will automatically build and distribute the app

## Project Structure

```
ios-app/
├── www/                      # Web app files (dashboard)
│   ├── index.html
│   ├── manifest.json
│   └── sw.js
├── ios/
│   └── App/                  # Xcode project
│       ├── App.xcodeproj/
│       ├── App/
│       │   ├── AppDelegate.swift
│       │   ├── Info.plist
│       │   ├── Assets.xcassets/
│       │   └── Base.lproj/
│       └── ExportOptions.plist
├── node_modules/             # Capacitor dependencies
├── package.json
├── capacitor.config.json
└── codemagic.yaml
```

## Configuration

### Bundle ID

Update in two places:
- `capacitor.config.json`: `"appId": "com.friday.assistant"`
- `ios/App/App/Info.plist`: `PRODUCT_BUNDLE_IDENTIFIER`

### App Name

Update in:
- `capacitor.config.json`: `"appName": "Friday Assistant"`
- `ios/App/App/Info.plist`: `CFBundleDisplayName`

### Permissions

The app requests these permissions (defined in `Info.plist`):
- Camera (for vision/photo features)
- Microphone (for voice commands)
- Location (for weather)
- Contacts (for address book)
- Calendar (for schedule)
- Reminders (for tasks)

## Offline Mode

The app works completely offline. All data is stored locally on the device using SQLite. The web dashboard at `localhost:8080` can be used for full desktop functionality.

## Troubleshooting

### "npx: command not found"
Install Node.js from https://nodejs.org/

### "xcodebuild: command not found"
Install Xcode from the App Store.

### Build fails with "Signing" error
1. Open the project in Xcode
2. Select the project in the navigator
3. Go to "Signing & Capabilities"
4. Select your development team

### CocoaPods not installed
```bash
sudo gem install cocoapods
```

## Manual Project Creation (if npx cap add ios fails)

If Capacitor can't create the iOS project automatically, the project structure is already included in this repository. Just open `ios/App/App.xcworkspace` in Xcode.

## Support

For issues with the iOS app, check the main Friday Assistant documentation or open an issue on GitHub.
