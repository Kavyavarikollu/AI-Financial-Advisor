# ==========================================
# IMPORTS
# ==========================================
import google.generativeai as genai
import streamlit as st
import pandas as pd
import numpy as np

from PIL import Image
import pytesseract

import matplotlib.pyplot as plt
import re
import io
from datetime import datetime

from sklearn.linear_model import LinearRegression

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
# ==========================================
# GEMINI CONFIGURATION
# ==========================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
st.write("Secret loaded successfully")

genai.configure(
    api_key=GEMINI_API_KEY
)

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide"
)



# ==========================================
# SESSION INITIALIZATION
# ==========================================

def init_session():

    if "transactions" not in st.session_state:

        st.session_state.transactions = []


    if "income" not in st.session_state:

        st.session_state.income = 0





# ==========================================
# CATEGORY PREDICTION
# ==========================================

def category_predict(merchant):

    merchant = str(merchant).lower()


    if any(
        x in merchant
        for x in [
            "swiggy",
            "zomato",
            "food",
            "restaurant"
        ]
    ):

        return "Food"



    elif any(
        x in merchant
        for x in [
            "uber",
            "ola",
            "metro",
            "bus"
        ]
    ):

        return "Transport"



    elif any(
        x in merchant
        for x in [
            "netflix",
            "prime",
            "movie"
        ]
    ):

        return "Entertainment"



    elif any(
        x in merchant
        for x in [
            "amazon",
            "flipkart",
            "shopping"
        ]
    ):

        return "Shopping"



    else:

        return "Transfer"






# ==========================================
# CREATE TRANSACTION
# ==========================================

def create_transaction(
        merchant,
        amount,
        date=None
):


    if date is None:

        date = datetime.now().strftime(
            "%Y-%m-%d"
        )



    return {

        "Merchant": merchant,

        "Amount": int(amount),

        "Category": category_predict(
            merchant
        ),

        "Date": date

    }





# ==========================================
# CSV PROCESSING
# ==========================================

def process_csv(file):


    df = pd.read_csv(file)



    if "Category" not in df.columns:

        df["Category"] = df["Merchant"].apply(
            category_predict
        )



    if "Date" not in df.columns:

        df["Date"] = datetime.now().strftime(
            "%Y-%m-%d"
        )



    return df






# ==========================================
# OCR FUNCTIONS
# ==========================================

def extract_text(image):

    return pytesseract.image_to_string(
        image
    )





def extract_amount(text):


    matches = re.findall(
        r'\d{2,6}',
        text
    )


    numbers = []


    for x in matches:

        value = int(x)


        if 10 <= value <= 100000:

            numbers.append(value)



    if numbers:

        return min(numbers)


    return 0






def detect_merchant(text):


    text = text.lower()



    merchants = {

        "swiggy":"Swiggy",

        "zomato":"Zomato",

        "uber":"Uber",

        "ola":"Ola",

        "netflix":"Netflix",

        "amazon":"Amazon"

    }



    for key,value in merchants.items():

        if key in text:

            return value



    return "Unknown"






def extract_date(text):


    pattern = r'\d{2}[/-]\d{2}[/-]\d{4}'


    result = re.search(
        pattern,
        text
    )


    if result:

        return result.group()



    return datetime.now().strftime(
        "%Y-%m-%d"
    )






# ==========================================
# ADD TRANSACTIONS
# ==========================================

def add_transactions(df):


    records = df.to_dict(
        "records"
    )


    st.session_state.transactions.extend(
        records
    )
    # ==========================================
# FINANCIAL DASHBOARD
# ==========================================

def dashboard(df):

    st.header(
        "📊 Financial Dashboard"
    )


    total = df["Amount"].sum()

    count = len(df)

    average = total / count if count > 0 else 0



    col1, col2, col3 = st.columns(3)



    with col1:

        st.metric(
            "💰 Total Spending",
            f"₹{total}"
        )



    with col2:

        st.metric(
            "📋 Transactions",
            count
        )



    with col3:

        st.metric(
            "📊 Average Expense",
            f"₹{average:.0f}"
        )





    # ==================================
    # INCOME AND BALANCE
    # ==================================


    st.subheader(
        "💵 Financial Balance"
    )


    income = st.number_input(

        "Enter Monthly Income",

        min_value=0,

        value=50000,

        key="income_input"

    )


    st.session_state.income = income



    balance = income - total



    col4, col5 = st.columns(2)



    with col4:

        st.metric(
            "Monthly Income",
            f"₹{income}"
        )


    with col5:

        st.metric(
            "Available Money",
            f"₹{balance}"
        )



    if balance < 0:

        st.error(
            "Your expenses are higher than your income!"
        )

    else:

        st.success(
            "You are within your income limit."
        )







    # ==================================
    # CATEGORY ANALYSIS
    # ==================================


    st.subheader(
        "📌 Category Spending"
    )


    category = (
        df.groupby("Category")
        ["Amount"]
        .sum()
    )


    st.dataframe(
        category,
        use_container_width=True
    )





    # ==================================
    # PIE CHART
    # ==================================


    fig1, ax1 = plt.subplots()


    category.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax1
    )


    ax1.set_ylabel("")


    st.pyplot(
        fig1
    )







    # ==================================
    # BAR CHART
    # ==================================


    fig2, ax2 = plt.subplots()


    category.plot(
        kind="bar",
        ax=ax2
    )


    ax2.set_xlabel(
        "Category"
    )


    ax2.set_ylabel(
        "Amount"
    )


    st.pyplot(
        fig2
    )







    # ==================================
    # SPENDING TREND
    # ==================================


    st.subheader(
        "📈 Spending Trends"
    )


    if "Date" in df.columns:


        df["Date"] = pd.to_datetime(
            df["Date"]
        )


        trend = (
            df.groupby("Date")
            ["Amount"]
            .sum()
        )


        fig3, ax3 = plt.subplots()


        trend.plot(
            marker="o",
            ax=ax3
        )


        ax3.set_title(
            "Daily Spending Trend"
        )


        st.pyplot(
            fig3
        )






    # ==================================
    # ANOMALY DETECTION
    # ==================================


    st.subheader(
        "🚨 Spending Anomaly Detection"
    )


    avg = df["Amount"].mean()



    anomalies = df[
        df["Amount"] > avg * 2
    ]



    if len(anomalies) > 0:


        st.warning(
            "Unusual expenses detected:"
        )


        st.dataframe(
            anomalies
        )



    else:


        st.success(
            "No unusual spending detected."
        )







    # ==================================
    # ML PREDICTION
    # ==================================


    st.subheader(
        "🤖 Future Spending Prediction"
    )


    if len(df) >= 3:


        data = df.copy()



        data["Index"] = range(
            len(data)
        )



        model = LinearRegression()



        model.fit(

            data[["Index"]],

            data["Amount"]

        )



        future_index = np.array(
            [[len(data)+1]]
        )



        prediction = model.predict(
            future_index
        )[0]



        st.info(

            f"Predicted next expense: ₹{prediction:.0f}"

        )



    else:


        st.info(
            "Add more transactions for ML prediction."
        )



    return total
    # ==========================================
# AI FINANCIAL ASSISTANT
# ==========================================
# ==========================================
# AI FINANCIAL ASSISTANT (GEMINI)
# ==========================================

def financial_chatbot(df):

    st.header(
        "🤖 AI Financial Assistant"
    )

    total = df["Amount"].sum()

    category = (
        df.groupby("Category")["Amount"]
        .sum()
        .to_dict()
    )

    income = st.session_state.get(
        "income",
        0
    )

    balance = income - total

    st.info(
        """
        Ask anything about your finances.

        Examples:

        • Analyze my spending habits

        • How can I save more money?

        • Which category is causing overspending?

        • Suggest an investment plan

        • Give me a monthly budget

        • How can I save ₹1 lakh in 1 year?
        """
    )

    question = st.text_input(
        "Ask your question",
        key="assistant_question"
    )

    if question:

        financial_summary = f"""

        USER FINANCIAL DATA

        Monthly Income: ₹{income}

        Total Spending: ₹{total}

        Remaining Balance: ₹{balance}

        Category-wise Spending:

        {category}

        Transaction Data:

        {df.to_string(index=False)}

        """

        prompt = f"""

        You are an expert AI Financial Advisor.

        Use Indian financial context.

        Provide practical advice.

        Explain clearly and simply.

        Do not give risky investment recommendations.

        Financial Data:

        {financial_summary}

        User Question:

        {question}

        """

        try:

            with st.spinner(
                "Analyzing finances..."
            ):

                response = gemini_model.generate_content(
                    prompt
                )

                st.success(
                    "AI Analysis"
                )

                st.write(
                    response.text
                )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )







# ==========================================
# INVESTMENT ADVISOR
# ==========================================

def investment_advisor():

    st.header(
        "📈 Investment Suggestions"
    )


    st.write(
        """
        Based on general financial planning:

        🟢 Low Risk:
        - Fixed Deposits
        - Government Bonds


        🟡 Medium Risk:
        - Mutual Funds
        - Index Funds


        🔴 Long Term:
        - Diversified Equity Investments


        Always consider your risk level before investing.
        """
    )







# ==========================================
# TAX SAVING ADVISOR
# ==========================================

def tax_saving_advisor():


    st.header(
        "📑 Tax Saving Suggestions"
    )


    income = st.number_input(

        "Annual Income",

        min_value=0,

        value=600000,

        key="tax_income_input"

    )



    if income > 0:


        st.write(
            "Possible tax saving options:"
        )


        st.info(
            """
            • ELSS Mutual Funds

            • Public Provident Fund (PPF)

            • National Pension System (NPS)

            • Insurance deductions
            """
        )







# ==========================================
# PDF REPORT CREATION
# ==========================================

def create_pdf(df):


    buffer = io.BytesIO()


    pdf = SimpleDocTemplate(
        buffer
    )


    styles = getSampleStyleSheet()


    content = []



    total = df["Amount"].sum()



    content.append(

        Paragraph(

            "AI Financial Advisor Report",

            styles["Heading1"]

        )

    )



    content.append(
        Spacer(
            1,
            20
        )
    )



    content.append(

        Paragraph(

            f"Total Spending: Rs {total}",

            styles["Normal"]

        )

    )



    category = (
        df.groupby("Category")
        ["Amount"]
        .sum()
    )



    for name,value in category.items():


        content.append(

            Paragraph(

                f"{name}: Rs {value}",

                styles["Normal"]

            )

        )



    pdf.build(
        content
    )



    buffer.seek(0)



    return buffer






# ==========================================
# REPORT SECTION
# ==========================================

def report_section(df):


    st.header(
        "📄 Financial Report"
    )


    pdf = create_pdf(
        df
    )


    st.download_button(

        "⬇ Download PDF Report",

        pdf,

        file_name="AI_Financial_Report.pdf",

        mime="application/pdf",

        key="pdf_report_download"

    )
    # ==========================================
# SMART FINANCIAL ADVICE
# ==========================================

def financial_advice(df):

    st.header("💡 Smart Financial Advice")

    total = df["Amount"].sum()

    category = (
        df.groupby("Category")["Amount"]
        .sum()
    )

    highest = category.idxmax()

    highest_amount = category.max()

    st.info(
        f"""
        Total Spending: ₹{total}

        Highest Spending Category:
        {highest}

        Amount:
        ₹{highest_amount}
        """
    )

    if highest == "Food":

        st.warning(
            "Food expenses are high. Try reducing online food orders."
        )

    elif highest == "Shopping":

        st.warning(
            "Shopping expenses are high. Review unnecessary purchases."
        )

    elif highest == "Entertainment":

        st.warning(
            "Entertainment expenses are high. Check subscriptions."
        )

    else:

        st.success(
            "Your spending pattern looks balanced."
        )
    # ==========================================
# MAIN APPLICATION
# ==========================================

def main():

    init_session()


    # ==============================
    # SIDEBAR
    # ==============================

    st.sidebar.title(
        "💰 AI Financial Advisor"
    )


    st.sidebar.info(
        "AI powered expense tracking and financial analysis"
    )


    page = st.sidebar.radio(

        "Navigation",

        [

            "🏠 Dashboard",

            "📂 Upload CSV",

            "📷 Upload Receipt",

            "🤖 AI Assistant",

            "📄 Reports"

        ],

        index=0,

        key="navigation_menu"

    )





    # ==============================
    # DASHBOARD FIRST PAGE
    # ==============================

    if page == "🏠 Dashboard":


        if len(st.session_state.transactions) > 0:


            df = pd.DataFrame(

                st.session_state.transactions

            )


            dashboard(df)


            st.divider()


            financial_advice(df)



        else:


            st.header(
                "💰 AI Financial Advisor"
            )


            st.write(
                """
                Welcome!

                Upload your expenses using CSV
                or scan payment screenshots
                to start your financial analysis.
                """
            )



    # ==============================
    # CSV UPLOAD
    # ==============================

    elif page == "📂 Upload CSV":


        st.header(
            "📂 Upload Expense CSV"
        )


        csv_file = st.file_uploader(

            "Choose CSV file",

            type=["csv"],

            key="csv_upload"

        )



        if csv_file:


            df = process_csv(
                csv_file
            )


            st.session_state.transactions = (

                df.to_dict("records")

            )


            st.success(
                "CSV uploaded successfully!"
            )


            st.subheader(
                "Transaction Preview"
            )


            st.dataframe(

                df,

                use_container_width=True

            )



            st.info(
                "Open Dashboard from sidebar to view analysis."
            )







    # ==============================
    # OCR RECEIPT UPLOAD
    # ==============================

    elif page == "📷 Upload Receipt":


        st.header(
            "📷 Payment Screenshot Scanner"
        )


        images = st.file_uploader(

            "Upload screenshots",

            type=[
                "png",
                "jpg",
                "jpeg"
            ],

            accept_multiple_files=True,

            key="receipt_upload"

        )



        if images:


            for file in images:


                image = Image.open(
                    file
                )


                st.image(

                    image,

                    caption=file.name,

                    width=500

                )



                text = extract_text(
                    image
                )


                amount = extract_amount(
                    text
                )


                merchant = detect_merchant(
                    text
                )


                date = extract_date(
                    text
                )



                transaction = create_transaction(

                    merchant,

                    amount,

                    date

                )



                st.session_state.transactions.append(

                    transaction

                )



                st.success(

                    f"Added: {merchant} ₹{amount}"

                )







    # ==============================
    # AI ASSISTANT
    # ==============================

    elif page == "🤖 AI Assistant":


        if len(st.session_state.transactions) > 0:


            df = pd.DataFrame(

                st.session_state.transactions

            )


            financial_chatbot(df)



        else:


            st.warning(
                "Upload expenses first."
            )







    # ==============================
    # REPORTS
    # ==============================

    elif page == "📄 Reports":



        if len(st.session_state.transactions) > 0:


            df = pd.DataFrame(

                st.session_state.transactions

            )


            investment_advisor()


            tax_saving_advisor()


            report_section(df)



        else:


            st.warning(
                "No transactions available."
            )







# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":

    main()
