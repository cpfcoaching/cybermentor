#!/usr/bin/env python3
"""
CyberMentor Cloudflare API Automation Tool

Handles:
1. Token verification
2. Finding Zone ID for breakingintocybersecurity.org
3. Creating/updating CNAME for client.breakingintocybersecurity.org
4. Configuring Full SSL and Always Use HTTPS
5. Purging Cloudflare Edge Cache

Usage:
  export CLOUDFLARE_API_TOKEN="your_token_here"
  python scripts/cloudflare_dns.py --action setup
  python scripts/cloudflare_dns.py --action purge
"""

import os
import sys
import argparse
import requests

CF_API_BASE = "https://api.cloudflare.com/client/v4"
ZONE_NAME = "breakingintocybersecurity.org"
RECORD_NAME = "client"
DEFAULT_TARGET = "ghs.googlehosted.com"  # Or your direct Cloud Run custom domain target


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def verify_token(token: str) -> bool:
    url = f"{CF_API_BASE}/user/tokens/verify"
    resp = requests.get(url, headers=get_headers(token), timeout=10)
    data = resp.json()
    if data.get("success"):
        print("✅ Cloudflare API Token is valid.")
        return True
    print(f"❌ Token verification failed: {data.get('errors')}")
    return False


def get_zone_id(token: str, zone_name: str) -> str:
    url = f"{CF_API_BASE}/zones"
    params = {"name": zone_name, "status": "active"}
    resp = requests.get(url, headers=get_headers(token), params=params, timeout=10)
    data = resp.json()
    
    if not data.get("success") or not data.get("result"):
        # Try without status filter
        resp = requests.get(url, headers=get_headers(token), params={"name": zone_name}, timeout=10)
        data = resp.json()

    if data.get("success") and data.get("result"):
        zone_id = data["result"][0]["id"]
        print(f"✅ Found Zone '{zone_name}' (ID: {zone_id})")
        return zone_id
    
    print(f"❌ Could not find active zone '{zone_name}'. Errors: {data.get('errors')}")
    return ""


def upsert_dns_record(token: str, zone_id: str, record_name: str, target: str, proxied: bool = True) -> bool:
    full_record_name = f"{record_name}.{ZONE_NAME}" if record_name != "@" else ZONE_NAME
    url = f"{CF_API_BASE}/zones/{zone_id}/dns_records"
    
    # Check if record already exists
    resp = requests.get(url, headers=get_headers(token), params={"name": full_record_name}, timeout=10)
    data = resp.json()
    existing_records = data.get("result", [])
    
    payload = {
        "type": "CNAME",
        "name": record_name,
        "content": target,
        "ttl": 1,  # Auto TTL when proxied
        "proxied": proxied,
        "comment": "CyberMentor Subdomain for All Things Agentic Hackathon"
    }

    if existing_records:
        record_id = existing_records[0]["id"]
        update_url = f"{url}/{record_id}"
        put_resp = requests.put(update_url, headers=get_headers(token), json=payload, timeout=10)
        put_data = put_resp.json()
        if put_data.get("success"):
            print(f"✅ Updated CNAME record '{full_record_name}' -> '{target}' (Proxied: {proxied})")
            return True
        print(f"❌ Failed to update record: {put_data.get('errors')}")
        return False
    else:
        post_resp = requests.post(url, headers=get_headers(token), json=payload, timeout=10)
        post_data = post_resp.json()
        if post_data.get("success"):
            print(f"✅ Created CNAME record '{full_record_name}' -> '{target}' (Proxied: {proxied})")
            return True
        print(f"❌ Failed to create record: {post_data.get('errors')}")
        return False


def set_ssl_strict(token: str, zone_id: str) -> bool:
    url = f"{CF_API_BASE}/zones/{zone_id}/settings/ssl"
    resp = requests.patch(url, headers=get_headers(token), json={"value": "strict"}, timeout=10)
    data = resp.json()
    if data.get("success"):
        print("✅ SSL Mode set to 'Full (strict)'")
        return True
    print(f"⚠️ Could not set SSL strict: {data.get('errors')}")
    return False


def enable_always_https(token: str, zone_id: str) -> bool:
    url = f"{CF_API_BASE}/zones/{zone_id}/settings/always_use_https"
    resp = requests.patch(url, headers=get_headers(token), json={"value": "on"}, timeout=10)
    data = resp.json()
    if data.get("success"):
        print("✅ 'Always Use HTTPS' enabled.")
        return True
    print(f"⚠️ Could not enable Always Use HTTPS: {data.get('errors')}")
    return False


def purge_cache(token: str, zone_id: str) -> bool:
    url = f"{CF_API_BASE}/zones/{zone_id}/purge_cache"
    resp = requests.post(url, headers=get_headers(token), json={"purge_everything": True}, timeout=10)
    data = resp.json()
    if data.get("success"):
        print("✅ Purged entire Cloudflare edge cache successfully.")
        return True
    print(f"❌ Cache purge failed: {data.get('errors')}")
    return False


def main():
    parser = argparse.ArgumentParser(description="CyberMentor Cloudflare Automation")
    parser.add_argument("--token", default=os.getenv("CLOUDFLARE_API_TOKEN"), help="Cloudflare API Token")
    parser.add_argument("--zone", default=ZONE_NAME, help="Zone domain name")
    parser.add_argument("--record", default=RECORD_NAME, help="Subdomain record (default: client)")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="CNAME Target (default: ghs.googlehosted.com)")
    parser.add_argument("--action", choices=["setup", "purge", "verify"], default="setup", help="Action to execute")
    parser.add_argument("--unproxied", action="store_true", help="Set DNS only (not proxied)")

    args = parser.parse_args()

    if not args.token:
        print("⚠️ No Cloudflare API Token found.")
        print("Set CLOUDFLARE_API_TOKEN environment variable or pass --token <TOKEN>")
        sys.exit(1)

    if not verify_token(args.token):
        sys.exit(1)

    zone_id = get_zone_id(args.token, args.zone)
    if not zone_id:
        sys.exit(1)

    if args.action == "verify":
        print("✅ Cloudflare Zone & Token verified successfully.")
    elif args.action == "setup":
        print(f"\n🚀 Setting up DNS & SSL for {args.record}.{args.zone}...")
        upsert_dns_record(args.token, zone_id, args.record, args.target, proxied=not args.unproxied)
        set_ssl_strict(args.token, zone_id)
        enable_always_https(args.token, zone_id)
        print("\n✨ Setup complete!")
    elif args.action == "purge":
        purge_cache(args.token, zone_id)


if __name__ == "__main__":
    main()
