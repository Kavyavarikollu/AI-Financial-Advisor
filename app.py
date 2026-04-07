import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance
import pandas as pd
from datetime import datetime
import re
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------------- PREPROCESS ----------------
def preprocess(image):
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(3)


# ---------------- CROP AMOUNT AREA ----------------
def crop_amount_area(image):
    width, height = image.size
    return image.crop((0, 0, width, height * 0.45))  # TOP AREA ONLY


# ---------------- OCR ----------------
def extract_text(image):
    image = preprocess(image)
    return pytesseract.image_to_string(image)


# ---------------- DETECT AMOUNT ----------------
def detect_amount(image):

    # 🔥 STEP 1: crop top area (MAIN FIX)
    cropped = crop_amount_area(image)
    text = extract_text(cropped)

    # STEP 2: ₹ detection
    rupee = re.findall(r'₹\s?(\d+)', text)
    if rupee:
        return int(rupee[0])

    # STEP 3: fallback only from cropped area
    nums = re.findall(r'\b\d{2,4}\b', text)

    for n in nums:
        val = int(n)
        if 100 <= val <= 5000:
            return val

    return 0


# ---------------- MERCHANT ----------------
def detect_merchant(text):

    text_lower = text.lower()

    if "swiggy" in text_lower:
        return "Swiggy"
    elif "netflix" in text_lower:
        return "Netflix"
    elif "amazon" in text_lower:
        return "Amazon"
    elif "google" in text_lower:
        return "Google Ads"

    match = re.search(r"to[:\s]+([A-Za-z]+(?:\s[A-Za-z]+)?)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    if "paytm" in text_lower or "upi" in text_lower:
        return "UPI Transfer"

    return "Unknown"


# ---------------- CATEGORY ----------------
def detect_category(merchant):
    merchant = merchant.lower()

    if merchant in ["swiggy"]:
        return "Food"
    elif merchant in ["netflix"]:
        return "Entertainment"
    else:
        return "Transfer"


# ---------------- UI ----------------

st.title("💰 AI Financial Advisor Dashboard (Final Winner Version)")

uploaded_files = st.file_uploader(
    "Upload Payment Screenshots",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# RESET
if st.button("Reset Data"):
    df = pd.DataFrame(columns=["Merchant", "Amount", "Category", "Date", "file_id"])
    df.to_csv("data.csv", index=False)
    st.success("Data cleared! Reload app.")

# LOAD
try:
    df = pd.read_csv("data.csv")
except:
    df = pd.DataFrame(columns=["Merchant", "Amount", "Category", "Date", "file_id"])

df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna()

# PROCESS
if uploaded_files:
    for file in uploaded_files:

        if file.name in df["file_id"].values:
            continue

        image = Image.open(file)
        st.image(image)

        full_text = extract_text(image)

        amount = detect_amount(image)
        merchant = detect_merchant(full_text)
        category = detect_category(merchant)

        new_row = {
            "Merchant": merchant,
            "Amount": amount,
            "Category": category,
            "Date": datetime.now(),
            "file_id": file.name
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

# SAVE
df.to_csv("data.csv", index=False)

# DISPLAY
st.header("📊 All Transactions")
st.dataframe(df)

if not df.empty:

    total = int(df["Amount"].sum())
    st.header(f"💸 Total Amount Spent: ₹{total}")

    category_spending = df.groupby("Category")["Amount"].sum()

    st.header("📌 Category Spending")
    st.dataframe(category_spending.reset_index())

    st.header("📊 Expense Distribution")
    fig, ax = plt.subplots()
    ax.pie(category_spending.values,
           labels=category_spending.index,
           autopct="%1.1f%%")
    st.pyplot(fig)

    highest = category_spending.idxmax()

    st.header("📈 Insights")
    st.write(f"You spend the most on: **{highest}**")

    save = int(category_spending.max() * 0.2)

    st.header("💡 Savings Suggestions")
    st.write(f"Reduce {highest} by 20% → Save ₹{save}")

    avg = df["Amount"].mean()
    pred = int(avg * len(df) * 1.2)

    st.header("🔮 Prediction")
    st.write(f"Next month expected spending: ₹{pred}")

    st.header("🎯 Budget Setting")
    budget = st.number_input("Enter Monthly Budget", min_value=0)

    if budget:
        if total > budget:
            st.error(f"Exceeded by ₹{total - int(budget)}")
        else:
            st.success("Within budget")