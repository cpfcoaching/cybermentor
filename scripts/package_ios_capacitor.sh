#!/usr/bin/env bash
set -e

echo "🍎 ========================================================"
echo "   CyberMentor — iOS Apple App Store (Capacitor) Builder"
echo "============================================================"

# Ensure project root
mkdir -p ios

echo "📦 Step 1: Installing Capacitor Core & iOS..."
npm install --save-dev @capacitor/core @capacitor/cli @capacitor/ios

echo "🔧 Step 2: Initializing Capacitor Configuration..."
if [ ! -f "capacitor.config.json" ]; then
cat <<EOF > capacitor.config.json
{
  "appId": "org.breakingintocybersecurity.cybermentor",
  "appName": "CyberMentor",
  "webDir": "web",
  "bundledWebRuntime": false,
  "server": {
    "url": "https://client.breakingintocybersecurity.org",
    "cleartext": false
  }
}
EOF
fi

echo "🔄 Step 3: Adding iOS platform & syncing web assets..."
npx cap add ios || true
npx cap sync ios

echo ""
echo "🎉 iOS Xcode workspace generated successfully!"
echo "📁 Location: ios/App/App.xcworkspace"
echo ""
echo "📝 Next Steps for Apple TestFlight (Registered Users Only):"
echo "   1. Open Xcode: npx cap open ios"
echo "   2. In Xcode: Select Product -> Archive"
echo "   3. Click 'Distribute App' -> 'App Store Connect'"
echo "   4. In https://appstoreconnect.apple.com -> TestFlight:"
echo "      - Add registered candidates to an External Testing Group"
echo "      - Candidates will receive an invite to install via TestFlight directly on iPhone!"
