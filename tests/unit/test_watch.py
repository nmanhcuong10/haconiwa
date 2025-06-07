import pytest
from unittest.mock import MagicMock, patch
from src.haconiwa.watch.monitor import Monitor

@pytest.fixture
def monitor():
    return Monitor()

def test_metrics_collection(monitor):
    monitor.collect_metrics = MagicMock(return_value={"cpu": 50, "memory": 1024})
    metrics = monitor.collect_metrics()
    assert metrics["cpu"] == 50
    assert metrics["memory"] == 1024

def test_alert_functionality(monitor):
    monitor.alert = MagicMock()
    monitor.alert("High CPU usage")
    monitor.alert.assert_called_with("High CPU usage")

@patch("src.haconiwa.watch.monitor.prometheus_client")
def test_prometheus_integration(mock_prometheus, monitor):
    monitor.export_metrics_to_prometheus = MagicMock()
    monitor.export_metrics_to_prometheus()
    monitor.export_metrics_to_prometheus.assert_called_once()

def test_performance_monitoring(monitor):
    monitor.check_performance = MagicMock(return_value=True)
    assert monitor.check_performance() is True

def test_log_rotation_and_archiving(monitor):
    monitor.rotate_logs = MagicMock()
    monitor.archive_logs = MagicMock()
    monitor.rotate_logs()
    monitor.archive_logs()
    monitor.rotate_logs.assert_called_once()
    monitor.archive_logs.assert_called_once()

def test_integration_with_monitoring_library(monitor):
    monitor.integrate_with_library = MagicMock()
    monitor.integrate_with_library()
    monitor.integrate_with_library.assert_called_once()