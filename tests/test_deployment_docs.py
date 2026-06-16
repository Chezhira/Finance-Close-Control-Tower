from __future__ import annotations

from pathlib import Path


def test_streamlit_cloud_entrypoint_exists() -> None:
    app_path = Path("app.py")
    content = app_path.read_text(encoding="utf-8")

    assert app_path.exists()
    assert "import streamlit as st" in content
    assert "st.file_uploader" not in content


def test_requirements_are_runtime_only_for_public_demo() -> None:
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()

    assert requirements == [
        "duckdb>=1.0",
        "openpyxl>=3.1",
        "pandas>=2.2",
        "streamlit>=1.36",
    ]
    assert not any("pytest" in requirement for requirement in requirements)
    assert not any("ruff" in requirement for requirement in requirements)
    assert "-e ." not in requirements


def test_readme_has_streamlit_cloud_public_demo_path() -> None:
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Streamlit Community Cloud Public Demo" in content
    assert "Public demo URL: `https://finance-close-control-tower.streamlit.app/`" in content
    assert "Set the app entrypoint to `app.py`" in content


def test_readme_positions_project_as_finance_control_layer() -> None:
    paragraphs = Path("README.md").read_text(encoding="utf-8").split("\n\n")
    first_paragraph = next(
        paragraph for paragraph in paragraphs if "Finance Close Control Tower is" in paragraph
    )

    assert "finance systems control layer" in first_paragraph
    assert "CFO-ready view" in first_paragraph
    assert "generic dashboard" not in first_paragraph.lower()


def test_release_readiness_docs_exist() -> None:
    for path in [
        Path("LICENSE"),
        Path("NOTICE"),
        Path("SECURITY.md"),
        Path("CHANGELOG.md"),
        Path("docs/release_checklist.md"),
        Path("docs/screenshots/README.md"),
    ]:
        assert path.exists(), str(path)


def test_readme_includes_release_required_sections() -> None:
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Target portfolio roles:" in content
    assert "Public demo URL: `https://finance-close-control-tower.streamlit.app/`" in content
    assert "Demo Outputs" in content
    assert "No employer, client, bank, payroll, customer, supplier" in content


def test_deployment_docs_define_supported_targets() -> None:
    content = Path("docs/deployment.md").read_text(encoding="utf-8")

    assert "Streamlit Community Cloud is the primary public MVP deployment target" in content
    assert "Docker and Google Cloud Run are secondary/stretch deployment targets" in content
    assert "GitHub Pages may be used only for static documentation" in content
    assert "must not be treated as the host for the Python Streamlit application" in content


def test_dockerignore_blocks_private_runtime_files() -> None:
    content = Path(".dockerignore").read_text(encoding="utf-8").splitlines()

    assert ".env" in content
    assert ".env.*" in content
    assert "data/private" in content
    assert "outputs/private" in content


def test_dockerfile_defaults_to_low_risk_demo_mode() -> None:
    content = Path("Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.11-slim" in content
    assert "READ_ONLY_DEMO=true" in content
    assert "ALLOW_FILE_UPLOADS=false" in content
    assert "PERSIST_UPLOADED_FILES=false" in content
    assert "ENABLE_LLM_COMMENTARY=false" in content
    assert "streamlit" in content


def test_no_private_paths_or_env_files_in_public_tree() -> None:
    forbidden_paths = [
        Path(".env"),
        Path("data/private"),
        Path("outputs/private"),
    ]

    for path in forbidden_paths:
        assert not path.exists(), str(path)

    text_suffixes = {
        "",
        ".css",
        ".dockerignore",
        ".env",
        ".example",
        ".gitignore",
        ".html",
        ".json",
        ".md",
        ".py",
        ".toml",
        ".txt",
        ".yml",
    }
    skipped_binary_suffixes = {
        ".gif",
        ".ico",
        ".jpeg",
        ".jpg",
        ".pdf",
        ".png",
        ".webp",
        ".bin",
        ".xlsx",
        ".pyc",
    }
    searchable_files = [
        path
        for path in Path(".").rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and ".ruff_cache" not in path.parts
        and ".pytest_tmp" not in path.parts
        and path.suffix.lower() not in skipped_binary_suffixes
        and path.suffix.lower() in text_suffixes
    ]
    forbidden_text = (
        "C:" + "\\Users",
        "OneDrive - " + "chezsolutions",
        "BEGIN " + "PRIVATE " + "KEY",
    )

    for path in searchable_files:
        content = path.read_text(encoding="utf-8")
        assert not any(token in content for token in forbidden_text), str(path)
