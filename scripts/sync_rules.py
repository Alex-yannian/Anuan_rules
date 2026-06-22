#!/usr/bin/env python3
"""Mirror upstream rule files and build a self-hosted OpenClash config."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Anuan_rules/1.0 (+https://github.com)"


def source(name: str, url: str, target: str, provider: str) -> dict[str, str]:
    return {"name": name, "url": url, "target": target, "provider": provider}


SOURCES: list[dict[str, str]] = []

DOMAIN_666OS = [
    "Tracking", "Advertising", "Direct", "LocationDKS", "Private", "Download",
    "Speedtest", "AI", "OpenAI", "Claude", "Gemini", "Telegram", "Twitter",
    "SocialMedia", "NewsMedia", "Games", "Crypto", "Netflix", "YouTube",
    "Disney", "XPTV", "Emby", "Streaming", "AppleCN", "Apple", "Google",
    "Microsoft", "Facebook", "GitHub", "Dev", "OneDrive", "Spotify", "Proxy",
    "China",
]
IP_666OS = [
    "Advertising", "Private", "AI", "Telegram", "SocialMedia", "XPTV", "Emby",
    "Netflix", "Streaming", "Google", "Facebook", "Proxy", "China",
]

for rule_name in DOMAIN_666OS:
    SOURCES.append(source(
        f"666OS-domain-{rule_name}",
        f"https://raw.githubusercontent.com/666OS/rules/release/mihomo/domain/{rule_name}.mrs",
        f"rules/666OS/domain/{rule_name}.mrs",
        "666OS/rules",
    ))

for rule_name in IP_666OS:
    SOURCES.append(source(
        f"666OS-ip-{rule_name}",
        f"https://raw.githubusercontent.com/666OS/rules/release/mihomo/ip/{rule_name}.mrs",
        f"rules/666OS/ip/{rule_name}.mrs",
        "666OS/rules",
    ))

METACUBEX = {
    "private-domain": ("geosite/private.mrs", "private_domain.mrs"),
    "private-ip": ("geoip/private.mrs", "private_ip.mrs"),
    "cn-domain": ("geosite/cn.mrs", "cn_domain.mrs"),
    "cn-ip": ("geoip/cn.mrs", "cn_ip.mrs"),
    "geolocation-not-cn": ("geosite/geolocation-!cn.mrs", "geolocation_not_cn.mrs"),
    "category-ads-all": ("geosite/category-ads-all.mrs", "category_ads_all.mrs"),
    "openai": ("geosite/openai.mrs", "openai.mrs"),
    "google": ("geosite/google.mrs", "google.mrs"),
    "youtube": ("geosite/youtube.mrs", "youtube.mrs"),
    "telegram": ("geosite/telegram.mrs", "telegram.mrs"),
    "github": ("geosite/github.mrs", "github.mrs"),
    "netflix": ("geosite/netflix.mrs", "netflix.mrs"),
    "disney": ("geosite/disney.mrs", "disney.mrs"),
    "steam": ("geosite/steam.mrs", "steam.mrs"),
    "steam-cn": ("geosite/steam@cn.mrs", "steam_cn.mrs"),
    "category-games": ("geosite/category-games.mrs", "category_games.mrs"),
    "category-games-cn": ("geosite/category-games@cn.mrs", "category_games_cn.mrs"),
    "apple": ("geosite/apple.mrs", "apple.mrs"),
    "apple-cn": ("geosite/apple-cn.mrs", "apple_cn.mrs"),
    "microsoft": ("geosite/microsoft.mrs", "microsoft.mrs"),
}

for name, (upstream_path, filename) in METACUBEX.items():
    SOURCES.append(source(
        f"metacubex-{name}",
        f"https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/{upstream_path}",
        f"rules/metacubex/{filename}",
        "MetaCubeX/meta-rules-dat",
    ))

for name, filename in {
    "geoip-dat": "geoip.dat",
    "geosite-dat": "geosite.dat",
    "geoip-metadb": "geoip.metadb",
    "asn-mmdb": "GeoLite2-ASN.mmdb",
}.items():
    SOURCES.append(source(
        f"metacubex-{name}",
        f"https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/{filename}",
        f"rules/metacubex/geo/{filename}",
        "MetaCubeX/meta-rules-dat",
    ))

SOURCES.extend([
    source(
        "awavenue-ads",
        "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/Filters/AWAvenue-Ads-Rule-Clash.yaml",
        "rules/awavenue/AWAvenue-Ads-Rule-Clash.yaml",
        "TG-Twilight/AWAvenue-Ads-Rule",
    ),
    source(
        "dustinwin-fakeip-filter",
        "https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/fakeip-filter.mrs",
        "rules/dustinwin/fakeip-filter.mrs",
        "DustinWin/ruleset_geodata",
    ),
])

for name in ["reject", "direct", "proxy", "private", "gfw", "cncidr", "lancidr", "applications"]:
    SOURCES.append(source(
        f"loyalsoldier-{name}",
        f"https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/{name}.txt",
        f"rules/loyalsoldier/{name}.txt",
        "Loyalsoldier/clash-rules",
    ))

for name in ["OpenAI", "Claude", "Gemini", "GitHub", "YouTube", "Netflix", "Telegram", "Steam"]:
    SOURCES.append(source(
        f"blackmatrix7-{name.lower()}",
        f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{name}/{name}.yaml",
        f"rules/blackmatrix7/{name}.yaml",
        "blackmatrix7/ios_rule_script",
    ))


def download(item: dict[str, str], retries: int = 3) -> dict[str, object]:
    request = urllib.request.Request(item["url"], headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
            if len(payload) < 16:
                raise ValueError(f"response too small: {len(payload)} bytes")
            prefix = payload[:256].lower()
            if b"<html" in prefix or b"<!doctype" in prefix:
                raise ValueError("upstream returned HTML instead of a rule file")

            target = ROOT / item["target"]
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(delete=False, dir=target.parent) as handle:
                handle.write(payload)
                temporary = Path(handle.name)
            os.replace(temporary, target)
            return {
                **item,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        except (OSError, ValueError, urllib.error.URLError) as error:
            last_error = error
            if attempt < retries:
                time.sleep(attempt * 2)
    raise RuntimeError(f"{item['name']}: {last_error}")


def sync_rules(workers: int) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(download, item): item for item in SOURCES}
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"synced {item['target']}")
            except Exception as error:  # noqa: BLE001 - report every failed source together
                errors.append(str(error))
                print(f"failed {error}", file=sys.stderr)
    if errors:
        raise RuntimeError("\n".join(errors))
    return sorted(results, key=lambda row: str(row["target"]))


def build_config(repository: str, branch: str) -> None:
    template = (ROOT / "config" / "Anuan.template.yaml").read_text(encoding="utf-8")
    template = template.replace("YOUR_GITHUB_USERNAME/Anuan_rules", repository)
    raw_base = f"https://raw.githubusercontent.com/{repository}/{branch}"
    for item in SOURCES:
        template = template.replace(item["url"], f"{raw_base}/{item['target']}")
    unresolved = [item["url"] for item in SOURCES if item["url"] in template]
    if unresolved:
        raise RuntimeError(f"unresolved upstream URLs in config: {unresolved}")
    (ROOT / "config" / "Anuan.yaml").write_text(template, encoding="utf-8", newline="\n")


def write_catalog(results: list[dict[str, object]]) -> None:
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "sources": results,
    }
    target = ROOT / "rules" / "manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default="YOUR_GITHUB_USERNAME/Anuan_rules")
    parser.add_argument("--branch", default="release")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--config-only", action="store_true")
    args = parser.parse_args()

    if args.config_only:
        build_config(args.repository, args.branch)
        return 0

    results = sync_rules(args.workers)
    write_catalog(results)
    build_config(args.repository, args.branch)
    print(f"completed: {len(results)} rules mirrored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
