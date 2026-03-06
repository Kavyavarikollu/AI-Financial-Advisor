import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import re

st.title("AI Financial Advisor & Expense Manager")

uploaded_files = st.file_uploader(
    "Upload Payment Screenshots",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
)

transactions = []

# ---------------- AMOUNT DETECTION ----------------

def detect_merchant(text):

    text_lower = text.lower()

    # Known merchants
    if "swiggy" in text_lower:
        return "Swiggy"

    elif "zomato" in text_lower:
        return "Zomato"

    elif "netflix" in text_lower:
        return "Netflix"

    elif "uber" in text_lower:
        return "Uber"

    elif "ola" in text_lower:
        return "Ola"

    # Transfer merchant detection
    match = re.search(r'To:\s*([A-Za-z ]+)', text)

    if match:
        return match.group(1).strip()

    return "Unknown"


# ---------------- MERCHANT DETECTION ----------------

def detect_merchant(text):

    text = text.lower()

    if "swiggy" in text:
        return "Swiggy"

    elif "zomato" in text:
        return "Zomato"

    elif "netflix" in text:
        return "Netflix"

    elif "uber" in text:
        return "Uber"

    elif "ola" in text:
        return "Ola"

    else:
        merchant_match = re.search(r'To:\s*(.*)', text)

        if merchant_match:
            return merchant_match.group(1).strip()

    return "Unknown"


# ---------------- CATEGORY DETECTION ----------------

def detect_category(merchant):

    merchant = merchant.lower()

    if merchant in ["swiggy","zomato"]:
        return "Food"

    elif merchant in ["uber","ola"]:
        return "Transport"

    elif merchant in ["netflix","prime"]:
        return "Entertainment"

    else:
        return "Transfer"


# ---------------- MAIN PROCESS ----------------

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


    df = pd.DataFrame(transactions)

    st.subheader("All Transactions")
    st.write(df)

    total_spent = df["Amount"].sum()

    st.header("Total Amount Spent")
    st.write(f"₹ {total_spent}")

    category_spending = df.groupby("Category")["Amount"].sum()

    st.header("Category Spending")
    st.write(category_spending)

    # ---------------- CHART ----------------

    fig, ax = plt.subplots()

    category_spending.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    plt.title("Expense Distribution")
    plt.ylabel("")

    st.pyplot(fig)

    # ---------------- CATEGORY ADVICE ----------------

    st.header("Category Wise Advice")

    if "Food" in category_spending.index:

        if category_spending["Food"] > 2000:
            st.warning("You are spending a lot on food. Try reducing food delivery.")

        else:
            st.success("Food spending is under control.")

    if "Transport" in category_spending.index:

        if category_spending["Transport"] > 1500:
            st.warning("Transport expenses are high. Try public transport.")

        else:
            st.success("Transport spending looks reasonable.")

    if "Entertainment" in category_spending.index:

        if category_spending["Entertainment"] > 1000:
            st.warning("Entertainment spending is high. Review subscriptions.")

        else:
            st.success("Entertainment spending is balanced.")

    if "Transfer" in category_spending.index:
        st.info("Money transfers detected.")

    # ---------------- OVERALL ADVICE ----------------

    st.header("Overall Financial Advice")

    if total_spent > 5000:
        st.error("Your overall spending is high. Consider budgeting.")

    elif total_spent > 2000:
        st.info("Moderate spending. Track expenses carefully.")

    else:
        st.success("Great! Your spending is under control.")
