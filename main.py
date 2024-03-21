from typing import Any, NamedTuple, cast
from bs4 import BeautifulSoup, Tag
import hishel
import re
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import csv

from display import DataSource, draw_line_chart
from lib import Subject, YleDatum
from yle import scrape_yle, scrape_yle_subject
from ytl import scrape_ytl

subjects = [
    Subject("Matematiikka (pitkä)", "Matematiikka, pitkä oppimäärä", 120, r"\d{4} (kevät|syksy): pitkä oppimäärä", "https://yle.fi/aihe/a/20-148033"),
    Subject("Fysiikka", "Fysiikka", 120, r"\d{4} (kevät|syksy): fysiikka", "https://yle.fi/aihe/a/20-147727"),
    Subject("Kirjoitustaito (suomi)", "Äidinkieli ja kirjallisuus, suomi", 120, r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, kirjoitustaidon koe", "https://yle.fi/aihe/a/20-147164"),
    Subject("Lukutaito (suomi)", "Äidinkieli ja kirjallisuus, suomi", 120, r"\d{4} (kevät|syksy): äidinkieli ja kirjallisuus, lukutaidon koe", "https://yle.fi/aihe/a/20-147164"),
    Subject("Kemia", "Kemia", 120, r"\d{4} (kevät|syksy): kemia", "https://yle.fi/aihe/a/20-147601"),
    Subject("Englanti (pitkä)", "Englanti, pitkä oppimäärä", 299, r"\d{4} (kevät|syksy): pitkä oppimäärä", "https://yle.fi/aihe/a/20-148186"),
    Subject("Maantiede", "Maantiede", 120, r"\d{4} (kevät|syksy): maantiede", "https://yle.fi/aihe/a/20-147518"),
    Subject("Biologia", "Biologia", 120, r"\d{4} (kevät|syksy): biologia", "https://yle.fi/aihe/a/20-147916")
]

async def main():
    yle_results = await scrape_yle(subjects)
    ytl_results = await scrape_ytl(subjects)
    
    #output_csv(yle_results, file_name="yle.csv")
    #output_csv(ytl_results, file_name="ytl.csv")
    
    #draw_line_chart([x for x in yle_results if x.question == "grade"], "semester", "answers", "subject", "YLEn kysely")
    #draw_line_chart([x for x in yle_results if x.question == "grade" and x.subject == "Englanti (pitkä)"], "semester", "answers", "option", "YLEn kysely - Englanti (pitkä)", percent_cats=True)
  #  draw_line_chart([x for x in yle_results if x.question == "grade" and x.subject == "Matematiikka (pitkä)"], "semester", "answers", "option", "YLEn kysely - Matematiikka (pitkä)", percent_cats=True)
    #draw_line_chart([x for x in ytl_results if x.grade == "L"], "semester", "value", "subject", "YTL pisterajat - Laudatur")
    #draw_line_chart([x for x in ytl_results if x.subject == "Matematiikka (pitkä)"], "semester", "value", "grade", "YTL pisterajat - Matematiikka (pitkä)")
    ds1 = DataSource([x for x in yle_results if x.option in ["L", "E", "En uskalla edes arvata"] and x.subject == "Matematiikka (pitkä)"], "answers", "option", True)
    ds2 = DataSource([x for x in ytl_results if x.grade == "L" and x.subject == "Matematiikka (pitkä)"], "value", None, False)
    draw_line_chart(ds1, ds2, "semester", "YLEn kysely - Matematiikka (pitkä)")
    
    #output_csv(yle_results, file_name="yle.csv")
    #point_results = await fetch_ytl_points()
    #print(point_results)
    #survey_results = await fetch_yle_survey_results()
   # print(survey_results)
   # await line_graph({k: v[0] for k, v in survey_results.items()}, {k: v[0] for k, v in point_results.items()})
   # survey(survey_results, categories, point_results)
    plt.show()
    
def output_csv(rows, file_name="output.csv"):
    field_names = rows[0]._fields
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(field_names)  # Write header row
        for row in rows:
            writer.writerow(row)
        
asyncio.run(main())
# 2021 kevät is good

