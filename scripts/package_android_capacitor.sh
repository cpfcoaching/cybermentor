#!/usr/bin/env bash
set -e

echo "🤖 ========================================================"
echo "   CyberMentor — Android Package Builder (APK & AAB)"
echo "============================================================"

# Set Java and Android SDK environment
if [ -d "/Library/Java/JavaVirtualMachines/temurin-25.jdk/Contents/Home" ]; then
  export JAVA_HOME="/Library/Java/JavaVirtualMachines/temurin-25.jdk/Contents/Home"
else
  export JAVA_HOME="/usr/local/opt/openjdk@21"
fi
export ANDROID_HOME=/usr/local/share/android-commandlinetools
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"

echo "🔧 Step 1: Syncing web assets into native Android project..."
npx cap sync android

echo "🔨 Step 2: Compiling Android APK with Gradle..."
cd android
./gradlew assembleDebug

echo ""
echo "🎉 Android APK generated successfully!"
echo "📁 Location: android/app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "☁️ Firebase Test Lab / Cloud Testing Instructions:"
echo "   1. Open Firebase Console -> Test Lab: https://console.firebase.google.com/project/cybermentor-506813/testlab"
echo "   2. Click 'Run a test' -> Select 'Robo test' or 'Instrumentation test'"
echo "   3. Upload 'android/app/build/outputs/apk/debug/app-debug.apk'"
echo "   4. Google Cloud will execute tests across real physical Pixel & Samsung devices and record video/logs!"
echo ""
echo "🚀 Google Play Closed Testing (.aab) Instructions:"
echo "   1. Open Android Studio: npx cap open android"
echo "   2. Select Build -> Generate Signed Bundle / APK -> Android App Bundle (.aab)"
echo "   3. Upload to Google Play Console -> Closed Testing for registered candidates only."
