import csv
from urllib.parse import urlparse

def norm(s):
    return str(s or "").strip().lower().replace(" ", "_").replace("-", "_")

def parse_students(file_obj):
    reader = csv.DictReader(file_obj)
    if not reader.fieldnames:
        raise ValueError("CSV has no header row.")
    headers = {norm(h): h for h in reader.fieldnames}
    url_col = next((headers[k] for k in ("google_skills_profile_url","profile_url","google_skills_url","profile","url") if k in headers), None)
    if not url_col:
        raise ValueError("Required column: Google Skills Profile URL")
    name_col = next((headers[k] for k in ("student","name","student_name","full_name","candidate") if k in headers), None)
    email_col = next((headers[k] for k in ("email","email_address") if k in headers), None)
    info_col = next((headers[k] for k in ("[info]","info","notes","reference_info") if k in headers), None)
    result=[]
    for i,row in enumerate(reader,1):
        url=(row.get(url_col) or "").strip()
        if url:
            result.append({"Student":(row.get(name_col) or "").strip() if name_col else f"Profile {i}",
                "Email":(row.get(email_col) or "").strip() if email_col else "",
                "Profile_URL":url,"Reference_Info":(row.get(info_col) or "").strip() if info_col else ""})
    return result

def validate_students(students):
    issues=[]; seen=set()
    for row in students:
        p=urlparse(row["Profile_URL"])
        if p.scheme not in ("http","https") or p.netloc.lower() not in ("www.skills.google","skills.google") or not p.path.startswith("/public_profiles/"):
            issues.append(f"{row['Student']}: URL is not a standard Google Skills public profile URL.")
        if row["Profile_URL"] in seen:
            issues.append(f"Duplicate profile URL: {row['Student']}.")
        seen.add(row["Profile_URL"])
    return students, issues
