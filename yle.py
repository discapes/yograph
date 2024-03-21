
import asyncio
import re
from bs4 import BeautifulSoup, Tag

from lib import Subject, YleDatum, get

async def scrape_yle(subjects: list[Subject]):
    yle_results_2d = await asyncio.gather(*[scrape_yle_subject(sub) for sub in subjects])
    yle_results: list[YleDatum] = [x for res in yle_results_2d for x in res]
    return yle_results

async def scrape_yle_subject(subject: Subject):
    listing = await get(subject.yle_url)
    soup = BeautifulSoup(listing.text, "html.parser")
    links = soup.find_all("a", string=re.compile(subject.link_regex))
    exams = [(l.text.split(":")[0], l["href"]) for l in links if int(l.text[:4]) >= 2021]
    
    futures = [scrape_yle_semester_subject(semester, subject.name, url) for semester, url in exams]
    future_results = await asyncio.gather(*futures, return_exceptions=False)
    results = [x for res in future_results if not isinstance(res, Exception) for x in res]
    return results

async def scrape_yle_semester_subject(semester: str, subject: str, url: str):
    page = await get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        elem = [x for x in soup.find_all(attrs={"data-ydd-tehtava-exam-id": True}) if x.parent.name != "details" and not x.find(string=re.compile("harjoittelukoe"))][-1]
        assert isinstance(elem, Tag)
        exam_id = elem["data-ydd-tehtava-exam-id"][3:]
    except: 
        try:
            elem = [x for x in soup.find_all(attrs={"data-exam-id": True}) if x.parent.name != "details" and not x.find(string=re.compile("harjoittelukoe"))][-1]
            assert isinstance(elem, Tag)
            exam_id = elem["data-exam-id"][3:]
        except:
            print(f"Survey not found for {semester} {subject}")
            return []
    
    exam = await get("https://tehtava.api.yle.fi/v1/public/exams.json", params={ "uuid": exam_id })
    questions = exam.json()["data"][0]["questions"]
    
    grade_question = next((q for q in questions if len(q["options"]) and q["options"][0]["text"] == "L" and "YTL" not in q["main_text"]), None)
    difficulty_question = next((q for q in questions if len(q["options"]) and q["options"][0]["text"] == "Helppo"), None)
    question_uuids = ",".join([x["uuid"] for x in [grade_question, difficulty_question] if x is not None])
    if grade_question is None: print(f"Grade question not found for {semester} {subject}")
    if difficulty_question is None: print(f"Difficulty question not found for {semester} {subject}")
    
    answers = await get("https://tehtava.api.yle.fi/v1/public/polls", 
                        params={ "question_uuids": question_uuids  })
    
    data = []
    for answer in answers.json()["data"]:
        question = next(q for q in questions if q["uuid"] == answer["question_uuid"])
        option = next(o for o in question["options"] if o["id"] == int(answer["option_id"]))
        value = answer["count_option"]
        if question == grade_question:
            # because the one with "En uskalla.." changed in 2021
            data.append(YleDatum(semester, subject, "grade", option["text"][:len("En uskalla edes arvata")], value))
        elif question == difficulty_question:
            data.append(YleDatum(semester, subject, "difficulty", option["text"], value))
    
    return data

#data = asyncio.run(scrape_yle_semester_subject("a", "a", "https://yle.fi/aihe/a/20-10005224"))
#print(data)