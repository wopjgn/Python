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
# CSS（ボタンデザイン）
# -------------------------
st.markdown("""
<style>
.time-btn, .person-btn {
    padding: 10px 16px;
    margin: 4px;
    border-radius: 20px;
    border: 1px solid #aaa;
    background-color: #eee;
    cursor: pointer;
    display: inline-block;
}
.time-btn.selected, .person-btn.selected {
    background-color: #ffcc00;
    color: black;
    font-weight: bold;
}
.time-btn:hover, .person-btn:hover {
    background-color: #ddd;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 時間ボタン
# -------------------------
st.write("かかった時間")

time_options = ["5分", "10分", "15分", "20分", "30分", "45分", "60分"]

time_html = ""
for t in time_options:
    selected_class = "selected" if st.session_state.selected_time == t else ""
    time_html += f"""
        <a href="/?time={t}" class="time-btn {selected_class}">{t}</a>
    """

st.markdown(time_html, unsafe_allow_html=True)

# URLパラメータ処理（時間）
params = st.query_params
if "time" in params:
    st.session_state.selected_time = params["time"]
    st.query_params.clear()
    st.rerun()

# -------------------------
# 名前ボタン
# -------------------------
st.write("担当者")

person_options = ["Piちゃん", "Miちゃん"]

person_html = ""
for p in person_options:
    selected_class = "selected" if st.session_state.selected_person == p else ""
    person_html += f"""
        <a href="/?person={p}" class="person-btn {selected_class}">{p}</a>
    """

st.markdown(person_html, unsafe_allow_html=True)

# URLパラメータ処理（担当者）
params = st.query_params
if "person" in params:
    st.session_state.selected_person = params["person"]
    st.query_params.clear()
    st.rerun()

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
# バージョン履歴
# -------------------------
with st.expander("バージョン履歴"):
    st.write("""
- v1.5 260208_時間・名前ボタンの選択状態が色で分かるように改善
- v1.4 260208_時間・名前をボタン選択式に変更
- v1.3 260208_時間入力（ラジオボタン）を追加
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
if "delete" in params:
    delete_task(params["delete"])
    st.query_params.clear()
    st.rerun()

st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji", conn)
df["no"] = range(1, len(df) + 1)

# -------------------------
# CSVダウンロード
# -------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 CSVをダウンロード",
    data=csv,
    file_name="kaji.csv",
    mime="text/csv"
)

# -------------------------
# CSS（一覧表示）
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
            <div>{row["time"]}</div>
        </div>
        <a class="delete-btn" href="/?delete={row['id']}">削除</a>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)