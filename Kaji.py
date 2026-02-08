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
st.title("🏠家事 実績🐖")

# -------------------------
# バージョン履歴（右上小さく固定）
# -------------------------
st.markdown("""
<style>
.version-box {
    position: absolute;
    top: 8px;
    right: 12px;
    z-index: 999;
    font-size: 12px;
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
# CSS：横スクロール行
# -------------------------
st.markdown("""
<style>
.scroll-row {
    display: flex;
    flex-direction: row;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 8px;
}
.scroll-row > div {
    flex: 0 0 auto;
}
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
    html = f"""
    <div class='row'>
        <div class='row-left'>
            <div>{row["no"]}</div>
            <div>{row["date"]}</div>
            <div>{row["task"]}</div>
            <div>{row["person"]}</div>
            <div>{row["time"]}</div>
        </div>
        <a class='delete-btn' href='/?delete={row["id"]}'>削除</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
