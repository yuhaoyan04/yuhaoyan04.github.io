"""Build the static execution-audit chart from the frozen quant experiment."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES = (
    ROOT.parent
    / "ai-quant-research"
    / "reports"
    / "experiments"
    / "rf_daily_retry_execution_v1"
    / "tables"
)
OUTPUT = ROOT / "assets" / "images" / "quant-execution-audit.svg"

WIDTH, HEIGHT = 720, 360
LEFT, RIGHT, TOP, BOTTOM = 58, 22, 62, 48
PLOT_W = WIDTH - LEFT - RIGHT
PLOT_H = HEIGHT - TOP - BOTTOM


def load_series(filename: str) -> list[tuple[date, float]]:
    with (TABLES / filename).open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        return [(date.fromisoformat(row["trade_date"]), float(row["nav"])) for row in rows]


ideal = load_series("rf_daily_ideal_daily__historical_oos_v1.csv")
constrained = load_series("rf_daily_retry_daily__historical_oos_v1.csv")
if [item[0] for item in ideal] != [item[0] for item in constrained]:
    raise ValueError("Execution series have different date axes")

dates = [item[0] for item in ideal]
all_values = [item[1] for item in ideal] + [item[1] for item in constrained]
y_min = 0.5
y_max = max(3.5, max(all_values) * 1.04)


def x(index: int) -> float:
    return LEFT + index * PLOT_W / (len(dates) - 1)


def y(value: float) -> float:
    return TOP + (y_max - value) * PLOT_H / (y_max - y_min)


def series_path(series: list[tuple[date, float]]) -> str:
    points = [f"{x(i):.2f},{y(value):.2f}" for i, (_, value) in enumerate(series)]
    return "M " + " L ".join(points)


year_ticks: list[tuple[int, int]] = []
seen: set[int] = set()
for index, day in enumerate(dates):
    if day.year not in seen:
        seen.add(day.year)
        year_ticks.append((index, day.year))

grid = []
for value in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
    if value <= y_max:
        py = y(value)
        grid.append(f'<line x1="{LEFT}" y1="{py:.2f}" x2="{WIDTH-RIGHT}" y2="{py:.2f}" class="grid" />')
        grid.append(f'<text x="{LEFT-10}" y="{py+4:.2f}" class="axis" text-anchor="end">{value:.1f}</text>')

x_labels = [
    f'<text x="{x(index):.2f}" y="{HEIGHT-20}" class="axis" text-anchor="middle">{year}</text>'
    for index, year in year_ticks
]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">RF historical OOS execution audit</title>
  <desc id="desc">Comparison of ideal full-fill and constrained daily-retry net asset values from 2021 to 2026.</desc>
  <style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; fill: #222; }}
    .title {{ font-size: 17px; font-weight: 600; }}
    .subtitle, .axis, .legend {{ fill: #666; font-size: 12px; }}
    .grid {{ stroke: #e7e7e7; stroke-width: 1; }}
    .ideal {{ fill: none; stroke: #9a9a9a; stroke-width: 2; }}
    .constrained {{ fill: none; stroke: #245b93; stroke-width: 2.5; }}
  </style>
  <rect width="100%" height="100%" fill="#fff" />
  <text x="{LEFT}" y="25" class="title">RF historical OOS execution audit</text>
  <text x="{LEFT}" y="44" class="subtitle">Non-overlapping daily NAV · 20bp transaction cost</text>
  {''.join(grid)}
  <line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{HEIGHT-BOTTOM}" stroke="#bbb" />
  <line x1="{LEFT}" y1="{HEIGHT-BOTTOM}" x2="{WIDTH-RIGHT}" y2="{HEIGHT-BOTTOM}" stroke="#bbb" />
  {''.join(x_labels)}
  <path d="{series_path(ideal)}" class="ideal" fill="none" stroke="#9a9a9a" stroke-width="2" />
  <path d="{series_path(constrained)}" class="constrained" fill="none" stroke="#245b93" stroke-width="2.5" />
  <line x1="470" y1="24" x2="492" y2="24" class="ideal" stroke="#9a9a9a" stroke-width="2" />
  <text x="500" y="28" class="legend">Ideal full-fill</text>
  <line x1="590" y1="24" x2="612" y2="24" class="constrained" stroke="#245b93" stroke-width="2.5" />
  <text x="620" y="28" class="legend">Daily retry</text>
</svg>
'''

OUTPUT.write_text(svg, encoding="utf-8")
print(OUTPUT)
