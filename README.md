# Specialty Coffee Outreach Research: North, West, Central, East & Northeast India

Who to sell premium roasted Indian specialty coffee beans to in **Maharashtra, Madhya Pradesh and everything north, east and west of it** (Gujarat, Goa, Rajasthan, Delhi NCR, Punjab/Chandigarh, Himachal, Uttarakhand, UP, Ladakh, West Bengal, Odisha, Bihar and the Northeast). South India is excluded on purpose.

Research date: **27 Oct 2026** (four passes; the fourth read each lead's own pages).

## Files

| File | What it is |
|---|---|
| `North_West_East_India_Specialty_Coffee_Leads.xlsx` | Main workbook. Tabs: Read Me · **Hot Leads (New & Upcoming)** · All Cafes (Premium+Normal) · **Lead Profiles & Strategy** · **Supply Map** · Roasters · Channel Partners · Excluded (Regular tier) · Summary by State · **Coverage by City** · Platform Coverage |
| `HOT_LEADS.md` | Quick-read table of the 92 new/upcoming cafés with their current coffee roster and supplier |
| `csv/` | Every tab as CSV for a CRM: hot leads, all cafés, profiles & strategy, supply map, roasters, channel partners, page findings, web supplier leads |
| `research/leads.py` → `enrichment.py` → `wave2.py` → `wave3.py` → `wave4.py` | Source data from five rounds: first discovery, a contact-enrichment pass, month-by-month openings with coffee-roster profiles, a city-by-city sweep, and the page-level check (corrections, suppliers, contacts). Every row has a source link |
| `research/discovered_urls.json` · `research/page_findings.json` | Pages found for each lead, and what the page checker extracted from them (snippet + page for every item) |
| `research/build.py` | Regenerates everything: `python3 research/build.py` |
| `research/check_pages.py` | Page checker: opens every café's and roaster's own pages in a browser and pulls out what they pour and who roasts it. Needs open web access (see below) |

## What's in it

| | Pass 1 | Pass 2 | Pass 3 | Now (pass 4) |
|---|---|---|---|---|
| Cafés (Premium + Normal) | 152 | 204 | 271 | **284** (109 Premium, 175 Normal) |
| New & upcoming (hot leads) | 42 | 90 | 91 | **92** |
| Priority A | 37 | 61 | 65 | **60** (unverified and in-house roasters moved down) |
| Multi-roaster cafés | 6 | 6 | 7 | **6** (2 foreign leads removed, Babka added) |
| With an Instagram handle | 64 | 64 | 115 | **113** |
| Profiled with roster, gap, offer and approach | — | 154 | 197 | **195** (all priority A/B) |
| Roasters | 72 | 76 | 84 | **88** |

### Coverage: how deep each city went (tab "Coverage by City")
Pass 3 ran a separate Instagram sweep and web search for each city. The coverage tab counts leads per city with live formulas.
- **Deep:** Mumbai, Delhi, Gurugram, Jaipur.
- **Medium:** Pune, Thane/Navi Mumbai, Nagpur, Nashik, Ahmedabad, Surat, Vadodara, North Goa, Indore, Bhopal, Udaipur/Jodhpur, Noida, Chandigarh tricity, Lucknow, Kolkata.
- **Light:** most other Tier-2/3 cities and the Northeast. Searched, but little shows up online and the specialty scene there is genuinely small.
- **Thin, nothing found:** Gandhinagar, Bhavnagar, Ujjain, Kota, Ajmer and Bikaner (apart from Alchemist's Ajmer café), Jammu, Meerut, Cuttack, Jamshedpur, Itanagar.

Pass 3 also corrected some leads:
- **Highbrooks (Jabalpur):** roasts its own beans, so moved down to priority C.
- **Three Beans (Nagpur):** trades as "Coffee Roasters", so it probably roasts in-house.
- **More Over Coffee:** has 4 outlets across Raipur, Bhilai and Bilaspur.
- **Mainline Coffee (Ahmedabad):** a multi-roaster café, now priority A.
- **Ruby's Coffee Goa:** publishes its café stockists, so Bastardo and Dodaa Atelier are now on the Supply Map.

### Each lead's profile (tab "Lead Profiles & Strategy")
For each café:
- **Roasts in-house?**
- **Current coffee roster:** what they pour today (origins and estates, single origin vs blend, signature drinks, brew formats).
- **Supplier / roaster**
- **Price signals**
- **Gap in their roster**
- **What we can offer**
- **Approach strategy:** channel, timing and hook.

Some examples of what the rosters show:
- **Stand By Coffee (Mumbai):** seven coffees, all from Chikmagalur, from outside roasting partners. The opening: non-Karnataka estates.
- **Thought Coffee (Mumbai):** a single-estate AA, plus an *imported* Colombian Castillo as its special. The opening: an Indian replacement for the import, and volume supply as it expands.
- **Flameback (Kolkata):** coffee menu is 100% imported (Ethiopian Guji and Colombian). **Kulture (Kolkata):** showcases Ethiopian Yirgacheffe. **Libertario (Delhi):** Colombian farms. **Coffee Capital (Mumbai):** a rotating international micro-lot slot. The opening in all four: Indian estates with comparable flavour profiles.
- **The Drop (Delhi):** Tamil Nadu estates only, through Subko, and the menu rotates monthly. The opening: a guest "drop" of non-TN lots.
- **In Good Co. (Delhi):** a single Chikkamagaluru AA. **Cafe Lento (Pune/Goa):** Salawara Estate only. The opening: a second estate.
- **Café Nola (Jaipur):** Araku and Kerala organic beans. **Carbon (Jaipur):** built around 18–96-hour cold brews. **JOKER (Mumbai):** brandy-barrel-aged pour-over. The opening: cold-brew-optimised and barrel-programme lots.
- **Known suppliers:** NOT FAR ← Corridor Seven · Overflow ← Bloom · Sidewalk ← Bili Hu · Indiroom ← Caarabi · The Drop ← Subko. Roasting in-house (pitch green coffee or guest lots only): 8th Day, Angry Toast, KaCoBa, IKVITI, NAKED, KOMO by Kaffa, Coffee Culture at The Unseen, Brewer's Café, Boojee.

### Tiers
- **Premium:** origin-driven. Single-origin, single-estate or micro-lot menus, a manual brew bar, multi-roaster or guest-roast programmes, or imported single origins.
- **Normal:** better than regular. Espresso-led specialty with a deliberate coffee programme; they buy a premium house blend plus one rotating estate.
- **Regular:** chains and commodity coffee. Excluded.

## Approach playbook (built into the "Approach strategy" column)
- **Pre-launch / coming soon:** send a 3-estate tasting kit and offer a menu-development session *before the menu locks*. Offer 90-day launch exclusivity in their micro-market and a fixed price for the first 6 months.
- **Just opened (≤6 months):** offer a guest-lot month plus a free barista calibration. Run a side-by-side cupping against their current beans, and ask which roaster and estates they use.
- **Multi-roaster cafés:** offer a monthly guest slot in 1 kg bags, with a story card (farm, altitude, process, cup score) and a roast date within 7 days.
- **Cafés pouring imported coffee:** position Indian naturals and anaerobics against the import on flavour, freshness and landed cost.
- **Cafés tied to one estate or one roaster:** offer to be the second estate or rotating roaster, not a replacement.
- **Multi-outlet brands and hospitality groups:** pitch central procurement with a fixed roast spec. Several leads belong to groups, so one deal travels: Passcode Hospitality (The Drop, Jamun, PCO, Saz), Aspect Hospitality (JOKER), Luna Hospitality (Lento) and Aditya Birla dining (In Good Co.).
- **Cafés that roast in-house:** don't pitch roasted coffee. Offer green coffee or a co-branded guest micro-lot.

## Why "about to launch" is still the thinnest bucket, and how to catch more
Pre-launch hype lives on Instagram stories and reels, and search engines index those poorly. To keep finding cafés *before* they open:
1. **Instagram:** follow `#comingsoon` plus `#specialtycoffee` with each city's name, interior-design studios that post café fit-outs, and the community accounts in Channel Partners (Jaipur Coffee Community, Goa Specialty Coffee, Mumbai Coffee Collective, r/PuneCoffee).
2. **Hiring:** barista job posts on Glassdoor, Apna, LinkedIn and Kaapi Solutions' Barista Hire usually go up 4–8 weeks before opening.
3. **Equipment and consultants:** café-setup consultants (Arrow, Kaapi Machines, Westend, Takumi) and machine dealers see every new café. Get on their recommended-supplier list.
4. **Monthly roundups:** Foodies of India (Mumbai), The Lab Mag, Curly Tales and The Nod (Delhi), Knocksense (Lucknow, Indore, Ahmedabad) and t2 (Kolkata). Wave 2 of this file came from these.

## Pass 4: reading each lead's own pages
Earlier passes worked from search-result snippets. Pass 4 found each lead's own pages and read them in a browser:
1. **Find the pages.** One web search per lead turned up its website, listings (EazyDiner, District, magicpin, Yappe), press and reviews. They are recorded in `research/discovered_urls.json` (472 pages for 235 leads; the rest had nothing beyond their original source).
2. **Read them.** `research/check_pages.py` opened every page with a headless browser and pulled out roasters named, origins and estates, processes, brew methods, prices, opening/hiring signals and published contacts, each with a snippet and the page it came from.
3. **Curate.** What the pages showed was checked by hand and written into `research/wave4.py`. That is what changed the profiles below.

### What pass 4 changed
- **Removed (not in India / chain):** Lucky's Coffee Garage is in New Hampshire, USA; Daily Daily Coffeemakers is in Auckland, NZ; Barista Diner is the Barista chain's flagship format. All three moved to the Excluded tab.
- **Roast their own (pitch green coffee only):** Thought Coffee ("single-estate AA, roasted in-house"), PICO in Kolkata (roasts on-site) and Kruti Coffee in Bhubaneswar (own Patia roastery and own Koraput estate).
- **Unverified:** Backstreet Cafe in Chandigarh rests on one AI-style guide whose author says they never visited, so it moved down to C. About 35 small cafés from the monthly roundups don't show up anywhere else online; they're flagged "confirm it is open" rather than deleted.
- **Suppliers now known:**

  | Café | Roaster |
  |---|---|
  | Mazi | Beverage Union |
  | Mokai | Common Man Roasters (Singapore) |
  | Project Hum, Blockheads | Subko |
  | Bouffage, Larder & Folk | Corridor Seven (Larder & Folk buys about 60 kg a month) |
  | The Dark Roast, Coffee Yard | Blue Tokai |
  | Babka | Half-Light, G-Shot and Kokoro (a multi-roaster café) |
  | ATE | Caarabi (sister company) |
  | Genre | Hosted a Nandan Coffee takeover, so it is open to guest roasters |
  | Artsy (Kolkata) | Blue Tokai and Bili Hu (stated on its own website) |
  | The Little Place (Novotel Goa) | The Coffee Co |
- **Cafés pouring imports (pitch an Indian replacement):** Mokai (Singapore-roasted, plus South American and African coffees), Cafe Sandoz (Italian beans), Coffee Capital (rotating international micro-lots), ATE (Peru Geisha) and Blondie (Ethiopia and Costa Rica on the slow bar).
- **Group deals (one pitch, several outlets):**
  - Bhatia Hospitality: Common Time (3 outlets) and Sidewalk (5)
  - Bastian Hospitality: Blondie, Janu and The Blondie House
  - Javaphile: Worli, Pali Hill and Shelter
  - Chains: Perch (5), Town Coffee in Jaipur (4–5), Greko in Punjab, Cafe Buddy's Espresso (4 cities) and Book Bar
- **Contacts added:** business phone numbers from public listings (LBB, Yappe, Trip.com) for One World, Coffee Therapy, RITUAL, Shelter, Bouffage, Coffeeboo, 801, Caffein, Coffee Stop, Absolute Coffee Brewers, Town Coffee, Brims, Kali Coffee and Curators. Websites were added for Caffein and Grind Bar. Emails and phone numbers each business publishes on its own site are in the "Contacts on its own pages" column.
- **New leads:** 16 cafés, mainly in Surat (from the Pulled coffee app), Goa (Candolim and Porvorim), Rajkot, Ludhiana and Bhopal, plus Roasted by Roseate. 4 roasters: Silk Road Coffee Company, Beverage Union, Kokoro and Bouee.
- **Competitor intel (in the Roasters tab):**
  - Blue Tokai's wholesale offer bundles beans and an espresso machine for one monthly fee, with barista training. That is the bar to beat.
  - Bloom supplies 150+ outlets and offers café consultancy.
  - Subko's "Caffeinated by Subko" programme is actively adding small accounts.

### Running the page checker yourself
```
pip install -r research/requirements.txt && python3 -m playwright install chromium
python3 research/check_pages.py --add "Lead name" https://... https://...   # record pages you found for a lead
python3 research/check_pages.py                                             # check every lead (resumable; pages are cached)
python3 research/check_pages.py --shard 0/4 &  ... --shard 3/4 &            # or run 4 in parallel, then:
python3 research/check_pages.py --merge
python3 research/build.py                                                   # folds the findings into the workbook
```
- **Outputs:**
  - `research/page_findings.json` and `csv/page_findings.csv`.
  - In the workbook, "Web check (auto — verify)" columns and a **Web Check — Supplier Leads** sheet.
  - This run read at least one page for 279 of 375 leads (491 pages in all). It found coffee-specific evidence for 133 cafés and published contacts for 23 cafés and 10 roasters.
  - The supplier sheet has 17 pairs. Each carries a **Checked by hand** verdict: 11 confirmed (Artsy's two roasters each appear twice), 2 same-company and 4 rejected as roundup noise.
  - A roaster counts as a supplier only when supply wording sits next to its name ("roasts from", "brewing with", "powered by", "using"). On listing and article pages, the café's own name must also be nearby.
- **Sites the checker doesn't open:** Zomato, Swiggy, Tripadvisor, RestaurantGuru, Justdial, Instagram and the search engines all refuse automated browsers. The checker records them as "not opened" and doesn't try to get around that. Their information came from ordinary web searches instead.
- **Still to do:** the web-search budget ran out before the Guwahati, Shillong, Gangtok and Aizawl leads and most C-tier cafés could be searched. Those rows were checked only against the pages already on file.

## Method and limits
- Every platform was searched separately; the "Platform Coverage" tab records what each one yielded.
- Contacts are **public business listings only**. No email was guessed, and a blank means not published.
- Small new cafés rarely publish their roaster. Those rows say "Not published — ask on first contact", so the first message doubles as discovery.
- Anything resting on one source, or with an unconfirmed city or name, is flagged in **Verify / notes**.
- Passes 1–3 read pages through search results only; pass 4 opened the pages themselves (see above). Zomato/Swiggy menus are still unread because those sites refuse automated browsers.
- The "What we can offer" column assumes a premium multi-estate Indian range. Swap in your actual estates, processes, MOQ and pricing to sharpen each pitch.
