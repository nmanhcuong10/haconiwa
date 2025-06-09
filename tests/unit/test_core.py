import os
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import yaml

from haconiwa.core.config import Config
from haconiwa.core.state import StateManager
from haconiwa.core.logging import haconiwaLogger
from haconiwa.core.upgrade import Upgrader

@pytest.fixture
def temp_config_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'version': '0.1.0',
            'core': {
                'log_level': 'INFO',
                'state_dir': '/tmp/haconiwa'
            }
        }, f)
    yield Path(f.name)
    os.unlink(f.name)

@pytest.fixture
def config(temp_config_file):
    return Config(config_path=temp_config_file)

@pytest.fixture
def state_manager(config):
    return StateManager(config_path=str(config.config_path))

@pytest.fixture
def logger(config):
    return haconiwaLogger("test", config)

class TestConfig:
    def test_load_config(self, config):
        assert config.version == '0.1.0'
        assert config.core.log_level == 'INFO'
        assert config.core.state_dir == '/tmp/haconiwa'

    def test_invalid_config_path(self):
        with pytest.raises(FileNotFoundError):
            Config(config_path=Path('/nonexistent/config.yaml'))

    def test_save_config(self, config, temp_config_file):
        config.core.log_level = 'DEBUG'
        config.save()
        
        loaded = yaml.safe_load(temp_config_file.read_text())
        assert loaded['core']['log_level'] == 'DEBUG'

class TestStateManager:
    def test_state_manager_initialization(self, state_manager):
        assert state_manager.state == {}

    def test_state_save_load(self, state_manager):
        test_data = {'key': 'value'}
        state_manager.update_state('test', test_data)
        loaded = state_manager.get_state('test')
        assert loaded == test_data

    @patch('os.path.exists')
    def test_state_load_from_file(self, mock_exists, state_manager):
        mock_exists.return_value = True
        
        with patch('builtins.open'), patch('pickle.load') as mock_load:
            mock_load.return_value = {'loaded': 'data'}
            state_manager.load_state('test.pkl')
            assert state_manager.state == {'loaded': 'data'}

class TestHaconiwaLogger:
    def test_logger_initialization(self, logger):
        assert logger.name == "test"
        assert logger.logger is not None

    def test_log_messages(self, logger):
        with patch('haconiwa.core.logging.haconiwaLogger._log') as mock_log:
            logger.info('test message')
            mock_log.assert_called_once()

    def test_log_levels(self, logger):
        with patch('haconiwa.core.logging.haconiwaLogger._log') as mock_log:
            logger.debug('debug message')
            logger.info('info message')
            logger.warning('warning message')
            logger.error('error message')
            logger.critical('critical message')
            
            assert mock_log.call_count == 5

class TestUpgrader:
    @pytest.fixture
    def upgrader(self, config):
        return Upgrader(config)

    def test_version_check(self, upgrader):
        assert upgrader.needs_upgrade('0.0.9') is True
        assert upgrader.needs_upgrade('0.1.1') is False

    @patch('haconiwa.core.upgrade.Upgrader.perform_upgrade')
    def test_upgrade_process(self, mock_upgrade, upgrader):
        upgrader.upgrade_if_needed('0.0.9')
        mock_upgrade.assert_called_once()

    def test_invalid_version(self, upgrader):
        with pytest.raises(ValueError):
            upgrader.needs_upgrade('invalid')

def test_core_integration(config, state_manager, logger):
    # ログ設定をスキップ（テスト環境では複雑になるため）
    state_manager.update_state('app_state', {'status': 'running'})
    
    loaded_state = state_manager.get_state('app_state')
    assert loaded_state == {'status': 'running'}
    
    logger.info('Integration test completed')
    assert logger.name == "test"