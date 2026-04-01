# MuseTalk-RT: MuseTalk 기반 런타임 후보의 제품화/검증 스택

- 언어: [English](README.md) | **한국어** | [日本語](README.ja.md)

## 이 프로젝트는 무엇인가요?
MuseTalk-RT는 MuseTalk 기반의 체감 실시간 대화형 아바타 런타임 후보를 위한 **제품화 + 검증 스택**입니다.

이 저장소는 아직 프로덕션 런타임 자체가 아닙니다.
대신, 플래그 기반 비프로덕션 검증 계층으로서 런타임 후보를 측정 가능하고, 디버깅 가능하며, 신뢰 가능한 상태로 만들고 카나리 준비도를 높이기 위해 존재합니다.

## 프로젝트 북극성 (North Star)
MuseTalk 파생 런타임 후보를 체감 실시간 대화형 아바타 시스템 방향으로 제품화하고,
플래그 기반 검증에서 사람 평가 근거를 갖춘 카나리 준비 단계로 전환하는 것입니다.

## Current Status (요약)
자세한 내용은 [docs/PROJECT_STATUS.ko.md](docs/PROJECT_STATUS.ko.md) 참고.

### 완료된 항목
- 웜 패스 정책 정의/운영
- 라이프사이클 검증 체인 구축 (readiness→dry-run→smoke→tiny real→lifecycle-aware→flagged e2e)
- 4개 핵심 라이프사이클 단계의 flagged 경로 provisional real-wired 확보
- 30회 flagged 신뢰성 검증: fallback 0, stage error 0
- bursty/jittery 스트레스 조건에서도 라이프사이클 안정성 유지
- 품질 텔레메트리 + 휴먼 QA 팩/스코어카드/의사결정 레이어 구축
- 로컬 GUI 및 다국어 문서 정비

### 남은 항목
- 실제 리뷰어 점수 수집/누적
- warn-only 카나리 증거 패키지 완성
- 모바일/네트워크 유사 조건에서의 지각 품질 근거 확보
- 더 넓은 제품 준비성 입증

## Korean quickstart
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
1. [docs/PROJECT_STATUS.ko.md](docs/PROJECT_STATUS.ko.md)
2. [docs/GETTING_STARTED.ko.md](docs/GETTING_STARTED.ko.md)
3. [docs/ARCHITECTURE.ko.md](docs/ARCHITECTURE.ko.md)
4. [docs/QA_WORKFLOW.ko.md](docs/QA_WORKFLOW.ko.md)
5. [docs/REPORTS_AND_DECISIONS.ko.md](docs/REPORTS_AND_DECISIONS.ko.md)
6. [docs/ROADMAP.ko.md](docs/ROADMAP.ko.md)

## 실행 준비 문서
- 리뷰어 인수인계: [docs/REVIEWER_HANDOFF.md](docs/REVIEWER_HANDOFF.md)
- 유지보수자 체크리스트: [docs/MAINTAINER_DECISION_CHECKLIST.md](docs/MAINTAINER_DECISION_CHECKLIST.md)

## 로컬 GUI
```bash
pip install streamlit
streamlit run app/qa_dashboard.py
```
