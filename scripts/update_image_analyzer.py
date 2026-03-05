"""Update the imageMetadataExtractor analyzer in Azure Content Understanding.

Recreates the custom analyzer with:
- disable_face_blurring = true (enables celebrity identification) — requires Azure Limited Access approval
- Updated Description and Caption prompts to reference identified persons
- New "Persons" field for identifying public figures

Usage:
    # Uses DefaultAzureCredential (az login or managed identity)
    python scripts/update_image_analyzer.py

    # Skip disable_face_blurring if Limited Access is not yet approved
    python scripts/update_image_analyzer.py --no-face-unblur

Requires environment variables (from .env or shell):
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT  — Azure CU endpoint URL
    AZURE_CONTENT_UNDERSTANDING_KEY       — (Optional) API key; uses DefaultAzureCredential if absent

Note:
    The disable_face_blurring parameter is an Azure Limited Access feature.
    The API will reject it with InvalidParameter unless your subscription
    has been approved via https://aka.ms/facerecognition.
    Use --no-face-unblur to deploy the analyzer without this setting.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

# Load .env from the API project if available
_env_path = Path(__file__).resolve().parent.parent / "MetadataGenerator.Api" / ".env"
if _env_path.exists():
    from dotenv import load_dotenv

    load_dotenv(_env_path)

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldDefinition,
    ContentFieldSchema,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ANALYZER_ID = "imageMetadataExtractor"

# ---------------------------------------------------------------------------
# Field definitions
# ---------------------------------------------------------------------------

DESCRIPTION_FIELD = ContentFieldDefinition(
    type="string",
    method="generate",
    description=(
        "Generate a detailed description of the image content in German. "
        "When recognizable public figures or celebrities are visible in the "
        "image, refer to them by their commonly used name in the description."
    ),
)

CAPTION_FIELD = ContentFieldDefinition(
    type="string",
    method="generate",
    description=(
        "Generate a concise caption for the image in German (one sentence). "
        "When recognizable public figures or celebrities are visible, name "
        "them in the caption."
    ),
)

KEYWORDS_FIELD = ContentFieldDefinition(
    type="array",
    method="generate",
    description=(
        "Generate a list of relevant keywords/tags for the image in German. "
        "Include subject matter, objects, scenes, and themes."
    ),
    item_definition=ContentFieldDefinition(type="string"),
)

PERSONS_FIELD = ContentFieldDefinition(
    type="array",
    method="generate",
    description=(
        "Identify any recognizable public figures, celebrities, politicians, "
        "athletes, or entertainers visible in the image and return their full "
        "commonly used names (e.g. 'Angela Merkel', 'Rafael Nadal'). "
        "Only identify well-known public figures — do not identify or name "
        "private individuals. If no public figures are recognizable, return an "
        "empty list. Do not return placeholder values like 'Unknown person' or "
        "'Unbekannte Person'."
    ),
    item_definition=ContentFieldDefinition(type="string"),
)


def build_analyzer(*, enable_face_unblur: bool = True) -> ContentAnalyzer:
    """Build the ContentAnalyzer resource definition.

    Args:
        enable_face_unblur: If True, sets disable_face_blurring=True.
            Requires Azure Limited Access approval. If False, omits the setting.
    """
    config = ContentAnalyzerConfig(
        disable_face_blurring=True,
    ) if enable_face_unblur else None

    return ContentAnalyzer(
        description="Custom image metadata extractor with celebrity identification",
        base_analyzer_id="prebuilt-image",
        config=config,
        field_schema=ContentFieldSchema(
            name="ImageMetadataSchema",
            description="Extracts description, caption, keywords, and identified persons from images",
            fields={
                "Description": DESCRIPTION_FIELD,
                "Caption": CAPTION_FIELD,
                "Keywords": KEYWORDS_FIELD,
                "Persons": PERSONS_FIELD,
            },
        ),
        models={"completion": "gpt-4.1-mini"},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the imageMetadataExtractor analyzer")
    parser.add_argument(
        "--no-face-unblur",
        action="store_true",
        help="Deploy without disable_face_blurring (use when Limited Access is not approved)",
    )
    args = parser.parse_args()

    enable_face_unblur = not args.no_face_unblur

    endpoint = os.environ.get("AZURE_CONTENT_UNDERSTANDING_ENDPOINT", "")
    key = os.environ.get("AZURE_CONTENT_UNDERSTANDING_KEY", "")

    if not endpoint:
        logger.error("AZURE_CONTENT_UNDERSTANDING_ENDPOINT is not set")
        sys.exit(1)

    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    logger.info("Connecting to %s", endpoint)
    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    analyzer = build_analyzer(enable_face_unblur=enable_face_unblur)

    if enable_face_unblur:
        logger.info("disable_face_blurring=True (requires Limited Access approval)")
    else:
        logger.info("disable_face_blurring omitted (--no-face-unblur flag set)")

    logger.info("Creating/updating analyzer '%s' with allow_replace=True ...", ANALYZER_ID)
    poller = client.begin_create_analyzer(
        analyzer_id=ANALYZER_ID,
        resource=analyzer,
        allow_replace=True,
    )
    result = poller.result()

    logger.info("Analyzer '%s' status: %s", ANALYZER_ID, result.status)
    if result.status == "ready":
        logger.info("Analyzer updated successfully.")
    else:
        logger.warning("Analyzer status is '%s' — check Azure portal for details.", result.status)
        if result.warnings:
            for w in result.warnings:
                logger.warning("  Warning: %s", w)


if __name__ == "__main__":
    main()
