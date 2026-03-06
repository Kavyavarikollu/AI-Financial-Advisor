import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import re

st.title("AI Financial Advisor & Expense Manager")

uploaded_file = st.file_uploader("Upload Payment Screenshot", type=["png","jpg","jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Receipt")

    # OCR TEXT EXTRACTION
    text = pytesseract.image_to_string(image)

    st.subheader("Extracted Text")
    st.write(text)

    # AMOUNT DETECTION
    amount_value = None

    match1 = re.search(r'=\s*(\d+)', text)
    if match1:
        amount_value = int(match1.group(1))

    if not amount_value:
        match2 = re.search(r'(\d+)\s*Rupees', text)
        if match2:
            amount_value = int(match2.group(1))

    # MERCHANT DETECTION
    merchant_match = re.search(r'To:\s*(.*)', text)

    if merchant_match:
        merchant = merchant_match.group(1).strip()
    else:
        merchant = "Unknown"

    st.subheader("Detected Details")
    st.write("Amount:", amount_value)
    st.write("Merchant:", merchant)

    # EXPENSE CATEGORIZATION
    merchant_lower = merchant.lower()

    if "swiggy" in merchant_lower or "zomato" in merchant_lower:
        category = "Food"
    elif "uber" in merchant_lower or "ola" in merchant_lower:
        category = "Transport"
    elif "amazon" in merchant_lower or "flipkart" in merchant_lower:
        category = "Shopping"
    elif "netflix" in merchant_lower or "prime" in merchant_lower:
        category = "Entertainment"
    else:
        category = "Transfer"

    # DATAFRAME
    data = {
        "Merchant":[merchant],
        "Amount":[amount_value],
        "Category":[category]
    }

    df = pd.DataFrame(data)

    st.subheader("Transaction Data")
    st.write(df)

    # EXPENSE VISUALIZATION
    category_counts = df["Category"].value_counts()

    fig, ax = plt.subplots()
    category_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)

    plt.title("Expense Distribution")
    plt.ylabel("")

    st.pyplot(fig)

    # FINANCIAL ADVICE
    st.subheader("Financial Advice")

    if amount_value and amount_value > 2000:
        st.warning("High expense detected. Consider reviewing your spending and setting a monthly budget.")
    elif amount_value and amount_value > 500:
        st.info("Moderate expense. Make sure this fits within your planned monthly expenses.")
    else:
        st.success("Good spending control. Keep tracking your expenses regularly!")
