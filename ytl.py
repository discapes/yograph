import asyncio
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from lib import Subject, YtlDatum, get

LETTERS = ["L", "E", "M", "C", "B", "A"]


def _extract_point_links(listing_html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(listing_html, "html.parser")
    links = soup("a", string=re.compile(r"Pisterajat (kevät|syksy) \d{4}"), class_="main-menu__link")

    return [
        (" ".join(link.text.split()[::-1][:2]), urljoin("https://www.ylioppilastutkinto.fi", link["href"]))
        for link in links
        if int(link.text[-4:]) >= 2021
    ]


def _parse_subject_row(row: BeautifulSoup, semester: str, subject: Subject) -> list[YtlDatum]:
    cells = row.find_all("td")
    if len(cells) < len(LETTERS) + 1:
        raise ValueError(f"Unexpected point table format for {semester} {subject.name}")

    results: list[YtlDatum] = []
    for cell, letter in zip(cells[1 : len(LETTERS) + 1], LETTERS, strict=True):
        results.append(YtlDatum(semester, subject.name, letter, int(cell.get_text(strip=True)) / subject.max_points))

    return results


async def scrape_ytl_semester(subjects: list[Subject], semester: str, url: str) -> list[YtlDatum]:
    page = await get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    results: list[YtlDatum] = []

    for subject in subjects:
        subject_elem = soup.find("td", string=subject.ytl_name)
        if subject_elem is None:
            raise ValueError(f"Subject not found in point table for {semester}: {subject.ytl_name}")
        row = subject_elem.parent
        if row is None:
            raise ValueError(f"Missing point table row for {semester}: {subject.ytl_name}")
        results.extend(_parse_subject_row(row, semester, subject))

    return results


async def scrape_ytl(subjects: list[Subject]) -> list[YtlDatum]:
    point_root = await get("https://www.ylioppilastutkinto.fi/fi/tutkinnon-suorittaminen/pisterajat")
    link_pairs = _extract_point_links(point_root.text)

    ytl_results_2d = await asyncio.gather(
        *[scrape_ytl_semester(subjects, semester, url) for semester, url in link_pairs],
        return_exceptions=False,
    )
    return [row for result in ytl_results_2d for row in result]
