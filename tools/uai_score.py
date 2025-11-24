"""Utility Assessment Index (UAI) calculator.

Run from repo root:

    python tools/uai_score.py --clarity 4 --completeness 3 --actionability 5 --safety 4 --verification 3 --efficiency 4

This prints per-dimension scores, the computed UAI (rounded to 2 decimals),
and calls out any dimensions that fall at or below 3 so you can tighten the draft
before publishing.
"""

import argparse
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Scores:
    clarity: float
    completeness: float
    actionability: float
    safety: float
    verification: float
    efficiency: float

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Scores":
        return cls(
            clarity=args.clarity,
            completeness=args.completeness,
            actionability=args.actionability,
            safety=args.safety,
            verification=args.verification,
            efficiency=args.efficiency,
        )

    def average(self) -> float:
        total = (
            self.clarity
            + self.completeness
            + self.actionability
            + self.safety
            + self.verification
            + self.efficiency
        )
        return round(total / 6, 2)

    def weak_dimensions(self, threshold: float = 3.0) -> List[str]:
        dims: Dict[str, float] = {
            "Clarity": self.clarity,
            "Completeness": self.completeness,
            "Actionability": self.actionability,
            "Safety & compliance": self.safety,
            "Verification": self.verification,
            "Efficiency": self.efficiency,
        }
        return [name for name, score in dims.items() if score <= threshold]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute the Utility Assessment Index (UAI)")
    parser.add_argument("--clarity", type=float, required=True, help="0–5")
    parser.add_argument("--completeness", type=float, required=True, help="0–5")
    parser.add_argument("--actionability", type=float, required=True, help="0–5")
    parser.add_argument("--safety", type=float, required=True, help="0–5 (safety & compliance)")
    parser.add_argument("--verification", type=float, required=True, help="0–5")
    parser.add_argument("--efficiency", type=float, required=True, help="0–5")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    scores = Scores.from_args(args)
    uai = scores.average()
    weak = scores.weak_dimensions()

    print("Utility Assessment")
    print(f"- Clarity: {scores.clarity}")
    print(f"- Completeness: {scores.completeness}")
    print(f"- Actionability: {scores.actionability}")
    print(f"- Safety & compliance: {scores.safety}")
    print(f"- Verification: {scores.verification}")
    print(f"- Efficiency: {scores.efficiency}")
    print(f"\nUAI: {uai} / 5")

    if weak:
        print("Weak dimensions (<=3): " + ", ".join(weak))
    else:
        print("No weak dimensions flagged (all >3).")


if __name__ == "__main__":
    main()
