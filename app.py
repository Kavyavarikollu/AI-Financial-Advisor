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

    text = pytesseract.image_to_string(image)

    st.subheader("Extracted Text")
    st.write(text)

    amount_value = None

    match1 = re.search(r'=\s*(\d+)', text)
    if match1:
        amount_value = int(match1.group(1))

    merchant_match = re.search(r'To:\s*(.*)', text)

    if merchant_match:
        merchant = merchant_match.group(1).strip()
    else:
        merchant = "Unknown"

    st.subheader("Detected Details")
    st.write("Amount:", amount_value)
    st.write("Merchant:", merchant)

    data = {
        "Merchant":[merchant],
        "Amount":[amount_value],
        "Category":["Transfer"]
    }

    df = pd.DataFrame(data)

    st.write(df)

    category_counts = df["Category"].value_counts()

    fig, ax = plt.subplots()
    category_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)

    st.pyplot(fig)
