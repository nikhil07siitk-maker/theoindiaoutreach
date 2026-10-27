# The O India — Specialty Coffee Outreach Research

Who to sell premium roasted Indian specialty coffee beans to in **Maharashtra, Madhya Pradesh and everything north, east and west of it** (Gujarat, Goa, Rajasthan, Delhi NCR, Punjab/Chandigarh, Himachal, Uttarakhand, UP, Ladakh, West Bengal, Odisha, Bihar and the Northeast). South India is excluded on purpose because it is already saturated.

Research date: **27 Oct 2026**.

## Files

| File | What it is |
|---|---|
| `North_West_East_India_Specialty_Coffee_Leads.xlsx` | Main workbook. Seven tabs: Read Me · Hot Leads (New & Upcoming) · All Cafes (Premium+Normal) · Roasters · Channel Partners · Excluded (Regular tier) · Summary by State · Platform Coverage |
| `HOT_LEADS.md` | Quick-read table of the 42 new/upcoming cafés and the 15 established cafés that already buy from outside roasters |
| `csv/` | The same tables as CSV, ready to import into a CRM or Google Sheets |
| `research/leads.py`, `research/enrichment.py` | Source data (every row has a source link). `enrichment.py` holds the per-platform contact pass |
| `research/build.py` | Regenerates the workbook, CSVs and `HOT_LEADS.md`: `python3 research/build.py` |

## What's in it

- **152 cafés**: 70 **Premium** and 82 **Normal**. Regular-tier chains are listed separately and not targeted.
- **42 hot leads**: upcoming, just opened in 2026, or opened late 2025.
- **37 priority-A cafés**: pre-launch or new cafés, **multi-roaster cafés** (Pilgrim in Nashik, Coffee Therapy Artisan in Bhopal, One World in Pune, Lucky's Coffee Garage, Daily Daily, Specialty Coffee House), and cafés known to buy from outside roasters (Overflow in Lucknow, Sidewalk in Kanpur/Agra, Indiroom and Babka in Goa, Kulture and Flameback in Kolkata).
- **72 roasters**: tagged Premium or Normal, with a partnership angle for each (competitor, guest-roast slot, co-roasting, distribution).
- **19 channel partners**: café-setup consultants, barista academies, coffee communities, marketplaces and events. These reach cafés *before* they launch.

### Tier definitions
- **Premium**: origin-driven specialty. Single-origin, single-estate or micro-lot menus, a manual brew bar, multi-roaster or guest-roast programmes, or international single origins on the menu. This is the core market for premium beans.
- **Normal**: better than regular. Specialty-leaning, espresso-led cafés with a deliberate coffee programme. They are a market for a premium house blend plus one rotating estate.
- **Regular**: commodity coffee or chains with central supply. Excluded.

## Where to start (this week)
1. **Pre-launch / just opened.** In Delhi NCR: The Drop (rotates its menu monthly), Therefore, In Good Co. (Aditya Birla-backed), ATE Omakase, Oro, Odd Culture and Coffee Bond (CP and Karkardooma opening soon). In Jaipur: Traut, Jacob's Brew House and Carbon. In Mumbai: Coffee Capital, Stand By Coffee, Thought Coffee, BBRWN and Cocoa & Katli. In Pune: Momoka, Cafe Lento and an unnamed Viman Nagar café that is still in planning. Elsewhere: More Over Coffee (Raipur) and Flameback (Kolkata).
2. **Multi-roaster cafés.** These have guest-bag slots every month: Pilgrim, Coffee Therapy Artisan, One World, Lucky's, Daily Daily and Specialty Coffee House.
3. **Channel partners that see cafés before launch.** Arrow Hospitality (Mumbai), Kaapi Machines, Kaapi Solutions (its Barista Hire board shows who is about to open) and Barista Training Academy (Delhi/Chandigarh).
4. **Wholesale price benchmarks from competitors.** BROOT charges from ₹1,050/kg with a 15 kg/month minimum. Rossette's minimum order is 10 kg for espresso and 1 kg for rarities.

## Method and limits
- I searched each platform separately: Instagram, LinkedIn, trade press, city food media, District/Zomato/EazyDiner/Tripadvisor, Reddit, job boards and coffee directories. The "Platform Coverage" tab records what each one yielded.
- Contacts are **public business listings only**. No email was guessed. A blank means the contact isn't published or wasn't found yet. Most small cafés publish only Instagram, so the "Best first contact" column usually says Instagram DM.
- Very new cafés (for example Therefore, Oro, Traut, The Drop and Flameback) are often not yet indexed by search on Instagram. They are flagged "look up by name on Instagram".
- Anything resting on one source, or with an unconfirmed city or name, is marked in **Verify / notes**. Check those before outreach.
- Pages were read through web search results. Direct page fetching was blocked by this environment's network policy, so some addresses and phone numbers that sit behind listing apps were not captured.
