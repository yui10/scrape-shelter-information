"""
NHK(https://www.nhk.or.jp/kishou-saigai/list/)より避難所情報を取得する
"""
import requests
import json
import csv
import sqlite3
from pathlib import Path

Path("./out").mkdir(exist_ok=True)


def parse(shelter):
    res = []
    for key, val in shelter.items():
        for item in val:
            for shelter in item["shelter"]:
                res.append(
                    [
                        key,
                        item["cityID"],
                        shelter["name"],
                        shelter["tel"],
                        shelter["address"],
                        shelter["status"],
                        shelter["shelterCode"],
                        item["timestamp"],
                    ]
                )
    return res


def export_csv(shelter):
    with open("./out/shelter.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "prefID",
                "cityID",
                "name",
                "tel",
                "address",
                "status",
                "shelterCode",
                "timestamp",
            ]
        )
        writer.writerows(parse(shelter))


def export_sqlite(shelter):
    db_path = Path("./out/shelter.db")
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE shelter (prefID, cityID, name, tel, address, status, shelterCode, timestamp)"
    )
    cur.executemany(
        "INSERT INTO shelter VALUES (?, ?, ?, ?, ?, ?, ?, ?)", parse(shelter)
    )
    conn.commit()
    conn.close()


# 避難情報が出ている都道府県の一覧を取得
hinan_all_url = "https://www5.nhk.or.jp/saigai-data/update/hinan_condition_all.json"

response_hinan = requests.get(hinan_all_url)
hinan = json.loads(response_hinan.text)["hinan_condition_all"]["flg"]
print(hinan)

# 避難所情報を取得
shelter_url = "https://www5.nhk.or.jp/saigai-data/update/ss/shelter_{0}.json"
shelter = {}
for val in hinan:
    prefID = val["prefID"]
    response_shelter = requests.get(shelter_url.format(prefID))
    shelter[prefID] = json.loads(response_shelter.text)["shelter"]

export_csv(shelter)

print("----shelter----")
for key, val in shelter.items():
    print(key)
    for item in val:
        print(item["cityID"], item["source"])
