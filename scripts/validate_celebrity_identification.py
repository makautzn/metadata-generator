"""PoC validation script for celebrity identification (task 016).

Uploads test images to the running API and records validation results
for each image against the acceptance criteria defined in the FRD.

Usage:
    # Place test images in scripts/test_images/ (JPEG/PNG/WebP)
    # Start the backend API on localhost:8000
    python scripts/validate_celebrity_identification.py

    # Custom API URL
    python scripts/validate_celebrity_identification.py --api-url http://localhost:8000

    # Custom image directory
    python scripts/validate_celebrity_identification.py --image-dir /path/to/images

The script expects a manifest file (test_images/manifest.json) that maps
image filenames to their expected persons:

    {
        "merkel_press.jpg": {
            "category": "single_celebrity",
            "expected_persons": ["Angela Merkel"],
            "has_non_public": false
        },
        "landscape.jpg": {
            "category": "no_people",
            "expected_persons": [],
            "has_non_public": false
        },
        "crowd.jpg": {
            "category": "non_public_only",
            "expected_persons": [],
            "has_non_public": true
        }
    }

Categories: single_celebrity, multiple_celebrities, non_public_only,
            mixed_celebrity_non_public, no_people
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_IMAGE_DIR = Path(__file__).resolve().parent / "test_images"
MANIFEST_FILE = "manifest.json"


def load_manifest(image_dir: Path) -> dict:
    manifest_path = image_dir / MANIFEST_FILE
    if not manifest_path.exists():
        logger.error("Manifest file not found: %s", manifest_path)
        logger.info("Create %s with expected persons per image. See script docstring for format.", MANIFEST_FILE)
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


def analyze_image(api_url: str, image_path: Path) -> dict:
    """Upload an image to the API and return the response JSON."""
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    suffix = image_path.suffix.lower()
    mime = mime_map.get(suffix, "application/octet-stream")

    with open(image_path, "rb") as f:
        response = httpx.post(
            f"{api_url}/api/v1/analyze/image",
            files={"file": (image_path.name, f, mime)},
            timeout=120.0,
        )
    response.raise_for_status()
    return response.json()


def validate_result(
    filename: str,
    result: dict,
    expected_persons: list[str],
    has_non_public: bool,
) -> dict:
    """Validate a single result against acceptance criteria."""
    keywords = result.get("keywords", [])
    description = result.get("description", "")
    caption = result.get("caption", "")

    findings: dict = {
        "file": filename,
        "expected_persons": expected_persons,
        "found_keywords": keywords,
        "description": description,
        "caption": caption,
        "checks": {},
    }

    # Check: expected persons found in keywords
    found_persons = []
    missing_persons = []
    for person in expected_persons:
        if any(person.lower() == kw.lower() for kw in keywords):
            found_persons.append(person)
        else:
            missing_persons.append(person)

    findings["found_persons"] = found_persons
    findings["missing_persons"] = missing_persons

    # True positive: identified correctly
    findings["checks"]["persons_in_keywords"] = len(missing_persons) == 0

    # No placeholders
    placeholders = {"unknown", "unbekannt", "person", "mann", "frau", "unknown person", "unbekannte person"}
    found_placeholders = [kw for kw in keywords if kw.lower() in placeholders]
    findings["checks"]["no_placeholders"] = len(found_placeholders) == 0
    if found_placeholders:
        findings["found_placeholders"] = found_placeholders

    # No duplicates
    lower_kws = [kw.lower() for kw in keywords]
    findings["checks"]["no_duplicates"] = len(lower_kws) == len(set(lower_kws))

    # Description references persons
    if expected_persons:
        desc_mentions = [p for p in expected_persons if p.lower() in description.lower()]
        findings["checks"]["description_references_persons"] = len(desc_mentions) == len(expected_persons)
    else:
        findings["checks"]["description_references_persons"] = True  # N/A

    # Caption references persons
    if expected_persons:
        cap_mentions = [p for p in expected_persons if p.lower() in caption.lower()]
        findings["checks"]["caption_references_persons"] = len(cap_mentions) == len(expected_persons)
    else:
        findings["checks"]["caption_references_persons"] = True  # N/A

    # False positive check (non-public individuals should not be named)
    # This is a manual assessment — we flag if the image has non-public people
    findings["checks"]["has_non_public_context"] = has_non_public

    all_passed = all(v for k, v in findings["checks"].items() if k != "has_non_public_context")
    findings["passed"] = all_passed

    return findings


def compute_metrics(results: list[dict], manifest: dict) -> dict:
    """Compute TP rate, FP rate, and overall pass/fail."""
    total_expected = 0
    total_found = 0
    non_public_images = 0
    false_positives = 0

    for r in results:
        expected = r["expected_persons"]
        total_expected += len(expected)
        total_found += len(r.get("found_persons", []))

        entry = manifest.get(r["file"], {})
        if entry.get("has_non_public", False) and not expected:
            non_public_images += 1
            # Check if any person-like keywords were added
            # (this requires manual review — we flag it)
            person_kws = [kw for kw in r["found_keywords"] if len(kw.split()) >= 2]
            if person_kws:
                false_positives += 1

    tp_rate = (total_found / total_expected * 100) if total_expected > 0 else 100
    fp_rate = (false_positives / non_public_images * 100) if non_public_images > 0 else 0

    return {
        "total_expected_persons": total_expected,
        "total_found_persons": total_found,
        "true_positive_rate": round(tp_rate, 1),
        "non_public_images": non_public_images,
        "false_positives": false_positives,
        "false_positive_rate": round(fp_rate, 1),
        "tp_threshold_met": tp_rate >= 80.0,
        "fp_threshold_met": fp_rate == 0.0,
    }


def print_report(results: list[dict], metrics: dict) -> None:
    """Print a formatted validation report."""
    print("\n" + "=" * 80)
    print("CELEBRITY IDENTIFICATION — PoC VALIDATION REPORT")
    print("=" * 80)

    print(f"\n{'File':<30} {'Expected':<25} {'Found':<25} {'Pass'}")
    print("-" * 80)
    for r in results:
        expected = ", ".join(r["expected_persons"]) or "(none)"
        found = ", ".join(r.get("found_persons", [])) or "(none)"
        status = "PASS" if r["passed"] else "FAIL"
        print(f"{r['file']:<30} {expected:<25} {found:<25} {status}")

    print("\n" + "-" * 80)
    print(f"True Positive Rate:  {metrics['true_positive_rate']}% (threshold: ≥80%)")
    print(f"False Positive Rate: {metrics['false_positive_rate']}% (threshold: 0%)")
    print(f"TP Threshold Met:    {'YES' if metrics['tp_threshold_met'] else 'NO'}")
    print(f"FP Threshold Met:    {'YES' if metrics['fp_threshold_met'] else 'NO'}")

    # Detail checks
    print("\nDetailed checks per image:")
    for r in results:
        print(f"\n  {r['file']}:")
        for check, passed in r["checks"].items():
            icon = "✓" if passed else "✗"
            print(f"    {icon} {check}")
        if r.get("missing_persons"):
            print(f"    Missing: {', '.join(r['missing_persons'])}")

    print("\n" + "=" * 80)
    overall = metrics["tp_threshold_met"] and metrics["fp_threshold_met"]
    print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate celebrity identification PoC")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Backend API URL")
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR, help="Test images directory")
    args = parser.parse_args()

    manifest = load_manifest(args.image_dir)
    logger.info("Loaded manifest with %d images", len(manifest))

    results = []
    for filename, entry in manifest.items():
        image_path = args.image_dir / filename
        if not image_path.exists():
            logger.warning("Image not found, skipping: %s", image_path)
            continue

        logger.info("Analyzing %s ...", filename)
        try:
            response = analyze_image(args.api_url, image_path)
        except Exception as exc:
            logger.error("Failed to analyze %s: %s", filename, exc)
            results.append({
                "file": filename,
                "expected_persons": entry.get("expected_persons", []),
                "found_persons": [],
                "found_keywords": [],
                "description": "",
                "caption": "",
                "checks": {"api_error": False},
                "passed": False,
            })
            continue

        validation = validate_result(
            filename=filename,
            result=response,
            expected_persons=entry.get("expected_persons", []),
            has_non_public=entry.get("has_non_public", False),
        )
        results.append(validation)

    metrics = compute_metrics(results, manifest)
    print_report(results, metrics)

    # Write JSON report
    report_path = args.image_dir / "validation_report.json"
    with open(report_path, "w") as f:
        json.dump({"results": results, "metrics": metrics}, f, indent=2, ensure_ascii=False)
    logger.info("Report written to %s", report_path)


if __name__ == "__main__":
    main()
