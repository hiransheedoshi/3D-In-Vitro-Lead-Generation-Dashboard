3D In‑Vitro Lead Generation Dashboard
📌 Overview
A Streamlit‑based dashboard that identifies, enriches, and ranks biotech leads for 3D in‑vitro models. It integrates Apollo/Clay exports, PubMed authors, and NIH grants, applying weighted scoring to prioritize high‑probability contacts.

🚀 Features
Upload CSV or Excel files from Apollo/Clay

Fetch PubMed authors by keyword queries

Retrieve NIH grant holders by research area

Seed demo dataset for quick testing

Weighted scoring engine (0–100) based on:

Role fit (+30)

Company funding (+20)

Technographics/NAMs (+15/+10)

Location hubs (+10)

Scientific intent (+40)

Dynamic filters: keyword, title, location, score threshold

Ranked leads table with clickable LinkedIn profiles and verified emails

Export filtered leads to CSV/Excel

🛠 Tech Stack
Frontend: Streamlit

Backend/Data: Python, Pandas

File Support: CSV & XLSX

Optional APIs: Apollo.io, PubMed, NIH RePORTER

📤 How to Run
Clone the repository:

bash
git clone https://github.com/yourusername/lead-generation-dashboard.git
cd lead-generation-dashboard
Install dependencies:

bash
pip install -r requirements.txt
Run the app:

bash
streamlit run app.py
Open the local URL (e.g., http://10.252.19.169:8508/) in your browser.

📊 Example Output
Director of Safety Assessment at a Series B biotech in Cambridge, MA who published on liver toxicity → Score: 95/100

Junior Scientist at a non‑funded startup → Score: 15/100

✨ Credits
Developed by Hiranshee Doshi  
Focused on biotech business development workflows, lead generation, and compliance.
