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
# バージョン履歴（expander）
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
# HTMLテーブル（スマホ最適化）
# -------------------------
table_html = """
<style>
.table-container {
    overflow-x: auto;
    width: 100%;
}
table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px; /* スマホで横スクロール */
}
th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
    white-space: nowrap; /* 折り返し防止 */
}
.delete-btn {
    color: white;
    background-color: red;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
}
</style>

<div class="table-container">
<table>
    <tr>
        <th>ID</th>
        <th>日付</th>
        <th>家事</th>
        <th>担当</th>
        <th>削除</th>
    </tr>
"""

for _, row in df.iterrows():
    table_html += f"""
    <tr>
        <td>{row['id']}</td>
        <td>{row['date']}</td>
        <td>{row['task']}</td>
        <td>{row['person']}</td>
        <td><a href="/?delete_id={row['id']}" class="delete-btn">削除</a></td>
    </tr>
    """

table_html += "</table></div>"

st.markdown(table_html, unsafe_allow_html=True)

# -------------------------
# 削除処理
# -------------------------
delete_id = st.query_params.get("delete_id")
if delete_id:
    delete_task(delete_id)
    st.experimental_rerun()