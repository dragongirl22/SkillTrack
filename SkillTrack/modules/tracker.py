import time
from datetime import datetime
from modules.profile_scraper import fetch_profile, extract_profile_data, ProfileError, RateLimitError

def status(count, required):
    if count>=required: return "Completed"
    if count==0: return "No badges yet"
    return "In progress"

def build_demo_results(students, required):
    counts=[10,6,0,None,4,8]; out=[]
    for i,row in enumerate(students):
        n=counts[i%len(counts)]
        out.append({"Student":row["Student"],"Profile name":"","Email":row["Email"],"Profile URL":row["Profile_URL"],
            "Badges":n,"Progress":f"{round(n/required*100)}%" if n is not None else "—",
            "Status":status(n,required) if n is not None else "Demo unavailable",
            "Reference note":row["Reference_Info"],"Checked":"DEMO — not verified","Details":"Fictional demo value only"})
    return out

def verify_students(students, required, delay_seconds=3, retries=2):
    out=[]
    for i,row in enumerate(students):
        count=None; profile_name=""; state="Could not verify"; details=""
        reference_note = (row.get("Reference_Info") or "").strip()
        # Some campaign CSVs include an administrator-supplied note identifying
        # profiles that have since become private. Use it transparently as
        # supplied evidence rather than pretending Google independently confirmed it.
        private_hint = "private" in reference_note.lower()
        if private_hint:
            state="Private profile"
            details="CSV reference note indicates this account is private; badges are not counted. Recheck if the profile is made public."
        else:
            try:
                data=extract_profile_data(fetch_profile(row["Profile_URL"],retries=retries))
                count=data["badge_count"]; profile_name=data["display_name"]; state=status(count,required)
                details="Counted explicit earned-date labels in returned profile HTML."
            except RateLimitError as exc:
                state="Rate limited"; details=str(exc)
            except ProfileError as exc:
                details=str(exc)
                if "PRIVATE_PROFILE:" in details:
                    state="Private profile"
                    details=details.replace("PRIVATE_PROFILE: ", "")
                elif "unavailable" in details.lower():
                    state="Unavailable"
                else:
                    state="Could not verify"
            except Exception as exc:
                details=f"Unexpected error: {exc}"
        student_name = row["Student"]
        if student_name.startswith("Profile ") and profile_name:
            student_name = profile_name
        out.append({"Student":student_name,"Profile name":profile_name,"Email":row["Email"],"Profile URL":row["Profile_URL"],
            "Badges":count,"Progress":f"{round(count/required*100)}%" if count is not None else "—","Status":state,
            "Reference note":reference_note,"Checked":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Details":details})
        if i<len(students)-1: time.sleep(delay_seconds)
    return out
