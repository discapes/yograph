from typing import Any, cast
from bs4 import BeautifulSoup, Tag
import hishel
import re
import asyncio
import matplotlib.pyplot as plt
import numpy as np

# caching so we can develop faster and wont strain APIs
client = hishel.AsyncCacheClient()
def get(*args, **kwargs):
    return client.get(*args, **kwargs, extensions={"force_cache": True})

categories = ["L", "E", "M", "C", "B", "A", "Pääsispä edes läpi..."]
#categories = ["Helppo", "Juuri sopiva", "Melko vaativa", "Ihan liian vaikea"]
letters = ["L", "E", "M", "C", "B", "A"]
year = 2021


title, ytl_name, max_points, link_regex, root_url = "Pitkä matematiikka YLE vastaukset ja YTL pisterajat", "Matematiikka, pitkä oppimäärä", 120, r"\d{4} (kevät|syksy): pitkä oppimäärä", "https://yle.fi/aihe/a/20-148033"
#title, ytl_name, link_regex, root_url = "Fysiikan YLE-kysely", "Fysiikka", r"\d{4} (kevät|syksy): fysiikka", "https://yle.fi/aihe/a/20-147727"
#title, link_regex, root_url = "Kirjoitustaidon YLE-kysely", r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, kirjoitustaidon koe", "https://yle.fi/aihe/a/20-147164"
# doesnt work #title, link_regex, root_url = "Lukutaidon YLE-kysely", r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, lukutaidon koe", "https://yle.fi/aihe/a/20-147164"
#title, link_regex, root_url = "Biologian YLE-kysely", r"\d{4} (kevät|syksy): biologia", "https://yle.fi/aihe/a/20-147916"
#title, link_regex, root_url = "Maantieteen YLE-kysely", r"\d{4} (kevät|syksy): maantiede", "https://yle.fi/aihe/a/20-147518"
#title, ytl_name, link_regex, max_points, root_url = "Kemian YLE-kysely", "Kemia", r"\d{4} (kevät|syksy): kemia", 120, "https://yle.fi/aihe/a/20-147601"
#title, ytl_name, max_points, link_regex, root_url = "Kirjoitustaidon YLE-kysely", "Äidinkieli ja kirjallisuus, suomi", 120, r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, kirjoitustaidon koe", "https://yle.fi/aihe/a/20-147164"
#title, ytl_name, max_points, link_regex, root_url = "Lukutaidon YLE-kysely", "Äidinkieli ja kirjallisuus, suomi", 120, r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, lukutaidon koe", "https://yle.fi/aihe/a/20-147164"
#title, ytl_name, max_points, link_regex, root_url = "Englannin YLE-kysely", "Englanti, pitkä oppimäärä", 299, r"\d{4} (kevät|syksy): pitkä oppimäärä", "https://yle.fi/aihe/a/20-148186"



def survey(results, category_names, points):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.colormaps['RdYlGn'](
        np.linspace(0.15, 0.85, data.shape[1]))[::-1]

    fig, ax = plt.subplots(figsize=(9.2, 5))
    fig.suptitle(title)
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    #ax.set_xlim(0, np.sum(data, axis=1).max())
    ax.set_xlim(0, 1)
    ax.format_coord = lambda x, y: f"x: {round((1 - x) * max_points)}"

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, labels=[f"{v:.0%}" for v in widths], label_type='center', color=text_color)
        
        if i < len(letters):
            for j, rect in enumerate(rects):
                label = labels[j]
                if label in points:
                    score = points[label][i]
                    ax.text(1 - score / max_points, rect.get_y() - 0.15, letters[i],
                            ha='center', va='center', color='black', fontsize=10, fontweight='bold')
                    ax.plot(1 - score / max_points, rect.get_y(), '.', color="black")
            
    ax.legend(ncols=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax

async def parse_exam(name: str, url: str):
    page = await get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        elem = [x for x in soup.find_all(attrs={"data-ydd-tehtava-exam-id": True}) if x.parent.name != "details" and not x.find(string=re.compile("harjoittelukoe"))][-1]
        assert isinstance(elem, Tag)
        exam_id = elem["data-ydd-tehtava-exam-id"][3:]
    except: 
        elem = [x for x in soup.find_all(attrs={"data-exam-id": True}) if x.parent.name != "details" and not x.find(string=re.compile("harjoittelukoe"))][-1]
        assert isinstance(elem, Tag)
        exam_id = elem["data-exam-id"][3:]
   # print(exam_id)
    exam = await get("https://tehtava.api.yle.fi/v1/public/exams.json", params={ "uuid": exam_id })
    question = next(x for x in exam.json()["data"][0]["questions"] if x["options"][0]["text"] == categories[0] and "YTL" not in x["main_text"])
    answers = await get("https://tehtava.api.yle.fi/v1/public/polls", params={ "question_uuids": question["uuid"] })
    values = [x["count_option"] for x in sorted(answers.json()["data"], key=lambda obj: int(obj["option_id"]))]
    assert len(values) >= len(categories)
    values_first = values[:len(categories)]
    val_perc = [v / sum(values_first) for v in values_first]
    return (name, val_perc)

async def fetch_yle_survey_results():
    listing = await get(root_url)
    soup = BeautifulSoup(listing.text, "html.parser")
    links = soup.find_all("a", string=re.compile(link_regex))
    exams = [(l.text.split(":")[0], l["href"]) for l in links if int(l.text[:4]) >= year]
    survey_results = await asyncio.gather(*[parse_exam(name, url) for name, url in exams], return_exceptions=True)
    successful_results = [x for x in survey_results if not isinstance(x, Exception)]
    return {k: v for k, v in cast(list[tuple[str, Any]], successful_results)}

async def parse_ytl(name: str, url: str):
    page = await get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    subject_elem = soup.find("td", string=ytl_name)
    assert subject_elem is not None
    row = subject_elem.parent
    assert row is not None
    cells = list(row.children)[1:]
    values = [int(x.text) for x in cells][:8]
    return (name, values)
    
async def fetch_ytl_points():
    point_root = await get("https://www.ylioppilastutkinto.fi/fi/tutkinnon-suorittaminen/pisterajat")
    soup = BeautifulSoup(point_root.text, "html.parser")
    links = soup("a", string=re.compile(r"Pisterajat (kevät|syksy) \d{4}"), class_="main-menu__link")
    link_pairs = [(" ".join(l.text.split()[::-1][:2]), "https://www.ylioppilastutkinto.fi" + l["href"]) for l in links if int(l.text[-4:]) >= year]
    point_results = await asyncio.gather(*[parse_ytl(name, url) for name, url in link_pairs], return_exceptions=True)
    successful_results = [x for x in point_results if not isinstance(x, Exception)]
    return {k: v for k, v in cast(list[tuple[str, Any]], successful_results)}

async def main():
    #survey_results = [await parse_exam("2021 kevät", "https://yle.fi/aihe/artikkeli/2021/08/24/2021-syksy-biologia")]
    point_results = await fetch_ytl_points()
    print(point_results)
    survey_results = await fetch_yle_survey_results()
    print(survey_results)
    survey(survey_results, categories, point_results)
    plt.show()
    
asyncio.run(main())
# 2021 kevät is good

