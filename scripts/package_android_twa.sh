#!/usr/bin/env bash
set -e

echo "📱 ========================================================"
echo "   CyberMentor — Android Google Play (TWA) Package Builder"
echo "============================================================"

# Ensure output directory exists
mkdir -p build/android

echo "📦 Step 1: Checking Bubblewrap CLI..."
if ! command -v bubblewrap &> /dev/null; then
    echo "⬇️  Installing Bubblewrap CLI via npm..."
    npm install -g @bubblewrap/cli
fi

echo "🔧 Step 2: Generating Android Trusted Web Activity project..."
# Initialize bubblewrap project using our live PWA manifest
if [ ! -f "build/android/twa-manifest.json" ]; then
    bubblewrap init \
      --manifest="https://client.breakingintocybersecurity.org/manifest.json" \
      --directory="build/android" \
      --metaData.name="CyberMentor" \
      --metaData.packageId="org.breakingintocybersecurity.cybermentor" \
      --metaData.host="client.breakingintocybersecurity.org"
fi

echo "🔨 Step 3: Building Android App Bundle (.aab)..."
cd build/android
bubblewrap build

echo ""
echo "🎉 Android App Bundle (.aab) created successfully!"
echo "📁 File located at: build/android/app-release-bundle.aab"
echo ""
echo "📝 Next Steps for Google Play Console (Closed Testing - Registered Users Only):"
echo "   1. Open https://play.google.com/console"
echo "   2. Select CyberMentor -> Testing -> Closed testing"
echo "   3. Create an email list containing your registered candidates"
echo "   4. Upload 'app-release-bundle.aab' and publish to the closed track"
echo "   5. Share your private Google Play invite link with registered users!"
