import io
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import streamlit as st

from analyzer import analyze_repository, build_markdown_report

st.set_page_config(
    page_title="RepoPilot",
    page_icon="🛠️",
    layout="wide",
)

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
.hero {padding: 1.2rem 1.4rem; border: 1px solid #30363d; border-radius: 14px; background: linear-gradient(135deg,#111827,#172033);}
.hero h1 {margin: 0; font-size: 2.2rem;}
.hero p {margin: .45rem 0 0; color: #b8c2d1;}
.metric-card {border:1px solid #30363d; border-radius:12px; padding:1rem; background:#111827;}
.small {color:#8b98aa;font-size:.9rem;}
.issue {padding:.8rem 1rem;border-radius:10px;border:1px solid #30363d;margin:.45rem 0;}
</style>
""", unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None

st.markdown("""
<div class="hero">
<h1>🛠️ RepoPilot</h1>
<p>Repository Health Assistant — inspect structure, dependencies, tests, documentation, and maintainability signals in one run.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Repository input")
    uploaded = st.file_uploader(
        "Upload a repository ZIP",
        type=["zip"],
        help="ZIP the project folder first. Do not upload secrets such as .env files or API keys."
    )
    st.caption("For the demo, use a small public/sample repository ZIP.")

    st.divider()
    st.subheader("Checks")
    st.write("✓ Repository structure")
    st.write("✓ Language detection")
    st.write("✓ Dependency files")
    st.write("✓ Test presence")
    st.write("✓ README/documentation")
    st.write("✓ Common secret-file detection")
    st.write("✓ Code-size signals")
    st.write("✓ Intelligent recommendations")

if uploaded:
    if st.button("🔍 Analyze repository", type="primary", use_container_width=True):
        temp_dir = Path(tempfile.mkdtemp(prefix="repopilot_"))
        try:
            data = uploaded.getvalue()
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                # Basic zip-slip protection
                for member in z.infolist():
                    target = (temp_dir / member.filename).resolve()
                    if not str(target).startswith(str(temp_dir.resolve())):
                        raise ValueError("Unsafe ZIP path detected.")
                z.extractall(temp_dir)

            # If ZIP contains a single top-level directory, analyze inside it.
            children = [p for p in temp_dir.iterdir()]
            repo_root = children[0] if len(children) == 1 and children[0].is_dir() else temp_dir

            result = analyze_repository(repo_root)
            result["project_name"] = uploaded.name.rsplit(".", 1)[0]
            result["analyzed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.result = result
        except Exception as e:
            st.error(f"Analysis failed: {e}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

result = st.session_state.result

if not result:
    st.info("Upload a repository ZIP and click **Analyze repository** to generate a health report.")
    st.markdown("### Demo flow")
    st.markdown("**ZIP → Scan → Health Score → Findings → Recommendations → Markdown Report**")
else:
    score = result["score"]
    status = "Healthy" if score >= 80 else "Needs attention" if score >= 60 else "At risk"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Health score", f"{score}/100")
    c2.metric("Files scanned", result["file_count"])
    c3.metric("Languages", len(result["languages"]))
    c4.metric("Findings", len(result["findings"]))

    st.subheader(f"Repository status: {status}")
    st.progress(score / 100)

    left, right = st.columns(2)
    with left:
        st.markdown("### 🧭 Repository profile")
        st.write(f"**Project:** {result['project_name']}")
        st.write(f"**Primary language:** {result['primary_language']}")
        st.write(f"**Languages:** {', '.join(result['languages']) or 'Not detected'}")
        st.write(f"**Source files:** {result['source_files']}")
        st.write(f"**Test files:** {result['test_files']}")
    with right:
        st.markdown("### 📦 Project signals")
        st.write(f"**README:** {'Present' if result['readme'] else 'Missing'}")
        st.write(f"**Dependencies:** {', '.join(result['dependency_files']) or 'Not detected'}")
        st.write(f"**CI/CD:** {'Detected' if result['ci_cd'] else 'Not detected'}")
        st.write(f"**Potential secret files:** {len(result['secret_files'])}")

    st.markdown("### 🚦 Findings")
    if not result["findings"]:
        st.success("No major repository-health findings detected.")
    else:
        for item in result["findings"]:
            icon = {"High":"🔴", "Medium":"🟠", "Low":"🟡"}.get(item["severity"], "ℹ️")
            st.markdown(
                f'<div class="issue"><b>{icon} {item["severity"]}: {item["title"]}</b><br>'
                f'{item["detail"]}<br><span class="small">Recommendation: {item["recommendation"]}</span></div>',
                unsafe_allow_html=True
            )

    st.markdown("### 🤖 Intelligent recommendations")
    for rec in result["recommendations"]:
        st.write(f"• {rec}")

    report = build_markdown_report(result)
    st.download_button(
        "⬇️ Download health report",
        data=report,
        file_name=f"{result['project_name']}_repopilot_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

    with st.expander("Technical analysis output"):
        st.json(result)
