import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import re

st.title("AI Financial Advisor & Expense Manager")

uploaded_file = st.file_uploader(
    "Upload Payment Screenshot", type=["png", "jpg", "jpeg"]
)

# function to convert words to number
number_words = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,
    "seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,
    "thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,
    "seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,
    "thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,
    "eighty":80,"ninety":90,"hundred":100,"thousand":1000
}

def words_to_number(text):
    words = text.lower().split()
    total = 0
    current = 0

    for word in words:
        if word in number_words:
            value = number_words[word]

            if value == 100:
                current *= value
            elif value == 1000:
                total += current * value
                current = 0
            else:
                current += value

    return total + current


if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Receipt")

    # OCR extraction
    text = pytesseract.image_to_string(image)

    st.subheader("Extracted Text")
    st.write(text)

    amount_value = None

    # 1️⃣ Detect numeric amount
    match1 = re.search(r'=\s*(\d+)', text)
    if match1:
        amount_value = int(match1.group(1)) % 1000

    # 2️⃣ Detect number before Rupees
    if not amount_value:
        match2 = re.search(r'(\d+)\s*Rupees', text)
        if match2:
            amount_value = int(match2.group(1))

    # 3️⃣ Detect amount from words
    if not amount_value:
        word_match = re.search(r'Rupees\s+(.*?)\s+Only', text, re.IGNORECASE)
        if word_match:
            amount_value = words_to_number(word_match.group(1))

    # 4️⃣ Safe fallback
    if not amount_value:
        numbers = re.findall(r'\d{2,4}', text)
        numbers = [int(x) for x in numbers if 10 <= int(x) <= 2000]

        if numbers:
            amount_value = min(numbers)

    # Merchant detection
    merchant_match = re.search(r'To:\s*(.*)', text)

    if merchant_match:
        merchant = merchant_match.group(1).strip()
    else:
        merchant = "Unknown"

    st.subheader("Detected Details")
    st.write("Amount:", amount_value)
    st.write("Merchant:", merchant)

    # Categorization
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

    data = {
        "Merchant":[merchant],
        "Amount":[amount_value],
        "Category":[category]
    }

    df = pd.DataFrame(data)

    st.subheader("Transaction Data")
    st.write(df)

    category_counts = df["Category"].value_counts()

    fig, ax = plt.subplots()
    category_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)

    plt.title("Expense Distribution")
    plt.ylabel("")

    st.pyplot(fig)

    st.subheader("Financial Advice")

    if amount_value is None:
        st.warning("Could not detect amount clearly.")

    elif amount_value > 2000:
        st.warning("High expense detected. Consider reviewing your spending.")

    elif amount_value > 500:
        st.info("Moderate expense. Ensure it fits within your monthly budget.")

    else:
        st.success("Good spending control. Keep tracking your expenses!")
