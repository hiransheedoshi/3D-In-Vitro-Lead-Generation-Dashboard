import re
import requests
import pandas as pd

# -------------------- PubMed (no API key needed) --------------------
def pubmed_recent_authors(query, max_results=30):
    """
    Fetch recent PubMed papers matching query and return author-centric rows.
    Example query: "Drug-Induced Liver Injury[Title] AND 3D cell culture"
    """
    try:
        esearch = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db":"pubmed","term":query,"retmode":"json","sort":"pub+date","retmax":max_results},
            timeout=20
        ).json()
        ids = esearch.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return pd.DataFrame([])

        esummary = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db":"pubmed","id":",".join(ids),"retmode":"json"},
            timeout=20
        ).json()

        rows = []
        for pid in ids:
            rec = esummary.get("result", {}).get(pid, {})
            title = rec.get("title", "")
            pubdate = rec.get("pubdate", "")
            year_match = re.search(r"(\d{4})", pubdate or "")
            year = int(year_match.group(1)) if year_match else 0
            authors = rec.get("authors", []) or []
            for a in authors[:5]:
                name = (a.get("name") or "").strip()
                if not name:
                    continue
                rows.append({
                    "Name": name,
                    "Title": "Author / Researcher",
                    "Company": "",
                    "Person location": "",
                    "Company HQ": "",
                    "Email": "",
                    "LinkedIn": "",
                    "Last paper title": title,
                    "Last paper year": year,
                    "Conference": "",
                    "Funding round": "",
                    "NAMs signal": "",
                    "Notes": "PubMed author",
                    "Action": "Research outreach"
                })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame([])

# -------------------- NIH RePORTER (no key) --------------------
def nih_reporter_grants(keyword, max_results=30):
    """
    Fetch NIH grants matching keyword. Useful for academic budget signal.
    """
    try:
        body = {
            "criteria": {"term": keyword},
            "include_fields": ["project_title","principal_investigators","org_city","org_state","org_name","project_start_date"],
            "offset": 0,
            "limit": max_results
        }
        resp = requests.post("https://api.reporter.nih.gov/v2/projects/search", json=body, timeout=30)
        data = resp.json().get("results", [])
        rows = []
        for r in data:
            pis = r.get("principal_investigators", []) or []
            name = pis[0].get("full_name", "") if pis else ""
            rows.append({
                "Name": name,
                "Title": "PI / Professor",
                "Company": r.get("org_name", ""),
                "Person location": f"{r.get('org_city','')}, {r.get('org_state','')}",
                "Company HQ": f"{r.get('org_city','')}, {r.get('org_state','')}",
                "Email": "",
                "LinkedIn": "",
                "Last paper title": r.get("project_title", ""),
                "Last paper year": "",
                "Conference": "",
                "Funding round": "Grant",
                "NAMs signal": "",
                "Notes": "NIH grant holder",
                "Action": "Grant-funded outreach"
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame([])
