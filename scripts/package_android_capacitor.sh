#!/usr/bin/env bash
set -e

echo "🤖 ========================================================"
echo "   CyberMentor — Android Google Play (Capacitor) Builder"
echo "============================================================"

# Ensure project root
mkdir -p android

echo "📦 Step 1: Installing Capacitor Android platform..."
npm install --save-dev @capacitor/android

echo "🔄 Step 2: Adding Android platform & syncing web assets..."
if [ ! -d "android/app" ]; then
    rm -rf android
    npx cap add android
fi

npx cap sync android

echo ""
echo "🎉 Android Studio project generated successfully!"
echo "📁 Location: android/"
echo ""
echo "📝 Next Steps for Google Play Console (Closed Testing - Registered Users Only):"
echo "   1. Open Android Studio: npx cap open android"
echo "   2. In Android Studio: Build -> Generate Signed Bundle / APK -> Android App Bundle (.aab)"
echo "   3. In https://play.google.com/console -> Closed testing:"
echo "      - Create an email list containing your registered candidates"
echo "      - Upload the generated .aab bundle"
echo "      - Candidates will receive an invite to install via Google Play directly on Android!"
