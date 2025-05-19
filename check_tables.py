import sqlite3

# データベースに接続
conn = sqlite3.connect('boatrace_data.db')
cursor = conn.cursor()

# データベース内のテーブルを取得
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# テーブル名を表示
print("データベース内のテーブル:")
for table in tables:
    print(table[0])

# 接続を閉じる
conn.close()
