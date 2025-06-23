import sys
import argparse
import numpy as np


def load_data(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    return np.array([float(line.strip()) for line in lines])


def main():
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(
        description="Compute relative difference between two numeric vectors."
    )
    parser.add_argument("file1", nargs="?", help="First input filename")
    parser.add_argument("file2", nargs="?", help="Second input filename")
    args = parser.parse_args()

    # 引数が足りなければ標準入力から取得
    if not args.file1:
        args.file1 = input("Enter first filename: ").strip()
    if not args.file2:
        args.file2 = input("Enter second filename: ").strip()

    # ファイル読み込み
    try:
        data1 = load_data(args.file1)
        data2 = load_data(args.file2)
    except Exception as e:
        print(f"Error loading files: {e}", file=sys.stderr)
        sys.exit(1)

    # 長さを揃えて計算
    min_len = min(len(data1), len(data2))
    vec1 = data1[:min_len]
    vec2 = data2[:min_len]

    # コサイン類似度（必要ならコメント解除）
    # cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    # print(f"Cosine Similarity: {cos_sim:.6f}")

    # 相対距離の計算
    relative_diff = np.linalg.norm(vec1 - vec2) / np.linalg.norm(vec1)
    print(f"Relative Difference: {relative_diff:.6f}")


if __name__ == "__main__":
    main()
