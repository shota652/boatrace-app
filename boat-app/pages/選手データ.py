import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import datetime
import sqlite3
import os

def get_race_data_from_db(player_name, course_num):
# 親ディレクトリのパスを取得して、そこからdbに接続
    db_path = os.path.join(os.path.dirname(__file__), "..", "boatrace_data.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    query = """
    SELECT 
        venue_name, race_number, player_name, course_in, move, second_place, lost_to, rank, st_eval,
        attack, flow, block, kawarizensoku, three_hari, flow_cabi, three_makurizashi,
        two_nokoshi, four_tsubushi, four_nokoshi
    FROM race_data
    WHERE player_name = ? AND course_in = ?
    """
    c.execute(query, (player_name, course_num))
    rows = c.fetchall()

    conn.close()
    return rows

# color_map を定義（app全体で共通化して使えるように）
color_map = {
    # ①（1コース）
    "逃げ": "blue",
    "差され": "green",
    "捲り差され": "yellow",
    "捲られ": "red",

    # ②〜⑥共通（色分類に基づいて設定）
    "差し": "green",
    "外マイ": "indianred",
    "ジカマ": "firebrick",
    "ツケマイ": "tomato",
    "絞り捲り": "lightcoral",
    "叩いて外マイ": "crimson",

    "捲り差し": "khaki",
    "後手捲り差し": "goldenrod",
    "叩いて捲り差し": "khaki",
    "1-2捲り差し": "gold",
    "2-4捲り差し": "goldenrod",
    "捲り差し・外マイ": "goldenrod",

    "2捲り展開": "mediumpurple",
    "展開差し・捲り差し": "slateblue",
    "他艇捲り展開": "mediumpurple",
    "展開捲り差し・外マイ": "slateblue",
    "展開差し・捲り差し・外マイ": "slateblue",

    "3捲り差され": "darkgray",
    "捲られ・叩かれ": "gray",
    "ブロック負け": "lightgray",
    "2外被り": "lightgray",
    "3差し被り": "lightgray",
    "4外被り": "lightgray",
    "5差し被り": "lightgray",
    "5捲り差され": "darkgray"
}


def show_movement_summary(data_rows):
    # data_rowsはget_race_data_from_dbの戻り値（リスト）
    if not data_rows:
        st.info("データがありません。")
        return

    # DataFrameに変換（カラム名付き）
    columns = [
        "場", "レース", "選手名", "進入コース", "動き", "2着", "負けたコース", "着順", "ST",
        "攻め", "流れ", "捲りブロック", "かわり全速", "3張", "流れ・キャビ", "3捲り差し1着",
        "2残し", "4潰し", "4残し"
    ]
    df = pd.DataFrame(data_rows, columns=columns)

    # 動き別にカウント・割合
    movement_counts = df["動き"].value_counts().reset_index()
    movement_counts.columns = ["動き", "回数"]
    movement_counts["割合"] = round(movement_counts["回数"] / movement_counts["回数"].sum() * 100, 1)

    st.markdown("---")
    st.markdown("#### 動きの傾向")
    st.dataframe(movement_counts)

    # 円グラフ表示
    fig = px.pie(movement_counts, names="動き", values="回数", title="動きの割合", hole=0.4, color="動き", color_discrete_map=color_map)
    st.plotly_chart(fig)

 # 動きの詳細選択
    selected_move = st.selectbox("表示する動きを選んでください", movement_counts["動き"])

    df_move = df[df["動き"] == selected_move]
    if df_move.empty:
        st.write("選択された動きのデータがありません。")
        return

    # 現在の進入コース（すべて同じはず）
    course_num = df_move["進入コース"].iloc[0]

    # 1コースの場合の詳細
    if course_num == 1:
        if selected_move == "逃げ":
            # 逃げ時の2着のコース
            if "2着" in df_move.columns:
                second_course_counts = df_move["2着"].value_counts().reset_index()
                second_course_counts.columns = ["2着コース", "回数"]
                fig = px.pie(second_course_counts, names="2着コース", values="回数", title="2着の相手コース", hole=0.3)
                st.plotly_chart(fig, use_container_width=True, key=f"pie_nige_2nd_{selected_move}_{course_num}")

        elif selected_move in ["差され", "捲られ", "捲り差され"]:
            # (1.2) 1コースで差され・捲られ・捲り差され
            if "負けたコース" in df_move.columns:
                rival_counts = df_move["負けたコース"].value_counts().reset_index()
                rival_counts.columns = ["負けたコース", "回数"]
                fig1 = px.pie(rival_counts, names="負けたコース", values="回数", title="負けたコース", hole=0.3)
                st.plotly_chart(fig1, use_container_width=True, key=f"pie_lose_course_{selected_move}_{course_num}")

            if "着順" in df_move.columns:
                order = ["1", "2", "3", "着外"]
                df_move["着順"] = df_move["着順"].astype(str)

                pos_counts = df_move["着順"].value_counts(normalize=False).reset_index()
                pos_counts.columns = ["着順", "回数"]
                fig2 = px.bar(pos_counts, x="回数", y="着順", orientation="h", category_orders={"着順": order}, title="着順割合")


                fig2.update_layout(
                    yaxis=dict(type='category'),
                    xaxis=dict(tickformat="d")
                )
                st.plotly_chart(fig2, use_container_width=True, key=f"pie_lose_rank_{selected_move}_{course_num}")

    else:
    # (2) 2〜6コース → 着順（表＋横棒グラフ）
        if "着順" in df_move.columns:
            order = ["1", "2", "3", "着外"]
            df_move["着順"] = df_move["着順"].astype(str)

            pos_df = df_move["着順"].value_counts(normalize=False).reset_index()
            pos_df.columns = ["着順", "回数"]
            pos_df["割合"] = (pos_df["回数"] / pos_df["回数"].sum() * 100).round(1)

            st.dataframe(pos_df, use_container_width=True)

            fig = px.bar(pos_df, x="回数", y="着順", orientation="h", category_orders={"着順": order}, title="着順割合",
                         text="割合", labels={"割合": "%"})

            fig.update_layout(
                yaxis=dict(type='category'),
                xaxis=dict(tickformat="d")
            )

            st.plotly_chart(fig, use_container_width=True, key=f"pie_rank_{selected_move}_{course_num}")


    ### ③ 補足項目（コース別に表示）
    補足項目 = {
        1: ["3張", "捲りブロック", "流れ", "かわり全速"],
        2: ["攻め", "流れ・キャビ", "3捲り差し1着", "かわり全速"],
        3: ["攻め", "流れ・キャビ", "2残し", "4潰し", "かわり全速"],
        4: ["攻め", "流れ・キャビ", "かわり全速"],
        5: ["攻め", "流れ・キャビ", "4残し", "かわり全速"],
        6: ["攻め"]
    }

    selected_items = 補足項目.get(course_num, [])

    if selected_items:
        st.markdown("#### 補足項目の統計")
        rows = []
        for item in selected_items:
            if item in df_move.columns:
                count = df_move[item].sum()
                total = len(df_move)
                rows.append({"項目": item, "回数": count, "割合": round(count / total * 100, 1)})

        if rows:
            df_supplement = pd.DataFrame(rows)
            st.dataframe(df_supplement, use_container_width=True)


    ### ④ ST評価（出遅・抜出）
    if "ST" in df_move.columns:
        st.markdown("#### ST評価")

        count_df = df_move["ST"].value_counts(dropna=False).reset_index()
        count_df.columns = ["評価", "回数"]
        total = count_df["回数"].sum()        
        count_df["割合(%)"] = (count_df["回数"] / total * 100).round(1)

        st.dataframe(count_df, use_container_width=True)


st.title("コース別選手データ")

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
def get_racer_names(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    name_tags = soup.select("div.is-fs18.is-fBold a")
    return [tag.text.strip() for tag in name_tags]

try:
    racer_names = get_racer_names(url)

    if racer_names:
        st.markdown(f"### {venue_name} {race_number}R 出走表")
        
        record_data = []

        for i, name in enumerate(racer_names, start=1):

            if i > 1:
                # 2人目以降の前に罫線を入れる
                st.markdown("<hr style='margin: 50px 0; border: 0.5px solid #000;'>", unsafe_allow_html=True)

            cols = st.columns([3, 1])  # 左に選手名、右にコース選択

            with cols[0]:
                st.markdown(f"<h2 style='font-size: 26px; font-weight: bold;'>{i}号艇　{name}</h2>",
            unsafe_allow_html=True)

            with cols[1]:
                selected_course = st.selectbox(
                    "コース",
                    options=[1, 2, 3, 4, 5, 6],
                    index=i - 1,
                    key=f"course_{i}"
                )
           
            # 必要に応じて、ここに選手名と選択されたコースを保存する処理などを追加できます
            # 例: record_data.append({"選手名": name, "進入コース": selected_course}

            race_data = get_race_data_from_db(name, selected_course)

            # 動きの表＋円グラフを表示 ←★ここで表示実行
            show_movement_summary(race_data)

except Exception as e:
    st.error(f"データの取得中にエラーが発生しました: {e}")
