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

st.title("🏠家事 実績🐖")

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

params = st.query_params

# 削除処理
if "delete" in params:
    delete_task(params["delete"])

    # URLパラメータを消す
    st.query_params.clear()

    # 再読み込み
    st.rerun()

st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji", conn)

# 表示用の連番
df["no"] = range(1, len(df) + 1)

# -------------------------
# CSS（横並び）
# -------------------------
st.markdown("""
<style>
.row {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #ddd;
    padding: 10px 0;
    white-space: nowrap;
    overflow-x: auto;
}
.row-left {
    display: flex;
    flex-direction: row;
    gap: 16px;
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
# 行を描画
# -------------------------
for _, row in df.iterrows():

    html = f"""
    <div class="row">
        <div class="row-left">
            <div>{row["no"]}</div>
            <div>{row["date"]}</div>
            <div>{row["task"]}</div>
            <div>{row["person"]}</div>
        </div>
        <a class="delete-btn" href="/?delete={row['id']}">削除</a>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)