import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# DB接続
conn = sqlite3.connect("kaji.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS kaji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    task TEXT,
    person TEXT
)
""")
conn.commit()

st.title("家事実績入力アプリ")

task = st.selectbox("家事の種類", ["🍳料理", "🫗皿洗い", "👕洗濯", "🧹掃除", "🛒買い物","🚮ゴミ出し","🛁風呂掃除","🚽トイレ掃除","💧水回り"])
person = st.selectbox("担当者", ["ぴちゃん", "みちゃん"])
date = st.date_input("日付", datetime.now())

if st.button("登録"):
    cur.execute("INSERT INTO kaji (date, task, person) VALUES (?, ?, ?)",
                (str(date), task, person))
    conn.commit()
    st.success("登録しました！")

st.subheader("実績一覧")
df = pd.read_sql_query("SELECT * FROM kaji", conn)
st.dataframe(df)

conn = sqlite3.connect(r"C:\Users\hikar\Python\kaji.db")