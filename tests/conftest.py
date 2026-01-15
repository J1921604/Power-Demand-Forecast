# -*- coding: utf-8 -*-
"""
Pytest Configuration and Fixtures
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

# Add AI directory to sys.path for imports
PROJECT_ROOT = Path(__file__).parent.parent
AI_DIR = PROJECT_ROOT / "AI"
sys.path.insert(0, str(AI_DIR))

# ================================================================
# Test Data Fixtures
# ================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """一時ディレクトリを作成して返す"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_power_csv(temp_dir: Path) -> Path:
    """サンプル電力データCSVを作成"""
    csv_path = temp_dir / "juyo-2024.csv"
    csv_content = """東京電力管内,電力需要実績,,,,,,,
年月日,時刻,実績(万kW),,,,,,,
2024/01/01,0:00,2500,,,,,,,
2024/01/01,1:00,2400,,,,,,,
2024/01/01,2:00,2300,,,,,,,
2024/01/01,3:00,2200,,,,,,,
2024/01/01,4:00,2150,,,,,,,
"""
    csv_path.write_text(csv_content, encoding='shift_jis')
    return csv_path


@pytest.fixture
def sample_temp_csv(temp_dir: Path) -> Path:
    """サンプル気温データCSVを作成"""
    csv_path = temp_dir / "temperature-2024.csv"
    csv_content = """東京,気温,,,,,,,
測定日,測定時刻,気温(℃),,,,,,,
ヘッダー1,ヘッダー2,ヘッダー3,,,,,,,
ヘッダー4,ヘッダー5,ヘッダー6,,,,,,,
2024/01/01,0:00,5.2,,,,,,,
2024/01/01,1:00,5.0,,,,,,,
2024/01/01,2:00,4.8,,,,,,,
2024/01/01,3:00,4.5,,,,,,,
2024/01/01,4:00,4.3,,,,,,,
"""
    csv_path.write_text(csv_content, encoding='shift_jis')
    return csv_path


@pytest.fixture
def mock_env_target_years(monkeypatch):
    """AI_TARGET_YEARS環境変数をモック"""
    def _set_years(years_str: str):
        monkeypatch.setenv('AI_TARGET_YEARS', years_str)
    return _set_years


# ================================================================
# Test Configuration
# ================================================================

def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (database, API)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full system)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests (benchmarking)"
    )
    config.addinivalue_line(
        "markers", "contract: Contract tests (API spec validation)"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on directory"""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "contract" in str(item.fspath):
            item.add_marker(pytest.mark.contract)
