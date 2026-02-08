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
# バージョン履歴
# -------------------------
with st.expander("バージョン履歴"):
    st.write("""
- v1.2 260208_削除機能を追加
- v1.2 260207_絵文字で分かりやすく表示
- v1.0 260207_初期リリース
    """)

# -------------------------
# 削除機能
# -------------------------
def delete_task(task_id):
    cur.execute("DELETE FROM kaji WHERE id = ?", (task_id,))
    conn.commit()

st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji", conn)

# -------------------------
# CSS：行を横並びに強制
# -------------------------
st.markdown("""
<style>
.row {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 16px;
    padding: 8px 0;
    border-bottom: 1px solid #ddd;
    overflow-x: auto;
    white-space: nowrap;
}
.cell {
    flex: 0 0 auto;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 行を描画（絶対に横並び）
# -------------------------
for _, row in df.iterrows():
    st.markdown('<div class="row">', unsafe_allow_html=True)

    st.markdown(f'<div class="cell">{row["id"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cell">{row["date"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cell">{row["task"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cell">{row["person"]}</div>', unsafe_allow_html=True)

    # 削除ボタン（Streamlit純正）
    if st.button("削除", key=f"del_{row['id']}"):
        delete_task(row["id"])
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)