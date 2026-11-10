import re, time, requests
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

class ProfileError(Exception): pass
class RateLimitError(ProfileError): pass

def valid_url(url):
    p=urlparse(str(url).strip())
    return p.scheme in ("http","https") and p.netloc.lower() in ("www.skills.google","skills.google") and p.path.startswith("/public_profiles/")

def retry_after(value, fallback):
    if not value: return fallback
    try: return max(1,min(300,int(value)))
    except ValueError:
        try: return max(1,min(300,int((parsedate_to_datetime(value)-datetime.now(parsedate_to_datetime(value).tzinfo)).total_seconds())))
        except Exception: return fallback

def fetch_profile(url, retries=2, timeout=20):
    if not valid_url(url): raise ProfileError("Invalid Google Skills public profile URL.")
    headers={"User-Agent":"SkillTrack-LearnWithCommunities/1.0","Accept":"text/html,application/xhtml+xml"}
    last=None
    with requests.Session() as session:
        for attempt in range(retries+1):
            try:
                r=session.get(url,headers=headers,timeout=timeout)
                if r.status_code==429:
                    wait=retry_after(r.headers.get("Retry-After"),30*(attempt+1))
                    if attempt>=retries: raise RateLimitError(f"HTTP 429. Stopped retrying; suggested wait {wait}s.")
                    time.sleep(wait); continue
                if r.status_code in (401, 403):
                    raise ProfileError("PRIVATE_PROFILE: This Google Skills profile is private or access-restricted. Badges cannot be verified.")
                if r.status_code in (404, 410):
                    raise ProfileError(f"Profile unavailable (HTTP {r.status_code}).")
                r.raise_for_status()
                return r.text
            except (ProfileError,RateLimitError): raise
            except requests.RequestException as exc:
                last=exc
                if attempt>=retries: break
                time.sleep(min(2**attempt,8))
    raise ProfileError(f"Network request failed: {last}")

EARNED=re.compile(r"\bEarned\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b",re.I)

def extract_profile_data(html):
    from html.parser import HTMLParser
    class Parser(HTMLParser):
        def __init__(self): super().__init__(); self.text=[]; self.title=[]; self.in_title=False
        def handle_starttag(self,tag,attrs):
            if tag.lower()=="title": self.in_title=True
        def handle_endtag(self,tag):
            if tag.lower()=="title": self.in_title=False
        def handle_data(self,data):
            s=data.strip()
            if s:
                self.text.append(s)
                if self.in_title: self.title.append(s)
    p=Parser(); p.feed(html)
    text=" ".join(p.text); title=" ".join(p.title)
    combined=(text+" "+title).lower()
    private_markers=("this profile is private", "profile is private", "private profile", "not publicly available", "this user has chosen to keep their profile private")
    if any(marker in combined for marker in private_markers):
        raise ProfileError("PRIVATE_PROFILE: This Google Skills profile is private. Badges cannot be verified.")
    count=len(EARNED.findall(text))
    markers=("member since","league","points","public profile","skills.google")
    if count==0 and not any(x in (text+" "+title).lower() for x in markers):
        raise ProfileError("Could not identify readable public profile content in returned HTML.")
    return {"display_name":title,"badge_count":count}
