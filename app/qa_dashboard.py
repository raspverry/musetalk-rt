import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="MuseTalk-RT QA Dashboard", layout="wide")

LANG = st.sidebar.selectbox("Language / 언어 / 言語", ["EN", "KO", "JA"])
texts = {
    "EN": {"title": "MuseTalk-RT Local QA Dashboard", "scope": "Flagged, non-production only", "overview": "Project overview", "flow": "Typical workflow", "reports": "Report browser", "qa": "QA scoring", "decision": "Decision review"},
    "KO": {"title": "MuseTalk-RT 로컬 QA 대시보드", "scope": "플래그 기반 비프로덕션 전용", "overview": "프로젝트 개요", "flow": "일반 워크플로", "reports": "리포트 브라우저", "qa": "QA 점수", "decision": "의사결정 검토"},
    "JA": {"title": "MuseTalk-RT ローカルQAダッシュボード", "scope": "フラグ付き非本番専用", "overview": "プロジェクト概要", "flow": "典型ワークフロー", "reports": "レポート閲覧", "qa": "QAスコア", "decision": "判定レビュー"},
}
T = texts[LANG]

st.title(T["title"])
st.caption(T["scope"])

tab1, tab2, tab3, tab4 = st.tabs([T["overview"], T["reports"], T["qa"], T["decision"]])

with tab1:
    st.markdown("""
- This dashboard is local and lightweight.
- It does not modify runtime orchestration.
- Use it to browse artifacts and guide human QA decisions.
""")
    st.markdown("### " + T["flow"])
    st.markdown("1. Reliability/quality reports -> 2. QA pack -> 3. Scorecard -> 4. Decision summary")

with tab2:
    base = Path("benchmarks/baseline/reports")
    files = sorted(base.glob("*.json"))
    name = st.selectbox("JSON report", [f.name for f in files])
    if name:
        data = json.loads((base / name).read_text())
        st.json(data)

with tab3:
    score_path = Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_scorecard_template.json")
    if score_path.exists():
        score = json.loads(score_path.read_text())
        st.write("Scorecard template path:", str(score_path))
        st.json(score)
        st.info("Edit the scorecard JSON locally, then re-run decision script.")
    else:
        st.warning("Scorecard template not found.")

with tab4:
    dec_path = Path("benchmarks/baseline/reports/lifecycle_e2e_flagged_human_qa_pack_v1_decision_summary.json")
    if dec_path.exists():
        dec = json.loads(dec_path.read_text())
        st.write("Decision:", dec.get("decision"))
        st.write("Reason:", dec.get("reason"))
        st.write("Rollback:", dec.get("rollback_recommendation"))
        st.json(dec)
    else:
        st.warning("Decision summary not found.")
