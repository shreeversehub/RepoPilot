# 🛠️ RepoPilot — Repository Health Assistant

RepoPilot is a lightweight developer tool that analyzes a software repository and produces a practical health report.

## Problem

Repository quality problems are often distributed across documentation, dependencies, tests, CI configuration, and accidental secret files. Developers can miss these issues during fast development.

## Solution

RepoPilot turns a repository ZIP into a structured health assessment:

**Repository → Static Scan → Engineering Signals → Health Score → Findings → Recommendations → Markdown Report**

### Features

- Repository structure analysis
- Programming-language detection
- Dependency manifest detection
- README/documentation check
- Test-file detection
- GitHub Actions / CI detection
- Potential secret-file detection
- Source-size signal
- Explainable health score
- Actionable recommendations
- Downloadable Markdown report

## Tech Stack

- Python
- Streamlit
- pathlib
- zipfile
- collections

Streamlit provides the interactive web interface and file-upload workflow.

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Demo

1. Create a ZIP of a small repository.
2. Open RepoPilot.
3. Upload the ZIP.
4. Click **Analyze repository**.
5. Show the health score and findings.
6. Download the Markdown report.

## Security note

RepoPilot is a prototype static analyzer. Do not upload private repositories, credentials, API keys, or sensitive files to an untrusted deployment.

## AI disclosure

This prototype uses deterministic, explainable engineering rules for its repository-health recommendations rather than a hosted generative-AI model. If an AI coding assistant was used 
while developing this project, disclose the tool and its role in the hackathon submission as required by the rules.

## 🔮 Future Improvements

RepoPilot can be extended with:

- **Sandboxed automated test execution**
- **AST-based code-quality analysis**
- **Dependency vulnerability scanning**
- **GitHub repository integration**
- **Pull-request health checks**
- **Historical repository health tracking**
- **Optional LLM-based explanations**

Our goal is to evolve RepoPilot from a simple repository analyzer into a practical **developer-assistance platform for maintaining healthier software projects**.

## Limitations

The analyzer does not execute arbitrary repository code. It uses static repository signals and filename/content metadata. A future version could add sandboxed test execution, dependency vulnerability scanning, AST-based code-quality analysis, and an optional local/hosted LLM explanation layer.
