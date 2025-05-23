import sqlite3

conn = sqlite3.connect("boatrace_data.db")
cursor = conn.cursor()

# カラム追加（存在しない場合のみ）
try:
    cursor.execute("ALTER TABLE race_data ADD COLUMN pressure INTEGER")
except sqlite3.OperationalError:
    print("カラム 'pressure' はすでに存在します")

# NULL を 0 に更新
cursor.execute("UPDATE race_data SET pressure = 0 WHERE pressure IS NULL")

conn.commit()
conn.close()