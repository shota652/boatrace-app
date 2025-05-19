import re
import csv

# テキストファイルを読み込む
with open("racers.txt", "r", encoding="shift-jis") as file:
    text_data = file.read()

# 正規表現パターンを調整
# 数字（選手ID）+ 名前 + 級別・登録番号 の形式でマッチ
pattern = r"(\d+)\s+([^\d]+?)\s{2,}([A-Za-z0-9]+)[^\d]*"

# 行ごとに解析して、必要な情報を抽出
racer_data = []

for match in re.finditer(pattern, text_data):
    # 選手ID、名前、級別、登録番号を取得
    racer_id = match.group(1)  # 選手ID
    name = match.group(2).strip()  # 選手名
    rank_and_number = match.group(3).strip()  # 級別と登録番号

    # 結果をリストに追加
    racer_data.append([name, rank_and_number])

# CSVに保存
with open("racer_data.csv", "w", newline="", encoding="shift-jis") as file:
    writer = csv.writer(file)
    writer.writerow(["名前", "級別・登録番号"])  # ヘッダー行
    writer.writerows(racer_data)

print("CSVファイルに保存しました。")
