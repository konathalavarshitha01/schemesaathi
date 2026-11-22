import re

FIELDS = ["age", "income", "category", "occupation", "gender"]

LAKH = re.compile(r"(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?|\u0c32\u0c15\u0c4d\u0c37|\u0932\u093e\u0916)", re.I)
BIGNUM = re.compile(r"(?<![\d,])(\d{1,3}(?:,\d{2,3})+|\d{5,8})(?![\d,])")
AGE1 = re.compile(r"(\d{1,2})\s*(?:years?|yrs?|yo|ella|ellu|saal|sal|varshalu)\b", re.I)
AGE2 = re.compile(r"\bage\D{0,3}(\d{1,2})\b", re.I)
CAT = re.compile(r"\b(sc|st|bc|obc|oc)\b", re.I)

STUDENT = ["student", "degree", "college", "btech", "b.tech", "intermediate",
           "studying", "chaduv", "school", "diploma", "polytechnic",
           "\u0c35\u0c3f\u0c26\u0c4d\u0c2f\u0c3e\u0c30\u0c4d\u0c25\u0c3f", "\u091b\u093e\u0924\u094d\u0930"]
FARMER = ["farmer", "raithu", "rythu", "vyavasayam", "kisan",
          "\u0c30\u0c48\u0c24\u0c41", "\u0915\u093f\u0938\u093e\u0928"]
FEMALE = ["female", "woman", "girl", "ammayi", "ammai", "mahila", "ladki",
          "\u0c05\u0c2e\u0c4d\u0c2e\u0c3e\u0c2f\u0c3f", "\u0932\u0921\u093c\u0915\u0940"]
MALE_WORDS = ["boy", "abbayi", "ladka"]
MALE_RE = re.compile(r"\b(male|man)\b", re.I)

QUESTIONS = {
    "age": {"en": "How old are you?", "te": "Mee vayasu entha?", "hi": "Aapki umar kitni hai?"},
    "income": {"en": "What is your family's yearly income?", "te": "Mee kutumba varshika adayam entha?", "hi": "Aapke parivar ki salana aay kitni hai?"},
    "category": {"en": "Which category are you (SC/ST/BC/OC)?", "te": "Mee category emiti (SC/ST/BC/OC)?", "hi": "Aapki category kya hai (SC/ST/BC/OC)?"},
    "occupation": {"en": "Are you a student or a farmer?", "te": "Meeru student aa leka raithu aa?", "hi": "Kya aap student hain ya kisan?"},
    "gender": {"en": "Are you male or female?", "te": "Meeru abbayi aa ammayi aa?", "hi": "Kya aap ladka hain ya ladki?"},
}

def extract_profile(message, existing=None):
    """Pull age, income, category, occupation, gender out of free text.
    Values found now override old ones; anything not found is kept."""
    profile = dict(existing or {})
    t = message.lower()

    m = AGE1.search(t) or AGE2.search(t)
    if m and 3 <= int(m.group(1)) <= 90:
        profile["age"] = int(m.group(1))

    m = LAKH.search(t)
    if m:
        profile["income"] = int(float(m.group(1)) * 100000)
    else:
        m = BIGNUM.search(t)
        if m:
            profile["income"] = int(m.group(1).replace(",", ""))

    m = CAT.search(t)
    if m:
        profile["category"] = m.group(1).upper()

    if any(w in t for w in STUDENT):
        profile["occupation"] = "student"
    elif any(w in t for w in FARMER):
        profile["occupation"] = "farmer"

    if any(w in t for w in FEMALE):
        profile["gender"] = "female"
    elif any(w in t for w in MALE_WORDS) or MALE_RE.search(t):
        profile["gender"] = "male"

    return profile

def missing_fields(profile):
    return [f for f in FIELDS if profile.get(f) is None]

def follow_up(missing, language="en"):
    lang = language if language in ("en", "te", "hi") else "en"
    return " ".join(QUESTIONS[f][lang] for f in missing) if missing else None

# ---- Telugu / Hindi script support (for voice input) ----
_base_extract = extract_profile

AGE_SCRIPT = re.compile(r"(\d{1,2})\s*(?:\u0c38\u0c02\u0c35\u0c24\u0c4d\u0c38\u0c30|\u0c0f\u0c33\u0c4d|\u0938\u093e\u0932|\u0935\u0930\u094d\u0937)")
AGE_SCRIPT2 = re.compile(r"(?:\u0c35\u0c2f\u0c38\u0c41|\u0909\u092e\u094d\u0930)\D{0,3}(\d{1,2})")
CAT_SCRIPT = [
    ("OBC", ["\u0913\u092c\u0940\u0938\u0940"]),
    ("SC", ["\u0c0e\u0c38\u0c4d\u0c38\u0c40", "\u090f\u0938\u0938\u0940"]),
    ("ST", ["\u0c0e\u0c38\u0c4d\u0c1f\u0c40", "\u090f\u0938\u091f\u0940"]),
    ("BC", ["\u0c2c\u0c40\u0c38\u0c40", "\u092c\u0940\u0938\u0940"]),
    ("OC", ["\u0c13\u0c38\u0c40"]),
]
STUDENT_SCRIPT = ["\u0c1a\u0c26\u0c41\u0c35", "\u0c21\u0c3f\u0c17\u0c4d\u0c30\u0c40", "\u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40",
                  "\u092a\u0922", "\u092a\u095d", "\u0921\u093f\u0917\u094d\u0930\u0940", "\u0915\u0949\u0932\u0947\u091c"]
FEMALE_SCRIPT = ["\u0932\u095c\u0915\u0940"]
MALE_SCRIPT = ["\u0c05\u0c2c\u0c4d\u0c2c\u0c3e\u0c2f\u0c3f", "\u0932\u095c\u0915\u093e", "\u0932\u0921\u093c\u0915\u093e"]

def extract_profile(message, existing=None):
    profile = _base_extract(message, existing)
    m = AGE_SCRIPT.search(message) or AGE_SCRIPT2.search(message)
    if m and 3 <= int(m.group(1)) <= 90:
        profile["age"] = int(m.group(1))
    for cat, words in CAT_SCRIPT:
        if any(w in message for w in words):
            profile["category"] = cat
            break
    if any(w in message for w in STUDENT_SCRIPT):
        profile["occupation"] = "student"
    if any(w in message for w in FEMALE_SCRIPT):
        profile["gender"] = "female"
    elif any(w in message for w in MALE_SCRIPT):
        profile["gender"] = "male"
    return profile

# ---- bare number reply (e.g. "varshitha 18") counts as age when age is missing ----
_prev_extract = extract_profile
BARE_AGE = re.compile(r"(?<![\d,.])(\d{1,2})(?![\d,.]|\s*(?:lakhs?|lacs?))", re.I)

def extract_profile(message, existing=None):
    profile = _prev_extract(message, existing)
    if profile.get("age") is None:
        m = BARE_AGE.search(message)
        if m and 3 <= int(m.group(1)) <= 90:
            profile["age"] = int(m.group(1))
    return profile

# ---- income shortcuts: 1lk, 1.5 lk, one lakh, 50k, 50 thousand ----
_prev_income = extract_profile
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
             "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
INC = re.compile(r"(\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten)\s*(lakhs?|lacs?|lks?|thousand|k)\b", re.I)

def extract_profile(message, existing=None):
    income = None
    cleaned = message
    m = INC.search(message)
    if m:
        raw = m.group(1).lower()
        num = NUM_WORDS[raw] if raw in NUM_WORDS else float(raw)
        mult = 1000 if m.group(2).lower() in ("thousand", "k") else 100000
        income = int(num * mult)
        cleaned = message[:m.start()] + " " + message[m.end():]
    profile = _prev_income(cleaned, existing)
    if income is not None:
        profile["income"] = income
    elif profile.get("income") is None and (existing or {}).get("age") is not None:
        # age already known and the reply is just a small number: treat it as lakhs
        s = message.strip()
        if re.fullmatch(r"\d{1,2}(\.\d+)?", s) and 0 < float(s) <= 50:
            profile["income"] = int(float(s) * 100000)
    return profile

# ---- state detection: AP / Telangana ----
_prev_state = extract_profile
STATE_TS = re.compile(r"\b(ts|telangana|hyderabad|warangal)\b", re.I)
STATE_AP = re.compile(r"\b(ap|andhra|andhra pradesh|vijayawada|guntur|visakhapatnam|vizag|tirupati)\b", re.I)

def extract_profile(message, existing=None):
    profile = _prev_state(message, existing)
    if STATE_TS.search(message):
        profile["state"] = "TS"
    elif STATE_AP.search(message):
        profile["state"] = "AP"
    return profile
