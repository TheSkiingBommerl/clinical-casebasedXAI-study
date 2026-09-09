"""
This file produces a graph that shows the amount of abnormality data in the filtered PTB-XL dataset
"""

from collections import Counter

import matplotlib.pyplot as plt

from AI_diagnostic_support.database.db_connection import extract_data


def get_AI_prediction():

    query = """Select "1dAVb", rbbb, lbbb, sb, st, af
                From "ptb-xl".gold_lable
            """

    rows = extract_data(query)

    return rows

rows = get_AI_prediction()


position_mapping = {
    0: "1dAVb",
    1: "RBBB",
    2: "LBBB",
    3: "SB",
    4: "AF",
    5: "ST"
}

abnormalities = []

for row in rows:
    abnormalities.append([position_mapping.get(idx) for idx, val in enumerate(row) if val == 1])

amount_normal = 0

amount_normal = sum(1 for arr in abnormalities if not arr)
amount_abnormal = sum(1 for arr in abnormalities if arr)

print(amount_normal, amount_abnormal)

abnormalities = [arr for arr in abnormalities if arr]

counts = Counter(tuple(arr) for arr in abnormalities)

labels = [' + '.join(key) for key in counts.keys()]
values = list(counts.values())

labels, values = zip(*sorted(zip(labels, values), key=lambda x: x[1], reverse=True))

plt.figure()
bars = plt.bar(labels, values)

for bar, val in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
             str(val), ha="center", va="bottom", fontsize=9)

plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.xticks(rotation=45, ha='right')
plt.xlabel("Abnormalities", fontweight="bold")
plt.ylabel("Count", fontweight="bold")
#plt.title("Frequency of Abnormalities - PTB-XL")
#plt.title("Frequency of Abnormalities - Code-test")

plt.tight_layout()
plt.show()
