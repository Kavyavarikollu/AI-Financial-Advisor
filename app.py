import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import re

st.title("💰 AI Financial Advisor Dashboard")

uploaded_files = st.file_uploader(
    "Upload Payment Screenshots",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
)

transactions = []

# -------- WORD TO NUMBER --------

number_words = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,
    "six":6,"seven":7,"eight":8,"nine":9,"ten":10,
    "twenty":20,"thirty":30,"forty":40,"fifty":50,
    "sixty":60,"seventy":70,"eighty":80,"ninety":90,
    "hundred":100,"thousand":1000
}

def words_to_number(text):
    words = text.lower().split()
    total = 0
    current = 0

    for word in words:
        if word in number_words:
            val = number_words[word]

            if val == 100:
                current *= val
            elif val == 1000:
                total += current * val
                current = 0
            else:
                current += val

    return total + current


# -------- AMOUNT DETECTION --------

def detect_amount(text):

    # 1️⃣ PRIORITY → words
    match_words = re.search(r'Rupees\s+(.*?)\s+Only', text, re.IGNORECASE)
    if match_words:
        return words_to_number(match_words.group(1))

    # 2️⃣ ₹ symbol
    match_rupee = re.search(r'₹\s*(\d+)', text)
    if match_rupee:
        return int(match_rupee.group(1))

    # 3️⃣ fallback numbers
    numbers = re.findall(r'\d{2,5}', text)
    numbers = [int(x) for x in numbers if 10 <= int(x) <= 5000]

    if numbers:
        return min(numbers) % 1000

    return None


# -------- MERCHANT --------

def detect_merchant(text):

    text_lower = text.lower()

    if "swiggy" in text_lower:
        return "Swiggy"
    elif "netflix" in text_lower:
        return "Netflix"
    elif "uber" in text_lower:
        return "Uber"
    elif "ola" in text_lower:
        return "Ola"

    match = re.search(r'To:\s*([A-Za-z ]+)', text)
    if match:
        return match.group(1).strip()

    return "Unknown"


# -------- CATEGORY --------

def detect_category(merchant):

    merchant = merchant.lower()

    if merchant in ["swiggy"]:
        return "Food"
    elif merchant in ["uber","ola"]:
        return "Transport"
    elif merchant in ["netflix"]:
        return "Entertainment"
    else:
        return "Transfer"


# -------- PROCESS --------

if uploaded_files:

    for file in uploaded_files:

        image = Image.open(file)
        st.image(image, caption=file.name)

        text = pytesseract.image_to_string(image)

        amount = detect_amount(text)
        merchant = detect_merchant(text)
        category = detect_category(merchant)

        transactions.append({
            "Merchant":merchant,
            "Amount":amount,
            "Category":category
        })


# -------- DASHBOARD --------

if transactions:

    df = pd.DataFrame(transactions)

    st.subheader("📊 All Transactions")
    st.write(df)

    total = df["Amount"].sum()

    st.header("💸 Total Amount Spent")
    st.write(f"₹ {total}")

    category_spending = df.groupby("Category")["Amount"].sum()

    st.header("📌 Category Spending")
    st.write(category_spending)

    fig, ax = plt.subplots()
    category_spending.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    plt.ylabel("")
    st.pyplot(fig)

    # -------- INSIGHTS --------

    st.header("📈 Spending Insights")

    highest = category_spending.idxmax()
    st.write(f"👉 You spend the most on: **{highest}**")

    # -------- ADVICE --------

    st.header("💡 Category Wise Advice")

    if highest == "Food":
        st.warning("Reduce food spending 🍔")
    elif highest == "Entertainment":
        st.warning("Reduce subscriptions 🎬")
    elif highest == "Transport":
        st.warning("Transport cost is high 🚗")
    else:
        st.info("Transfers detected")

    st.header("🧠 Overall Financial Advice")

    if total > 5000:
        st.error("Too much spending ⚠️")
    elif total > 2000:
        st.info("Moderate spending")
    else:
        st.success("Good control 👍")
