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
# 削除処理
# -------------------------
def delete_task(task_id):
    cur.execute("DELETE FROM kaji WHERE id = ?", (task_id,))
    conn.commit()

# URL パラメータで削除
params = st.query_params
if "delete" in params:
    delete_task(params["delete"])
    st.experimental_rerun()

st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji", conn)

# -------------------------
# CSS（横並びを強制）
# -------------------------
st.markdown("""
<style>
.row {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 16px;
    padding: 10px 0;
    border-bottom: 1px solid #ddd;
    white-space: nowrap;
    overflow-x: auto;
}
.cell {
    flex: 0 0 auto;
}
.delete-btn {
    background-color: red;
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 行を描画（削除ボタンは HTML）
# -------------------------
for _, row in df.iterrows():
    st.markdown('<div class="row">', unsafe_allow_html=True)

    st.markdown(f'<div class="cell">{row["id"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cell">{row["date"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cell">{row["task"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cell">{row["person"]}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<a class="delete-btn" href="/?delete={row["id"]}">削除</a>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)