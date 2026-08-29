#!/bin/bash
set -e

echo "🚀 Friday Assistant iOS App Setup"
echo "===================================="
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required. Install from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js found: $(node --version)"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required."
    exit 1
fi

echo "✓ npm found: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔄 Syncing Capacitor..."
npm run sync

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Open Xcode:    npm run open"
echo "2. Build for device/simulator in Xcode"
echo "3. Or use Codemagic CI/CD with the included codemagic.yaml"
echo ""
echo "For App Store submission, update the bundle ID in:"
echo "  ios/App/App/Info.plist"
echo "  capacitor.config.json"
