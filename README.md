
# 🕵️‍♂️ SkipTracer Pro — Cross-Referenced Address & City/State Edition

**SkipTracer Pro** is a modular, Python-based skip-tracing utility for gathering and cross-referencing public name, address, and contact data from multiple people-search sources (Spokeo, Whitepages, TruePeopleSearch, FastPeopleSearch, etc.).

It can:
- Crawl people-search engines.
- Extract names, phones, emails, and addresses.
- Cross-reference individuals by shared addresses.
- Filter results by city/state before crawling.
- Save, search, and export data from a local SQLite database.

---

## 🚀 Features

✅ Crawl multiple data sources simultaneously  
✅ Extract names, emails, phones, and physical addresses  
✅ Cross-reference shared addresses for linked identities  
✅ Exact city/state prefiltering to reduce false positives  
✅ Results stored locally in `skiptrace.db`  
✅ Optional CSV export (`skiptrace_export.csv`)  
✅ CLI with simple numbered options  

---

## ⚙️ Installation

**Requirements**
- Python 3.9 or later  
- Internet connection  
- Windows/macOS/Linux compatible  

### 1️⃣ Clone or download this repository

```bash
git clone https://github.com/yourusername/skiptracer-pro.git
cd skiptracer-pro
````

### 2️⃣ Set up your virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

Or, if `requirements.txt` is not present:

```bash
pip install requests beautifulsoup4
```

---

## 🧭 Usage

Run the CLI:

```bash
python skiptracer.py
```

You’ll see:

```
=== 🕵️‍♂️ SkipTracer Pro – City/State Filter Edition ===

Options:
 [1] Crawl all supported sites for a name (optional City/State filter)
 [2] Search database
 [3] Export all to CSV
 [4] Exit
```

---

### 🔍 Option 1 — Targeted Crawl by Full Name + City + State

Enter:

```
Full name: John Doe
City: Pasadena
State: CA
Max pages per site (default 3): 5
```

SkipTracer will:

* Build site-specific URLs (e.g. `https://www.spokeo.com/john-doe/pasadena-ca`)
* Crawl and extract visible public data
* Filter results by city/state pre-crawl
* Save records in `skiptrace.db`
* Display and optionally export to CSV

---

### 🗃️ Option 2 — Search Database

You can search any stored record:

```
Search term (name/email/phone/address): Pasadena
```

Results will include matched records with name, address, and source.

---

### 📤 Option 3 — Export Results

Exports all stored records into:

```
skiptrace_export.csv
```

Columns: `Source, Name, Email, Phone, Address, City, Zip, URL, Date Found`

---

## 🧩 Notes & Upcoming Features

Use this section to record ideas, tweaks, or feature plans as development evolves.

| Date       | Feature/Change                                | Notes/Status                                                        |
| ---------- | --------------------------------------------- | ------------------------------------------------------------------- |
| 2025-11-11 | Add fuzzy city/state matching                 | Consider using `rapidfuzz` or `difflib` for partial-match filtering |
| 2025-11-11 | Integrate Playwright for JS-rendered profiles | Allow optional full page rendering for dynamic content              |
| 2025-11-11 | Add deduplication by name + phone             | Avoid redundant rows across multiple sources                        |
| 2025-11-11 | Create GUI frontend                           | Simple Tkinter or web dashboard to view records                     |
| 2025-11-11 | Add export to JSON and Excel formats          | Extend `export_csv()`                                               |
| —          | —                                             | —                                                                   |

---

## 🧰 File Structure

```
skiptracer/
│
├── skiptracer.py           # main program (CLI, crawl, DB)
├── skiptrace.db            # SQLite database (auto-created)
├── skiptrace_export.csv    # optional export file
├── README.md               # this file
└── requirements.txt        # dependencies (optional)
```

---

## ⚖️ Legal Disclaimer

This project is for **educational and ethical research** purposes only.
You are solely responsible for complying with the **terms of service** and **privacy policies** of the data sources you access.
Do **not** use SkipTracer Pro for stalking, harassment, discrimination, or illegal investigations.

---

### 👨‍💻 Author Notes

Created by **Jeremy Engram**
Version: *City/State Filter Edition 1.0*
License: MIT

---

### 🗒️ Quick Add Notes Section

You can jot quick development notes right here:

```
- [ ] Improve regex precision for address parsing
- [ ] Filter out placeholder emails ("mail@example.com")
- [ ] Cache crawls per session to speed re-runs
- [ ] Add Google Maps reverse-lookup integration
```

---

```

---

Would you like me to include **auto-generated changelog support** (e.g., append new feature notes directly to README via Python updates)?  
That way, every time you refactor or add a feature, it updates this table automatically.
```
