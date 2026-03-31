# MuseTalk-RT（フラグ付き・非本番向け評価ツールキット）

- 言語: [English](README.md) | [한국어](README.ko.md) | **日本語**

## このプロジェクトは何か？
MuseTalk-RTは、MuseTalk系のセッション開始・連続性品質を検証するための**ローカル評価/QAツール群**です。
本番向けUIや運用オーケストレーションではなく、安定条件と劣化条件の比較、ライフサイクル計測、人的レビュー、カナリア判断を支援します。

## 現在の成熟度
- フラグ付き検証として、信頼性・品質・ストレス評価の流れは整備済み
- Human QAパックと判断レイヤーを利用可能
- ただし、製品準備完了の主張には追加エビデンスが必要（複数回の人手評価と評価者間整合）

## Japanese quickstart
```bash
python benchmarks/baseline/run_flagged_e2e_human_qa_pack.py   --stable-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_qv12_report.json   --bursty-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_bursty_qv12_report.json   --jittery-report benchmarks/baseline/reports/lifecycle_e2e_flagged_session_probe_audio_session_real_stress_jittery_qv12_report.json

python benchmarks/baseline/run_flagged_e2e_human_qa_decision.py   --qa-pack benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1.json   --scorecard benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_scorecard_template.json
```

## Typical workflow
1. [docs/GETTING_STARTED.ja.md](docs/GETTING_STARTED.ja.md)
2. [docs/ARCHITECTURE.ja.md](docs/ARCHITECTURE.ja.md)
3. [docs/QA_WORKFLOW.ja.md](docs/QA_WORKFLOW.ja.md)
4. [docs/REPORTS_AND_DECISIONS.ja.md](docs/REPORTS_AND_DECISIONS.ja.md)

## ローカルGUI
```bash
pip install streamlit
streamlit run app/qa_dashboard.py
```
