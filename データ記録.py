import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
import sqlite3

st.title("選手データ記録")

# SQLite接続とテーブル作成
conn = sqlite3.connect('boatrace_data.db')
cursor = conn.cursor()

# 選手データを保存するテーブルを作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS race_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name TEXT,
    race_number INTEGER,
    player_name TEXT,
    course_in INTEGER,
    move TEXT,
    second_place TEXT,
    lost_to TEXT,
    rank TEXT,
    st_eval TEXT,

    -- 共通補足項目
    attack INTEGER,            -- 2～6コース
    flow INTEGER,              -- 1コース専用
    block INTEGER,             -- 1コース専用
    kawarizensoku INTEGER,     -- 全コース共通
    three_hari INTEGER,             -- 1コース
    flow_cabi INTEGER,         -- 2～5コース
    three_makurizashi INTEGER,     -- 2コース
    two_nokoshi INTEGER,         -- 3コース
    four_tsubushi INTEGER,        -- 3コース
    four_nokoshi INTEGER          -- 5コース

)
''')
conn.commit()

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
            st.markdown("<hr style='border:1px solid #ccc;'>", unsafe_allow_html=True)
            st.subheader(f"{i}号艇　{name}")

            # 進入コース（デフォルトは号艇番号）
            course_in = st.selectbox(
                "進入コース",
                [1, 2, 3, 4, 5, 6],
                index=i - 1,
                key=f"course_{i}"
            )

            additional_data = {}

            # 進入コースごとの処理
            if course_in == 1:
                move = st.selectbox("動き", ["逃げ", "差され", "捲られ", "捲り差され"], key=f"move_{i}")
                if move == "逃げ":
                    second_place = st.selectbox("2着の艇番", [2, 3, 4, "記録なし"], key=f"second_{i}")
                    additional_data["2着"] = second_place
                else:
                    lost_to = st.selectbox("負けたコース", [2, 3, 4, 5, 6, "複数"], key=f"lost_{i}")
                    my_rank = st.selectbox("着順", ["2", "3", "着外"], key=f"rank_{i}")
                    additional_data["負けたコース"] = lost_to
                    additional_data["着順"] = my_rank

                # 1コースの補足項目
                three_hari = st.checkbox("3張", key=f"3_hari_{i}")
                block = st.checkbox("捲りブロック", key=f"block_{i}")
                flow = st.checkbox("流れ", key=f"flow_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"allspeed_{i}")
                additional_data["3張"] = three_hari
                additional_data["捲りブロック"] = block
                additional_data["流れ"] = flow
                additional_data["かわり全速"] = kawarizensoku

            elif course_in == 2:
                move = st.selectbox("動き", ["差し", "外マイ", "ジカマ", "ツケマイ", "3捲り差され", "捲られ・叩かれ", "ブロック負け"], key=f"move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"rank_{i}")
                additional_data["着順"] = rank

                # 2コースの補足項目
                attack = st.checkbox("攻め", key=f"attack_{i}")
                flow_cabi = st.checkbox("流れ・キャビ", key=f"flow_cabi_{i}")
                three_makurizashi = st.checkbox("3捲り差し1着", key=f"3_makurizashi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"kawarizensoku_{i}")
                additional_data["攻め"] = attack
                additional_data["流れ・キャビ"] = flow_cabi
                additional_data["3捲り差し1着"] = three_makurizashi
                additional_data["かわり全速"] = kawarizensoku

            elif course_in == 3:
                move = st.selectbox("動き", ["外マイ", "絞り捲り", "ツケマイ", "捲り差し", "後手捲り差し", "差し", "2捲り展開", "展開差し・捲り差し", "2外被り", "捲られ・叩かれ", "ブロック負け"], key=f"move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"rank_{i}")
                additional_data["着順"] = rank
                attack = st.checkbox("攻め", key=f"attack_{i}")
                flow_cabi = st.checkbox("流れ・キャビ", key=f"flow_cabi_{i}")
                two_nokoshi = st.checkbox("2残し", key=f"2_nokoshi_{i}")
                four_tsubushi = st.checkbox("4潰し", key=f"4_tsubushi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"kawarizensoku_{i}")
                additional_data["攻め"] = attack
                additional_data["流れ・キャビ"] = flow_cabi
                additional_data["2残し"] = two_nokoshi
                additional_data["4潰し"] = four_tsubushi
                additional_data["かわり全速"] = kawarizensoku

            elif course_in == 4:
                move = st.selectbox("動き", ["差し", "捲り差し", "外マイ", "捲り", "叩いて捲り差し", "叩いて外マイ", "他艇捲り展開", "展開捲り差し・外マイ", "3差し被り", "5捲り差され", "捲られ・叩かれ", "ブロック負け"], key=f"move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"rank_{i}")
                additional_data["着順"] = rank
                attack = st.checkbox("攻め", key=f"attack_{i}")
                flow_cabi = st.checkbox("流れ・キャビ", key=f"flow_cabi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"kawarizensoku_{i}")
                additional_data["攻め"] = attack
                additional_data["流れ・キャビ"] = flow_cabi
                additional_data["かわり全速"] = kawarizensoku

            elif course_in == 5:
                move = st.selectbox("動き", ["1-2捲り差し", "2-4捲り差し", "外マイ", "差し", "捲り", "叩いて捲り差し", "叩いて外マイ", "他艇捲り展開", "展開差し・捲り差し・外マイ", "4外被り", "叩かれ・捲られ", "ブロック負け"], key=f"move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"rank_{i}")
                additional_data["着順"] = rank
                attack = st.checkbox("攻め", key=f"attack_{i}")
                flow_cabi = st.checkbox("流れ・キャビ", key=f"flow_cabi_{i}")
                four_nokoshi = st.checkbox("4残し", key=f"4_nokoshi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"kawarizensoku_{i}")
                additional_data["攻め"] = attack
                additional_data["流れ・キャビ"] = flow_cabi
                additional_data["4残し"] = four_nokoshi
                additional_data["かわり全速"] = kawarizensoku

            elif course_in == 6:
                move = st.selectbox("動き", ["差し", "捲り差し・外マイ", "捲り", "叩いて捲り差し", "叩いて外マイ", "他艇捲り展開", "展開差し・捲り差し・外マイ", "5差し被り", "ブロック負け"], key=f"move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"rank_{i}")
                additional_data["着順"] = rank
                attack = st.checkbox("攻め", key=f"attack_{i}")
                additional_data["攻め"] = attack

            # ST評価
            st_eval = st.selectbox(
                "ST評価",
                ["なし", "抜出（内より-0.10）", "出遅（外より+0.10）"],
                key=f"st_dev_{i}"
            )

            record_data.append({
                "選手名": name,
                "進入コース": course_in,
                "動き": move,
                **additional_data,
                "ST評価": st_eval,
            })

        # Submit button to save the data into SQLite
        if st.button("保存"):
            for record in record_data:
                cursor.execute('''
                    INSERT INTO race_data (
                        venue_name, race_number, player_name, course_in, move, second_place,
                        lost_to, rank, st_eval,
                        attack, flow, block, kawarizensoku, three_hari,
                        flow_cabi, three_makurizashi, two_nokoshi, four_tsubushi, four_nokoshi
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    venue_name,
                    race_number,
                    record["選手名"],
                    record["進入コース"],
                    record["動き"],
                    record.get("2着", None),
                    record.get("負けたコース", None),
                    record.get("着順", None),
                    record["ST評価"],

                    # 以下、補足項目（未入力は0）
                    int(record.get("攻め", 0)),
                    int(record.get("流れ", 0)),
                    int(record.get("捲りブロック", 0)),
                    int(record.get("かわり全速", 0)),
                    int(record.get("3張", 0)),
                    int(record.get("流れ・キャビ", 0)),
                    int(record.get("3捲り差し1着", 0)),
                    int(record.get("2残し", 0)),
                    int(record.get("4潰し", 0)),
                    int(record.get("4残し", 0))
                ))
            conn.commit()
            st.success("データが保存されました")

except requests.exceptions.RequestException as e:
    st.error(f"データの取得に失敗しました: {e}")

# SQLite接続を閉じる
conn.close()