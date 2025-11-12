import os, re, csv, sqlite3, requests
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote_plus
from collections import deque, defaultdict
from bs4 import BeautifulSoup

DB_FILE = "skiptrace.db"

# ================================================================
# 🗃️ Database
# ================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, url TEXT, name TEXT, email TEXT, phone TEXT,
            address TEXT, city TEXT, zip_code TEXT, date_found TEXT
        )
    """)
    conn.commit(); conn.close()

def save_to_db(records):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor(); new_count = 0
    for r in records:
        c.execute("""SELECT 1 FROM records WHERE url=? AND name=? AND address=?""",
                  (r['url'], r['name'], r['address']))
        if not c.fetchone():
            c.execute("""
                INSERT INTO records
                (source,url,name,email,phone,address,city,zip_code,date_found)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (r['source'], r['url'], r['name'], r['email'], r['phone'],
                  r['address'], r['city'], r['zip_code'],
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            new_count += 1
    conn.commit(); conn.close()
    print(f"💾 Saved {new_count} new records to {DB_FILE}")

def search_db(term):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    like = f"%{term}%"
    c.execute("""SELECT source,name,email,phone,address,city,zip_code,url,date_found
                 FROM records
                 WHERE name LIKE ? OR city LIKE ? OR address LIKE ? OR zip_code LIKE ?
                 ORDER BY date_found DESC""",
              (like, like, like, like))
    rows = c.fetchall(); conn.close()
    if not rows: print(f"🔍 No matches for '{term}'"); return
    print(f"\n🔍 Results for '{term}':")
    for src,n,e,p,a,ct,z,u,d in rows:
        print(f" [{src}] {n or '-'} | {e or '-'} | {p or '-'} | "
              f"{a or '-'}, {ct or '-'} {z or '-'} | {u} | {d}")

# ================================================================
# 🧠 Extraction
# ================================================================
NAME = re.compile(r"\b[A-Z][a-z]+(?:\s[A-Z]\.)?\s[A-Z][a-z]+\b")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
ADDR = re.compile(r"\b\d{1,5}\s(?:[A-Za-z0-9#.\-]+\s){1,5}"
                  r"(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b", re.I)
CITY = re.compile(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s[A-Z]{2}\b")
ZIP = re.compile(r"\b\d{5}(?:-\d{4})?\b")

def extract_entities(text):
    return (set(NAME.findall(text)),
            set(EMAIL.findall(text)),
            set(PHONE.findall(text)),
            set(ADDR.findall(text)),
            set(CITY.findall(text)),
            set(ZIP.findall(text)))

def get_visible_text(html):
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script","style","noscript"]): t.extract()
    return s.get_text(" ", strip=True)

# ================================================================
# 🌐 Crawl
# ================================================================
def fetch_html(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        if "text/html" in r.headers.get("Content-Type",""): return r.text
    except Exception as e: print(f"⚠️ {url}: {e}")
    return ""

def crawl(url, label, max_pages=3):
    seen, q, out = set(), deque([url]), []
    while q and len(seen) < max_pages:
        u = q.popleft()
        if u in seen: continue
        seen.add(u); print(f"\n🌐 Crawling: {u}")
        html = fetch_html(u)
        if not html: continue
        txt = get_visible_text(html)
        n,e,p,a,c,z = extract_entities(txt)
        for name in n or [""]:
            rec = {"source":label,"url":u,"name":name,
                   "email":next(iter(e),""),
                   "phone":next(iter(p),""),
                   "address":next(iter(a),""),
                   "city":next(iter(c),""),
                   "zip_code":next(iter(z),"")}
            out.append(rec)
            print(f" 🔹 {rec['name']} | {rec['email'] or '-'} | {rec['phone'] or '-'} | "
                  f"{rec['address'] or '-'}, {rec['city'] or '-'} {rec['zip_code'] or '-'}")
        soup = BeautifulSoup(html,"html.parser")
        for l in soup.find_all("a",href=True):
            nu = urljoin(u,l["href"])
            if urlparse(nu).scheme in ["http","https"] and nu not in seen:
                q.append(nu)
    print(f"\n📊 {label} crawl complete. {len(out)} records.")
    return out

# ================================================================
# 🔍 Sites & Cross-ref
# ================================================================
SITES = {
    "Spokeo":"https://www.spokeo.com/%s",
    "Whitepages":"https://www.whitepages.com/name/%s",
    "TruePeopleSearch":"https://www.truepeoplesearch.com/results?name=%s",
    "FastPeopleSearch":"https://www.fastpeoplesearch.com/name/%s",
}

def cross_reference(records):
    groups = defaultdict(list)
    for r in records:
        a = r.get("address","").lower()
        if a: groups[a].append(r)
    matches = {k:v for k,v in groups.items() if len(v)>1}
    if not matches: print("\n⚠️ No shared addresses found."); return
    print("\n🏠 Cross-Referenced Addresses:")
    for a,rs in matches.items():
        print(f"\n📍 {a.title()} ({len(rs)} people):")
        for r in rs:
            print(f"  - {r['name']} ({r['source']}) | {r['phone']} | {r['url']}")
    return matches

def filter_by_city_state(records, city, state):
    """Keep only results matching city/state substrings."""
    if not city and not state: return records
    filt = []
    city = (city or "").lower(); state = (state or "").lower()
    for r in records:
        text = f"{r['city']} {r['address']}".lower()
        if (not city or city in text) and (not state or state in text):
            filt.append(r)
    print(f"📍 Filtered {len(filt)} / {len(records)} matching {city.title()} {state.upper()}")
    return filt

# ================================================================
# 📤 Export
# ================================================================
def export_csv(rows):
    if not rows: print("⚠️ Nothing to export."); return
    with open("skiptrace_export.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Source","Name","Email","Phone","Address","City","Zip","URL"])
        for r in rows: w.writerow([r[k] for k in
            ("source","name","email","phone","address","city","zip_code","url")])
    print("📄 Exported skiptrace_export.csv")

# ================================================================
# 🚀 CLI
# ================================================================
def main():
    print("=== 🕵️‍♂️ SkipTracer Pro – City/State Filter Edition ===")
    init_db()
    while True:
        print("\nOptions:")
        print(" [1] Crawl all supported sites for a name (optional City/State filter)")
        print(" [2] Search database")
        print(" [3] Export all to CSV")
        print(" [4] Exit")
        choice = input("\nEnter choice: ").strip()

        if choice=="1":
            name = input("Full name: ").strip()
            if not name: print("⚠️ Name required."); continue
            city = input("Optional City filter: ").strip()
            state = input("Optional State filter (e.g. CA): ").strip()
            maxp = input("Max pages per site (default 3): ").strip()
            maxp = int(maxp) if maxp.isdigit() else 3

            encoded = quote_plus(name)
            allrec=[]
            for lbl,urlp in SITES.items():
                url=urlp%encoded; print(f"\n🚀 {lbl}: {url}")
                rec=crawl(url,lbl,max_pages=maxp)
                allrec.extend(rec)
            # Filter by City/State before save
            filtered = filter_by_city_state(allrec,city,state)
            save_to_db(filtered)
            cross_reference(filtered)
            if input("Export to CSV? (y/n): ").lower()=="y":
                export_csv(filtered)

        elif choice=="2":
            term=input("Search term: ").strip()
            if term: search_db(term)
        elif choice=="3":
            conn=sqlite3.connect(DB_FILE); c=conn.cursor()
            c.execute("SELECT source,name,email,phone,address,city,zip_code,url FROM records")
            rows=[dict(zip([d[0] for d in c.description],r)) for r in c.fetchall()]
            conn.close(); export_csv(rows)
        elif choice=="4":
            print("👋 Goodbye."); break
        else: print("⚠️ Invalid option.")

if __name__=="__main__":
    main()
