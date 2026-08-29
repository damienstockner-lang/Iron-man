#!/bin/bash
# Friday Assistant iOS Setup Script for macOS
set -e

echo "🚀 Friday Assistant iOS Setup"
echo "===================================="
echo ""

# Check for macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script must be run on macOS"
    exit 1
fi

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is required. Install from the App Store."
    exit 1
fi

echo "✓ Xcode found: $(xcodebuild -version | head -n1)"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install node
fi

echo "✓ Node.js found: $(node --version)"

# Check for CocoaPods
if ! command -v pod &> /dev/null; then
    echo "📦 Installing CocoaPods..."
    sudo gem install cocoapods
fi

echo "✓ CocoaPods found: $(pod --version)"

# Install npm dependencies
echo ""
echo "📦 Installing npm dependencies..."
npm install

# Add iOS platform if not exists
if [ ! -d "ios/App" ]; then
    echo ""
    echo "🔄 Adding iOS platform..."
    npx cap add ios
else
    echo "✓ iOS platform already exists"
fi

# Sync assets
echo ""
echo "🔄 Syncing Capacitor..."
npm run sync

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Open Xcode:    npm run open"
echo "2. Select your team in Xcode (Signing & Capabilities)"
echo "3. Build and run on your device"
echo ""
echo "To build IPA for distribution:"
echo "  npm run build:ipa"
