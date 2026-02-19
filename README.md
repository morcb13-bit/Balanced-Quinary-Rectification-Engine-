# B-QRE: Balanced Quinary Rectification Engine

平衡5進数を使ったGNSSデッドレコニング補正 — Proof of Concept

---

## 概要

GPS信号が途絶えた30秒間、スマホの位置表示は止まる。  
B-QREはその空白を、スマホ内蔵センサーと平衡5進数の対称性で埋める試みです。

簡易シミュレーションでは、信号ロスト30秒後の位置誤差を **27.81 m → 12.69 m（約54%削減）** できることを確認しました。

**本リポジトリはProof of Conceptです。実機検証は未実施です。**

---

## ファイル構成

```
├── README.md           # このファイル
├── bqre_simulation.py  # シミュレーションコード本体
└── B-QRE_article.md    # Zenn記事（詳細解説）
```

---

## 実行方法

```bash
pip install numpy matplotlib
python bqre_simulation.py
```

出力: シミュレーション結果のグラフ（PNG）とRMSE数値

---

## ライセンス

MIT License

フィードバック・プルリクエスト歓迎します。
