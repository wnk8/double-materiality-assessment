#!/usr/bin/env python3
"""
Double Materiality Assessment Tool — CLI entry point.

Usage:
    python main.py generate-template [--output PATH]
    python main.py run --input PATH --company NAME --year YEAR [--output-dir DIR]
"""

import argparse
import os
import sys


def cmd_generate_template(args) -> int:
    from src.template_generator import generate_template

    output = args.output or os.path.join("data", "iro_template.xlsx")
    try:
        generate_template(output)
        return 0
    except OSError as e:
        print(f"[FEHLER] {e}", file=sys.stderr)
        return 1


def cmd_run(args) -> int:
    from src.data_loader import load_iros
    from src.scoring_engine import score_iros, aggregate_by_topic
    from src.matrix_generator import generate_matrix
    from src.heatmap_generator import generate_heatmap
    from src.report_generator import generate_report
    from src.exceptions import InvalidScoreError, MissingIROError

    output_dir = args.output_dir or "outputs"
    os.makedirs(output_dir, exist_ok=True)

    matrix_path = os.path.join(output_dir, "materiality_matrix.png")
    heatmap_path = os.path.join(output_dir, "esrs_heatmap.png")
    report_path = os.path.join(output_dir, "dma_report.pdf")

    # ── Load & validate ──────────────────────────────────────────────────────
    print(f"\nLade IRO-Daten aus: {args.input}")
    try:
        iros = load_iros(args.input)
    except FileNotFoundError as e:
        print(f"[FEHLER] {e}", file=sys.stderr)
        return 1
    except (MissingIROError, InvalidScoreError) as e:
        print(f"[VALIDIERUNGSFEHLER] {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"[FEHLER] {e}", file=sys.stderr)
        return 1

    print(f"  {len(iros)} IROs erfolgreich geladen.")

    # ── Score ────────────────────────────────────────────────────────────────
    print("Berechne Wesentlichkeitsscores (EFRAG-Methodik)...")
    scored = score_iros(iros)
    aggregates = aggregate_by_topic(scored)

    # ── Summary to stdout ────────────────────────────────────────────────────
    n_impact = sum(1 for i in scored if i["is_impact_material"])
    n_financial = sum(1 for i in scored if i["is_financial_material"])
    n_doubly = sum(1 for i in scored if i["is_doubly_material"])

    print("\n" + "─" * 52)
    print(f"  Unternehmen : {args.company}")
    print(f"  Berichtsjahr: {args.year}")
    print("─" * 52)
    print(f"  IROs gesamt               : {len(scored)}")
    print(f"  Auswirkungswesentlich     : {n_impact}")
    print(f"  Finanziell wesentlich     : {n_financial}")
    print(f"  Doppelt wesentlich        : {n_doubly}")
    print("─" * 52)

    print("\nDoppelt wesentliche IROs:")
    for iro in scored:
        if iro["is_doubly_material"]:
            print(
                f"  {iro['iro_id']:8s} | "
                f"Auswirkung: {iro['impact_score']:.2f} | "
                f"Finanziell: {iro['financial_score']:.2f}"
            )

    # ── Visualisations ───────────────────────────────────────────────────────
    print("\nErstelle Wesentlichkeitsmatrix...")
    try:
        generate_matrix(scored, matrix_path)
    except OSError as e:
        print(f"[FEHLER] Matrix: {e}", file=sys.stderr)
        return 1

    print("Erstelle ESRS-Heatmap...")
    try:
        generate_heatmap(aggregates, heatmap_path)
    except OSError as e:
        print(f"[FEHLER] Heatmap: {e}", file=sys.stderr)
        return 1

    # ── PDF report ───────────────────────────────────────────────────────────
    print("Erstelle PDF-Bericht...")
    try:
        generate_report(
            scored_iros=scored,
            topic_aggregates=aggregates,
            company=args.company,
            year=args.year,
            matrix_path=matrix_path,
            heatmap_path=heatmap_path,
            output_path=report_path,
        )
    except OSError as e:
        print(f"[FEHLER] PDF: {e}", file=sys.stderr)
        return 1

    print(f"\nAlle Ausgaben gespeichert in: {os.path.abspath(output_dir)}/")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dma",
        description="CSRD/ESRS Doppelte Wesentlichkeitsanalyse — EFRAG-Methodik",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate-template
    p_gen = subparsers.add_parser(
        "generate-template",
        help="Excel-IRO-Template generieren",
    )
    p_gen.add_argument(
        "--output", "-o",
        default=os.path.join("data", "iro_template.xlsx"),
        help="Ausgabepfad für das Template (Standard: data/iro_template.xlsx)",
    )

    # run
    p_run = subparsers.add_parser(
        "run",
        help="Wesentlichkeitsanalyse durchführen und Outputs generieren",
    )
    p_run.add_argument(
        "--input", "-i",
        required=True,
        help="Pfad zur ausgefüllten Excel-Datei",
    )
    p_run.add_argument(
        "--company", "-c",
        required=True,
        help="Unternehmensname (erscheint im PDF-Bericht)",
    )
    p_run.add_argument(
        "--year", "-y",
        required=True,
        type=int,
        help="Berichtsjahr (z. B. 2025)",
    )
    p_run.add_argument(
        "--output-dir", "-d",
        default="outputs",
        help="Ausgabeverzeichnis (Standard: outputs/)",
    )

    args = parser.parse_args()

    if args.command == "generate-template":
        sys.exit(cmd_generate_template(args))
    elif args.command == "run":
        sys.exit(cmd_run(args))


if __name__ == "__main__":
    main()
