import streamlit as st
import json
import os
from datetime import datetime, timedelta

SAVE_DIR = "local_racecards"
LIST_FILE = "manual_list.json"

# ------------------
# 狙い目リストのロード
# ------------------
if not os.path.exists(LIST_FILE):
    with open(LIST_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

with open(LIST_FILE, "r", encoding="utf-8") as f:
    manual_list = json.load(f)

# ------------------
# 明日・今日の狙い目リスト表示（日付切替）
# ------------------
st.title("狙い目リスト＆管理ページ")

# 今日と明日の日付
today = datetime.now().strftime("%Y%m%d")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")

# 日付セレクト
selected_label = st.selectbox("日付を選択", ["今日", "明日"])
selected_date = today if selected_label == "今日" else tomorrow

# 選択日のファイルを取得
files = sorted([f for f in os.listdir(SAVE_DIR) if f.startswith(selected_date)])

st.header(f"📌 {selected_label}の狙い目リスト")
if not files:
    st.warning(f"{selected_date} の出走表が見つかりません")
else:
    venue_races = {}
    for filename in files:
        date, venue, race = filename.replace(".json","").split("_")
        with open(os.path.join(SAVE_DIR, filename), "r", encoding="utf-8") as f:
            racers = json.load(f)

        for r in racers:
            match = next((m for m in manual_list if m["name"] == r["name"] and m["lane"] == r["lane"]), None)
            if match:
                color = "green" if match["mark"] == "◯" else "red"
                text = {
                    "lane": r["lane"],
                    "name": r["name"],
                    "note": match["note"],
                    "mark": match["mark"],
                    "color": color
                }
                venue_races.setdefault(venue, {}).setdefault(int(race), []).append(text)

    # 場ごと・レースごとに表示
    for venue, races in venue_races.items():
        st.subheader(f"{venue}")
        for race_num in sorted(races.keys()):
            st.markdown(f"**{race_num}R**")
            for line in races[race_num]:
                col1, col2, col3 = st.columns([1,2,4])
                col1.markdown(f"<span style='color:{line['color']}; font-weight:bold;'>{line['lane']}コース</span>", unsafe_allow_html=True)
                col2.markdown(f"<span style='color:{line['color']}; font-weight:bold;'>{line['name']}</span>", unsafe_allow_html=True)
                col3.markdown(f"<span style='color:{line['color']};'>{line['note']}（{line['mark']}）</span>", unsafe_allow_html=True)

# ------------------
# 狙い目リスト管理（検索・編集・削除・追加）
# ------------------
st.header("🔍 狙い目リスト検索")
col_last, col_first = st.columns([1,1])
search_last = col_last.text_input("苗字で検索")
search_first = col_first.text_input("名前で検索")

if search_last or search_first:
    search_name = f"{search_last}　　{search_first}".strip()
    results = [m for m in manual_list if search_name in m["name"]]

    if results:
        st.subheader("検索結果")
        for i, m in enumerate(results):
            col1, col2, col3, col4, col5, col6 = st.columns([2,1,1,2,1,1])
            col1.write(m["name"])
            col2.write(f"{m['lane']}コース")
            col3.write(m["mark"])
            col4.write(m["note"])
            if col5.button("編集", key=f"edit_{i}"):
                st.session_state[f"edit_{i}"] = True
            if col6.button("削除", key=f"del_{i}"):
                manual_list.pop(i)
                with open(LIST_FILE, "w", encoding="utf-8") as f:
                    json.dump(manual_list, f, ensure_ascii=False, indent=2)
                st.success("削除しました")
                st.rerun()

            if st.session_state.get(f"edit_{i}", False):
                with st.form(f"form_edit_{i}"):
                    last_name, first_name = m["name"].split("　　")
                    new_last = st.text_input("苗字", value=last_name)
                    new_first = st.text_input("名前", value=first_name)
                    new_lane = st.selectbox("コース", [1,2,3,4,5,6], index=m["lane"]-1)
                    new_note = st.text_input("メモ", value=m["note"])
                    new_mark = st.radio("評価", ["◯","△"], index=0 if m["mark"]=="◯" else 1)
                    submitted = st.form_submit_button("更新")
                    if submitted:
                        m["name"] = f"{new_last}　　{new_first}"
                        m["lane"] = new_lane
                        m["note"] = new_note
                        m["mark"] = new_mark
                        with open(LIST_FILE, "w", encoding="utf-8") as f:
                            json.dump(manual_list, f, ensure_ascii=False, indent=2)
                        st.success("更新しました")
                        st.session_state[f"edit_{i}"] = False
                        st.rerun()
    else:
        st.info("見つかりません")

# 新規追加フォーム（苗字・名前別）
st.subheader("新規追加")
with st.form("add_form", clear_on_submit=True):
    col_last, col_first = st.columns([1,1])
    last_name = col_last.text_input("苗字")
    first_name = col_first.text_input("名前")

    lane = st.selectbox("コース", [1,2,3,4,5,6])
    note = st.text_input("メモ")
    mark = st.radio("評価", ["◯", "△"])
    submitted = st.form_submit_button("追加")

if submitted:
    full_name = f"{last_name}　　{first_name}"  # 全角スペース2つで結合
    new_entry = {"name": full_name, "lane": lane, "note": note, "mark": mark}
    manual_list.append(new_entry)
    with open(LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(manual_list, f, ensure_ascii=False, indent=2)
    st.success("追加しました！")