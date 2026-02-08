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

/* form が横に伸びる問題を解決 */
.button-row form {
    display: inline-block !important;
    margin: 0;
    padding: 0;
}

/* 角丸ボタン */
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

/* 時間：青 */
.btn.time-selected {
    background-color: #4da3ff !important;
    color: white !important;
    font-weight: bold !important;
}

/* 担当者：緑 */
.btn.person-selected {
    background-color: #4dcc88 !important;
    color: white !important;
    font-weight: bold !important;
}

/* hover */
.btn:hover {
    background-color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 時間ボタン（フォーム方式）
# -------------------------
st.write("かかった時間")

time_options = ["5分", "10分", "15分", "20分", "30分", "45分", "60分"]

html = '<div class="button-row">'
for t in time_options:
    selected = "time-selected" if st.session_state.selected_time == t else ""
    html += f"""
        <form method="get">
            <input type="hidden" name="time" value="{t}">
            <button class="btn {selected}" type="submit">{t}</button>
        </form>
    """
html += "</div>"

st.markdown(html, unsafe_allow_html=True)

# 選択処理
params = st.query_params
if "time" in params:
    st.session_state.selected_time = params["time"]
    st.query_params.clear()
    st.rerun()

# -------------------------
# 担当者ボタン（フォーム方式）
# -------------------------
st.write("担当者")

person_options = ["Piちゃん", "Miちゃん"]

html = '<div class="button-row">'
for p in person_options:
    selected = "person-selected" if st.session_state.selected_person == p else ""
    html += f"""
        <form method="get">
            <input type="hidden" name="person" value="{p}">
            <button class="btn {selected}" type="submit">{p}</button>
        </form>
    """
html += "</div>"

st.markdown(html, unsafe_allow_html=True)

# 選択処理
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
- v2.0 260208_角丸ボタン（青/緑）＋1クリック選択＋改行なし 完全安定版
- v1.9 260208_1クリック選択・改行なし・完全安定版
- v1.8 260208_1クリック選択方式に完全対応
- v1.7 260208_URLパラメータ方式を廃止
- v1.6 260208_時間ボタンの改行問題を修正
- v1.5 260208_選択状態が色で分かるように改善
- v1.4 260208_時間・名前をボタン選択式に変更
- v1.3 260208_時間入力（ラジオボタン）を追加
- v1.2 260208_削除機能を追加
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

# 最新順（降順）
df = pd.read_sql_query("SELECT * FROM kaji ORDER BY id DESC", conn)
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