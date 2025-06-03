import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 出走表の保存先ディレクトリ
SAVE_DIR = "local_racecards"

# 必要ならフォルダを作成
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_racecard(date: str, venue: str, race_num: int):
    url = f"https://www.boatrace.jp/owpc/pc/race/racelist?rno={race_num}&jcd={VENUE_CODES[venue]}&hd={date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    name_tags = soup.select("div.is-fs18.is-fBold a")
    if not name_tags:
        return None

    racers = []
    for i, tag in enumerate(name_tags[:6]):
        racers.append({
            "lane": i + 1,
            "name": tag.text.strip()
        })

    return racers if racers else None

# 会場名 → 場コード対応（必要に応じて追加）
VENUE_CODES = {
    "桐生": "01", "戸田": "02", "江戸川": "03", "平和島": "04", "多摩川": "05",
    "浜名湖": "06", "蒲郡": "07", "常滑": "08", "津": "09", "三国": "10",
    "びわこ": "11", "住之江": "12", "尼崎": "13", "鳴門": "14", "丸亀": "15",
    "児島": "16", "宮島": "17", "徳山": "18", "下関": "19", "若松": "20",
    "芦屋": "21", "福岡": "22", "唐津": "23", "大村": "24"
}

def save_day_racecards(date: str, venue: str):
    """
    指定日・会場の1〜12Rの出走表を保存
    """
    for race_num in range(1, 13):
        data = fetch_racecard(date, venue, race_num)
        if data:
            filename = f"{date}_{venue}_{race_num:02}.json"
            path = os.path.join(SAVE_DIR, filename)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"{filename} 保存完了")
        else:
            print(f"{race_num}R の出走表が見つかりません")

if __name__ == "__main__":
    input_date = input("日付 (例: 20250528): ")
    input_venues = input("場名（カンマ区切り可 例: 桐生,蒲郡）: ")

    venues_list = [v.strip() for v in input_venues.split(",")]

    for venue in venues_list:
        if venue not in VENUE_CODES:
            print(f"対応していない場名です: {venue}")
        else:
            save_day_racecards(input_date, venue)