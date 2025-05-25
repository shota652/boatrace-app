import sqlite3

conn = sqlite3.connect("boatrace_data.db")
cursor = conn.cursor()

# カラム追加（存在しない場合のみ）
try:
    cursor.execute("ALTER TABLE race_data ADD COLUMN flow INTEGER")
except sqlite3.OperationalError:
    print("カラム 'flow' はすでに存在します")

# カラム追加（存在しない場合のみ）
try:
    cursor.execute("ALTER TABLE race_data ADD COLUMN cabi INTEGER")
except sqlite3.OperationalError:
    print("カラム 'cabi' はすでに存在します")


# NULL を 0 に更新
cursor.execute("UPDATE race_data SET pressure = 0 WHERE flow IS NULL")
cursor.execute("UPDATE race_data SET pressure = 0 WHERE cabi IS NULL")

conn.commit()
conn.close()