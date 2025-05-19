import sqlite3
import pandas as pd

# SQLiteファイル名
DB_FILE = "boatrace_data.db"
# エクスポート先CSVファイル名
CSV_FILE = "boatrace_data.csv"

# SQLiteからデータを読み込んでDataFrameに変換
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql_query("SELECT * FROM race_data", conn)
conn.close()

# CSVとして保存（index列なし、UTF-8で保存）
df.to_csv(CSV_FILE, index=False, encoding="utf-8")

print(f"エクスポート完了: {CSV_FILE}")