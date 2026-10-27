"""Merge leads + enrichment and write the outreach workbook, CSVs and a Markdown summary.

Run from the repo root:  python3 research/build.py
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from openpyxl import Workbook  # noqa: E402
from openpyxl.formatting.rule import FormulaRule  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

import enrichment as E  # noqa: E402
import leads as L  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_XLSX = os.path.join(ROOT, "North_West_East_India_Specialty_Coffee_Leads.xlsx")
CSV_DIR = os.path.join(ROOT, "csv")

REGION_ORDER = [L.WEST, L.CENTRAL, L.NORTH, L.EAST, L.NE]
STATE_ORDER = [
    "Maharashtra", "Gujarat", "Goa", "Madhya Pradesh", "Chhattisgarh", "Rajasthan", "Delhi", "Delhi NCR",
    "Delhi NCR (TBC)", "Haryana", "Uttar Pradesh", "Uttar Pradesh / Punjab", "Uttar Pradesh (TBC)", "Punjab",
    "Chandigarh", "Himachal Pradesh", "Uttarakhand", "Ladakh", "West Bengal", "West Bengal / Nagaland", "Odisha",
    "Bihar", "Assam", "Meghalaya", "Sikkim", "Nagaland", "TBC",
]
STATUS_ORDER = [L.UP_, L.NEW26, L.NEW25, L.EST]
APPEND_FIELDS = ("evidence", "verify")


def merge(base, updates):
    out = []
    for row in base:
        row = dict(row)
        upd = updates.get(row["name"], {})
        for k, v in upd.items():
            if k in APPEND_FIELDS and row.get(k):
                row[k] = f"{row[k]} {v}"
            else:
                row[k] = v
        out.append(row)
    unknown = set(updates) - {r["name"] for r in base}
    if unknown:
        raise SystemExit(f"Enrichment keys with no matching lead: {sorted(unknown)}")
    return out


def order_key(row):
    region = REGION_ORDER.index(row["region"]) if row["region"] in REGION_ORDER else 99
    state = STATE_ORDER.index(row["state"]) if row["state"] in STATE_ORDER else 98
    return region, state, row["city"], row.get("priority", "Z"), row.get("tier", ""), row["name"]


def ig_url(handle):
    h = handle.strip()
    if h.startswith("@") and " " not in h and "/" not in h:
        return f"https://www.instagram.com/{h[1:]}/"
    return ""


def first_contact(row):
    if row.get("email"):
        return "Email"
    if row.get("ig", "").startswith("@"):
        return "Instagram DM"
    if row.get("phone"):
        return "Call / WhatsApp"
    if row.get("linkedin"):
        return "LinkedIn"
    if row.get("web"):
        return "Website contact form"
    return "Walk-in / Google Maps listing"


cafes = merge(L.CAFES, E.CAFE_UPDATES) + [dict(c) for c in E.NEW_CAFES]
roasters = merge(L.ROASTERS, E.ROASTER_UPDATES) + [dict(r) for r in E.NEW_ROASTERS]
channels = list(L.CHANNELS) + list(E.NEW_CHANNELS)

for c in cafes:
    assert c["tier"] in ("Premium", "Normal"), c["name"]
    assert c["status"] in STATUS_ORDER, c["name"]
    c["ig_url"] = ig_url(c.get("ig", ""))
    c["contact_route"] = first_contact(c)
for r in roasters:
    r["ig_url"] = ig_url(r.get("ig", "").split(" ")[0])

cafes.sort(key=order_key)
roasters.sort(key=lambda r: order_key(dict(r, priority="", tier=r["tier"])))
for i, c in enumerate(cafes, 1):
    c["id"] = f"C{i:03d}"
for i, r in enumerate(roasters, 1):
    r["id"] = f"R{i:03d}"

hot = [c for c in cafes if c["status"] != L.EST]
hot.sort(key=lambda c: (STATUS_ORDER.index(c["status"]), c["priority"], c["tier"] != "Premium", order_key(c)))

CAFE_COLS = [
    ("ID", "id", 7), ("Priority", "priority", 8), ("Status", "status", 18), ("Tier", "tier", 9), ("Name", "name", 30),
    ("Type", "type", 22), ("Roasts in-house?", "roasts", 12), ("Beans / origins on menu", "beans", 32),
    ("Region", "region", 10), ("State", "state", 14), ("City", "city", 16), ("Area / address", "area", 32),
    ("Evidence (why this tier)", "evidence", 60), ("Pitch angle", "angle", 45), ("Best first contact", "contact_route", 16),
    ("Instagram", "ig", 24), ("Instagram URL", "ig_url", 34), ("Website", "web", 30), ("Email", "email", 28),
    ("Phone", "phone", 22), ("LinkedIn", "linkedin", 30), ("Listing (Zomato / EazyDiner / Reddit)", "listing", 34),
    ("Key people (public)", "people", 30), ("Source", "src", 45), ("Verify / notes", "verify", 40),
]
ROASTER_COLS = [
    ("ID", "id", 7), ("Tier", "tier", 9), ("Roaster", "name", 32), ("Region", "region", 10), ("State", "state", 16),
    ("City", "city", 22), ("Model / outlets", "model", 50), ("Evidence", "evidence", 50), ("Partnership angle", "angle", 40),
    ("Instagram", "ig", 26), ("Instagram URL", "ig_url", 34), ("Website", "web", 30), ("Email", "email", 26), ("Phone", "phone", 18),
    ("LinkedIn", "linkedin", 40), ("Key people (public)", "people", 34), ("Source", "src", 45), ("Verify / notes", "verify", 30),
]
CHANNEL_COLS = [
    ("Category", "category", 18), ("Name", "name", 34), ("City", "city", 24), ("What it is", "what", 50),
    ("How to use it", "angle", 50), ("Instagram", "ig", 26), ("Website", "web", 40), ("Email", "email", 24),
    ("Phone", "phone", 16), ("LinkedIn", "linkedin", 30), ("Source", "src", 50),
]

FONT = "Arial"
HEAD_FILL = PatternFill("solid", fgColor="3B2A20")
HEAD_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY_FONT = Font(name=FONT, size=10)
LINK_FONT = Font(name=FONT, size=10, color="1F4E9E", underline="single")
THIN = Side(style="thin", color="D9D2C9")
BORDER = Border(bottom=THIN)
A_FILL = PatternFill("solid", fgColor="E3F1DF")
PREM_FILL = PatternFill("solid", fgColor="FBEFD9")
UP_FILL = PatternFill("solid", fgColor="FDE2E1")
LINK_KEYS = {"ig_url", "web", "linkedin", "listing", "src"}


def write_table(ws, cols, rows):
    for j, (head, _, width) in enumerate(cols, 1):
        cell = ws.cell(row=1, column=j, value=head)
        cell.font, cell.fill = HEAD_FONT, HEAD_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = width
    for i, row in enumerate(rows, 2):
        for j, (_, key, _) in enumerate(cols, 1):
            val = row.get(key, "") or ""
            cell = ws.cell(row=i, column=j, value=val)
            cell.font = BODY_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER
            if key in LINK_KEYS and isinstance(val, str) and val.startswith("http"):
                cell.hyperlink = val
                cell.font = LINK_FONT
    ws.freeze_panes = "F2" if cols is CAFE_COLS else "D2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{max(len(rows) + 1, 2)}"
    ws.row_dimensions[1].height = 30


def highlight_cafes(ws, n):
    last = get_column_letter(len(CAFE_COLS))
    rng = f"A2:{last}{n + 1}"
    ws.conditional_formatting.add(rng, FormulaRule(formula=['$C2="Upcoming / Coming soon"'], fill=UP_FILL))
    ws.conditional_formatting.add(rng, FormulaRule(formula=['$B2="A"'], fill=A_FILL))
    ws.conditional_formatting.add(f"D2:D{n + 1}", FormulaRule(formula=['$D2="Premium"'], fill=PREM_FILL))


wb = Workbook()
readme = wb.active
readme.title = "Read Me"

ws = wb.create_sheet("Hot Leads (New & Upcoming)")
write_table(ws, CAFE_COLS, hot)
highlight_cafes(ws, len(hot))

ws = wb.create_sheet("All Cafes (Premium+Normal)")
write_table(ws, CAFE_COLS, cafes)
highlight_cafes(ws, len(cafes))

ws = wb.create_sheet("Roasters")
write_table(ws, ROASTER_COLS, roasters)
ws.conditional_formatting.add(f"B2:B{len(roasters) + 1}", FormulaRule(formula=['$B2="Premium"'], fill=PREM_FILL))

ws = wb.create_sheet("Channel Partners")
write_table(ws, CHANNEL_COLS, channels)

ws = wb.create_sheet("Excluded (Regular tier)")
write_table(ws, [("Operator", "name", 40), ("Why excluded", "why", 90)], [dict(name=n, why=w) for n, w in L.EXCLUDED])

# ---- Region summary with live formulas
ws = wb.create_sheet("Summary by State")
AC = "'All Cafes (Premium+Normal)'"
heads = ["State", "Cafes (total)", "Premium", "Normal", "Priority A", "New / Upcoming", "Roasters"]
for j, h in enumerate(heads, 1):
    cell = ws.cell(row=1, column=j, value=h)
    cell.font, cell.fill = HEAD_FONT, HEAD_FILL
    ws.column_dimensions[get_column_letter(j)].width = 22 if j == 1 else 15
all_states = {c["state"] for c in cafes} | {r["state"] for r in roasters}
present = [s for s in STATE_ORDER if s in all_states]
present += sorted(all_states - set(present))
n_c, n_r = len(cafes) + 1, len(roasters) + 1
for i, s in enumerate(present, 2):
    ws.cell(row=i, column=1, value=s)
    ws.cell(row=i, column=2, value=f'=COUNTIF({AC}!$J$2:$J${n_c},A{i})')
    ws.cell(row=i, column=3, value=f'=COUNTIFS({AC}!$J$2:$J${n_c},A{i},{AC}!$D$2:$D${n_c},"Premium")')
    ws.cell(row=i, column=4, value=f'=COUNTIFS({AC}!$J$2:$J${n_c},A{i},{AC}!$D$2:$D${n_c},"Normal")')
    ws.cell(row=i, column=5, value=f'=COUNTIFS({AC}!$J$2:$J${n_c},A{i},{AC}!$B$2:$B${n_c},"A")')
    ws.cell(row=i, column=6, value=f'=COUNTIF({AC}!$J$2:$J${n_c},A{i})-COUNTIFS({AC}!$J$2:$J${n_c},A{i},{AC}!$C$2:$C${n_c},"Established")')
    ws.cell(row=i, column=7, value=f"=COUNTIF(Roasters!$E$2:$E${n_r},A{i})")
tot = len(present) + 2
ws.cell(row=tot, column=1, value="Total")
for j in range(2, 8):
    col = get_column_letter(j)
    ws.cell(row=tot, column=j, value=f"=SUM({col}2:{col}{tot - 1})")
for row in ws.iter_rows(min_row=2, max_row=tot):
    for cell in row:
        cell.font = Font(name=FONT, size=10, bold=cell.row == tot)
ws.freeze_panes = "B2"

# ---- Platform coverage
ws = wb.create_sheet("Platform Coverage")
PLAT = [
    ("Platform", "What was searched", "What it yielded", "Limits"),
    ("Instagram", "Per-city sweeps ('specialty coffee <city>', 'coming soon') and one search per lead name.",
     "Most handles in this file; 'coming soon' / relaunch posts (Coffee Bond, Brewtown, Cafe Serenity, Craft Coffee Siliguri, Lento Pune); multi-roaster bios (Pilgrim, Coffee Therapy Artisan, Lucky's, Daily Daily, Specialty Coffee House); bio phone numbers.",
     "Search index lags new accounts; DMs are the main contact route for small cafes."),
    ("LinkedIn", "Company pages for roasters/chains; founder 'launching our cafe' posts; cafe hiring posts.",
     "Company pages (Blue Tokai, Subko, KC Roasters, Half Light, Toffee, KaCoBa, 93 Degrees); founders; hiring signals (The Coffee Project Nagpur, Blue Tokai Punjab/Haryana).",
     "Small cafes rarely have pages; profiles of individuals listed only where they are public founders/brand pages."),
    ("News / trade press", "Restaurant India, Indian Retailer, Franchise India, World Coffee Portal, Hotelier India, BW Hotelier, ANI/ThePrint.",
     "Dated openings (Oro, Jacob's Brew House, Momoka, Pour Over Santushti, Gram Street, Cocoa & Katli, Stand By Juhu, Coffee Capital).",
     "Press-release driven: favours funded brands."),
    ("City food media", "The Nod, Outlook Traveller (OT Pours), Curly Tales, The Lab Mag, LBB, Time Out, Esquire, Free Press Journal, t2 (Kolkata), Elle Decor.",
     "Monthly 'new openings' lists: The Drop, Therefore, In Good Co., ATE Omakase, Odd Culture, Traut, Flameback, Lento Pune.",
     "Covers metros far better than Tier-2 cities."),
    ("District / Zomato / EazyDiner / Tripadvisor", "City specialty guides, listings for addresses and ratings.",
     "Addresses, ratings, price-for-two (Toise, Traut, Pull and Pour, Kulture, Pilgrim).",
     "Phone numbers mostly behind app; not scraped."),
    ("Reddit", "r/PuneCoffee and city coffee threads.", "Pre-launch founder post (Viman Nagar, Pune).", "Few city subs are active."),
    ("Job boards", "Glassdoor, Apna, Foundit, Weekday barista listings.",
     "Hiring = opening soon signal (Kerb Coffee Co., Basque by breve, Bhatia Speciality Coffee LLP, 729 Grams).", "Employer names sometimes legal entities."),
    ("Directories", "Indian Coffee Beans, Indian Coffee Guide, Speciality Coffee Online, BrewAtlas, Wanderlog.",
     "Roaster lists by city; wholesale terms of competitors (BROOT, Rossette).", "Some directory entries could not be corroborated (flagged)."),
    ("Email", "Searched '<name> email contact' for priority leads.",
     "Few cafes publish email (Artsy, PICO, Roastery Coffee House). Instagram DM / phone is the realistic first touch.",
     "No email has been guessed or constructed — blank means not published."),
]
for i, row in enumerate(PLAT, 1):
    for j, v in enumerate(row, 1):
        cell = ws.cell(row=i, column=j, value=v)
        cell.font = HEAD_FONT if i == 1 else BODY_FONT
        if i == 1:
            cell.fill = HEAD_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="top")
for j, w in enumerate([22, 55, 70, 45], 1):
    ws.column_dimensions[get_column_letter(j)].width = w

# ---- Read Me
lines = [
    ("Premium Indian Specialty Coffee — Outreach Leads (North, West, Central, East & Northeast India)", True),
    ("Research date: 27 Oct 2026. South India deliberately excluded (Goa is included as West coast).", False),
    ("", False),
    ("TIERS", True),
    ("Premium — origin-driven specialty: single-origin / single-estate or micro-lot menus, manual brew bar (V60, Chemex, AeroPress, siphon), multi-roaster or guest-roast programmes, or imports international single origins. Core market for premium beans.", False),
    ("Normal — better than regular: specialty-leaning, espresso-led cafes with a quality house blend, maybe one filter option; food/dessert-led concepts with a deliberate coffee programme. Market for a premium house blend + one rotating estate.", False),
    ("Regular — commodity / chain cafes. Not targeted; listed only in 'Excluded (Regular tier)' for reference.", False),
    ("", False),
    ("PRIORITY", True),
    ("A — act this week: upcoming or just-opened cafes still choosing suppliers, multi-roaster cafes, and cafes known to buy from outside roasters.", False),
    ("B — strong fit: established Premium/Normal independents that do not roast in-house.", False),
    ("C — nurture: roaster-owned cafes (collab/guest lot only), chains, or thin evidence.", False),
    ("", False),
    ("STATUS", True),
    ("Upcoming / Coming soon — announced or 'opening soon' on social/press but not open (the pre-launch hype window).", False),
    ("New (opened 2026) / New (late 2025) — opened recently; supplier relationships still forming.", False),
    ("", False),
    ("HOW TO USE", True),
    ("1. Start with 'Hot Leads (New & Upcoming)' — sorted Upcoming → New, then priority. Row colours: pink = upcoming, green = priority A, cream tier cell = Premium.", False),
    ("2. 'Best first contact' picks the most direct public channel found (email > Instagram DM > phone > LinkedIn > website > walk-in).", False),
    ("3. Every row has a Source link. 'Verify / notes' flags single-source facts, unconfirmed cities and handles not yet indexed by search.", False),
    ("4. 'Roasters' lists competitors and possible partners (guest-roast slots in multi-roaster cafes, co-roasting, distribution). 'Channel Partners' lists cafe consultants, barista academies, communities and events that reach cafes before launch.", False),
    ("5. 'Summary by State' recounts automatically (COUNTIF formulas) if you add or retag rows.", False),
    ("", False),
    ("CONTACT DATA POLICY", True),
    ("Only publicly listed business contacts were recorded. Nothing was guessed (no constructed emails). Blank = not published / not found yet. Individual names appear only as publicly credited founders or brand leads.", False),
    ("", False),
    ("COUNTS", True),
]
for i, (text, bold) in enumerate(lines, 1):
    cell = readme.cell(row=i, column=1, value=text)
    cell.font = Font(name=FONT, size=13 if i == 1 else 10, bold=bold)
    cell.alignment = Alignment(wrap_text=True, vertical="top")
r0 = len(lines) + 1
HL = "'Hot Leads (New & Upcoming)'"
count_rows = [
    ("Cafes — total (Premium + Normal)", f"=COUNTA({AC}!$A$2:$A${n_c})"),
    ("Cafes — Premium", f'=COUNTIF({AC}!$D$2:$D${n_c},"Premium")'),
    ("Cafes — Normal", f'=COUNTIF({AC}!$D$2:$D${n_c},"Normal")'),
    ("Cafes — Priority A", f'=COUNTIF({AC}!$B$2:$B${n_c},"A")'),
    ("Hot leads (new & upcoming)", f"=COUNTA({HL}!$A$2:$A${len(hot) + 1})"),
    ("Upcoming / coming soon", f'=COUNTIF({AC}!$C$2:$C${n_c},"Upcoming / Coming soon")'),
    ("Multi-roaster cafes", f'=COUNTIF({AC}!$F$2:$F${n_c},"Multi-roaster cafe")'),
    ("With an Instagram handle", f'=COUNTIF({AC}!$P$2:$P${n_c},"@*")'),
    ("Roasters", f"=COUNTA(Roasters!$A$2:$A${n_r})"),
    ("Channel partners", f"=COUNTA('Channel Partners'!$A$2:$A${len(channels) + 1})"),
]
for k, (label, formula) in enumerate(count_rows):
    readme.cell(row=r0 + k, column=1, value=label).font = BODY_FONT
    c = readme.cell(row=r0 + k, column=2, value=formula)
    c.font = Font(name=FONT, size=10, bold=True)
readme.column_dimensions["A"].width = 120
readme.column_dimensions["B"].width = 12

wb.save(OUT_XLSX)

# ---- CSVs
os.makedirs(CSV_DIR, exist_ok=True)


def dump(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([h for h, _, _ in cols])
        for row in rows:
            w.writerow([row.get(k, "") or "" for _, k, _ in cols])


dump(os.path.join(CSV_DIR, "hot_leads_new_upcoming.csv"), CAFE_COLS, hot)
dump(os.path.join(CSV_DIR, "cafes_premium_normal.csv"), CAFE_COLS, cafes)
dump(os.path.join(CSV_DIR, "roasters.csv"), ROASTER_COLS, roasters)
dump(os.path.join(CSV_DIR, "channel_partners.csv"), CHANNEL_COLS, channels)

# ---- Markdown table of hot leads + external-roaster buyers
def md_cell(v):
    return (v or "").replace("|", "/").replace("\n", " ")


def md_contact(c):
    parts = [c.get("ig", "") if c.get("ig", "").startswith("@") else "", c.get("email", ""), c.get("phone", ""), c.get("web", "")]
    return " · ".join(p for p in parts if p) or "—"


buyers = [c for c in cafes if c["status"] == L.EST and c["priority"] == "A"]
with open(os.path.join(ROOT, "HOT_LEADS.md"), "w", encoding="utf-8") as f:
    f.write("# Hot leads — new & upcoming premium cafes\n\n")
    f.write("Generated by `research/build.py` from `research/leads.py` + `research/enrichment.py`. "
            "Full detail (evidence, sources, verify notes) is in the workbook.\n\n")
    f.write("| ID | Pri | Status | Tier | Cafe | City | Contact found | Pitch |\n|---|---|---|---|---|---|---|---|\n")
    for c in hot:
        f.write(f"| {c['id']} | {c['priority']} | {c['status']} | {c['tier']} | {md_cell(c['name'])} | {md_cell(c['city'])} | "
                f"{md_cell(md_contact(c))} | {md_cell(c['angle'])} |\n")
    f.write("\n## Established cafes that already buy from outside roasters (priority A)\n\n")
    f.write("| ID | Cafe | Type | City | Contact found | Pitch |\n|---|---|---|---|---|---|\n")
    for c in buyers:
        f.write(f"| {c['id']} | {md_cell(c['name'])} | {c['type']} | {md_cell(c['city'])} | {md_cell(md_contact(c))} | {md_cell(c['angle'])} |\n")

print(f"cafes={len(cafes)} hot={len(hot)} roasters={len(roasters)} channels={len(channels)}")
print(f"premium={sum(c['tier'] == 'Premium' for c in cafes)} normal={sum(c['tier'] == 'Normal' for c in cafes)} "
      f"A={sum(c['priority'] == 'A' for c in cafes)} ig={sum(c.get('ig', '').startswith('@') for c in cafes)}")
