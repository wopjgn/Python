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

# タイトル
st.title("🏠家事 実績🐖")

# -------------------------
# バージョン履歴（右上固定）
# -------------------------
st.markdown("""
<style>
.version-box {
    position: fixed;
    top: 8px;
    right: 12px;
    z-index: 999;
    font-size: 12px;
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="version-box">', unsafe_allow_html=True)
    with st.expander("📘 バージョン", expanded=False):
        st.markdown("""
**v1.3（2025-02-08）**  
- 時間スライダー追加  
- 横スクロール UI 改善  
- CSV ダウンロード追加  
""")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# 入力UI
# -------------------------
time_value = st.slider("作業時間を選択", 1, 120, 15)
person = st.radio("担当者を選択", ["Piちゃん", "Miちゃん"], horizontal=True)
task = st.selectbox("家事の種類", [
    "🍳料理", "🫗皿洗い", "👕洗濯", "🧹掃除", "🛒買い物",
    "🚮ゴミ出し", "🛁風呂掃除", "🚽トイレ掃除", "💧水回り"
])
date = st.date_input("日付", datetime.now())

if st.button("登録"):
    cur.execute(
        "INSERT INTO kaji (date, task, person, time) VALUES (?, ?, ?, ?)",
        (str(date), task, person, f"{time_value}分")
    )
    conn.commit()
    st.success("登録しやした！")
    st.rerun()

# -------------------------
# 一覧表示
# -------------------------
st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji ORDER BY id DESC", conn)

# CSVダウンロード
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 CSVをダウンロード", csv, "kaji.csv", "text/csv")

# -------------------------
# 表示 & 削除（横並び）
# -------------------------
for _, row in df.iterrows():
    col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 2, 2])

    col1.write(row["id"])
    col2.write(row["date"])
    col3.write(row["task"])
    col4.write(row["person"])

    if col5.button("削除", key=f"del_{row['id']}"):
        cur.execute("DELETE FROM kaji WHERE id = ?", (row["id"],))
        conn.commit()
        st.rerun()
