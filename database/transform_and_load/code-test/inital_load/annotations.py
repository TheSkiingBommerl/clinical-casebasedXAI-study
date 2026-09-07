import pandas as pd
from database.db_connection import store_data

def load_annotations(file_name, table_name):
    df = pd.read_csv(f"automatic-ecg-diagnosis/data/annotations/{file_name}.csv")

    rows = []

    for i in range(827):

        row = (
            i,
            int(df.iloc[i]["1dAVb"]),
            int(df.iloc[i]["RBBB"]),
            int(df.iloc[i]["LBBB"]),
            int(df.iloc[i]["SB"]),
            int(df.iloc[i]["AF"]),
            int(df.iloc[i]["ST"])
        )

        rows.append(row)

    query = f"""
    INSERT INTO "code-test".{table_name}
    (id, "1dAVb",RBBB,LBBB,SB,AF,ST)   
    VALUES %s
    """

    store_data(query, rows)

load_annotations("gold_standard", "gold_lable")
load_annotations("dnn", "dnn_annotations")
 
