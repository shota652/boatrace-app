"""
データ記録
"""
import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
import sqlite3
import os
import json

# レース番号の初期化（セッションに保持）
if "race_number" not in st.session_state:
    st.session_state["race_number"] = 1
race_number = st.session_state["race_number"]

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

st.title("選手データ記録")

# SQLite接続とテーブル作成
conn = sqlite3.connect('boatrace_data.db')
cursor = conn.cursor()

# 選手データを保存するテーブルを作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS race_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    venue_name TEXT,
    race_number INTEGER,
    course_in INTEGER,
    player_name TEXT,
    move TEXT,
    second_place INTEGER,
    lost_to INTEGER,
    rank INTEGER,
    flow INTEGER,
    cabi INTEGER,
    kawarizensoku INTEGER,
    attack INTEGER,
    pressure INTEGER,
    block INTEGER,
    three_hari INTEGER,
    three_makurizashi INTEGER,
    two_nokoshi INTEGER,
    four_tsubushi INTEGER,
    four_nokoshi INTEGER,
    st_eval TEXT,
    two_shizumase INTEGER,
    four_shizumase INTEGER,
    makurizashi_flow_cabi
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
today = datetime.date.today().isoformat()
date = st.date_input("日付を選択", today)
date_str = date.strftime("%Y%m%d")

col1, col2 = st.columns(2)
with col1:
    venue_name = st.selectbox("場を選択", list(venues.keys()))
with col2:
    race_number = st.selectbox("レースを選択", list(range(1, 13)), index=st.session_state["race_number"] - 1)

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

racer_names = get_racer_names(url, date_str, venue_name, race_number)

try:
    if racer_names:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {venue_name} {race_number}R 出走表")

        with col2:  
            st.write("")
        # 「次のレースへ」ボタン（12R未満のときだけ表示）
            if race_number < 12:
                if st.button("次のレースへ"):
                    st.session_state["race_number"] = race_number + 1
                    st.rerun()
            else:
                st.info("これが最終レース（12R）です。")
        
        record_data = []

        for i, name in enumerate(racer_names, start=1):
            key_prefix = f"{date}_{race_number}_{name}"

            st.markdown("<hr style='border:1px solid #ccc;'>", unsafe_allow_html=True)
            st.subheader(f"{i}号艇　{name}")

            # 進入コース（デフォルトは号艇番号）
            course_in = st.selectbox(
                "進入コース",
                [1, 2, 3, 4, 5, 6],
                index=i - 1,
                key=f"{key_prefix}_course_{i}"
            )

            additional_data = {}

            # 進入コースごとの処理
            if course_in == 1:
                move = st.selectbox("動き", ["逃げ", "差され", "捲られ", "捲り差され", "抜かれ"], key=f"{key_prefix}_move_{i}")
                if move == "逃げ":
                    second_place = st.selectbox("2着の艇番", [2, 3, 4, "記録なし"], key=f"{key_prefix}_second_{i}")
                    additional_data["2着"] = second_place
                else:
                    lost_to = st.selectbox("負けたコース", [2, 3, 4, 5, 6, "複数"], key=f"{key_prefix}_lost_{i}")
                    my_rank = st.selectbox("着順", ["2", "3", "着外"], key=f"{key_prefix}_rank_{i}")
                    additional_data["負けたコース"] = lost_to
                    additional_data["着順"] = my_rank

                # 1コースの補足項目
                flow = st.checkbox("流れ", key=f"{key_prefix}_flow_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"{key_prefix}_kawarizensoku_{i}")
                block = st.checkbox("捲りブロック", key=f"{key_prefix}_block_{i}")
                three_hari = st.checkbox("3張", key=f"{key_prefix}_3_hari_{i}")
                additional_data["流れ"] = flow
                additional_data["かわり全速"] = kawarizensoku
                additional_data["捲りブロック"] = block
                additional_data["3張"] = three_hari

            elif course_in == 2:
                move = st.selectbox("動き", ["差し", "外マイ", "ジカマ", "ツケマイ", "3捲り差され", "捲られ・叩かれ", "ブロック負け", "3ツケマイ展開"], key=f"{key_prefix}_move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"{key_prefix}_rank_{i}")
                additional_data["着順"] = rank

                # 2コースの補足項目
                flow = st.checkbox("流れ", key=f"{key_prefix}_flow_{i}")
                cabi = st.checkbox("キャビ", key=f"{key_prefix}_cabi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"{key_prefix}_kawarizensoku_{i}")
                attack = st.checkbox("攻め", key=f"{key_prefix}_attack_{i}")
                pressure = st.checkbox("圧", key=f"{key_prefix}_pressure_{i}")
                three_makurizashi = st.checkbox("3捲り差し1着", key=f"{key_prefix}_3_makurizashi_{i}")
                additional_data["流れ"] = flow
                additional_data["キャビ"] = cabi
                additional_data["かわり全速"] = kawarizensoku
                additional_data["攻め"] = attack
                additional_data["圧"] = pressure
                additional_data["3捲り差し1着"] = three_makurizashi

            elif course_in == 3:
                move = st.selectbox("動き", ["外マイ", "絞り捲り", "ツケマイ", "箱捲り", "捲り差し", "後手捲り差し", "2凹捲り差し", "差し", "2外見て差し", "2捲り展開", "展開差し・捲り差し", "2外被り", "捲られ・叩かれ", "ブロック負け"], key=f"{key_prefix}_move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"{key_prefix}_rank_{i}")
                additional_data["着順"] = rank

                flow = st.checkbox("流れ", key=f"{key_prefix}_flow_{i}")
                cabi = st.checkbox("キャビ", key=f"{key_prefix}_cabi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"{key_prefix}_kawarizensoku_{i}")
                attack = st.checkbox("攻め", key=f"{key_prefix}_attack_{i}")
                pressure = st.checkbox("圧", key=f"{key_prefix}_pressure_{i}")
                two_nokoshi = st.checkbox("2残し", key=f"{key_prefix}_2_nokoshi_{i}")
                four_tsubushi = st.checkbox("4潰し", key=f"{key_prefix}_4_tsubushi_{i}")
                two_shizumase = st.checkbox("2沈ませ", key=f"{key_prefix}_2_shizumase_{i}")
                makurizashi_flow_cabi = st.checkbox("捲り差し流れ・キャビ", key=f"{key_prefix}_makurizashi_flow_cabi_{i}")
                additional_data["流れ"] = flow
                additional_data["キャビ"] = cabi
                additional_data["かわり全速"] = kawarizensoku 
                additional_data["攻め"] = attack
                additional_data["圧"] = pressure
                additional_data["2残し"] = two_nokoshi
                additional_data["4潰し"] = four_tsubushi
                additional_data["2沈ませ"] = two_shizumase
                additional_data["捲り差し流れ・キャビ"] = makurizashi_flow_cabi

            elif course_in == 4:
                move = st.selectbox("動き", ["差し", "捲り差し", "外マイ", "捲り", "叩いて捲り差し", "叩いて外マイ", "2捲り展開", "3捲り展開", "3絞り展開", "3ツケマイ展開", "展開捲り差し・外マイ", "3差し被り", "5捲り差され", "捲られ・叩かれ", "ブロック負け", "後手"], key=f"{key_prefix}_move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"{key_prefix}_rank_{i}")
                additional_data["着順"] = rank

                flow = st.checkbox("流れ", key=f"{key_prefix}_flow_{i}")
                cabi = st.checkbox("キャビ", key=f"{key_prefix}_cabi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"{key_prefix}_kawarizensoku_{i}")
                attack = st.checkbox("攻め", key=f"{key_prefix}_attack_{i}")
                pressure = st.checkbox("圧", key=f"{key_prefix}_pressure_{i}")
                additional_data["流れ"] = flow
                additional_data["キャビ"] = cabi
                additional_data["かわり全速"] = kawarizensoku 
                additional_data["攻め"] = attack
                additional_data["圧"] = pressure              

            elif course_in == 5:
                move = st.selectbox("動き", ["1-2捲り差し", "2-4捲り差し", "外マイ", "差し", "4外見て差し", "捲り", "叩いて捲り差し", "叩いて外マイ", "他艇捲り展開", "4捲り展開", "4絞り展開", "3ツケマイ展開", "展開差し・捲り差し・外マイ", "4外被り", "捲られ・叩かれ", "ブロック負け", "後手"], key=f"{key_prefix}_move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"{key_prefix}_rank_{i}")
                additional_data["着順"] = rank

                flow = st.checkbox("流れ", key=f"{key_prefix}_flow_{i}")
                cabi = st.checkbox("キャビ", key=f"{key_prefix}_cabi_{i}")
                kawarizensoku = st.checkbox("かわり全速", key=f"{key_prefix}_kawarizensoku_{i}")
                attack = st.checkbox("攻め", key=f"{key_prefix}_attack_{i}")
                pressure = st.checkbox("圧", key=f"{key_prefix}_pressure_{i}")
                four_nokoshi = st.checkbox("4残し", key=f"{key_prefix}_4_nokoshi_{i}")
                four_shizumase = st.checkbox("4沈ませ", key=f"{key_prefix}_4_shizumase_{i}")
                additional_data["流れ"] = flow
                additional_data["キャビ"] = cabi
                additional_data["かわり全速"] = kawarizensoku 
                additional_data["攻め"] = attack
                additional_data["圧"] = pressure
                additional_data["4残し"] = four_nokoshi
                additional_data["4沈ませ"] = four_shizumase


            elif course_in == 6:
                move = st.selectbox("動き", ["差し", "捲り差し・外マイ", "捲り", "叩いて捲り差し", "叩いて外マイ", "他艇捲り展開", "4捲り展開", "5捲り展開", "5絞り展開", "展開差し・捲り差し・外マイ", "5差し被り", "ブロック負け", "後手"], key=f"{key_prefix}_move_{i}")
                additional_data["動き"] = move
                rank = st.selectbox("着順", ["1", "2", "3", "着外"], key=f"{key_prefix}_rank_{i}")
                additional_data["着順"] = rank
                attack = st.checkbox("攻め", key=f"{key_prefix}_attack_{i}")
                pressure = st.checkbox("圧", key=f"{key_prefix}_pressure_{i}")
                additional_data["攻め"] = attack
                additional_data["圧"] = pressure

            # ST評価
            st_eval = st.selectbox(
                "ST評価",
                ["なし", "抜出（内より-0.10）", "出遅（外より+0.10）"],
                key=f"{key_prefix}_st_dev_{i}"
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
                    SELECT COUNT(*) FROM race_data
                    WHERE player_name = ? AND race_number = ? AND venue_name = ? AND date = ?
                ''', (record["選手名"], race_number, venue_name, date.isoformat()))
                count = cursor.fetchone()[0]

                if count == 0:
                    cursor.execute('''
                        INSERT INTO race_data (
                            date, venue_name, race_number, course_in, player_name, move, second_place,
                            lost_to, rank,
                            flow, cabi, kawarizensoku, attack, pressure, block, three_hari,
                            three_makurizashi, two_nokoshi, four_tsubushi, four_nokoshi, st_eval, two_shizumase, four_shizumase, makurizashi_flow_cabi
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        date.isoformat(),
                        venue_name,
                        race_number,
                        record["進入コース"],
                        record["選手名"],
                        record["動き"],
                        record.get("2着", None),
                        record.get("負けたコース", None),
                        record.get("着順", None),

                        # 以下、補足項目（未入力は0）

                        int(record.get("流れ", 0)),
                        int(record.get("キャビ", 0)),
                        int(record.get("かわり全速", 0)),
                        int(record.get("攻め", 0)),
                        int(record.get("圧", 0)),
                        int(record.get("捲りブロック", 0)),
                        int(record.get("3張", 0)),
                        int(record.get("3捲り差し1着", 0)),
                        int(record.get("2残し", 0)),
                        int(record.get("4潰し", 0)),
                        int(record.get("4残し", 0)),
                        record["ST評価"],
                        int(record.get("2沈ませ", 0)),
                        int(record.get("4沈ませ", 0)),
                        int(record.get("捲り差し流れ・キャビ", 0))
                    ))
                    conn.commit()
                else:
                    st.warning(f"{record['選手名']}のデータはすでに保存されています。")
            st.success("データが保存されました")

except requests.exceptions.RequestException as e:
    st.error(f"データの取得に失敗しました: {e}")

# SQLite接続を閉じる
conn.close()