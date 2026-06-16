from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finance_close_control_tower.exports import write_sample_close_pack  # noqa: E402
from finance_close_control_tower.ingestion import load_sample_data  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the synthetic close-control smoke pipeline.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/sample_close_pack"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    datasets = load_sample_data(args.data_dir)
    markdown_path, excel_path, pdf_path = write_sample_close_pack(datasets, args.output_dir)
    print(f"Created {markdown_path}")
    print(f"Created {excel_path}")
    print(f"Created {pdf_path}")


if __name__ == "__main__":
    main()
