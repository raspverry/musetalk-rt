# アーキテクチャ（フラグ付き検証スタック）

- 言語: [EN](ARCHITECTURE.md) | [KO](ARCHITECTURE.ko.md) | **JA**

## 構成
- harness、baseline runner、approx fixture、reliability/quality/human-QA/decision スクリプト
- 生成物は `reports/` に集約

## Real と Proxy の境界
- 一部ライフサイクルはフラグ条件で real-wired 観測
- フレーム生成やケイデンスは fixture による近似
- fallback の可視性はレポートで維持

