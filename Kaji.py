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
    person TEXT,
    time TEXT
)
""")
conn.commit()

st.title("🏠家事 実績🐖")

# -------------------------
# セッション状態
# -------------------------
if "selected_time" not in st.session_state:
    st.session_state.selected_time = None

if "selected_person" not in st.session_state:
    st.session_state.selected_person = None

# -------------------------
# 時間ボタン
# -------------------------
st.write("かかった時間")

time_options = ["5分", "10分", "15分", "20分", "30分", "45分", "60分"]

cols = st.columns(len(time_options))
for i, t in enumerate(time_options):
    if cols[i].button(t):
        st.session_state.selected_time = t

# 選択中の時間表示
if st.session_state.selected_time:
    st.success(f"選択中の時間：{st.session_state.selected_time}")

# -------------------------
# 担当者ボタン
# -------------------------
st.write("担当者")

person_options = ["Piちゃん", "Miちゃん"]

cols = st.columns(len(person_options))
for i, p in enumerate(person_options):
    if cols[i].button(p):
        st.session_state.selected_person = p

# 選択中の担当者表示
if st.session_state.selected_person:
    st.success(f"選択中の担当者：{st.session_state.selected_person}")

# -------------------------
# 家事の種類
# -------------------------
task = st.selectbox("家事の種類", [
    "🍳料理", "🫗皿洗い", "👕洗濯", "🧹掃除", "🛒買い物",
    "🚮ゴミ出し", "🛁風呂掃除", "🚽トイレ掃除", "💧水回り"
])

date = st.date_input("日付", datetime.now())

# -------------------------
# 登録処理
# -------------------------
if st.button("登録"):
    if not st.session_state.selected_time or not st.session_state.selected_person:
        st.error("時間と担当者を選択してください")
    else:
        cur.execute(
            "INSERT INTO kaji (date, task, person, time) VALUES (?, ?, ?, ?)",
            (str(date), task, st.session_state.selected_person, st.session_state.selected_time)
        )
        conn.commit()
        st.success("登録しやした！")

# -------------------------
# 一覧表示
# -------------------------
st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji ORDER BY id DESC", conn)
df["no"] = range(1, len(df) + 1)

# CSVダウンロード
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 CSVをダウンロード", csv, "kaji.csv", "text/csv")

# -------------------------
# 表示 & 削除
# -------------------------
for _, row in df.iterrows():
    cols = st.columns([1, 3, 3, 2, 2, 2])
    cols[0].write(row["no"])
    cols[1].write(row["date"])
    cols[2].write(row["task"])
    cols[3].write(row["person"])
    cols[4].write(row["time"])

    if cols[5].button("削除", key=f"del_{row['id']}"):
        cur.execute("DELETE FROM kaji WHERE id = ?", (row["id"],))
        conn.commit()
        st.rerun()