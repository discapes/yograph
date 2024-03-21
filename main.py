from bs4 import BeautifulSoup, Tag
from httpx import AsyncClient
import re
import asyncio
import matplotlib.pyplot as plt
import numpy as np

client = AsyncClient()

categories = ["L", "E", "M", "C", "B", "A", "Pääsispä edes läpi...", "En uskalla edes arvata tai toivoa mitään."]
#title, link_regex, root_url = "Matematiikan YLE-kysely", r"\d{4} (kevät|syksy): pitkä oppimäärä", "https://yle.fi/aihe/a/20-148033"
#title, link_regex, root_url = "Fysiikan YLE-kysely", r"\d{4} (kevät|syksy): fysiikka", "https://yle.fi/aihe/a/20-147727"
#title, link_regex, root_url = "Kirjoitustaidon YLE-kysely", r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, kirjoitustaidon koe", "https://yle.fi/aihe/a/20-147164"
# doesnt work title, link_regex, root_url = "Lukutaidon YLE-kysely", r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, lukutaidon koe", "https://yle.fi/aihe/a/20-147164"


def survey(results, category_names):
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
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    fig.suptitle(title)
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, labels=[f"{v:.0%}" for v in widths], label_type='center', color=text_color)
    ax.legend(ncols=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax

async def parse_exam(name: str, url: str):
    page = await client.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        elem = [x for x in soup.find_all(attrs={"data-ydd-tehtava-exam-id": True}) if x.parent.name != "details" and not x.find(string=re.compile("harjoittelukoe"))][-1]
        assert isinstance(elem, Tag)
        exam_id = elem["data-ydd-tehtava-exam-id"][3:]
    except: 
        elem = [x for x in soup.find_all(attrs={"data-exam-id": True}) if x.parent.name != "details" and not x.find(string=re.compile("harjoittelukoe"))][-1]
        assert isinstance(elem, Tag)
        exam_id = elem["data-exam-id"][3:]
    print(exam_id)
    exam = await client.get("https://tehtava.api.yle.fi/v1/public/exams.json", params={ "uuid": exam_id })
    question = next(x for x in exam.json()["data"][0]["questions"] if x["options"][0]["text"] == "L" and "YTL" not in x["main_text"])
    answers = await client.get("https://tehtava.api.yle.fi/v1/public/polls", params={ "question_uuids": question["uuid"] })
    values = [x["count_option"] for x in sorted(answers.json()["data"], key=lambda obj: int(obj["option_id"]))]
    val_perc = [v / sum(values) for v in values]
    return (name, val_perc)

async def main():
    listing = await client.get(root_url)
    soup = BeautifulSoup(listing.text, "html.parser")
    links = soup.find_all("a", string=re.compile(link_regex))
    exams = [(l.text.split(":")[0], l["href"]) for l in links if int(l.text[:4]) >= 2021]
    coro_results = await asyncio.gather(*[parse_exam(name, url) for name, url in exams], return_exceptions=True)
    exams_results = [x for x in coro_results if not isinstance(x, Exception)]
    #exams_results = [await parse_exam("2021 kevät", "https://yle.fi/aihe/artikkeli/2021/02/15/2021-kevat-matematiikka-pitka-oppimaara")]
    res = {k: v for k, v in exams_results}
    survey(res, categories)
    plt.show()
    
asyncio.run(main())
# 2021 kevät is good

