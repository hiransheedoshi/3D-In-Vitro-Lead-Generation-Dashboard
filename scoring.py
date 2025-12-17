import re
from datetime import datetime

HUBS = ["boston","cambridge","bay area","basel","oxford","cambridge uk","uk golden triangle","golden triangle","san francisco"]

def score_row(row):
    title = str(row.get("Title","")).lower()
    funding = str(row.get("Funding round","")).lower()
    nams = str(row.get("NAMs signal","")).strip().lower()
    person_loc = str(row.get("Person location","")).lower()
    hq = str(row.get("Company HQ","")).lower()
    paper_title = str(row.get("Last paper title","")).lower()
    try:
        paper_year = int(str(row.get("Last paper year","0")).strip())
    except:
        paper_year = 0

    score = 0
    # Role fit (+30)
    if re.search(r"toxicolog|safety|hepatic|3d", title):
        score += 30
    # Funding (+20)
    if re.search(r"series a|series b", funding):
        score += 20
    # Technographic (+15 if explicit, +10 if implied in paper title)
    if nams in ["yes","true","y"]:
        score += 15
    elif re.search(r"nam|in vitro|organoid|organ-on-chip|3d cell|spheroid", paper_title):
        score += 10
    # Location hub (+10)
    if any(h in (person_loc + " " + hq) for h in HUBS):
        score += 10
    # Scientific intent: DILI in last 2 years (+40)
    this_year = datetime.now().year
    if paper_year >= this_year - 2 and re.search(r"drug\-induced liver injury|dili", paper_title):
        score += 40

    return min(score, 100)
