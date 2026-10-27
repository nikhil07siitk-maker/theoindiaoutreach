"""Open each lead's public pages and record what they pour, who roasts it and how to reach them.

Needs open web access. The cloud session's default network policy blocks it, so either widen
Network access for the environment or run this on your own computer:

    pip install -r research/requirements.txt && python3 -m playwright install chromium
    python3 research/check_pages.py --dry-run           # list what would be opened; writes research/allowed_domains.txt
    python3 research/check_pages.py                     # every cafe and roaster (resumable: leads and pages are cached)
    python3 research/check_pages.py --only "Stand By" --only Oro
    python3 research/build.py                           # folds research/page_findings.json into the workbook

Per lead it:
  1. opens the URLs already on file (website, Instagram, listing, LinkedIn, source articles);
  2. searches the web for the lead and opens its own site and listing pages, plus a couple of articles;
  3. on its own site, follows a few menu / coffee / shop / stockist links;
  4. pulls out roasters named, Indian regions and estates, imported origins, processes and varietals,
     brew methods, coffee prices, opening and hiring signals, and the emails and phone numbers the
     business publishes on its own pages. On pages that cover many cafes (roundups) only the text
     around the lead's name is read.
Everything is auto-extracted with a snippet and the page it came from, so it can be checked by eye.
"""

import argparse
import base64
import csv
import glob
import hashlib
import json
import os
import random
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from urllib.parse import parse_qs, quote_plus, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(ROOT, "csv")
CACHE_DIR = os.path.join(ROOT, "research", ".page_cache")
OUT_JSON = os.path.join(ROOT, "research", "page_findings.json")
OUT_CSV = os.path.join(CSV_DIR, "page_findings.csv")
DOMAINS_TXT = os.path.join(ROOT, "research", "allowed_domains.txt")

SEARCH_ENGINES = [
    ("duckduckgo", "https://html.duckduckgo.com/html/?q={q}&kl=in-en", "a.result__a"),
    ("bing", "https://www.bing.com/search?q={q}&setlang=en-IN&cc=IN", "li.b_algo h2 a"),
]
LISTING_DOMAINS = ("zomato.com", "swiggy.com", "district.in", "magicpin.in", "eazydiner.com", "tripadvisor.",
                   "restaurantguru.com", "justdial.com", "linkedin.com")
SKIP_DOMAINS = ("facebook.com", "youtube.com", "youtu.be", "twitter.com", "x.com", "pinterest.", "google.", "bing.com",
                "duckduckgo.com", "wikipedia.org", "amazon.", "flipkart.com", "threads.net", "tiktok.com", "quora.com")
PLATFORM_EMAIL = ("zomato", "swiggy", "district", "magicpin", "eazydiner", "tripadvisor", "instagram", "linkedin", "facebook",
                  "wix", "sentry", "shopify", "godaddy", "example", "domain.com")
FOLLOW_RE = re.compile(r"menu|coffee|bean|shop|store|about|story|stockist|where[-_ ]?to[-_ ]?buy|find[-_ ]?us|partner|"
                       r"wholesale|cafes|outlets|locations|visit|career|jobs|join", re.I)
ROASTER_FOLLOW_RE = re.compile(r"stockist|where[-_ ]?to[-_ ]?buy|find[-_ ]?us|partner|wholesale|cafes|outlets|shop|coffee", re.I)
NOT_HTML_RE = re.compile(r"\.(pdf|jpe?g|png|webp|gif|mp4|zip)(\?|$)", re.I)

NAME_STOP = {"cafe", "café", "coffee", "the", "co", "co.", "company", "roasters", "roastery", "roaster", "house", "bar",
             "kitchen", "and", "&", "specialty", "speciality", "brew", "brewing", "studio", "lab", "bakery",
             "bakehouse", "deli", "bistro", "india", "pvt", "ltd", "llp", "store", "shop", "room"}


# ---------------------------------------------------------------- vocabulary
# Each entry: canonical label, regex alternatives, and whether a coffee word must sit within ~25 characters
# (for words that also mean something else on a menu: natural, honey, bourbon, Mexican ...).
def V(label, *pats, ctx=False):
    return label, pats or (lit(label),), ctx


def lit(s):
    """A literal name as a regex that tolerates hyphens/extra spaces and curly apostrophes."""
    return re.escape(s).replace(r"\ ", r"[\s\-]+").replace("'", "['’]?")


COFFEE_CTX = re.compile(r"coffee|espresso|arabica|robusta|bean|roast|brew|pour|filter|lot\b|estate|process|cup|"
                        r"origin|farm|cherry|altitude|masl|washed|ferment", re.I)

INDIAN_ORIGINS = [
    V("Chikmagalur", r"Chikk?a?magal[uo]ru?", r"Chickmagal[uo]r"), V("Coorg / Kodagu", "Coorg", "Kodagu"),
    V("Baba Budangiri", r"Baba ?Budan(?:giri)?"), V("Araku"), V("Biligiri / BR Hills", r"Biligiri(?:rangana)?", r"B\.? ?R\.? Hills"),
    V("Nilgiris", r"Nilgiris?"), V("Wayanad"), V("Shevaroys / Yercaud", r"Shevaroys?", "Yercaud"),
    V("Pulney / Kodaikanal", "Pulney", "Palani Hills", "Kodaikanal"), V("Sakleshpur", r"Saka?leshpur"), V("Manjarabad"),
    V("Anamalai / Valparai", r"Anamall?ai?s?", "Valparai"), V("Brahmagiri"), V("Koraput"),
    V("Karnataka", ctx=True), V("Kerala", ctx=True), V("Tamil Nadu", ctx=True),
    V("Meghalaya", ctx=True), V("Nagaland", ctx=True), V("Mizoram", ctx=True), V("Manipur", ctx=True), V("Arunachal", ctx=True),
    V("Monsooned Malabar", r"Monsoon(?:ed)? Malabar"),
]
ESTATE_RE = re.compile(r"\b((?:[A-Z][\w'’-]+ )?[A-Z][\w'’-]+) Estates?\b")
ESTATE_STOP = {"Real", "Single", "The", "Our", "This", "Coffee", "Tea", "Family", "One", "An", "A", "Same", "Each", "Its",
               "Indian", "Private", "Their", "From", "Of", "Specialty", "Speciality", "Multiple", "Different", "Single-Estate"}
INTL_ORIGINS = [
    V("Ethiopia", r"Ethiopian?"), V("Yirgacheffe", r"Yirgach?eff?e"), V("Guji"), V("Sidama / Sidamo", "Sidama", "Sidamo"),
    V("Kenya", r"Kenyan?", ctx=True), V("Colombia", r"Colombian?"), V("Panama", r"Panama(?:nian)?", ctx=True),
    V("Brazil", r"Brazil(?:ian)?(?! nuts?)", ctx=True), V("Guatemala", r"Guatemalan?"), V("Costa Rica", r"Costa Rican?"),
    V("Honduras", r"Hondura[ns]"), V("El Salvador"), V("Rwanda", r"Rwandan?"), V("Burundi"), V("Peru", r"Peru(?:vian)?", ctx=True),
    V("Bolivia", r"Bolivian?", ctx=True), V("Ecuador", ctx=True), V("Mexico", r"Mexic(?:o|an)", ctx=True),
    V("Nicaragua", r"Nicaraguan?"), V("Sumatra", r"Sumatran?"), V("Java", ctx=True), V("Yemen", r"Yemen[i]?"),
    V("Tanzania", r"Tanzanian?", ctx=True), V("Uganda", r"Ugandan?", ctx=True), V("Papua New Guinea"),
    V("Vietnam", r"Vietnam(?:ese)?", ctx=True), V("Indonesia", r"Indonesian?", ctx=True),
]
PROCESSES = [
    V("Washed", r"(?:fully )?washed", ctx=True), V("Natural", r"naturals?", ctx=True),
    V("Honey", r"(?:red |yellow |black |white )?honey[- ]process(?:ed)?", r"(?:red|yellow|black|white) honey"),
    V("Anaerobic", r"anaerobic"), V("Carbonic maceration", "carbonic maceration"), V("Co-fermented", r"co-?ferment(?:ed|ation)?"),
    V("Thermal shock", "thermal shock"), V("Double fermentation", r"double[- ]ferment(?:ed|ation)"),
    V("Yeast fermented", r"yeast[- ](?:fermented|inoculated|process)"), V("Experimental lot", r"experimental(?: lot| process)?", ctx=True),
    V("Pulped natural", "pulped natural"), V("Semi-washed", r"semi[- ]washed"), V("Wet-hulled", r"wet[- ]hulled"),
    V("Micro-lot", r"micro[- ]?lots?", r"nano[- ]?lots?"), V("Single origin", r"single[- ]origins?"),
    V("Single estate", r"single[- ]estates?"), V("House blend", r"(?:house|signature|espresso) blend"),
    V("Guest roaster / rotating", r"guest (?:roast(?:er|s)?|coffee|lot|beans)", r"rotating (?:coffee|roast|menu|beans|origins?|single)"),
    V("Cup score", r"cup(?:ping)? score", r"SCA ?\d\d"),
]
VARIETALS = [
    V("SL795", r"S\.?L\.? ?-?795", r"S ?795", r"Selection ?795"), V("SL9", r"S\.?L\.? ?-?9"), V("Chandragiri"), V("Catimor", ctx=True),
    V("Cauvery", ctx=True), V("Kent", ctx=True), V("Geisha / Gesha", "Geisha", "Gesha"), V("Bourbon", ctx=True), V("Typica"),
    V("Caturra"), V("Catuai"), V("Pacamara"), V("Sarchimor"), V("Hemavathy"), V("Peaberry"), V("Robusta"),
    V("Cherry Robusta", "cherry robusta"), V("Liberica"), V("Excelsa"),
]
BREW = [
    V("V60", r"V-?60"), V("Pour over", r"pour[- ]?overs?"), V("AeroPress", r"aero ?press"), V("Chemex"), V("Kalita"),
    V("Origami", ctx=True), V("Siphon", r"s[iy]phon"), V("French press"), V("Cold brew", r"cold[- ]brews?"),
    V("Nitro", r"nitro", ctx=True), V("Cold drip / Kyoto", r"cold[- ]drip", r"kyoto[- ](?:drip|style)"),
    V("Espresso tonic", r"espresso tonic"), V("South Indian filter", r"filter (?:coffee|kaapi|kapi)", r"degree coffee"),
    V("Moka pot", r"moka(?: pot)?"), V("Batch brew", r"batch[- ]brew"), V("Flat white"), V("Cortado"), V("Piccolo", ctx=True),
    V("Gibraltar"), V("Affogato"), V("Tasting flight / omakase", r"(?:coffee|tasting|espresso) flight", r"omakase", r"cupping"),
    V("Cascara"), V("Japanese iced", r"japanese[- ]iced", r"iced pour[- ]?over"), V("Decaf", r"decaf(?:feinated)?"),
]
COMMODITY = [V("Lavazza"), V("illy", ctx=True), V("Segafredo"), V("Nespresso"), V("Davidoff", ctx=True), V("Nescafé", r"Nescaf[eé]"),
             V("Starbucks"), V("Bru", ctx=True)]
FOREIGN_ROASTERS = [V("Square Mile"), V("Onyx Coffee"), V("Tim Wendelboe"), V("La Cabra"), V("Sey Coffee"),
                    V("Coffee Collective"), V("Proud Mary"), V("Five Elephant"), V("Nomad Coffee"), V("April Coffee")]
SIGNALS = [
    V("Coming soon", r"coming soon", r"opening soon", r"launching soon", r"soft launch", r"pre-?launch", r"opening (?:on|this|next)"),
    V("Now open", r"now open", r"grand opening", r"newly opened", r"we(?:'|’| a)re (?:now )?open"),
    V("Hiring", r"we(?:'|’| a)re hiring", r"now hiring", r"baristas? wanted", r"join our team", r"hiring (?:baristas?|now)", r"vacanc(?:y|ies)"),
    V("Retail beans", r"beans? (?:available|for sale)", r"buy (?:our )?beans", r"retail bags?", r"take[- ]home beans",
      r"(?:250|200|500) ?g(?:m|ms|rams?)?", ctx=True),
    V("Wholesale / cafe partners", r"wholesale", r"for caf[eé]s", r"B2B", r"partner with us", r"caf[eé] partners", r"HoReCa"),
]

# Roasters: aliases come from csv/roasters.csv, plus well-known Indian roasters that are not in this file.
# Short forms that are also ordinary words or coffee terms are kept only in their full form.
AMBIGUOUS_SHORT = {"bloom", "candor", "antidote", "alchemist", "noir", "kaffa", "first", "first crack", "drum", "shack",
                   "craft", "pour over", "tulum", "the good stuff", "potboiler", "gram street", "the bean co", "the aroma",
                   "koraput", "7 elements", "taffeta", "30 days", "93 degrees", "yours truly", "nandan", "doubleshot",
                   "sussegado", "toffee", "coffee"}
CASE_SENSITIVE = {"First Coffee", "Coffee Culture", "Indian Bean", "Craft Coffee India", "Coffee Sutra", "Shack Coffee Co.",
                  "Moonpeak Espresso", "Potboiler Coffee", "Gram Street Coffee", "The Bean Co Roasters", "nada coffee"}
EXTRA_ALIASES = {
    "Devan's South Indian Coffee & Tea": ["Devan's", "Devans"], "Pour Over Coffee Roasters (POCR)": ["POCR"],
    "KC Roasters (by Koinonia)": ["Koinonia"], "Kaffa Cerrado — The Roastery": ["Kaffa Cerrado"],
    "Ruby's Coffee Goa": ["Ruby's Coffee"], "Savorworks Coffee & Chocolate": ["Savorworks"],
    "Bloom Coffee Roasters": ["Bloom Coffee"], "Toffee Coffee Roasters": ["Toffee Coffee"],
}
ALIAS_OVERRIDE = {"nada": ["nada coffee"]}  # the bare brand name is an ordinary word
OTHER_INDIAN_ROASTERS = ["Black Baza", "Kapi Kottai", "Halli Berri", "Naivo", "Dope Coffee", "Maverick & Farmer", "Bili Hu",
                         "Hunkal Heights", "Fraction 9", "Seven Beans", "Kurangu Hill", "Sleepy Owl", "Flying Squirrel",
                         "Ainmane", "Marc's Coffee", "Third Wave Coffee Roasters"]
ROASTER_SUFFIXES = ["coffee roasters", "coffee roastery", "coffee roaster", "coffee company", "coffee co.", "coffee co",
                    "coffee lab", "coffee house & roastery", "cafe & roastery", "cafe and roastery", "roastery & cafe",
                    "& roastery", "— the roastery", "& brew studio", "& bakehouse", "roasters", "roastery", "roaster",
                    "coffee", "cafe"]


def base_name(name):
    """Drop '(…)' notes and ' — Juhu'-style location suffixes."""
    return re.sub(r"\s+[—–]\s+.*$", "", re.sub(r"\s*\(.*?\)", "", name)).strip()


def core_name(name):
    """The distinctive part: generic words trimmed from both ends ('Stand By Coffee' -> 'Stand By')."""
    words = base_name(name).split()
    while words and words[0].lower() in NAME_STOP:
        words = words[1:]
    while words and words[-1].lower() in NAME_STOP:
        words = words[:-1]
    return " ".join(words)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def compile_terms(entries):
    return [(label, re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(pats) + r")(?![A-Za-z0-9])", re.I), ctx)
            for label, pats, ctx in entries]


def roaster_aliases(name):
    base = base_name(name)
    if base.lower() in ALIAS_OVERRIDE:
        return ALIAS_OVERRIDE[base.lower()]
    aliases, short = {base}, base
    for _ in range(3):
        for suf in ROASTER_SUFFIXES:
            if short.lower().endswith(" " + suf):
                short = short[: -len(suf) - 1].strip(" &-—")
                break
    if short != base and len(short) >= 4 and short.lower() not in AMBIGUOUS_SHORT:
        aliases.add(short)
    aliases.update(EXTRA_ALIASES.get(name, []))
    return sorted(aliases)


def roaster_terms(roaster_rows):
    """One term per roaster (label = its name), matching any of its aliases."""
    out, seen = [], set()
    named = [(base_name(r["Roaster"]), roaster_aliases(r["Roaster"])) for r in roaster_rows]
    named += [(n, [n]) for n in OTHER_INDIAN_ROASTERS]
    for label, aliases in named:
        if label.lower() in seen:
            continue
        seen.add(label.lower())
        loose = [lit(a) for a in aliases if a not in CASE_SENSITIVE]
        strict = [lit(a) for a in aliases if a in CASE_SENSITIVE]
        alts = []
        if loose:
            alts.append("(?i:" + "|".join(loose) + ")")
        alts += strict
        out.append((label, re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(alts) + r")(?![A-Za-z0-9])"), False))
    return out


def name_regex(name):
    """Case-sensitive as written (plus ALL CAPS), so generic-sounding names don't match ordinary prose."""
    base = base_name(name)
    forms = {base, base.upper()}
    short = core_name(name)
    if short and short != base and (len(short) >= 6 or " " in short):
        forms.update({short, short.upper()})
    alts = "|".join(lit(f) for f in sorted(forms, key=len, reverse=True))
    return re.compile(r"(?<![A-Za-z0-9])(?:" + alts + r")(?![A-Za-z0-9])")


def generic_name(name):
    """Single short words ('Grounded', 'Habit') need a coffee word nearby before they count as a mention."""
    words = core_name(name).split()
    return len(words) <= 1 and len("".join(words)) < 9


def snippet(text, start, end, pad=80):
    return re.sub(r"\s+", " ", text[max(0, start - pad): end + pad]).strip()


def find_terms(text, terms):
    hits = {}
    for label, rx, ctx in terms:
        for m in rx.finditer(text):
            if ctx and not COFFEE_CTX.search(text[max(0, m.start() - 25): m.start()] + " " + text[m.end(): m.end() + 25]):
                continue
            h = hits.setdefault(label, {"term": label, "count": 0, "snippet": snippet(text, m.start(), m.end())})
            h["count"] += 1
    return hits


PRICE_RE = re.compile(r"(?:₹|Rs\.?|INR)\s?(\d{2,5})(?:\.00)?(?:\s?/-)?", re.I)
PRICE_CTX = re.compile(r"espresso|americano|cappuccino|latte|flat white|cortado|pour[- ]?over|v60|aeropress|cold brew|filter|"
                       r"mocha|macchiato|coffee|beans|tonic|chemex|cold drip|piccolo|affogato|estate|roast|blend|"
                       r"single origin|\d{3} ?g\b", re.I)
FOR_TWO_RE = re.compile(r"(?:₹|Rs\.?)\s?([\d,]{3,6})\s+for (?:two|2)", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+91[\s-]?|0)?[6-9]\d{4}[\s-]?\d{5}(?!\d)")
IG_META_RE = re.compile(r"([\d.,]+[KkMm]?) Followers, ([\d.,]+[KkMm]?) Following, ([\d.,]+[KkMm]?) Posts")
IG_BIO_RE = re.compile(r"on Instagram: [\"“](.*)[\"”]\s*$", re.S)
IG_HANDLE_RE = re.compile(r"instagram\.com/([A-Za-z0-9._]{2,30})/?(?:$|\?)")

TERM_GROUPS = [("indian_origins", compile_terms(INDIAN_ORIGINS)), ("intl_origins", compile_terms(INTL_ORIGINS)),
               ("processes", compile_terms(PROCESSES)), ("varietals", compile_terms(VARIETALS)), ("brew", compile_terms(BREW)),
               ("commodity_brands", compile_terms(COMMODITY)), ("foreign_roasters", compile_terms(FOREIGN_ROASTERS)),
               ("signals", compile_terms(SIGNALS))]
GROUPS = [g for g, _ in TERM_GROUPS] + ["roasters", "estates"]


def extract(text, rterms):
    found = {g: find_terms(text, terms) for g, terms in TERM_GROUPS}
    found["roasters"] = find_terms(text, rterms)
    masked = text  # blank roaster names so "Blue Tokai Attikan Estate" reads as "Attikan Estate"
    for _, rx, _ in rterms:
        masked = rx.sub(lambda m: " " * len(m.group(0)), masked)
    estates = {}
    for m in ESTATE_RE.finditer(masked):
        words = m.group(1).split()
        while words and words[0] in ESTATE_STOP:
            words = words[1:]
        if not words:
            continue
        label = " ".join(words) + " Estate"
        h = estates.setdefault(label, {"term": label, "count": 0, "snippet": snippet(text, m.start(), m.end())})
        h["count"] += 1
    found["estates"] = estates
    prices = []
    for m in PRICE_RE.finditer(text):  # the menu line the price sits on, so neighbouring dishes don't bleed in
        s, e = text.rfind("\n", 0, m.start()) + 1, text.find("\n", m.end())
        line = text[s: e if e != -1 else len(text)]
        if len(line) > 160:
            line = text[max(0, m.start() - 60): m.end() + 20]
        line = re.sub(r"\s+", " ", line).strip()
        if PRICE_CTX.search(line) and 40 <= int(m.group(1)) <= 5000 and line not in prices:
            prices.append(line)
    found["prices"] = prices[:8]
    m = FOR_TWO_RE.search(text)
    found["cost_for_two"] = m.group(0) if m else ""
    return found


def windows(text, rx, pad=1200):
    """Text around each mention of the lead's name, for pages that cover many cafes."""
    merged = []
    for m in rx.finditer(text):
        s, e = max(0, m.start() - pad), m.end() + pad
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return "\n…\n".join(text[s:e] for s, e in merged)


def parse_instagram(meta):
    desc = meta.get("og:description") or meta.get("description") or ""
    out = {}
    m = IG_META_RE.search(desc)
    if m:
        out.update(followers=m.group(1), following=m.group(2), posts=m.group(3))
    b = IG_BIO_RE.search(desc)
    if b:
        out["bio"] = re.sub(r"\s+", " ", b.group(1)).strip()
    return out


def clean_emails(text):
    keep = []
    for e in EMAIL_RE.findall(text):
        low = e.lower()
        if re.search(r"\.(png|jpe?g|webp|svg|gif)$", low) or "@2x" in low or any(p in low.split("@")[1] for p in PLATFORM_EMAIL):
            continue
        if low not in (k.lower() for k in keep):
            keep.append(e)
    return keep[:5]


def clean_phones(text):
    keep = []
    for p in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", p)[-10:]
        if digits not in keep:
            keep.append(digits)
    return ["+91 " + d[:5] + " " + d[5:] for d in keep[:4]]


# ---------------------------------------------------------------- targets
def domain(url):
    host = urlparse(url).netloc.lower().split(":")[0]
    return host[4:] if host.startswith("www.") else host


def on(d, names):
    """Is host d one of names? An entry ending in '.' matches any TLD (google. = google.com, google.co.in ...)."""
    for s in names:
        if s.endswith("."):
            if d.startswith(s) or "." + s in d:
                return True
        elif d == s or d.endswith("." + s):
            return True
    return False


def read_csv(name):
    with open(os.path.join(CSV_DIR, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


URL_RE = re.compile(r"https?://[^\s,;)\]]+")


def load_targets():
    targets = []
    for kind, fname, name_col in (("cafe", "cafes_premium_normal.csv", "Name"), ("roaster", "roasters.csv", "Roaster")):
        for row in read_csv(fname):
            urls, seen = [], set()
            site = row.get("Website", "")
            for col, role in (("Website", "own"), ("Instagram URL", "instagram"), ("Listing (Zomato / EazyDiner / Reddit)", "own"),
                              ("LinkedIn", "own"), ("Source", "source")):
                for u in URL_RE.findall(row.get(col, "")):
                    u = u.rstrip(".")
                    if u in seen:
                        continue
                    seen.add(u)
                    r = role
                    if role == "source":
                        r = "instagram" if "instagram.com" in u else "own" if site and domain(u) == domain(site) else "mention"
                    if "reddit.com" in u:
                        r = "mention"
                    urls.append((u, r))
            targets.append(dict(kind=kind, id=row["ID"], name=row[name_col], city=re.split(r"[/(,]", row.get("City", ""))[0].strip(),
                                ig=(row.get("Instagram", "").split() or [""])[0], urls=urls))
    return targets


def classify(url, target):
    """own = the lead's own site or listing; instagram; mention = a page that may cover many places; None = skip."""
    d = domain(url)
    if on(d, SKIP_DOMAINS) or NOT_HTML_RE.search(url):
        return None
    if on(d, ("instagram.com",)):
        return "instagram"
    slug, full = norm(core_name(target["name"])), norm(base_name(target["name"]))
    if on(d, LISTING_DOMAINS):
        if len(slug) >= 4 and slug in norm(urlparse(url).path):
            return "own"
        return None if on(d, ("linkedin.com",)) else "mention"
    host = norm(d.rsplit(".", 1)[0])
    if (len(slug) >= 5 and slug in host) or (len(full) >= 6 and full in host):
        return "own"
    return "mention"


# ---------------------------------------------------------------- browser
def cache_path(url):
    return os.path.join(CACHE_DIR, hashlib.sha1(url.encode()).hexdigest()[:20] + ".json")


def launch(pw, headed):
    kw = {"headless": not headed}
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        kw["proxy"] = {"server": proxy, "bypass": os.environ.get("NO_PROXY", "")}
    if os.environ.get("CHROMIUM_PATH"):
        return pw.chromium.launch(executable_path=os.environ["CHROMIUM_PATH"], **kw)
    try:
        return pw.chromium.launch(**kw)
    except Exception:
        found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux64/chrome"))
        if not found:
            raise
        return pw.chromium.launch(executable_path=found[-1], **kw)


class Browser:
    def __init__(self, page, delay, timeout, refresh):
        self.page, self.delay, self.timeout, self.refresh = page, delay, timeout, refresh
        self.misses = {}

    def pause(self, scale=1.0):
        time.sleep(self.delay * scale * random.uniform(0.7, 1.4))

    def visit(self, url):
        path = cache_path(url)
        if not self.refresh and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        rec = {"url": url, "final_url": url, "status": 0, "title": "", "text": "", "meta": {}, "links": [],
               "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        try:
            resp = self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
            self.page.wait_for_timeout(1500)
            for _ in range(3):  # menus and listings often render as you scroll
                self.page.mouse.wheel(0, 2500)
                self.page.wait_for_timeout(500)
            rec["status"] = resp.status if resp else 0
            rec["final_url"] = self.page.url
            rec["title"] = self.page.title()
            rec["text"] = self.page.inner_text("body")[:300000]
            rec["meta"] = self.page.eval_on_selector_all(
                "meta[name=description], meta[property^='og:']",
                "els => Object.fromEntries(els.map(e => [e.getAttribute('name') || e.getAttribute('property'), e.content || '']))")
            rec["links"] = self.page.eval_on_selector_all(
                "a[href]", "els => els.slice(0, 500).map(e => [(e.innerText || '').trim().slice(0, 80), e.href])")
        except Exception as e:  # timeouts, DNS failures, policy denials: record and move on
            rec["status"] = -1
            rec["error"] = (str(e).strip().splitlines() or ["error"])[0][:200]
        if rec["status"] > 0:  # failures are not cached, so a later run retries them
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False)
        self.pause()
        return rec

    def search(self, query, n):
        """Result URLs from the first engine that answers; an engine that comes back empty 3 times running is dropped."""
        for engine, tmpl, selector in SEARCH_ENGINES:
            if self.misses.get(engine, 0) >= 3:
                continue
            try:
                self.page.goto(tmpl.format(q=quote_plus(query)), wait_until="domcontentloaded", timeout=self.timeout)
                hrefs = self.page.eval_on_selector_all(selector, "els => els.map(e => e.href)")
            except Exception:
                hrefs = []
            self.pause(1.5)
            results = [u for u in dict.fromkeys(decode_result(h, engine) for h in hrefs) if u and not on(domain(u), SKIP_DOMAINS)]
            if results:
                self.misses[engine] = 0
                return results[:n]
            self.misses[engine] = self.misses.get(engine, 0) + 1
        return []


def decode_result(href, engine):
    """Unwrap the engines' click-tracking redirects."""
    if not href or not href.startswith("http"):
        return None
    p = urlparse(href)
    if engine == "duckduckgo" and "duckduckgo.com" in p.netloc:
        q = parse_qs(p.query).get("uddg")
        return q[0] if q else None
    if engine == "bing" and "bing.com" in p.netloc:
        u = parse_qs(p.query).get("u", [""])[0]
        if p.path.startswith("/ck/") and u.startswith("a1"):
            try:
                return base64.urlsafe_b64decode(u[2:] + "=" * (-len(u[2:]) % 4)).decode()
            except Exception:
                return None
        return None
    return href


# ---------------------------------------------------------------- per lead
def check_lead(br, target, rterms, cafe_names, n_search, max_pages):
    name_rx = name_regex(target["name"])
    texts = {"own": [], "mention": []}
    queue = list(target["urls"])
    if n_search:
        q = f'"{base_name(target["name"])}" {target["city"]} '
        q += "coffee roasters" if target["kind"] == "roaster" else "cafe coffee menu"
        known = {u for u, _ in queue}
        for u in br.search(q, n_search):
            role = classify(u, target)
            if role and u not in known:
                queue.append((u, role))
    rank = {"own": 0, "instagram": 1, "mention": 2}
    queue.sort(key=lambda x: rank.get(x[1], 3))  # own site and listings first, then Instagram, then articles
    known_ig = target["ig"].lower() if target["ig"].startswith("@") else ""
    pages, seen, followed, ig, ig_candidates = [], set(), 0, {}, []
    while queue and len(pages) < max_pages:
        url, role = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        rec = br.visit(url)
        text, used = rec.get("text", ""), role
        if not 200 <= rec["status"] < 300 or not text.strip():
            used = "failed" if not 200 <= rec["status"] < 300 else "empty"
        elif role == "instagram":
            meta = rec.get("meta", {})
            info = parse_instagram(meta)
            m = IG_HANDLE_RE.search(url)
            handle = "@" + m.group(1) if m else ""
            caption = meta.get("og:description") or meta.get("description") or ""
            if "/accounts/login" in rec["final_url"] and not info:
                used = "login wall"
            elif handle and handle.lower() == known_ig:
                ig = dict(info, handle=handle)
                texts["own"].append((url, info.get("bio", "") + "\n" + caption))
            elif handle and not known_ig:
                ig_candidates.append(dict(info, handle=handle))
                used = "candidate handle"
            elif windows(caption, name_rx, pad=600):  # a post or someone else's profile that names the lead
                texts["mention"].append((url, caption))
                used = "mention"
            else:
                used = "name not on page"
        elif role == "own":
            texts["own"].append((url, text))
            d = domain(url)
            path = urlparse(url).path.rstrip("/")
            if on(d, ("zomato.com",)) and path.count("/") == 2:  # a Zomato restaurant page lists dishes and prices on /order
                queue.insert(0, (url.rstrip("/") + "/order", "own"))
            elif not on(d, LISTING_DOMAINS):  # follow a few menu / coffee / stockist links on the lead's own site
                follow_rx, cap = (ROASTER_FOLLOW_RE, 5) if target["kind"] == "roaster" else (FOLLOW_RE, 3)
                for label, href in rec.get("links", []):
                    href = href.split("#")[0]
                    if followed >= cap:
                        break
                    if (domain(href) == d and href not in seen and href.rstrip("/") != url.rstrip("/") and not NOT_HTML_RE.search(href)
                            and (follow_rx.search(label) or follow_rx.search(urlparse(href).path))):
                        queue.insert(0, (href, "own"))
                        followed += 1
        else:
            win = windows(text, name_rx)
            if win:
                texts["mention"].append((url, win))
            else:
                used = "name not on page"
        pages.append({"url": url, "final_url": rec["final_url"], "role": role, "used": used, "status": rec["status"],
                      "title": rec.get("title", "")[:120], **({"error": rec["error"]} if rec.get("error") else {})})
    return summarise(target, pages, texts, ig, ig_candidates, rterms, cafe_names)


def summarise(target, pages, texts, ig, ig_candidates, rterms, cafe_names):
    out = {"kind": target["kind"], "id": target["id"], "name": target["name"], "city": target["city"],
           "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "pages": pages,
           "instagram": ig, "ig_candidates": ig_candidates, "own": {}, "mention": {}, "prices": [], "cost_for_two": "",
           "emails": [], "phones": [], "cafes_named": []}
    self_label = base_name(target["name"]).lower()
    for role in ("own", "mention"):
        groups = {g: {} for g in GROUPS}
        for url, text in texts[role]:
            f = extract(text, rterms)
            for g in GROUPS:
                for label, h in f[g].items():
                    d = groups[g].setdefault(label, {"term": label, "count": 0, "snippet": h["snippet"], "url": url})
                    d["count"] += h["count"]
            out["prices"] += [{"snippet": p, "url": url} for p in f["prices"]]
            out["cost_for_two"] = out["cost_for_two"] or f["cost_for_two"]
            if role != "own":
                continue
            out["emails"] += [e for e in clean_emails(text) if e not in out["emails"]]
            out["phones"] += [p for p in clean_phones(text) if p not in out["phones"]]
            if target["kind"] == "roaster":  # stockist / partner pages that name cafes in this file
                for cname, rx, generic in cafe_names:
                    if any(c["cafe"] == cname for c in out["cafes_named"]):
                        continue
                    for m in rx.finditer(text):
                        # a one-word name counts only as a list entry near coffee words, not mid-sentence ("Grounded in ...")
                        if generic and (re.match(r" [a-z]", text[m.end(): m.end() + 2])
                                        or not COFFEE_CTX.search(text[max(0, m.start() - 60): m.end() + 60])):
                            continue
                        out["cafes_named"].append({"cafe": cname, "snippet": snippet(text, m.start(), m.end()), "url": url})
                        break
        groups["roasters"].pop(next((k for k in groups["roasters"] if k.lower() == self_label), None), None)
        out[role] = {g: sorted(v.values(), key=lambda h: -h["count"]) for g, v in groups.items() if v}
    out["prices"], out["emails"], out["phones"] = out["prices"][:10], out["emails"][:5], out["phones"][:4]
    return out


# ---------------------------------------------------------------- summaries (also used by build.py)
def terms(f, role, group, n=6):
    return [h["term"] for h in f.get(role, {}).get(group, [])[:n]]


def summary_fields(f):
    roast_own = terms(f, "own", "roasters")
    roast_men = [t for t in terms(f, "mention", "roasters") if t not in roast_own]
    parts = []
    if roast_own:
        parts.append("Roasters named on its own pages: " + ", ".join(roast_own))
    if roast_men:
        parts.append("Roasters named in articles about it: " + ", ".join(roast_men))
    for label, groups in (("Indian origins/estates", ("indian_origins", "estates")), ("Imported origins", ("intl_origins",)),
                          ("Processes / format", ("processes",)), ("Varietals", ("varietals",)), ("Brew", ("brew",)),
                          ("Commodity brands", ("commodity_brands",)), ("Foreign roasters", ("foreign_roasters",))):
        vals = []
        for g in groups:
            for t in terms(f, "own", g, 8) + terms(f, "mention", g, 4):
                if t not in vals:
                    vals.append(t)
        if vals:
            parts.append(f"{label}: " + ", ".join(vals[:8]))
    if f.get("prices"):
        parts.append("Prices: " + " | ".join(p["snippet"] for p in f["prices"][:3]))
    if f.get("cost_for_two"):
        parts.append(f["cost_for_two"])
    sig = terms(f, "own", "signals")
    sig += [t for t in terms(f, "mention", "signals") if t not in sig]
    if sig:
        parts.append("Signals: " + ", ".join(sig))
    pages = f.get("pages", [])
    ok = [p for p in pages if p["used"] in ("own", "instagram", "mention")]
    ig = f.get("instagram") or {}
    return {
        "web_check": "; ".join(parts),
        "ig_followers": ig.get("followers", ""),
        "ig_bio": ig.get("bio", ""),
        "web_contacts": " · ".join(f.get("emails", []) + f.get("phones", [])),
        "web_pages": f"{len(ok)} of {len(pages)} read: " + " ".join(p["url"] for p in ok[:4]) if pages else "",
        "roasters_own": roast_own,
        "roasters_mention": roast_men,
    }


def opened_any(f):
    """Leads where nothing opened (blocked network, dead links) are retried on the next run."""
    return any(200 <= p["status"] < 300 for p in f.get("pages", []))


CSV_COLS = [("Kind", "kind"), ("ID", "id"), ("Name", "name"), ("City", "city"), ("Pages", "web_pages"),
            ("IG followers", "ig_followers"), ("IG bio", "ig_bio"), ("Roster evidence (auto — verify)", "web_check"),
            ("Cafes named on its pages (roasters)", "cafes"), ("Contacts on its own pages", "web_contacts"),
            ("IG handles found for leads without one", "ig_candidates")]


def write_outputs(findings):
    findings = sorted(findings, key=lambda f: (f["kind"], f["id"]))
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(findings, fh, ensure_ascii=False, indent=1)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([h for h, _ in CSV_COLS])
        for f in findings:
            row = dict(f, **summary_fields(f))
            row["cafes"] = ", ".join(c["cafe"] for c in f.get("cafes_named", []))
            row["ig_candidates"] = ", ".join(c["handle"] for c in f.get("ig_candidates", []))
            w.writerow([row.get(k, "") for _, k in CSV_COLS])


def write_domains(targets):
    hosts = {urlparse(u).netloc.lower() for t in targets for u, _ in t["urls"]}
    hosts |= {urlparse(tmpl).netloc for _, tmpl, _ in SEARCH_ENGINES}
    hosts |= {"www.zomato.com", "www.swiggy.com", "www.district.in", "magicpin.in", "www.eazydiner.com", "www.tripadvisor.in",
              "www.instagram.com", "www.linkedin.com", "in.linkedin.com"}
    with open(DOMAINS_TXT, "w", encoding="utf-8") as fh:
        fh.write("# Hosts check_pages.py opens: the lead URLs on file, the search engines and the main listing sites.\n"
                 "# Cafe websites found through search are not known in advance, so an allowlist will miss them:\n"
                 "# full network access is the practical setting for this script.\n")
        fh.writelines(h + "\n" for h in sorted(hosts) if h)
    return hosts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="list leads and URLs, write allowed_domains.txt, open nothing")
    ap.add_argument("--only", action="append", default=[], help="lead name (substring, case-insensitive); repeatable")
    ap.add_argument("--kind", choices=["cafe", "roaster", "all"], default="all")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many leads")
    ap.add_argument("--search", type=int, default=6, help="search results to consider per lead (0 = no search)")
    ap.add_argument("--pages", type=int, default=8, help="max pages opened per lead")
    ap.add_argument("--delay", type=float, default=2.5, help="seconds between page loads (jittered)")
    ap.add_argument("--timeout", type=int, default=25000, help="page load timeout, ms")
    ap.add_argument("--refresh", action="store_true", help="ignore cached pages and leads already checked")
    ap.add_argument("--headed", action="store_true", help="show the browser window (some sites refuse headless browsers)")
    args = ap.parse_args()

    targets = load_targets()
    if args.kind != "all":
        targets = [t for t in targets if t["kind"] == args.kind]
    if args.only:
        targets = [t for t in targets if any(o.lower() in t["name"].lower() for o in args.only)]
    if args.limit:
        targets = targets[: args.limit]

    if args.dry_run:
        for t in targets:
            print(f"{t['id']} {t['kind']:7} {t['name']} ({t['city']}): " + ", ".join(f"{r}={u}" for u, r in t["urls"]))
        hosts = write_domains(load_targets())
        print(f"\n{len(targets)} leads; {len(hosts)} known hosts written to {os.path.relpath(DOMAINS_TXT, ROOT)}")
        return

    from playwright.sync_api import sync_playwright

    done = {}
    if os.path.exists(OUT_JSON):
        with open(OUT_JSON, encoding="utf-8") as fh:
            done = {(f["kind"], f["name"]): f for f in json.load(fh)}
    rterms = roaster_terms(read_csv("roasters.csv"))
    cafe_names = [(c["Name"], name_regex(c["Name"]), generic_name(c["Name"])) for c in read_csv("cafes_premium_normal.csv")]

    with sync_playwright() as pw:
        browser = launch(pw, args.headed)
        page = browser.new_context(locale="en-IN", viewport={"width": 1280, "height": 900}).new_page()
        br = Browser(page, args.delay, args.timeout, args.refresh)
        streak = 0
        try:
            for i, t in enumerate(targets, 1):
                key = (t["kind"], t["name"])
                if key in done and opened_any(done[key]) and not args.refresh and not args.only:
                    continue
                print(f"[{i}/{len(targets)}] {t['kind']} {t['name']} ({t['city']})", flush=True)
                done[key] = check_lead(br, t, rterms, cafe_names, args.search, args.pages)
                s = summary_fields(done[key])
                print("   " + (s["web_check"][:220] or "nothing coffee-specific found") + f"  [{s['web_pages'][:16]}]", flush=True)
                write_outputs(list(done.values()))
                streak = 0 if opened_any(done[key]) else streak + 1
                if streak >= 10:
                    print("No page opened for the last 10 leads: web access looks blocked here. Stopping; rerun once it is open.")
                    break
        except KeyboardInterrupt:
            print("stopped; progress so far is saved")
        browser.close()
    write_outputs(list(done.values()))
    print(f"{len(done)} leads in {os.path.relpath(OUT_JSON, ROOT)} and {os.path.relpath(OUT_CSV, ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
