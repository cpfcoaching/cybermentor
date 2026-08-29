# 📱 CyberMentor: App Store Packaging & Gating to Registered Users

This guide explains how to package CyberMentor for the **Apple App Store** and **Google Play Store**, and how to restrict access so the app is accessible **only to registered / invited users**.

---

## 📊 Current App Deployment Status

CyberMentor is currently deployed as an **installable Progressive Web App (PWA)** hosted at:

- 🌐 **Marketing Landing Page**: [`https://client.breakingintocybersecurity.org/home.html`](https://client.breakingintocybersecurity.org/home.html)
- 🚀 **AI Coach Studio**: [`https://client.breakingintocybersecurity.org`](https://client.breakingintocybersecurity.org)
- 📲 **Instant Home Screen Install**: Users on iOS (Safari $\rightarrow$ *Add to Home Screen*) and Android (Chrome $\rightarrow$ *Install App*) can install CyberMentor directly without going through app store review queues.

---

## 🔒 Part 1: How to Restrict the App to Registered Users Only

To ensure that only registered users can access coaching features:

```text
                      ┌───────────────────────────────────────────────┐
                      │                 User Arrives                  │
                      └───────────────────────┬───────────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │ Is User Authenticated via SSO?  │
                             └────────┬───────────────┬────────┘
                                      │ No            │ Yes
                                      ▼               ▼
                        ┌─────────────────────┐ ┌─────────────────────┐
                        │ 🔒 Gate Screen      │ │ 🔓 Unlock AI Coach  │
                        │ • Sign In Required  │ │ • Load Firestore    │
                        │ • Whitelist Check   │ │   Profile & Goals   │
                        └─────────────────────┘ └─────────────────────┘
```

### 1. Enable Mandatory Google SSO / Email Authentication

In `web/index.html` and `web/js/app.js`:

- Disable the "Guest / Temporary Session" bypass.
- Require all users to authenticate via **Firebase Authentication** (Google SSO or Email/Password).

### 2. Whitelist Check in Cloud Firestore

In `api/routes/chat.py` and `api/auth.py`:

- When a user sends a prompt or connects to the stream, verify their email against the `registered_users` collection in Cloud Firestore.
- If the email is not found or not approved, return `403 Forbidden: Account pending registration approval`.

### 3. Enforce Strict Firestore Security Rules

Ensure `firestore.rules` blocks unauthenticated reads and writes:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /registered_users/{email} {
      allow read: if request.auth != null;
      allow write: if false; // Admin-only via Cloud Console
    }
  }
}
```

---

## 🤖 Part 2: Packaging for Google Play Store (Closed/Internal Testing)

Google Play provides **Closed Testing** and **Internal Testing tracks** that allow publishing an app that is **invisible in public search** and downloadable **only by invited/registered email addresses**.

### Step-by-Step with Bubblewrap (Trusted Web Activity)

1. **Install Bubblewrap CLI**:

   ```bash
   npm install -g @bubblewrap/cli
   ```

2. **Initialize the Android Project**:

   ```bash
   bubblewrap init --manifest="https://client.breakingintocybersecurity.org/manifest.json"
   ```

   - Package ID: `org.breakingintocybersecurity.cybermentor`
   - App Name: `CyberMentor`
   - Host: `client.breakingintocybersecurity.org`

3. **Build the Android App Bundle (`.aab`)**:

   ```bash
   bubblewrap build
   ```

   This generates `app-release-bundle.aab`.

4. **Upload to Google Play Console (Closed Testing Only)**:

   - Go to [Google Play Console](https://play.google.com/console).
   - Create an app $\rightarrow$ `CyberMentor`.
   - Go to **Testing $\rightarrow$ Closed testing** (or **Internal testing**).
   - Under **Testers**, create an **Email List** (e.g. `registered-cyber-coaching-candidates`).
   - Add the specific email addresses of your registered users.
   - Upload `app-release-bundle.aab` and click **Save**.
   - Share the private opt-in link with registered users. Only they will be able to download and install it!

---

## 🍎 Part 3: Packaging for Apple App Store (TestFlight & Unlisted Distribution)

Apple offers two primary methods to distribute apps exclusively to registered users without public App Store indexing:

1. **TestFlight (Private Beta Track)**: Up to 10,000 external users via email invite or private link.
2. **Unlisted App Distribution**: The app is approved by Apple but accessible **only via a direct private link** (hidden from App Store search and categories).

### Step-by-Step with Capacitor

1. **Initialize Capacitor**:

   ```bash
   npm install @capacitor/core @capacitor/cli @capacitor/ios
   npx cap init "CyberMentor" "org.breakingintocybersecurity.cybermentor" --web-dir "web"
   npx cap add ios
   ```

2. **Sync Web Assets**:

   ```bash
   npx cap sync ios
   ```

3. **Open Xcode**:

   ```bash
   npx cap open ios
   ```

4. **Archive & Upload to App Store Connect**:

   - In Xcode: Select **Product $\rightarrow$ Archive**.
   - Click **Distribute App** $\rightarrow$ **App Store Connect**.

5. **Make Available to Registered Users Only**:

   - **Method A (TestFlight - Immediate)**:
     - In App Store Connect, go to **TestFlight**.
     - Add registered users to an **External Testing Group** via email.
     - Users receive an invite to install CyberMentor via the TestFlight app.
   - **Method B (Unlisted App)**:
     - In App Store Connect, submit a request under **App Distribution Methods** $\rightarrow$ select **Unlisted App**.
     - Once approved, Apple provides a private URL that only registered users can open to install the app.

---

## 📋 Summary Checklist

| Platform | Packaging Method | Distribution Method (Registered Only) |
| :--- | :--- | :--- |
| **Web / Mobile Browser** | Progressive Web App (PWA) | Mandatory Google SSO / Firestore Email Whitelist |
| **Google Play (Android)** | Bubblewrap / TWA (`.aab`) | Google Play Console $\rightarrow$ **Closed / Internal Testing Track** |
| **Apple App Store (iOS)** | Capacitor / Xcode (`.ipa`) | App Store Connect $\rightarrow$ **TestFlight Group** or **Unlisted App** |
