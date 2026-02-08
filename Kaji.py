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
.row-wrap {
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
</style>
""", unsafe_allow_html=True)

# -------------------------
# 行を描画（HTML + Streamlit ボタン）
# -------------------------
for _, row in df.iterrows():

    # 左側（ID, 日付, 家事, 担当）
    left_html = f"""
    <div class="row-wrap">
        <div class="row-left">
            <div>{row["id"]}</div>
            <div>{row["date"]}</div>
            <div>{row["task"]}</div>
            <div>{row["person"]}</div>
        </div>
    """

    st.markdown(left_html, unsafe_allow_html=True)

    # 右側（削除ボタン）
    if st.button("削除", key=f"del_{row['id']}"):
        delete_task(row["id"])
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)