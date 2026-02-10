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

# -------------------------
# 入力フォーム
# -------------------------
task = st.selectbox("家事の種類", ["🍳料理", "🫗皿洗い", "👕洗濯", "🧹掃除", "🛒買い物","🚮ゴミ出し","🛁風呂掃除","🚽トイレ掃除","💧水回り"])
person = st.selectbox("担当者", ["ぴちゃん", "みちゃん"])
date = st.date_input("日付", datetime.now())

if st.button("登録"):
    cur.execute("INSERT INTO kaji (date, task, person) VALUES (?, ?, ?)",
                (str(date), task, person))
    conn.commit()
    st.success("登録しました！")

# -------------------------
# 削除機能
# -------------------------

def delete_task(task_id):
    cur.execute("DELETE FROM kaji WHERE id = ?", (task_id,))
    conn.commit()

st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji", conn)

# 削除ボタン付きの表を作る
for index, row in df.iterrows():
    cols = st.columns([1, 3, 3, 3, 2])  # 表示の幅調整
    cols[0].write(row["id"])
    cols[1].write(row["date"])
    cols[2].write(row["task"])
    cols[3].write(row["person"])
    if cols[4].button("削除", key=f"del_{row['id']}"):
        delete_task(row["id"])
        st.experimental_rerun()

# -------------------------
# バージョン履歴（expander）
# -------------------------
with st.expander("バージョン履歴"):
    st.write("""
- v1.3 削除機能を追加
- v1.2 UI を改善
- v1.1 データベース保存を安定化
- v1.0 初期リリース
    """)
