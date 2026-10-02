from pathlib import Path
from collections import Counter
import re

IGNORE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", "node_modules", "venv", ".venv",
    "dist", "build", ".next", ".idea", ".vscode", "coverage"
}

SOURCE_EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".java": "Java",
    ".c": "C", ".cpp": "C++", ".h": "C/C++", ".cs": "C#",
    ".go": "Go", ".rs": "Rust", ".php": "PHP", ".rb": "Ruby",
    ".kt": "Kotlin", ".swift": "Swift", ".sql": "SQL"
}

DEPENDENCY_FILES = {
    "requirements.txt", "pyproject.toml", "poetry.lock", "Pipfile",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "pom.xml", "build.gradle", "go.mod", "Cargo.toml", "Gemfile"
}

TEST_HINTS = ("test", "tests", "spec", "__tests__")
SECRET_NAMES = {".env", ".env.local", ".env.production", "credentials.json", "service-account.json"}

def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        yield p

def analyze_repository(root: Path):
    files = list(iter_files(root))
    suffixes = Counter()
    languages = Counter()
    dependency_files = []
    test_files = []
    secret_files = []
    source_files = 0
    total_lines = 0

    for p in files:
        suffix = p.suffix.lower()
        suffixes[suffix] += 1
        if suffix in SOURCE_EXTENSIONS:
            languages[SOURCE_EXTENSIONS[suffix]] += 1
            source_files += 1
            try:
                total_lines += len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
            except Exception:
                pass
        if p.name.lower() in {x.lower() for x in DEPENDENCY_FILES}:
            dependency_files.append(str(p.relative_to(root)))
        low = str(p.relative_to(root)).lower()
        if any(h in low for h in TEST_HINTS):
            test_files.append(str(p.relative_to(root)))
        if p.name.lower() in SECRET_NAMES or ".env" in p.name.lower():
            secret_files.append(str(p.relative_to(root)))

    readme = any(p.name.lower().startswith("readme") for p in files)
    ci_cd = any(
        ".github" in p.parts and "workflows" in p.parts
        for p in files
    )

    findings = []
    score = 100

    if not readme:
        score -= 15
        findings.append({
            "severity": "Medium",
            "title": "README documentation is missing",
            "detail": "A new developer may not know how to install, configure, and run the project.",
            "recommendation": "Add a README with overview, prerequisites, setup, usage, and screenshots."
        })

    if not dependency_files:
        score -= 10
        findings.append({
            "severity": "Low",
            "title": "Dependency manifest not detected",
            "detail": "The repository does not contain a common dependency/lock file.",
            "recommendation": "Add a dependency manifest such as requirements.txt, pyproject.toml, or package.json."
        })

    if not test_files:
        score -= 20
        findings.append({
            "severity": "High",
            "title": "No test files detected",
            "detail": "Automated tests were not detected using common naming conventions.",
            "recommendation": "Add unit tests for core functions and run them before releases."
        })

    if not ci_cd:
        score -= 10
        findings.append({
            "severity": "Low",
            "title": "CI workflow not detected",
            "detail": "No GitHub Actions workflow was found in .github/workflows.",
            "recommendation": "Add CI to install dependencies and run tests on every pull request."
        })

    if secret_files:
        score -= min(25, 10 + 5 * (len(secret_files) - 1))
        findings.append({
            "severity": "High",
            "title": "Potential secret files detected",
            "detail": f"Found {len(secret_files)} file(s) that commonly contain credentials.",
            "recommendation": "Remove secrets from Git history, rotate exposed credentials, and use environment variables."
        })

    if total_lines > 15000:
        score -= 5
        findings.append({
            "severity": "Low",
            "title": "Large source footprint",
            "detail": f"Approximately {total_lines:,} source lines were detected.",
            "recommendation": "Consider modularizing large components and adding architecture documentation."
        })

    primary = languages.most_common(1)[0][0] if languages else "Unknown"

    recommendations = []
    if not readme:
        recommendations.append("Create a concise README before onboarding another developer.")
    if not test_files:
        recommendations.append("Introduce tests around the most important business logic.")
    if not ci_cd:
        recommendations.append("Add a lightweight CI workflow so every change gets automated validation.")
    if secret_files:
        recommendations.append("Audit repository history for credentials before making the repository public.")
    if dependency_files:
        recommendations.append("Pin or lock dependencies to improve reproducibility.")
    if not recommendations:
        recommendations.append("Maintain the current engineering hygiene and review findings on every release.")

    return {
        "score": max(0, min(100, score)),
        "file_count": len(files),
        "source_files": source_files,
        "test_files": len(test_files),
        "languages": [x for x, _ in languages.most_common()],
        "primary_language": primary,
        "dependency_files": dependency_files,
        "secret_files": secret_files,
        "readme": readme,
        "ci_cd": ci_cd,
        "total_source_lines": total_lines,
        "findings": findings,
        "recommendations": recommendations,
    }

def build_markdown_report(r):
    lines = [
        f"# RepoPilot Health Report — {r['project_name']}",
        "",
        f"Generated: {r.get('analyzed_at', '')}",
        "",
        f"## Health score: {r['score']}/100",
        "",
        "| Signal | Result |",
        "|---|---|",
        f"| Files scanned | {r['file_count']} |",
        f"| Source files | {r['source_files']} |",
        f"| Primary language | {r['primary_language']} |",
        f"| Languages | {', '.join(r['languages']) or 'None detected'} |",
        f"| README | {'Present' if r['readme'] else 'Missing'} |",
        f"| Tests detected | {r['test_files']} |",
        f"| CI/CD | {'Detected' if r['ci_cd'] else 'Not detected'} |",
        f"| Potential secret files | {len(r['secret_files'])} |",
        "",
        "## Findings",
        ""
    ]
    if r["findings"]:
        for f in r["findings"]:
            lines.append(f"- **{f['severity']} — {f['title']}**: {f['detail']} Recommendation: {f['recommendation']}")
    else:
        lines.append("- No major findings detected.")
    lines += ["", "## Recommendations", ""]
    lines += [f"- {x}" for x in r["recommendations"]]
    return "\n".join(lines)
