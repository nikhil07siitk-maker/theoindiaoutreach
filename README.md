# Specialty Coffee Outreach Research: North, West, Central, East & Northeast India

Who to sell premium roasted Indian specialty coffee beans to in **Maharashtra, Madhya Pradesh and everything north, east and west of it** (Gujarat, Goa, Rajasthan, Delhi NCR, Punjab/Chandigarh, Himachal, Uttarakhand, UP, Ladakh, West Bengal, Odisha, Bihar and the Northeast). South India is excluded on purpose.

Research date: **27 Oct 2026** (two passes).

## Files

| File | What it is |
|---|---|
| `North_West_East_India_Specialty_Coffee_Leads.xlsx` | Main workbook. Tabs: Read Me · **Hot Leads (New & Upcoming)** · All Cafes (Premium+Normal) · **Lead Profiles & Strategy** · **Supply Map** · Roasters · Channel Partners · Excluded (Regular tier) · Summary by State · Platform Coverage |
| `HOT_LEADS.md` | Quick-read table of the 90 new/upcoming cafés with their current coffee roster and supplier |
| `csv/` | Every tab as CSV for a CRM: hot leads, all cafés, profiles & strategy, supply map, roasters, channel partners |
| `research/leads.py` → `enrichment.py` → `wave2.py` | Source data in three passes (first discovery, contact enrichment, second pass with month-by-month openings and coffee-roster profiles). Every row has a source link |
| `research/build.py` | Regenerates everything: `python3 research/build.py` |

## What's in it

| | Pass 1 | Now |
|---|---|---|
| Cafés (Premium + Normal) | 152 | **204** (89 Premium, 115 Normal) |
| New & upcoming (hot leads) | 42 | **90** (81 opened in 2026, 5 in late 2025, 4 announced or coming soon, including the unnamed Viman Nagar café, which is still in planning) |
| Priority A | 37 | **61** |
| Profiled with roster, gap, offer and approach | — | **154** (all priority A/B) |
| Roasters | 72 | 76 |

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

## Method and limits
- Every platform was searched separately; the "Platform Coverage" tab records what each one yielded.
- Contacts are **public business listings only**. No email was guessed, and a blank means not published.
- Small new cafés rarely publish their roaster. Those rows say "Not published — ask on first contact", so the first message doubles as discovery.
- Anything resting on one source, or with an unconfirmed city or name, is flagged in **Verify / notes**.
- Pages were read through web-search results only. Direct page fetching was blocked by this environment's network policy, so full menus and listing-app phone numbers were not captured.
- The "What we can offer" column assumes a premium multi-estate Indian range. Swap in your actual estates, processes, MOQ and pricing to sharpen each pitch.
