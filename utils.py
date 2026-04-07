import pytesseract
from PIL import Image, ImageEnhance
import re

# Set path if needed (Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -------------------------------
# PREPROCESS IMAGE (VERY IMPORTANT)
# -------------------------------
def preprocess_image(image):
    image = image.convert('L')  # grayscale

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # increase contrast

    return image


# -------------------------------
# EXTRACT TEXT
# -------------------------------
def extract_text(image):
    processed = preprocess_image(image)
    return pytesseract.image_to_string(processed)


# -------------------------------
# EXTRACT AMOUNT (STRONG LOGIC)
# -------------------------------
def extract_amount(image):
    text = extract_text(image)

    print("OCR TEXT:", text)  # DEBUG

    # Try ₹ values first
    rupee_matches = re.findall(r'₹\s?\d+[.,]?\d*', text)

    amounts = []

    for amt in rupee_matches:
        amt = amt.replace("₹", "").replace(",", "").strip()
        try:
            value = float(amt)
            if value > 50:
                amounts.append(value)
        except:
            continue

    # Fallback
    if not amounts:
        generic_matches = re.findall(r'\d+[.,]\d+|\d+', text)

        for amt in generic_matches:
            try:
                value = float(amt)
                if value > 100:  # stricter filter
                    amounts.append(value)
            except:
                continue

    if amounts:
        return int(max(amounts))

    return 0


# -------------------------------
# MERCHANT
# -------------------------------
def extract_merchant(text):
    text = text.lower()

    if "swiggy" in text:
        return "Swiggy"
    elif "netflix" in text:
        return "Netflix"
    elif "amazon" in text:
        return "Amazon"
    elif "google" in text:
        return "Google Ads"
    elif "uber" in text:
        return "Uber"
    elif "ola" in text:
        return "Ola"
    elif "bhim" in text:
        return "UPI Transfer"
    else:
        return "Unknown"


# -------------------------------
# CATEGORY
# -------------------------------
def categorize(merchant):
    merchant = merchant.lower()

    if merchant in ["swiggy", "zomato"]:
        return "Food"
    elif merchant in ["netflix", "prime", "spotify"]:
        return "Entertainment"
    elif merchant in ["uber", "ola"]:
        return "Transport"
    elif merchant in ["amazon", "flipkart"]:
        return "Shopping"
    else:
        return "Transfer"


# -------------------------------
# MAIN
# -------------------------------
def process_image(image):
    text = extract_text(image)

    amount = extract_amount(image)
    merchant = extract_merchant(text)
    category = categorize(merchant)

    return {
        "merchant": merchant,
        "amount": amount,
        "category": category
    }