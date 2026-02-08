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
# 行を描画（1行＝1つのHTMLブロック）
# -------------------------
for _, row in df.iterrows():

    html = f"""
    <div class="row">
        <div class="cell">{row["id"]}</div>
        <div class="cell">{row["date"]}</div>
        <div class="cell">{row["task"]}</div>
        <div class="cell">{row["person"]}</div>
        <form action="" method="post">
            <input type="hidden" name="delete_id" value="{row['id']}">
            <button class="delete-btn">削除</button>
        </form>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

# -------------------------
# POSTで削除を受け取る
# -------------------------
if "delete_id" in st.session_state:
    delete_task(st.session_state["delete_id"])
    st.session_state.pop("delete_id")
    st.rerun()

# HTMLフォームのPOSTを拾う
if st.query_params.get("delete_id"):
    st.session_state["delete_id"] = st.query_params["delete_id"]
    st.rerun()