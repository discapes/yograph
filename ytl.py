import asyncio
import re
from bs4 import BeautifulSoup

from lib import Subject, YtlDatum, get

letters = ["L", "E", "M", "C", "B", "A"]

async def scrape_ytl_semester(subjects: list[Subject], semester: str, url: str):
    page = await get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    results = []
    
    for subject in subjects: 
        subject_elem = soup.find("td", string=subject.ytl_name)
        assert subject_elem is not None
        row = subject_elem.parent
        assert row is not None
        cells = list(row.children)[1:9]
        
        for cell, letter in zip(cells, letters):
            results.append(YtlDatum(semester, subject.name, letter, int(cell.text) / subject.max_points))
        
    return results
    
async def scrape_ytl(subjects: list[Subject]):
    point_root = await get("https://www.ylioppilastutkinto.fi/fi/tutkinnon-suorittaminen/pisterajat")
    soup = BeautifulSoup(point_root.text, "html.parser")
    links = soup("a", string=re.compile(r"Pisterajat (kevät|syksy) \d{4}"), class_="main-menu__link")
    link_pairs = [(" ".join(l.text.split()[::-1][:2]), "https://www.ylioppilastutkinto.fi" + l["href"]) for l in links if int(l.text[-4:]) >= 2021]
    
    ytl_results_2d = await asyncio.gather(*[scrape_ytl_semester(subjects, semester, url) for semester, url in link_pairs], return_exceptions=False)
    ytl_results: list[YtlDatum] = [x for res in ytl_results_2d for x in res]
    return ytl_results