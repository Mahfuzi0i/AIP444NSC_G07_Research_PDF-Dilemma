import os
import csv
import base64
import time
import glob
import difflib
from openai import OpenAI
from pdf2image import convert_from_path
from dotenv import load_dotenv

load_dotenv()

PDFS_DIR = "./pdfs"
OUTPUTS_DIR = "./outputs"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def calculate_similarity(text1, text2):
    if not text1 or not text2:
        return 0
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return round(matcher.ratio() * 100, 2)

# Member 3: Vision-Based Parsing Pipeline (OpenRouter → Gemini 2.5 Flash)
def extract_via_vision(pdf_path: str, output_dir: str) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=200)
    page_results = []
    total_cost = 0.0
    full_text = ""

    for i, page_img in enumerate(pages):
        img_path = os.path.join(output_dir, f"page_{i+1}.png")
        page_img.save(img_path, "PNG")

        with open(img_path, "rb") as f:
            img_data = base64.standard_b64encode(f.read()).decode("utf-8")

        start = time.time()
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            max_tokens=2048,
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
                            "For any charts or figures, describe what data they show. "
                            "Output only the extracted content — no commentary."
                        )
                    }
                ]
            }]
        )
        elapsed = time.time() - start

        text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # Gemini 2.5 Flash pricing via OpenRouter: $0.15/M input, $0.60/M output
        cost = (input_tokens * 0.00000015) + (output_tokens * 0.0000006)
        total_cost += cost
        full_text += f"=== PAGE {i+1} ===\n{text}\n\n"

        page_results.append({
            "page": i + 1,
            "text": text,
            "latency_s": round(elapsed, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
        })

        print(f"  Page {i+1}: {elapsed:.2f}s | ${cost:.5f} | {input_tokens}in/{output_tokens}out tokens")

    # Save concatenated text output
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(output_dir, f"{pdf_name}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    total_latency = sum(r["latency_s"] for r in page_results)
    print(f"  Total cost: ${total_cost:.4f} | Total latency: {total_latency:.2f}s")

    return {
        "pdf_name": pdf_name,
        "pages": page_results,
        "full_text": full_text,
        "total_cost_usd": round(total_cost, 6),
        "total_latency_s": round(total_latency, 2),
    }


if __name__ == "__main__":
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    pdf_files = glob.glob(os.path.join(PDFS_DIR, "*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {PDFS_DIR}/")
        exit(0)

    print(f"[*] Found {len(pdf_files)} PDF file(s) to process.")

    csv_rows = []

    for pdf_path in pdf_files:
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        out_dir = os.path.join(OUTPUTS_DIR, "vision", pdf_name)

        print(f"\nProcessing: {pdf_path}")
        result = extract_via_vision(pdf_path, out_dir)

        # Accuracy vs ground truth (mirrors text pipeline behaviour)
        ground_truth_path = os.path.join(PDFS_DIR, f"{pdf_name}_ground_truth.txt")
        accuracy = ""
        if os.path.exists(ground_truth_path):
            with open(ground_truth_path, "r", encoding="utf-8") as f:
                ground_truth = f.read()
            accuracy = calculate_similarity(ground_truth, result["full_text"])
            print(f"  Accuracy vs ground truth: {accuracy}%")

        csv_rows.append({
            "pdf_name": pdf_name,
            "tool": "gemini-2.5-flash",
            "time_sec": result["total_latency_s"],
            "accuracy": accuracy,
            "cost_usd": result["total_cost_usd"],
            "pages": len(result["pages"]),
            "content_completeness": "",  # manual review
            "table_preservation": "",    # manual review
        })

    # Save summary CSV — parallel to outputs/text_results.csv
    csv_path = os.path.join(OUTPUTS_DIR, "vision_results.csv")
    fields = ["pdf_name", "tool", "time_sec", "accuracy", "cost_usd", "pages",
              "content_completeness", "table_preservation"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"\n[+] Done. Results saved to {csv_path}")
