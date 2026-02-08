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

# タイトル
st.title("🏠家事 実績🐖←み")

# -------------------------
# バージョン履歴（右上固定）
# -------------------------
st.markdown("""
<style>
.version-box {
    position: fixed;
    top: 8px;
    right: 12px;
    z-index: 999;
    font-size: 12px;
    pointer-events: none;
}
.version-box .streamlit-expanderHeader {
    font-size: 12px !important;
    padding: 2px 4px !important;
}
.version-box .streamlit-expanderContent {
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

version_container = st.container()
with version_container:
    st.markdown('<div class="version-box">', unsafe_allow_html=True)
    with st.expander("📘 バージョン", expanded=False):
        st.markdown("""
**v1.3（2025-02-08）**  
- 時間スライダー追加  
- 横スクロール UI 改善  
- CSV ダウンロード追加  

**v1.2**  
- 削除ボタン安定化  
- DB 永続化改善  

**v1.1**  
- 家事カテゴリに絵文字追加  

**v1.0**  
- 初期リリース  
""")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# セッション状態
# -------------------------
if "selected_time" not in st.session_state:
    st.session_state.selected_time = None

if "selected_person" not in st.session_state:
    st.session_state.selected_person = None

# -------------------------
# 一覧用 CSS
# -------------------------
st.markdown("""
<style>
.record-row {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #444;
}
.record-row div {
    padding-right: 8px;
}
.col-no { width: 40px; }
.col-date { width: 120px; }
.col-task { width: 120px; }
.col-person { width: 80px; }
.col-time { width: 80px; }
.col-del { width: 60px; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# 時間スライダー
# -------------------------
time_value = st.slider(
    "作業時間を選択",
    min_value=1,
    max_value=120,
    value=15,
    step=1
)

st.session_state.selected_time = f"{time_value}分"
st.success(f"選択中の時間：{st.session_state.selected_time}")

# -------------------------
# 担当者
# -------------------------
person = st.radio(
    "担当者を選択",
    ["Piちゃん", "Miちゃん"],
    horizontal=True
)

st.session_state.selected_person = person
st.success(f"選択中の担当者：{person}")

# -------------------------
# 家事の種類
# -------------------------
task = st.selectbox("家事の種類", [
    "🍳料理", "🫗皿洗い", "👕洗濯", "🧹掃除", "🛒買い物",
    "🚮ゴミ出し", "🛁風呂掃除", "🚽トイレ掃除", "💧水回り"
])

date = st.date_input("日付", datetime.now())

# -------------------------
# 登録処理
# -------------------------
if st.button("登録"):
    cur.execute(
        "INSERT INTO kaji (date, task, person, time) VALUES (?, ?, ?, ?)",
        (str(date), task, st.session_state.selected_person, st.session_state.selected_time)
    )
    conn.commit()
    st.success("登録しやした！")

st.subheader("実績一覧")

df = pd.read_sql_query("SELECT * FROM kaji", conn)

# HTMLテーブルを作成
table_html = """
<style>
.table-container {
    overflow-x: auto;
    width: 100%;
}
table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px; /* スマホでも横スクロール可能にする */
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
        <td><button class="delete-btn" onclick="fetch('/?delete_id={row['id']}')">削除</button></td>
    </tr>
    """

table_html += "</table></div>"

st.markdown(table_html, unsafe_allow_html=True)

# 削除処理
delete_id = st.query_params.get("delete_id")
if delete_id:
    delete_task(delete_id)
    st.experimental_rerun()
