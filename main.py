import asyncio
import csv
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

from dashboard import build_dashboard_payload, save_dashboard_html
from lib import Subject
from ytl import scrape_ytl

SUBJECTS = [
    Subject("Matematiikka (pitkä)", "Matematiikka, pitkä oppimäärä", 120),
    Subject("Fysiikka", "Fysiikka", 120),
    Subject("Kirjoitustaito (suomi)", "Äidinkieli ja kirjallisuus, suomi", 120),
    Subject("Lukutaito (suomi)", "Äidinkieli ja kirjallisuus, suomi", 120),
    Subject("Kemia", "Kemia", 120),
    Subject("Englanti (pitkä)", "Englanti, pitkä oppimäärä", 299),
    Subject("Maantiede", "Maantiede", 120),
    Subject("Biologia", "Biologia", 120),
]


async def main(
    *,
    subjects: list[Subject] | None = None,
    output_path: str | Path = "dashboard.html",
) -> tuple[Path, list]:
    subjects = SUBJECTS if subjects is None else subjects
    ytl_results = await scrape_ytl(subjects)
    payload = build_dashboard_payload(subjects, ytl_results)
    generated_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    path = save_dashboard_html(output_path, payload, generated_at)
    return path, ytl_results


def output_csv(rows, file_name: str = "output.csv") -> None:
    if not rows:
        raise ValueError("rows must not be empty")

    field_names = rows[0]._fields
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(field_names)
        for row in rows:
            writer.writerow(row)


def run() -> None:
    path, _ = asyncio.run(main())
    print(f"Dashboard written to {path.resolve()}")
    webbrowser.open(path.resolve().as_uri())


if __name__ == "__main__":
    run()
