import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import datetime
import os
import json

# --- オフライン用の読み込み関数 ---
def load_local_racecard(date_str, venue_name, race_number):
    file_name = f"{date_str}_{venue_name}_{race_number:02}.json"
    file_path = os.path.join("local_racecards", file_name)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [entry["name"] for entry in data]
    else:
        return None

def get_race_data_from_csv(player_name, course_num):
    # CSVファイルのパスを指定（SQLiteのdb_pathと同じディレクトリ構成を想定）
    csv_path = os.path.join(os.path.dirname(__file__), "..", "boatrace_data.csv")
    df = pd.read_csv(csv_path)

    # 条件でフィルタリング
    filtered_df = df[(df["player_name"] == player_name) & (df["course_in"] == course_num)]

    # もし空なら空リストを返す
    if filtered_df.empty:
        return []

    # SQLiteのfetchall()と同様にリストのタプルに変換して返す
    return filtered_df.values.tolist()

# color_map を定義（app全体で共通化して使えるように）
color_map = {
    # ①（1コース）
    "逃げ": "blue",
    "差され": "green",
    "捲り差され": "yellow",
    "捲られ": "red",

    # ②〜⑥共通（色分類に基づいて設定）
    "差し": "green",
    "2外見て差し":"green",
    "4外見て差し":"green",
    "外マイ": "indianred",
    "ジカマ": "firebrick",
    "ツケマイ": "tomato",
    "箱捲り": "tomato",
    "絞り捲り": "lightcoral",
    "叩いて外マイ": "crimson",

    "捲り差し": "khaki",
    "後手捲り差し": "goldenrod",
    "叩いて捲り差し": "khaki",
    "1-2捲り差し": "gold",
    "2-4捲り差し": "goldenrod",
    "捲り差し・外マイ": "goldenrod",

    "2捲り展開": "rebeccapurple",
    "3捲り展開": "rebeccapurple",
    "4捲り展開": "rebeccapurple",
    "5捲り展開": "rebeccapurple",
    "3ツケマイ展開": "rebeccapurple",
    "3絞り展開": "slateblue",
    "4絞り展開": "slateblue",
    "5絞り展開": "slateblue",
    "展開差し・捲り差し": "thistle",
    "他艇捲り展開": "thistle",
    "展開捲り差し・外マイ": "thistle",
    "展開差し・捲り差し・外マイ": "thistle",

    "3捲り差され": "darkgray",
    "捲られ・叩かれ": "gray",
    "ブロック負け": "lightgray",
    "2外被り": "lightgray",
    "3差し被り": "lightgray",
    "4外被り": "lightgray",
    "5差し被り": "lightgray",
    "5捲り差され": "darkgray",
    "後手": "darkslategray",

    "2": "black",
    "3": "red",
    "4": "blue",
    "5": "yellow",
    "6": "green",
    "記録なし": "gray"
}


def show_movement_summary(data_rows,player_name):
    # data_rowsはget_race_data_from_dbの戻り値（リスト）
    if not data_rows:
        st.info("データがありません。")
        return

    # DataFrameに変換（カラム名付き）
    columns = [
        "id", "date", "venue_name", "race_number", "course_in", "player_name", "move", 
        "second_place", "lost_to", "rank",
        "flow", "cabi", "kawarizensoku", "attack", "pressure",
        "block","three_hari",
        "three_makurizashi", "two_nokoshi", "four_tsubushi", "four_nokoshi", "st_eval", "two_shizumase", "four_shizumase", "makurizashi_flow_cabi"
    ]
    df = pd.DataFrame(data_rows, columns=columns)


    # rankの前後スペースを除去しておく（表記ブレ対策）
    df["rank"] = df["rank"].astype(str).str.strip()

    # 1着の判定：rankが"1" または course_in==1 かつ move=="逃げ"
    df["is_win"] = ((df["rank"] == "1") | ((df["course_in"] == 1) & (df["move"] == "逃げ")))

    # 着順ごとの判定（1コース逃げ以外は rank に値がある
    df["is_2nd"] = (df["rank"] == "2")
    df["is_3rd"] = (df["rank"] == "3")
    df["is_out"] = (df["rank"] == "着外")

    # 動きごとに集計
    movement_summary = df.groupby("move").agg(
        count=('move', 'count'),
        win=('is_win', 'sum'),
        place2=('is_2nd', 'sum'),
        place3=('is_3rd', 'sum'),
        out=('is_out', 'sum')
    ).reset_index()

    # 回数順に並べ替え
    movement_summary = movement_summary.sort_values("count", ascending=False)

    # 表表示（割合なし）
    movement_summary = movement_summary[["move", "count", "win", "place2", "place3", "out"]]
    movement_summary = movement_summary.rename(columns={
        "move": "動き", "count": "回数", "win": "1着", "place2": "2着", "place3": "3着", "out": "着外"
    })

    st.markdown("---")
    st.markdown("#### 動きの傾向")
    st.dataframe(movement_summary, use_container_width=True, hide_index=True)

    # 円グラフ（割合表示あり）
    fig = px.pie(
        movement_summary,
        names="動き",
        values="回数",
        title="動きの割合",
        hole=0.4,
        color="動き",
        color_discrete_map=color_map
    )
    fig.update_traces(textinfo='percent+label')  # ← 割合とラベルを表示
    st.plotly_chart(fig, key=f"move_summary_{player_name}")

    df_move = df[df["move"].notnull()]  # 念のためnull除外（任意）

    if df_move.empty:
        st.write("データがありません。")
        return

    # 現在の進入コース（すべて同じはず）
    course_num = df_move["course_in"].iloc[0]

    # 1コースの場合のみ動きのセレクトボックスと詳細表示
    if course_num == 1:
        selected_move = st.selectbox("表示する動きを選んでください", movement_summary["動き"], key=f"select_move_{player_name}")
        df_move = df_move[df_move["move"] == selected_move]

        if df_move.empty:
            st.write("選択された動きのデータがありません。")
            return

        if selected_move == "逃げ":
            if "second_place" in df_move.columns:
                second_course_counts = df_move["second_place"].value_counts().reset_index()
                second_course_counts.columns = ["2着コース", "回数"]
                fig = px.pie(second_course_counts, names="2着コース", values="回数", title="2着の相手コース", hole=0.3, color="2着コース", color_discrete_map=color_map)
                st.plotly_chart(fig, use_container_width=True, key=f"pie_nige_2nd_{player_name}_{selected_move}_{course_num}")

        elif selected_move in ["差され", "捲られ", "捲り差され"]:
            if "lost_to" in df_move.columns:
                rival_counts = df_move["lost_to"].value_counts().reset_index()
                rival_counts.columns = ["負けたコース", "回数"]
                fig1 = px.pie(rival_counts, names="負けたコース", values="回数", title="負けたコース", hole=0.3, color="負けたコース",color_discrete_map=color_map)
                st.plotly_chart(fig1, use_container_width=True, key=f"pie_lose_course_{player_name}_{selected_move}_{course_num}")

    ### ③ 補足項目（コース別に表示）
    補足項目 = {
        1: ["flow", "kawarizensoku", "block", "three_hari"],
        2: ["flow", "cabi", "kawarizensoku", "attack", "pressure", "three_makurizashi"],
        3: ["flow", "cabi", "kawarizensoku", "attack", "pressure", "two_nokoshi", "four_tsubushi", "two_shizumase", "makurizashi_flow_cabi"],
        4: ["flow", "cabi", "kawarizensoku", "attack", "pressure"],
        5: ["flow", "cabi", "kawarizensoku", "attack", "pressure", "four_nokoshi", "four_shizumase"],
        6: ["attack", "pressure"]
    }

    # 英語 → 日本語 の対応辞書
    japanese_labels = {
        "flow": "流れ",
        "cabi": "キャビ",
        "kawarizensoku": "かわり全速",
        "attack": "攻め",
        "pressure": "圧",
        "block": "捲りブロック",
        "three_hari": "3張",
        "three_makurizashi": "3捲り差し1着",
        "two_nokoshi": "2残し",
        "four_tsubushi": "4潰し",
        "four_nokoshi": "4残し",
        "two_shizumase": "2沈ませ",
        "four_shizumase": "4沈ませ",
        "makurizashi_flow_cabi": "捲り差し流れ・キャビ"
    }


    selected_items = 補足項目.get(course_num, [])

    if selected_items:
        st.markdown("#### 補足項目")
        rows = []
        for item in selected_items:
            if item in df.columns:
                count = df[item].sum()
                total = len(df)
                rows.append({"項目": japanese_labels.get(item, item), "回数": count, "割合": f"{round(count / total * 100, 1)}%"})

        if rows:
            df_supplement = pd.DataFrame(rows)
            st.dataframe(df_supplement, use_container_width=True, hide_index=True)


    ### ④ ST評価（出遅・抜出）
    if "st_eval" in df.columns:
        st.markdown("#### ST評価")

        count_df = df["st_eval"].value_counts(dropna=False).reset_index()
        count_df.columns = ["評価", "回数"]
        total = count_df["回数"].sum()
        count_df["割合"] = count_df["回数"].apply(
            lambda x: f"{round(x / total * 100)}%"
        )

        st.dataframe(count_df, use_container_width=True, hide_index=True)


st.markdown("<h2 style='text-align: center;'>コース別選手データ</h2>", unsafe_allow_html=True)

# 会場情報
venues = {
    "桐生": "01", "戸田": "02", "江戸川": "03", "平和島": "04",
    "多摩川": "05", "浜名湖": "06", "蒲郡": "07", "常滑": "08", "津": "09", "三国": "10",
    "びわこ": "11", "住之江": "12", "尼崎": "13", "鳴門": "14", "丸亀": "15",
    "児島": "16", "宮島": "17", "徳山": "18", "下関": "19", "若松": "20", 
    "芦屋": "21", "福岡": "22", "唐津": "23", "大村": "24"
}

# 日付と場・レース選択
today = datetime.date.today()
date = st.date_input("日付を選択", today)
date_str = date.strftime("%Y%m%d")

col1, col2 = st.columns(2)
with col1:
    venue_name = st.selectbox("場を選択", list(venues.keys()))
with col2:
    race_number = st.selectbox("レースを選択", list(range(1, 13)))

venue_code = venues[venue_name]
url = f"https://www.boatrace.jp/owpc/pc/race/racelist?rno={race_number}&jcd={venue_code}&hd={date_str}"

@st.cache_data(ttl=3600)
def get_racer_names(url, date_str, venue_name, race_number):
    # ① まずローカルに出走表があるか確認
    local_data = load_local_racecard(date_str, venue_name, race_number)
    if local_data:
        return local_data

    # ② なければオンラインで取得
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
        name_tags = soup.select("div.is-fs18.is-fBold a")

        if not name_tags:
            # オンラインでも選手名が取得できない（ページ構成変化 or 未公開）
            st.warning("出走表が見つかりませんでした（ローカルにもオンラインにもありません）")
            return []

        return [tag.text.strip() for tag in name_tags]

    except requests.exceptions.RequestException as e:
        st.warning("通信エラーが発生しました（オフラインとみなします）")
        with st.expander("エラーの詳細を見る"):
            st.code(str(e))
        return []

    except Exception as e:
        st.error("解析中に予期しないエラーが発生しました。")
        with st.expander("エラーの詳細を見る"):
            st.code(str(e))
        return []

# 先に関数としてリセット処理を定義しておく
def reset_shortcut_and_course_states(date_str, race_number, venue_name, url):

    # --- コース進入セレクトボックスのリセット（UI） ---
    for i in range(6):
        st.session_state[f"course_pos_{i}"] = i + 1

    # --- 選手ごとのステート初期化 ---
    racer_names = get_racer_names(url, date_str, venue_name, race_number)
    for i, name in enumerate(racer_names, start=1):
        key_prefix = f"{date_str}_{race_number}_{name}"
        keys_to_clear = [
            f"{key_prefix}_course_in",
            f"{key_prefix}_move_{i}",
            f"{key_prefix}_rank_{i}",
            f"{key_prefix}_lost_{i}",
            f"{key_prefix}_second_{i}",
        ]
        for key in keys_to_clear:
            st.session_state.pop(key, None)

# 必要なセッションステートを初期化
if "prev_race_number" not in st.session_state:
    st.session_state.prev_race_number = race_number
if "prev_date_str" not in st.session_state:
    st.session_state.prev_date_str = date_str

# レース or 日付が変わったらリセット
if st.session_state.prev_race_number != race_number or st.session_state.prev_date_str != date_str:
    reset_shortcut_and_course_states(date_str, race_number, venue_name, url)
    st.session_state.prev_race_number = race_number
    st.session_state.prev_date_str = date_str




racer_names = get_racer_names(url, date_str, venue_name, race_number)

try:
    if racer_names:
        st.markdown(f"### {venue_name} {race_number}R 出走表")

        st.markdown("### 進入コース")

        course_order = []  # 選手番号（1〜6）がどのコースに入ったか（例: [2, 3, 1, 4, 5, 6]）
        course_cols = st.columns(6)

        for i in range(6):
            with course_cols[i]:
                key=f"course_pos_{i}"    
                default = st.session_state.get(key, i + 1)             
                course = st.selectbox(
                    f"{i+1}コース",            # ラベル：1コース〜6コース
                    [1, 2, 3, 4, 5, 6],        # 選手番号（1〜6号艇）
                    index=[1, 2, 3, 4, 5, 6].index(default),
                    key=key  # キー名は自由（意味の通るものに）
                )
                course_order.append(course)

        # 毎回セッションに保持
        st.session_state["course_order"] = course_order

        # --- 選手ごとの進入コース（course_in）をセッションステートに反映 ---
        for i, name in enumerate(racer_names, start=1):  # i: 1〜6号艇
            key_prefix = f"{date}_{race_number}_{name}"
            course_key = f"{key_prefix}_course_in"

            if i in course_order:
                course_in = course_order.index(i) + 1  # 進入コースは1〜6（リストindexなので+1）
                st.session_state[course_key] = course_in
            else:
                st.session_state[course_key] = 0  # 不正な場合は0（空白）で初期化

        
        record_data = []

        for i, name in enumerate(racer_names, start=1):
            key_prefix = f"{date}_{race_number}_{name}"


            if i > 1:
                # 2人目以降の前に罫線を入れる
                st.markdown("<hr style='margin: 50px 0; border: 0.5px solid #000;'>", unsafe_allow_html=True)

            cols = st.columns([3, 1])  # 左に選手名、右にコース選択

            with cols[0]:
                st.markdown(f"<h2 style='font-size: 26px; font-weight: bold;'>{i}号艇　{name}</h2>",
            unsafe_allow_html=True)

            with cols[1]:
                # --- 進入コースのセッション保存付き選択 ---
                saved_course_in = st.session_state.get(f"{key_prefix}_course_in", i)
                index = saved_course_in - 1 if 1 <= saved_course_in <= 6 else i - 1

                course_in = st.selectbox(
                    "進入コース",
                    options=[1, 2, 3, 4, 5, 6],
                    index=index,
                    key=f"{key_prefix}_course_in_selectbox"
                )

                course_key = f"{key_prefix}_course_in"
                if course_in != saved_course_in:
                    st.session_state[course_key] = course_in


                additional_data = {}

                # ---------------------------------------
           
            # 必要に応じて、ここに選手名と選択されたコースを保存する処理などを追加できます
            # 例: record_data.append({"選手名": name, "進入コース": selected_course}

            race_data = get_race_data_from_csv(name, course_in)

            # 動きの表＋円グラフを表示 ←★ここで表示実行
            show_movement_summary(race_data, name)

        # 最後に course_order を保存
        st.session_state["course_order"] = course_order

except Exception as e:
    st.error(f"データの取得中にエラーが発生しました: {e}")