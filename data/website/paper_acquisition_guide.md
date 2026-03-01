# Paper Acquisition Guide — Top 50 Missing Papers

**Status:** 1,055 papers in corpus | 1,965 high-relevance papers identified but missing | Top 50 listed below

---

## Method 1: Zotero + UCSD Library (RECOMMENDED — Bulk)

### Setup
1. Install/open **Zotero** desktop
2. Go to **Edit → Preferences → Advanced → Config Editor**
3. Search for `extensions.zotero.proxies` and add your UCSD proxy:
   - Proxy: `https://login.ezproxy.library.ucsd.edu/login?url=%u`
4. Or install the Zotero browser connector and use it while signed into UCSD Library

### Bulk Import
In Zotero: **File → Add Item by Identifier** — paste these DOIs one at a time or in batch:

```
10.3390/bs4040394
10.1152/japplphysiol.00165.2011
10.1136/bjsports-2012-091877
10.1186/s41235-020-00243-4
10.3390/ijerph15112392
10.1121/1.4817924
10.1177/1477153511435961
10.3390/ijerph14020151
10.1177/0013916582143007
10.3389/fneur.2021.624861
10.1177/1477153519828419
10.3390/ijerph111212204
10.1121/1.3652902
10.1186/S40327-017-0058-X
10.1162/leon.2006.39.3.245
10.3390/su12177064
10.1111/apha.12552
10.1177/1420326X18820089
10.3390/su11195290
10.3390/su12104051
10.1177/0031512519876395
10.1038/s41598-018-36791-5
10.1177/1420326X16673214
10.3390/buildings9090199
10.1177/1420326X20942572
10.1038/s41598-021-83246-5
10.1177/1420326X17690911
10.1111/joid.12159
10.3390/su13010339
10.1177/1351010X19868546
10.1177/0143624418824232
10.1111/jpi.12655
10.1152/ajpregu.00478.2005
10.1177/0013916509336813
10.1177/001872087201400502
10.1177/1477153514564098
10.3390/ijerph15112358
10.1177/1420326X19875795
10.3390/ijerph16020280
10.1016/j.apacoust.2018.06.019
10.3390/ijerph10062348
10.1177/1351010X18779518
10.1177/1351010X18758478
10.1121/1.4818776
10.1177/1477153521990645
10.1177/0013916514567127
10.11113/ijbes.v6.n3.360
10.1177/0956797612464659
10.1121/1.2816563
10.1177/1420326X09358028
```

Zotero will pull metadata + attempt PDF via UCSD proxy. Many of these are open-access (MDPI, Frontiers, Nature SR) so you'll get PDFs automatically.

### After Download
Export PDFs from Zotero to: `data/pdfs_snowball/`
Then run: `python scripts/run_pdf_queue_until_empty.py` to extract them.

---

## Method 2: Google Scholar AI Prompt (Manual but Targeted)

Go to [Google Scholar](https://scholar.google.com/) and use their AI features, or paste this prompt into **Google AI Studio / Gemini** with Scholar grounding:

### Prompt for Google Scholar AI:

> I am building a research corpus for a project on **Cognitive Neuroscience for Architecture** — how the built environment affects human cognition, perception, emotion, and behavior through neuroscience mechanisms.
>
> I need to find full-text PDFs for the following categories of papers that are missing from my corpus. Please find me the most important, highly-cited papers (with direct PDF links where possible) in each area:
>
> **1. Biophilic Design & Nature Exposure (need ~10 papers)**
> - Effects of indoor plants, nature views, and natural materials on stress, attention, and wellbeing
> - Attention Restoration Theory (Kaplan) applied to architectural settings
> - Biophilic design frameworks and evidence reviews
>
> **2. Lighting, Circadian Rhythms & Architecture (need ~10 papers)**
> - Effects of LED color temperature on alertness, mood, and melatonin
> - Daylight exposure in buildings and non-visual biological effects
> - Architectural design for circadian health (melanopic illuminance)
>
> **3. Soundscape & Acoustic Environment (need ~10 papers)**
> - Indoor soundscape perception in offices, hospitals, and homes
> - Restorative soundscapes vs. noise stress
> - Audiovisual interactions in architectural spaces
>
> **4. Spatial Cognition & Wayfinding (need ~5 papers)**
> - Neural basis of spatial navigation in buildings
> - Environmental legibility and cognitive mapping
> - VR studies of architectural space perception
>
> **5. Thermal Comfort & Cognitive Performance (need ~5 papers)**
> - Temperature effects on cognitive performance in office buildings
> - Cross-modal effects of thermal and visual environment
>
> **6. Material Psychology & Neuroaesthetics (need ~5 papers)**
> - Wood, concrete, and natural materials' effects on stress and perceived warmth
> - Fractal patterns in architecture and perceptual fluency
> - Neuroaesthetic responses to architectural form
>
> For each paper, provide: Authors, Year, Title, Journal, DOI, and whether a free PDF is available.
> Prioritize papers from 2010–2025 with >50 citations when possible.

---

## Method 3: Direct Open-Access Download (Automated)

Many of our top 50 are from open-access journals. I can attempt automated download of these DOIs via Unpaywall or direct publisher links. ~30 of the 50 are likely freely available (MDPI, Frontiers, PLOS, Nature Scientific Reports).

---

## Topic Distribution of Missing Papers

| Topic | Count (top 100) |
|-------|-----------------|
| Environment / Sustainability | 40 |
| Acoustics / Soundscape | 11 |
| Architecture / Building | 10 |
| Health / Neuroscience | 10 |
| Lighting / Circadian | 10 |
| Perception / Psychology | 5 |
| Other | 14 |

---

## Top 10 Most Important Missing Papers

| # | Year | Paper | Cited | DOI |
|---|------|-------|-------|-----|
| 1 | 2014 | Nature in Coping with Psycho-Physiological Stress (Berto) | 650x | 10.3390/bs4040394 |
| 2 | 2011 | LED-backlit screen affects circadian physiology (Cajochen) | 577x | 10.1152/japplphysiol.00165.2011 |
| 3 | 2015 | Urban brain: outdoor activity with mobile EEG (Aspinall) | 423x | 10.1136/bjsports-2012-091877 |
| 4 | 2020 | Senses of place: multisensory mind design (Spence) | 199x | 10.1186/s41235-020-00243-4 |
| 5 | 2018 | Positive Health Effects & Soundscapes (Aletta) | 193x | 10.3390/ijerph15112392 |
| 6 | 2013 | Designing sound components for urban soundscapes (Hong) | 170x | 10.1121/1.4817924 |
| 7 | 2012 | Framework for non-visual effects of daylight (Andersen) | 141x | 10.1177/1477153511435961 |
| 8 | 2017 | Older People's Mobility and Mood in Urban (Tilley) | 129x | 10.3390/ijerph14020151 |
| 9 | 1982 | Privacy & Communication in Open-Plan Office (Sundstrom) | 127x | 10.1177/0013916582143007 |
| 10 | 2014 | Biophilic Site Office Buildings (Gray & Birrell) | 111x | 10.3390/ijerph111212204 |
