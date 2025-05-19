# backup_to_csv.py

import sqlite3
import pandas as pd
from datetime import datetime

# 日付付きファイル名を生成
today = datetime.now().strftime("%Y-%m-%d")
filename = f"boatrace_backup_{today}.csv"

# データベースに接続
conn = sqlite3.connect("boatrace_data.db")
df = pd.read_sql_query("SELECT * FROM records", conn)
conn.close()

# CSVとして保存
df.to_csv(filename, index=False, encoding="utf-8-sig")

print(f"{filename} にバックアップを保存しました。")


#バックアップのコマンドプロンプト　python backup_to_csv.py
