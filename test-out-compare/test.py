import numpy as np


def load_data(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    # 数値に変換してリストに
    return np.array([float(line.strip()) for line in lines])


# ファイル読み込み
data1 = load_data("1.txt")
data2 = load_data("2.txt")

# 最小の長さで切り揃え
min_len = min(len(data1), len(data2))
vec1 = data1[:min_len]
vec2 = data2[:min_len]

# コサイン類似度の計算
# cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
# print(f"Cosine Similarity: {cos_sim}")

# 相対距離の計算
relative_diff = np.linalg.norm(vec1 - vec2) / np.linalg.norm(vec1)
print(f"Relative Difference: {relative_diff}")
