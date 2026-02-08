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

# time列がなければ追加
try:
    cur.execute("ALTER TABLE kaji ADD COLUMN time TEXT")
except:
    pass

st.title("🏠家事 実績🐖")

# -------------------------
# セッション状態の初期化
# -------------------------
if "selected_time" not in st.session_state:
    st.session_state.selected_time = None

if "selected_person" not in st.session_state:
    st.session_state.selected_person = None

# -------------------------
# CSS（角丸ボタンデザイン）
# -------------------------
st.markdown("""
<style>
.button-row {
    display: flex;
    flex-direction: row;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 8px;
}

.button-row form {
    display: inline-block !important;
    margin: 0;
    padding: 0;
}

.btn {
    padding: 10px 18px !important;
    border-radius: 12px !important;
    border: 1px solid #aaa !important;
    background-color: #f2f2f2 !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    font-size: 16px !important;
    color: black !important;
}

.btn.time-selected {
    background-color: #4da3ff !important;
    color: white !important;
    font-weight: bold !important;
}

.btn.person-selected {
    background-color: #4dcc88 !important;
    color: white !important;
    font-weight: bold !important;
}

.btn:hover {
    background-color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 時間ボタン
# -------------------------
st.write("かかった時間")

time_options = ["5分", "10分", "15分", "20分", "30分", "45分", "60分"]

html = '<div class="button-row">'
for t in time_options:
    selected = "time-selected" if st.session_state.selected_time == t else ""
    html += f'''
        <form method="get">
            <input type="hidden" name="time" value="{t}">
            <button class="btn {selected}" type="submit">{t}</button>
        </form>
    '''
html += "</div>"

st.markdown(html, unsafe_allow_html=True)

params = st.query_params
if "time" in params:
    st.session_state.selected_time = params["time"]
    st.query_params.clear()

# -------------------------
# 担当者ボタン
# -------------------------
st.write("担当者")

person_options = ["Piちゃん", "Miちゃん"]

html = '<div class="button-row">'
for p in person_options:
    selected = "person-selected" if st.session_state.selected_person == p else ""
    html += f'''
        <form method="get">
            <input type="hidden" name="person" value="{p}">
            <button class="btn {selected}" type="submit">{p}</button>
        </form>
    '''
html += "</div>"

st.markdown(html, unsafe_allow_html=True)

params = st.query_params
if "person" in params:
    st.session_state.selected_person = params["person"]
    st.query_params.clear()

# -------------------------
# 家事の種類
# -------------------------
task = st.selectbox("家事の種類", ["🍳料理", "🫗皿洗い", "👕洗濯", "🧹掃除", "🛒買い物",
                                "🚮ゴミ出し","🛁風呂掃除","🚽トイレ掃除","💧水回り"])

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
# 削除処理
# -------------------------
def delete_task(task_id):
    cur.execute("DELETE FROM kaji WHERE id = ?", (task_id,))
    conn.commit()

params = st.query_params
if "delete" in params:
    delete_task(params["delete"])
    st.query_params.clear()
    st.rerun()

# -------------------------
# 一覧表示
# -------------------------
st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji ORDER BY id DESC", conn)
df["no"] = range(1, len(df) + 1)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 CSVをダウンロード", csv, "kaji.csv", "text/csv")

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

for _, row in df.iterrows():
    html = f'''
    <div class="row">
        <div class="row-left">
            <div>{row["no"]}</div>
            <div>{row["date"]}</div>
            <div>{row["task"]}</div>
            <div>{row["person"]}</div>
            <div>{row["time"]}</div>
        </div>
        <a class="delete-btn" href="/?delete={row['id']}">削除</a>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)