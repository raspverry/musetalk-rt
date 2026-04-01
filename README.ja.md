# MuseTalk-RT：MuseTalk系ランタイム候補の製品化・検証スタック

- 言語: [English](README.md) | [한국어](README.ko.md) | **日本語**

## このプロジェクトは何か？
MuseTalk-RTは、MuseTalkベースの「体感リアルタイム会話アバター」ランタイム候補を前進させるための**製品化＋検証スタック**です。

本リポジトリは、まだ本番ランタイムそのものではありません。
一方で、単なるQAツール集でもありません。ランタイム候補を計測可能・デバッグ可能・信頼可能な状態へ引き上げ、
フラグ付き非本番の範囲でカナリア準備度を判断するための中核レイヤーです。

## プロジェクトの北極星
MuseTalk派生ランタイム候補を、体感リアルタイム会話アバター基盤として成立させること。
そのために、検証スタックで得た技術的・品質的エビデンスを段階的に積み上げ、限定カナリアへ移行することを目標とします。

## Current Status（要約）
詳細は [docs/PROJECT_STATUS.ja.md](docs/PROJECT_STATUS.ja.md) を参照してください。

### 完了したこと
- Warm-pathポリシーを定義し運用化
- ライフサイクル検証チェーンを整備（readiness→dry-run→smoke→tiny real→lifecycle-aware→flagged e2e）
- 4つの主要ライフサイクル段階を、flagged経路で provisional real-wired 化
- 30-run 信頼性検証で fallback 0 / stage error 0
- bursty/jittery ストレス条件でもライフサイクル安定性を維持
- 品質テレメトリ、Human QAパック、スコアカード、判定レイヤーを整備
- ローカルGUIと多言語ドキュメントを整備

### 未完了のこと
- 実レビュアーによるスコア収集の本格運用
- warn-only カナリア判断の証拠パッケージ完成
- モバイル/ネットワーク劣化想定での知覚品質エビデンス
- より広い製品準備性の立証

## Japanese quickstart
```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py \
  --stable-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_qv12_report.json \
  --bursty-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_bursty_qv12_report.json \
  --jittery-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_jittery_qv12_report.json

python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py \
  --qa-pack benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1.json \
  --scorecard benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_scorecard_template.json
```

## Typical workflow
1. [docs/PROJECT_STATUS.ja.md](docs/PROJECT_STATUS.ja.md)
2. [docs/GETTING_STARTED.ja.md](docs/GETTING_STARTED.ja.md)
3. [docs/ARCHITECTURE.ja.md](docs/ARCHITECTURE.ja.md)
4. [docs/QA_WORKFLOW.ja.md](docs/QA_WORKFLOW.ja.md)
5. [docs/REPORTS_AND_DECISIONS.ja.md](docs/REPORTS_AND_DECISIONS.ja.md)
6. [docs/ROADMAP.ja.md](docs/ROADMAP.ja.md)

## 実行準備ドキュメント
- レビュアー引き継ぎ: [docs/REVIEWER_HANDOFF.md](docs/REVIEWER_HANDOFF.md)
- メンテナ向け判定チェックリスト: [docs/MAINTAINER_DECISION_CHECKLIST.md](docs/MAINTAINER_DECISION_CHECKLIST.md)

## ローカルGUI
```bash
pip install streamlit
streamlit run app/qa_dashboard.py
```
