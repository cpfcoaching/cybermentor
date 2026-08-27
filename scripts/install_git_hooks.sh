#!/bin/bash
# Install local Git pre-commit security hook
HOOK_PATH="$(git rev-parse --git-dir)/hooks/pre-commit"

cat << 'EOF' > "$HOOK_PATH"
#!/bin/bash
echo "🛡️ Running Pre-Commit / Pre-Merge Security Audit..."
python3 scripts/security_check.py
if [ $? -ne 0 ]; then
    echo "❌ Commit rejected due to security vulnerability or secret leakage."
    exit 1
fi
EOF

chmod +x "$HOOK_PATH"
echo "✅ Git pre-commit security hook installed at $HOOK_PATH"
