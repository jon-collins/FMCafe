"""Submit a ComfyUI icon-generation prompt for a given menu item.

Usage:
    uv run comfyui/generate_icon.py "espresso cup"
    uv run comfyui/generate_icon.py "espresso cup" --name latte
    uv run comfyui/generate_icon.py "espresso cup" --output src/fmcafe/kiosk/static/icons/espresso_cup.png

Loads the FMCafe Icons.json workflow, fills in the requested item in place of
the <<ITEM_REQUEST>> placeholder, posts it to a locally running ComfyUI
server's /prompt endpoint (http://127.0.0.1:8188), waits for it to finish, and
downloads the resulting image to comfyui/output/<name>.png -- or an exact path
via --output -- regardless of where ComfyUI's own output folder is configured.
"""

import argparse
import json
import random
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

WORKFLOW_PATH = Path(__file__).parent / "FMCafe Icons.json"
COMFYUI_URL = "http://127.0.0.1:8188"
PLACEHOLDER = "<<ITEM_REQUEST>>"
SAVE_IMAGE_NODE_ID = "9"
SAMPLER_NODE_ID = "57:3"
IMAGE_SIZE = 512

def build_prompt(item: str) -> dict:
    """Load the workflow, substitute item for the placeholder, and randomize the seed.

    The workflow file has a hardcoded seed. Without randomizing it, submitting
    the same item text twice is byte-identical to ComfyUI, which then serves
    the whole graph -- including the save step -- from cache instead of
    running it again, so no new output ever gets produced.
    """
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    escaped_item = json.dumps(item)[1:-1]  # escape quotes/backslashes for the JSON string context
    workflow_text = workflow_text.replace("<<ITEM_WIDTH>>", str(IMAGE_SIZE))
    workflow_text = workflow_text.replace("<<ITEM_HEIGHT>>", str(IMAGE_SIZE))

    prompt = json.loads(workflow_text.replace(PLACEHOLDER, escaped_item))
    prompt[SAMPLER_NODE_ID]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
    return prompt


def submit(item: str) -> dict:
    """Post the filled-in workflow to ComfyUI's /prompt endpoint and return its response."""
    body = json.dumps({"prompt": build_prompt(item)}).encode("utf-8")
    request = urllib.request.Request(
        f"{COMFYUI_URL}/prompt", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def wait_for_outputs(
    prompt_id: str, poll_interval: float = 1.0, timeout: float = 300.0
) -> dict:
    """Poll ComfyUI's history endpoint until the prompt finishes, returning its outputs."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
            history = json.loads(response.read())
        entry = history.get(prompt_id)
        if entry and entry.get("outputs"):
            return entry["outputs"]
        time.sleep(poll_interval)
    raise TimeoutError(f"ComfyUI did not finish prompt {prompt_id} within {timeout}s")


def download_image(image_info: dict) -> bytes:
    query = urllib.parse.urlencode(
        {
            "filename": image_info["filename"],
            "subfolder": image_info.get("subfolder", ""),
            "type": image_info.get("type", "output"),
        }
    )
    with urllib.request.urlopen(f"{COMFYUI_URL}/view?{query}") as response:
        return response.read()


def generate_icon(item: str, output_path: Path) -> Path:
    """Submit the prompt, wait for it to finish, and save the resulting image to output_path."""
    prompt_id = submit(item)["prompt_id"]
    outputs = wait_for_outputs(prompt_id)
    image_info = outputs[SAVE_IMAGE_NODE_ID]["images"][0]
    image_bytes = download_image(image_info)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return output_path


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("item", help="the item to generate an icon for, e.g. 'espresso cup'")
    parser.add_argument(
        "--name",
        help="filename to save as (without extension), if different from the item name",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="exact output path to save to, overriding --name and the default location",
    )
    args = parser.parse_args()

    if args.output:
        output_path = args.output
    else:
        slug = slugify(args.name) if args.name else slugify(args.item)
        output_path = Path(__file__).parent / "output" / f"{slug}.png"

    print(f"Submitting prompt for {args.item!r}...")
    saved_path = generate_icon(args.item, output_path)
    print(f"Saved icon to {saved_path}")


if __name__ == "__main__":
    main()
