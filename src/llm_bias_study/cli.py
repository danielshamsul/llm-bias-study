from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyze_results
from .config import get_settings
from .evaluation import build_rubric_template
from .runner import run_collection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LLM bias and hallucination study workflow"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run prompts against configured LLM APIs")
    run_parser.add_argument("--prompt-file", required=True, help="Path to the prompt CSV file")
    run_parser.add_argument(
        "--models",
        nargs="+",
        choices=["openai", "anthropic", "xai", "gemini", "mock"],
        help="Optional subset of providers to run",
    )

    rubric_parser = subparsers.add_parser(
        "rubric-template",
        help="Create a scoring template from collected responses",
    )
    rubric_parser.add_argument("--responses", required=True, help="Path to a responses CSV file")

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Build summary tables and charts from a scored rubric",
    )
    analyze_parser.add_argument("--responses", required=True, help="Path to a responses CSV file")
    analyze_parser.add_argument("--rubric", required=True, help="Path to a scored rubric CSV file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()

    if args.command == "run":
        responses, output_path = run_collection(
            prompt_file=args.prompt_file,
            settings=settings,
            selected_models=args.models,
        )
        print(f"Saved {len(responses)} responses to {output_path}")
        return

    if args.command == "rubric-template":
        output_path = build_rubric_template(args.responses, settings.output_dir)
        print(f"Saved rubric template to {output_path}")
        return

    if args.command == "analyze":
        output_paths = analyze_results(
            responses_path=args.responses,
            rubric_path=args.rubric,
            output_dir=Path(settings.output_dir),
        )
        for label, output_path in output_paths.items():
            print(f"{label}: {output_path}")
        return


if __name__ == "__main__":
    main()
