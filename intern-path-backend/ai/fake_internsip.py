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

    # 1️⃣ Payment related keywords
    payment_keywords = [
        "registration fee",
        "training fee",
        "security deposit",
        "pay ₹",
        "payment required",
        "course fee"
    ]
    for word in payment_keywords:
        if word in text:
            score += 3
            reasons.append("Asks for payment")
            break

    # 2️⃣ Public email domains
    if re.search(r"(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com)", text):
        score += 2
        reasons.append("Uses public email domain")

    # 3️⃣ Unrealistic salary detection (₹50000+ per month internship)
    high_salary = re.findall(r"₹\s?(\d{5,6})", text)
    if high_salary:
        for salary in high_salary:
            if int(salary) >= 50000:
                score += 2
                reasons.append("Suspiciously high salary for internship")
                break

    # 4️⃣ Urgency tactics
    urgency_words = [
        "apply immediately",
        "limited seats",
        "hurry up",
        "only today",
        "last chance"
    ]
    for word in urgency_words:
        if word in text:
            score += 1
            reasons.append("Uses urgency tactics")
            break

    # 5️⃣ WhatsApp contact only
    if "whatsapp" in text:
        score += 2
        reasons.append("WhatsApp-only contact")

    # 6️⃣ No proper company information
    if "about us" not in text and "our company" not in text:
        score += 1
        reasons.append("No clear company information")

    # 7️⃣ Suspicious buzzwords
    scam_words = [
        "easy money",
        "guaranteed job",
        "100% placement",
        "no interview",
        "earn daily"
    ]
    for word in scam_words:
        if word in text:
            score += 2
            reasons.append("Contains scam-like phrases")
            break

    # 8️⃣ Suspicious domain (new / random looking)
    domain = urlparse(url).netloc
    if len(domain.split(".")) > 3:
        score += 1
        reasons.append("Suspicious domain structure")

    # Final Risk Classification
    if score >= 7:
        risk = "High Risk"
    elif score >= 3:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    confidence = min(95, 50 + score * 5)

    return {
        "risk_level": risk,
        "risk_score": score,
        "confidence_percentage": confidence,
        "reasons": reasons if reasons else ["No major red flags detected"]
    }


def analyze_internship(url: str):
    text = scrape_website(url)

    if not text:
        return {
            "risk_level": "High Risk",
            "confidence_percentage": 90,
            "reasons": ["Unable to access website"]
        }

    return calculate_risk(text, url)