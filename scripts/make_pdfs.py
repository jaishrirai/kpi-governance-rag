"""
Builds the 5 policy PDFs (POL-01 to POL-05) with reportlab.
PDFs have no YAML header, so their metadata lives only in data/corpus_manifest.csv.
Run from the repo root:  python scripts/make_pdfs.py
"""
import csv
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

MANIFEST = {r["doc_id"]: r for r in csv.DictReader(open("data/corpus_manifest.csv", encoding="utf-8"))}
S = getSampleStyleSheet()

# One-line definitions for the glossary. Owner and status come from the manifest, not from here.
SHORT_DEF = {
    "KPI-001": "Sales after discounts, returns and refunds, excluding sales tax.",
    "KPI-002": "(Net Revenue - COGS) / Net Revenue.",
    "KPI-003": "Average days to collect payment on B2B invoices.",
    "KPI-004": "Net Revenue / completed orders.",
    "KPI-005": "App and web sessions with an order / qualifying sessions.",
    "KPI-006": "Identified customers with a purchase in the last 30 days.",
    "KPI-007": "Start-base customers with no purchase for 180 days.",
    "KPI-008": "Units sold / completed orders.",
    "KPI-009": "Store transactions / door-counter footfall.",
    "KPI-010": "12-month net revenue kept from an existing customer cohort.",
    "KPI-011": "Annual gross margin per customer x expected lifetime.",
    "KPI-012": "New customers buying again within 90 days.",
    "KPI-013": "% promoters (9-10) minus % detractors (0-6).",
    "KPI-014": "Acquisition spend / new customers.",
    "KPI-015": "Attributed net revenue / paid media spend.",
    "KPI-016": "12-month COGS / average inventory at cost.",
    "KPI-017": "Active SKU-locations with zero sellable stock at 06:00.",
    "KPI-018": "Orders delivered or ready by the promised date.",
    "KPI-019": "Returned value / gross sales, by month of sale.",
    "KPI-020": "App users with a session in the last 30 days (no purchase needed).",
}


def cell(text):
    # Wrapping text inside table cells needs a Paragraph, not a plain string
    return Paragraph(text, S["BodyText"])


def table(rows, widths):
    t = Table([[cell(c) for c in r] for r in rows], colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def glossary_rows():
    rows = [["ID", "KPI", "Owner", "Status", "Short definition"]]
    for doc_id, d in SHORT_DEF.items():
        m = MANIFEST[doc_id]
        rows.append([doc_id, m["title"], m["owner"], m["certification"], d])
    return rows


CONTENT = {
    "POL-01": [
        ("h", "1. Purpose"), ("p", "This policy sets how Kestrel Retail Group defines, owns and certifies the data and KPIs used for decisions."),
        ("h", "2. Scope"), ("p", "All KPIs, dashboards and source tables listed in the data catalog, in every channel (stores, app and web)."),
        ("h", "3. Roles"), ("p", "The KPI Council, chaired by the Head of Data Governance, approves certification and major changes. Each KPI and data asset has one accountable owner, a domain head named in the data catalog. Data stewards check definitions and data quality."),
        ("h", "4. Certification levels"), ("p", "<b>Certified:</b> approved by the KPI Council and safe for board reporting. <b>Provisional:</b> in use but not yet approved; must be labelled on dashboards and must not be used in board packs. <b>Deprecated:</b> replaced by a newer version; must not be used for any reporting."),
        ("h", "5. Principles"), ("p", "There is one certified definition per KPI. Informal definitions in team notes, slides or FAQs have no standing; when they conflict with a Certified KPI definition, the Certified definition applies."),
        ("h", "6. Compliance"), ("p", "Breaches are reported to the Head of Data Governance. Procedures supporting this policy are SOP-01 to SOP-08."),
    ],
    "POL-02": [
        ("h", "1. Purpose"), ("p", "This policy sets safe use of AI tools, including chat assistants and internal RAG assistants, at Kestrel."),
        ("h", "2. Approved tools"), ("p", "Only tools on the approved list published by the Head of Data Governance may be used with company data."),
        ("h", "3. Data rules"), ("p", "Public and Internal data may be used with approved tools. Confidential and Restricted data (see POL-03) must never be entered into public AI tools. Customer-level data must not leave approved systems."),
        ("h", "4. Answers about KPIs"), ("p", "An AI assistant that answers KPI questions must cite the governed source document for every answer, must state the certification level of the KPI, and must say it does not know when the answer is not in the governed documents."),
        ("h", "5. Human review"), ("p", "AI output used in board packs or external communication must be checked by a person, who stays accountable for it."),
    ],
    "POL-03": [
        ("h", "1. Purpose"), ("p", "This standard defines the four data classification levels and how each must be handled."),
        ("h", "2. Classification levels"),
        ("table", [["Level", "Description", "Examples", "Handling"],
                   ["Public", "Approved for release outside Kestrel.", "Published store locations, press releases.", "No restrictions."],
                   ["Internal", "For employees only; low harm if disclosed.", "Dashboards with aggregated KPIs, SOPs.", "Line manager approval for access."],
                   ["Confidential", "Harm to customers or Kestrel if disclosed.", "customers table, invoices, unreleased results.", "Data owner approval; no public AI tools."],
                   ["Restricted", "Serious harm or legal breach if disclosed.", "Payment data, staff health records.", "Head of Data Governance approval; 90-day access."]],
         [70, 130, 140, 130]),
        ("h", "3. Default level"), ("p", "Any data asset without a classification is treated as Confidential until it is classified."),
    ],
    "POL-04": [
        ("p", "Official list of KPIs. The full definition of each KPI is in its own KPI document. Deprecated versions are not listed; Customer Churn Rate v1 (KPI-007-V1) was replaced by KPI-007 on 2026-04-01."),
        ("table", glossary_rows(), [52, 95, 100, 62, 165]),
    ],
    "POL-05": [
        ("p", "Meeting date: 2026-07-10. Chair: Head of Data Governance. Attendees: Heads of Finance, Sales, Customer, Marketing and Supply Chain Analytics; Head of Digital Product."),
        ("h", "Decisions"),
        ("p", "1. Customer Churn Rate v2 (KPI-007) is confirmed as live since 2026-04-01. v1 has been removed from all dashboards."),
        ("p", "2. Active User (app 30-day) (KPI-020) is approved as Provisional, version 0.8. The Council asked for duplicate user ids to be fixed before certification."),
        ("p", "3. Basket Size (KPI-008) certification is postponed to Q4 2026 because of the multi-pack unit counting issue."),
        ("p", "4. Marketing ROI (ROAS) (KPI-015) stays Provisional until the attribution review closes."),
        ("h", "Actions"),
        ("table", [["Action", "Owner", "Due"],
                   ["Fix multi-pack unit counts in store tills", "Head of Sales Analytics", "2026-09-30"],
                   ["Remove duplicate app user ids", "Head of Digital Product", "2026-10-31"],
                   ["Close attribution review for ROAS", "Head of Marketing Analytics", "2026-11-30"]],
         [220, 150, 80]),
    ],
}


def build(doc_id):
    m = MANIFEST[doc_id]
    story = [Paragraph(f"Kestrel Retail Group: {m['title']}", S["Title"]),
             Paragraph(f"{doc_id} | Version {m['version']} | Effective {m['effective_date']} | Owner: {m['owner']}", S["Italic"]),
             Spacer(1, 12)]
    for kind, *args in CONTENT[doc_id]:
        if kind == "h":
            story.append(Paragraph(args[0], S["Heading2"]))
        elif kind == "p":
            story.append(Paragraph(args[0], S["BodyText"]))
        else:
            story += [table(*args), Spacer(1, 8)]
    SimpleDocTemplate(m["source_path"], pagesize=A4).build(story)
    print("wrote", m["source_path"])


if __name__ == "__main__":
    for doc_id in CONTENT:
        build(doc_id)
