#!/bin/bash
# ─────────────────────────────────────────────────────
# CyberMentor — Cloud Run Deployment Script
# ─────────────────────────────────────────────────────
set -euo pipefail

# ── Configuration ────────────────────────────────────
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
SERVICE_NAME="cybermentor"
REGION="us-central1"
IMAGE="us-central1-docker.pkg.dev/${PROJECT_ID}/cybermentor/${SERVICE_NAME}"

echo "🚀 Deploying CyberMentor to Cloud Run"
echo "   Project : ${PROJECT_ID}"
echo "   Service : ${SERVICE_NAME}"
echo "   Region  : ${REGION}"
echo ""

# ── Enable required APIs ─────────────────────────────
echo "🔧 Enabling required GCP APIs..."
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    --project="${PROJECT_ID}"

# ── Build and push container ─────────────────────────
echo "🐳 Building and pushing container..."
gcloud builds submit --tag "${IMAGE}" --project="${PROJECT_ID}"

# ── Deploy to Cloud Run ──────────────────────────────
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image="${IMAGE}" \
    --platform=managed \
    --region="${REGION}" \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --set-env-vars="APP_ENV=production,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-secrets="GEMINI_API_KEY=cybermentor-gemini-key:latest" \
    --project="${PROJECT_ID}"

# ── Get the service URL ──────────────────────────────
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --platform=managed \
    --region="${REGION}" \
    --format="value(status.url)" \
    --project="${PROJECT_ID}")

echo ""
echo "✅ Deployment complete!"
echo "   URL: ${SERVICE_URL}"
echo ""
echo "📝 Next steps:"
echo "   1. Update web/js/app.js API_BASE_URL to: ${SERVICE_URL}"
echo "   2. Visit ${SERVICE_URL}/docs for the API documentation"
