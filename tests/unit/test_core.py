import os
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import yaml

from haconiwa.core.config import Config
from haconiwa.core.state import State
from haconiwa.core.logging import Logger
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
def state(config):
    return State(config)

@pytest.fixture
def logger(config):
    return Logger(config)

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

class TestState:
    def test_state_initialization(self, state):
        assert state.is_initialized() is False

    def test_state_save_load(self, state):
        test_data = {'key': 'value'}
        state.save_state('test', test_data)
        loaded = state.load_state('test')
        assert loaded == test_data

    @patch('haconiwa.core.state.State.save_state')
    def test_state_save_error(self, mock_save, state):
        mock_save.side_effect = IOError
        with pytest.raises(IOError):
            state.save_state('test', {})

class TestLogger:
    def test_logger_initialization(self, logger):
        assert logger.get_level() == 'INFO'

    def test_log_messages(self, logger):
        with patch('haconiwa.core.logging.Logger._write_log') as mock_write:
            logger.info('test message')
            mock_write.assert_called_once()

    def test_log_rotation(self, logger):
        with patch('logging.handlers.RotatingFileHandler') as mock_handler:
            logger.setup_file_logging('/tmp/test.log')
            mock_handler.assert_called_once()

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

def test_core_integration(config, state, logger):
    state.initialize()
    logger.setup_file_logging(Path(config.core.state_dir) / 'haconiwa.log')
    
    test_data = {'status': 'running'}
    state.save_state('app_state', test_data)
    
    loaded_state = state.load_state('app_state')
    assert loaded_state == test_data
    
    logger.info('Integration test completed')
    assert logger.get_level() == config.core.log_level