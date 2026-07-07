import os
import pandas as pd

OUTPUTS_DIR = "./outputs"
TEXT_CSV = os.path.join(OUTPUTS_DIR, "text_results.csv")
VISION_CSV = os.path.join(OUTPUTS_DIR, "vision_results.csv")

# Member 4: Evaluation & Comparative Analysis

def load_results():
    text_df = pd.read_csv(TEXT_CSV)
    vision_df = pd.read_csv(VISION_CSV)

    # Align schemas: text tools have no cost/pages, vision has no separate tool split
    text_df["cost_usd"] = 0.0
    text_df["pages"] = pd.NA

    combined = pd.concat([text_df, vision_df], ignore_index=True)
    combined = combined[[
        "pdf_name", "tool", "time_sec", "char_count", "accuracy",
        "failed", "cost_usd", "pages", "content_completeness", "table_preservation",
    ]]
    return combined


def build_comparison_matrix(df, value_col, filename):
    matrix = df.pivot(index="pdf_name", columns="tool", values=value_col)
    out_path = os.path.join(OUTPUTS_DIR, filename)
    matrix.to_csv(out_path)
    print(f"[+] Saved {value_col} comparison matrix to {out_path}")
    return matrix


def build_tool_summary(df):
    summary = df.groupby("tool").agg(
        pdfs_processed=("pdf_name", "count"),
        failures=("failed", "sum"),
        avg_time_sec=("time_sec", "mean"),
        avg_char_count=("char_count", "mean"),
        total_cost_usd=("cost_usd", "sum"),
    ).round(4)
    out_path = os.path.join(OUTPUTS_DIR, "tool_summary.csv")
    summary.to_csv(out_path)
    print(f"[+] Saved per-tool summary to {out_path}")
    return summary


def compare_pipelines():
    print("Evaluating pipeline results...")

    if not os.path.exists(TEXT_CSV) or not os.path.exists(VISION_CSV):
        print(f"[-] Missing results. Run pipeline_text.py and pipeline_vision.py first.")
        return

    df = load_results()

    time_matrix = build_comparison_matrix(df, "time_sec", "comparison_time_sec.csv")
    chars_matrix = build_comparison_matrix(df, "char_count", "comparison_char_count.csv")
    tool_summary = build_tool_summary(df)

    print("\n=== Processing Time (s) by PDF x Tool ===")
    print(time_matrix.to_string())

    print("\n=== Char Count by PDF x Tool ===")
    print(chars_matrix.to_string())

    print("\n=== Per-Tool Summary ===")
    print(tool_summary.to_string())

    failed_rows = df[df["failed"] == True]
    if not failed_rows.empty:
        print("\n=== Failures ===")
        print(failed_rows[["pdf_name", "tool"]].to_string(index=False))
    else:
        print("\n[+] No failures across any tool.")


if __name__ == "__main__":
    compare_pipelines()
