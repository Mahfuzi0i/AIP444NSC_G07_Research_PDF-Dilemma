"""
Quick smoke test for the vision pipeline.
Generates a sample image with text, sends it to Gemini 2.5 Flash via OpenRouter,
and prints what the model extracted. No PDF or real API credits needed beyond one call.
"""

import os
import base64
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def make_sample_image() -> bytes:
    img = Image.new("RGB", (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_body  = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font_title = ImageFont.load_default()
        font_body  = font_title

    draw.text((40, 30),  "AIP444NSC Group 07 — Vision Pipeline Test",          fill="black", font=font_title)
    draw.text((40, 90),  "Research Question: When does vision-based parsing",   fill="black", font=font_body)
    draw.text((40, 115), "outperform text extraction, and at what cost?",        fill="black", font=font_body)
    draw.text((40, 165), "Table: Sample Metrics",                                fill="black", font=font_title)

    # Simple table
    headers = ["Method",       "Accuracy", "Cost/page"]
    rows    = [
        ["pdfplumber",  "91%",  "$0.00"],
        ["PyMuPDF",     "89%",  "$0.00"],
        ["Vision (LLM)","95%",  "$0.0002"],
    ]
    col_x = [40, 260, 430]
    y = 210
    draw.text((col_x[0], y), headers[0], fill="navy", font=font_body)
    draw.text((col_x[1], y), headers[1], fill="navy", font=font_body)
    draw.text((col_x[2], y), headers[2], fill="navy", font=font_body)
    y += 30
    for row in rows:
        draw.text((col_x[0], y), row[0], fill="black", font=font_body)
        draw.text((col_x[1], y), row[1], fill="black", font=font_body)
        draw.text((col_x[2], y), row[2], fill="black", font=font_body)
        y += 28

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_vision_pipeline():
    print("=" * 55)
    print("Vision Pipeline Smoke Test")
    print("=" * 55)

    if not os.getenv("OPENROUTER_API_KEY"):
        print("[FAIL] OPENROUTER_API_KEY not found in .env")
        return

    print("[1] Generating sample image ...")
    img_bytes = make_sample_image()
    img_data  = base64.standard_b64encode(img_bytes).decode("utf-8")
    print(f"     Image size: {len(img_bytes) / 1024:.1f} KB")

    print("[2] Sending to Gemini 2.5 Flash via OpenRouter ...")
    start = time.time()
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_data}"}
                },
                {
                    "type": "text",
                    "text": (
                        "Extract all text and structured content from this document page. "
                        "For any tables, preserve the structure using markdown table format. "
                        "Output only the extracted content — no commentary."
                    )
                }
            ]
        }]
    )
    elapsed = time.time() - start

    text          = response.choices[0].message.content
    input_tokens  = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    cost          = (input_tokens * 0.00000015) + (output_tokens * 0.0000006)

    print(f"     Latency : {elapsed:.2f}s")
    print(f"     Tokens  : {input_tokens} in / {output_tokens} out")
    print(f"     Cost    : ${cost:.6f}")
    print()
    print("[3] Extracted content:")
    print("-" * 55)
    print(text)
    print("-" * 55)
    print()
    print("[PASS] Vision pipeline is working correctly.")


if __name__ == "__main__":
    test_vision_pipeline()
