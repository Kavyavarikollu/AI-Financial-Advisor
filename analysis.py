import pandas as pd

def get_total(df):
    return df["Amount"].sum()

def get_category_spending(df):
    return df.groupby("Category")["Amount"].sum()

def get_highest_category(category_spending):
    return category_spending.idxmax()

def get_prediction(df):
    avg = df["Amount"].mean()
    return int(avg * len(df) * 1.2)

def get_savings(category_spending, highest):
    return int(category_spending[highest] * 0.2)

def get_goal_plan(goal, total):
    monthly = int(goal / 10)
    return monthly