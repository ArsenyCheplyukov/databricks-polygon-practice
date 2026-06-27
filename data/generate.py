"""Generate synthetic, skewed, messy US insurance data."""

import argparse
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from common.paths import GENERATED_DIR, RAW_DIR, generated_manifest_path

STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
PRODUCTS = ["auto", "home", "life", "health"]
SEGMENTS = ["basic", "premium", "enterprise"]
POLICY_STATUSES = ["active", "cancelled", "pending"]
CLAIM_STATUSES = ["approved", "denied", "pending"]


def _skewed_choice(options, dominant, dominant_share):
    if random.random() < dominant_share:
        return dominant
    return random.choice([o for o in options if o != dominant])


def _random_date(start=datetime(2020, 1, 1), end=datetime(2024, 12, 31)):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def _format_date_iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def _format_date_messy(d: datetime) -> str:
    fmt = random.choice(["%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"])
    return d.strftime(fmt)


def generate(scale: str, seed: int = 42):
    random.seed(seed)
    if scale == "small":
        n_clients, n_policies, n_claims = 1_000, 5_000, 10_000
    elif scale == "large":
        n_clients, n_policies, n_claims = 50_000, 250_000, 750_000
    else:
        raise ValueError(f"Unknown scale: {scale}")

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    clients = []
    for i in range(1, n_clients + 1):
        state = _skewed_choice(STATES, "CA", 0.40)
        signup = _random_date()
        segment = _skewed_choice(SEGMENTS, "basic", 0.50) if random.random() > 0.05 else None
        clients.append({
            "client_id": i,
            "name": f"Client {i}",
            "state": state,
            "signup_date": _format_date_messy(signup) if random.random() < 0.30 else _format_date_iso(signup),
            "segment": segment,
        })

    policies = []
    for i in range(1, n_policies + 1):
        product = _skewed_choice(PRODUCTS, "auto", 0.35)
        start = _random_date()
        status = random.choice(POLICY_STATUSES)
        policies.append({
            "policy_id": i,
            "client_id": random.randint(1, n_clients),
            "product": product,
            "premium": round(random.uniform(200, 2000), 2) if random.random() > 0.03 else None,
            "start_date": _format_date_messy(start) if random.random() < 0.25 else _format_date_iso(start),
            "status": status,
        })

    claims = []
    for i in range(1, n_claims + 1):
        claim_date = _random_date()
        amount = round(random.uniform(100, 50000), 2)
        claims.append({
            "claim_id": i,
            "policy_id": random.randint(1, n_policies),
            "amount": amount if random.random() > 0.04 else None,
            "claim_date": _format_date_messy(claim_date) if random.random() < 0.20 else _format_date_iso(claim_date),
            "status": random.choice(CLAIM_STATUSES),
        })

    # Add ~2% duplicates to raw files for bronze dedup practice
    dupes_clients = random.sample(clients, int(len(clients) * 0.02))
    dupes_policies = random.sample(policies, int(len(policies) * 0.02))
    dupes_claims = random.sample(claims, int(len(claims) * 0.02))

    clients_path = RAW_DIR / "clients.jsonl"
    policies_path = RAW_DIR / "policies.csv"
    claims_path = RAW_DIR / "claims.jsonl"

    with clients_path.open("w", encoding="utf-8") as f:
        for row in clients + dupes_clients:
            f.write(json.dumps(row) + "\n")

    with policies_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["policy_id", "client_id", "product", "premium", "start_date", "status"])
        writer.writeheader()
        for row in policies + dupes_policies:
            writer.writerow(row)

    with claims_path.open("w", encoding="utf-8") as f:
        for row in claims + dupes_claims:
            f.write(json.dumps(row) + "\n")

    manifest = {
        "scale": scale,
        "seed": seed,
        "clients": {"unique": len(clients), "with_dupes": len(clients) + len(dupes_clients)},
        "policies": {"unique": len(policies), "with_dupes": len(policies) + len(dupes_policies)},
        "claims": {"unique": len(claims), "with_dupes": len(claims) + len(dupes_claims)},
        "files": {
            "clients": str(clients_path.relative_to(GENERATED_DIR)),
            "policies": str(policies_path.relative_to(GENERATED_DIR)),
            "claims": str(claims_path.relative_to(GENERATED_DIR)),
        },
    }
    generated_manifest_path().write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", default="small", choices=["small", "large"])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    manifest = generate(args.scale, args.seed)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
