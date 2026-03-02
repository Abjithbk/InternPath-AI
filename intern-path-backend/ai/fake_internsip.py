import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def scrape_website(url: str):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ").lower()
        return text
    except Exception:
        return None

def calculate_risk(text: str, url: str):
    score = 0
    reasons = []
    safe_reasons = []

    # 1️⃣ Payment related keywords
    payment_keywords = [
        "registration fee",
        "training fee",
        "security deposit",
        "pay ₹",
        "payment required",
        "course fee"
    ]
    if any(word in text for word in payment_keywords):
        score += 3
        reasons.append("Asks for payment or course fee")
    else:
        safe_reasons.append("No payment required")

    # 2️⃣ Public email domains
    if re.search(r"(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com)", text):
        score += 2
        reasons.append("Uses public email domain (not official company email)")
    else:
        safe_reasons.append("Official/company email present")

    # 3️⃣ Unrealistic salary detection (₹50000+ per month)
    high_salary = re.findall(r"₹\s?(\d{5,6})", text)
    if high_salary:
        for salary in high_salary:
            if int(salary) >= 50000:
                score += 2
                reasons.append("Suspiciously high salary for internship")
                break
        else:
            safe_reasons.append("Salary seems realistic")
    else:
        safe_reasons.append("Salary mentioned and seems reasonable")

    # 4️⃣ Urgency tactics
    urgency_words = [
        "apply immediately",
        "limited seats",
        "hurry up",
        "only today",
        "last chance"
    ]
    if any(word in text for word in urgency_words):
        score += 1
        reasons.append("Uses urgency tactics to rush applicants")
    else:
        safe_reasons.append("No urgency tactics used")

    # 5️⃣ WhatsApp contact only
    if "whatsapp" in text and not re.search(r"(@|\.)", text):
        score += 2
        reasons.append("Only WhatsApp contact provided, no email or official contact")
    else:
        safe_reasons.append("Other contact methods available")

    # 6️⃣ Company info
    if "about us" not in text and "our company" not in text:
        score += 1
        reasons.append("No clear company information provided")
    else:
        safe_reasons.append("Company information is available")

    # 7️⃣ Suspicious buzzwords
    scam_words = [
        "easy money",
        "guaranteed job",
        "100% placement",
        "no interview",
        "earn daily"
    ]
    found_scam = [word for word in scam_words if word in text]
    if found_scam:
        score += 2
        reasons.append(f"Contains suspicious phrases like {', '.join(found_scam)}")
    else:
        safe_reasons.append("No scammy buzzwords detected")

    # 8️⃣ Domain check
    domain = urlparse(url).netloc
    if len(domain.split(".")) > 3 or re.match(r"[a-z0-9]{10,}", domain.split(".")[0]):
        score += 1
        reasons.append("Suspicious or unusual domain structure")
    else:
        safe_reasons.append("Domain looks legitimate")

    # Final Risk Classification
    if score >= 7:
        risk = "High Risk"
    elif score >= 3:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    confidence = min(95, 50 + score * 5)

    # Combine reasons with safe signals
    all_reasons = reasons + safe_reasons if safe_reasons else reasons
    if not all_reasons:
        all_reasons = ["No major red flags detected"]

    return {
        "risk_level": risk,
        "risk_score": score,
        "confidence_percentage": confidence,
        "reasons": all_reasons
    }

def analyze_internship(url: str):
    text = scrape_website(url)
    if not text:
        return {
            "risk_level": "High Risk",
            "confidence_percentage": 90,
            "reasons": ["Unable to access website, treat as suspicious"]
        }
    return calculate_risk(text, url)