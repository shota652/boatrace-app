import sqlite3

# データベースに接続
conn = sqlite3.connect('boatrace_data.db')  # boatrace_data.dbがある場所を指定
cursor = conn.cursor()

# データを確認
cursor.execute("SELECT * FROM race_data")  # recordsテーブルを選択
rows = cursor.fetchall()

# 結果を表示
for row in rows:
    print(row)

# 接続を閉じる
conn.close()
