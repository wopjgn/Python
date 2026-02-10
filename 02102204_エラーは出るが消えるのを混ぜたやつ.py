import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# DB接続
import os
DB_PATH = os.path.join(os.getcwd(), "kaji.db")
conn = sqlite3.connect(DB_PATH)

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

# -------------------------
# 削除処理（新しい query_params API）
# -------------------------
params = st.query_params

if "delete_id" in params:
    raw = params["delete_id"]

    # リストでも文字列でも対応
    if isinstance(raw, list):
        raw = raw[0]

    try:
        delete_id = int(raw)
        cur.execute("DELETE FROM kaji WHERE id = ?", (delete_id,))
        conn.commit()
    except Exception as e:
        st.write("削除エラー:", e)

    # クエリパラメータをクリア
    st.query_params = {}
    st.rerun()


# タイトル
st.title("🏠家事 実績🐖")

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

# -------------------------
# スマホ対応テーブル（横スクロール & 改行禁止）
# -------------------------
table_html = """<style>
.table-wrap { overflow-x: auto; width: 100%; }
table { border-collapse: collapse; width: 100%; min-width: 750px; }
th, td { border: 1px solid #ccc; padding: 6px 10px; white-space: nowrap; }
.del-link {
    background-color: red;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    text-decoration: none;
}
</style>
<div class="table-wrap">
<table>
<tr>
<th>ID</th><th>日付</th><th>家事</th><th>担当</th><th>時間</th><th>削除</th>
</tr>
"""

for _, row in df.iterrows():
    table_html += (
        f"<tr>"
        f"<td>{row['id']}</td>"
        f"<td>{row['date']}</td>"
        f"<td>{row['task']}</td>"
        f"<td>{row['person']}</td>"
        f"<td>{row['time']}</td>"
        f"<td><a class='del-link' href='?delete_id={row['id']}'>削除</a></td>"
        f"</tr>"
    )

table_html += "</table></div>"

st.markdown(table_html, unsafe_allow_html=True)


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

    

# CSVダウンロード
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 CSVをダウンロード", csv, "kaji.csv", "text/csv")


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
