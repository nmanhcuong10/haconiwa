import pytest
from unittest.mock import Mock, patch, MagicMock
from haconiwa.space.tmux import TmuxSession, TmuxSessionError
from haconiwa.core.config import Config

@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    return config

@pytest.fixture
def tmux_session(mock_config):
    with patch('haconiwa.space.tmux.libtmux.Server'):
        return TmuxSession(mock_config)

class TestTmuxSession:
    @patch('subprocess.run')
    def test_validate_tmux_success(self, mock_run, mock_config):
        mock_run.return_value.returncode = 0
        session = TmuxSession(mock_config)
        # Should not raise exception

    @patch('subprocess.run')
    def test_validate_tmux_failure(self, mock_run, mock_config):
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(TmuxSessionError):
            TmuxSession(mock_config)

    @patch('haconiwa.space.tmux.libtmux.Server')
    def test_create_session_success(self, mock_server_class, mock_config):
        mock_server = Mock()
        mock_server_class.return_value = mock_server
        mock_server.has_session.return_value = False
        mock_session = Mock()
        mock_server.new_session.return_value = mock_session
        
        with patch('subprocess.run'):
            session = TmuxSession(mock_config)
            result = session.create_session('test')
            
            assert result == mock_session
            mock_server.new_session.assert_called_once()

    @patch('haconiwa.space.tmux.libtmux.Server')
    def test_create_session_exists(self, mock_server_class, mock_config):
        mock_server = Mock()
        mock_server_class.return_value = mock_server
        mock_server.has_session.return_value = True
        
        with patch('subprocess.run'):
            session = TmuxSession(mock_config)
            with pytest.raises(TmuxSessionError):
                session.create_session('test')

    def test_list_sessions(self, tmux_session):
        mock_session = Mock()
        mock_session.name = 'test-session'
        mock_session.get.return_value = '2024-01-01'
        mock_session.list_windows.return_value = [Mock(), Mock()]
        mock_session.attached = True
        
        tmux_session.server.list_sessions.return_value = [mock_session]
        
        sessions = tmux_session.list_sessions()
        
        assert len(sessions) == 1
        assert sessions[0]['name'] == 'test-session'
        assert sessions[0]['windows'] == 2

    def test_get_session_found(self, tmux_session):
        mock_session = Mock()
        tmux_session.server.find_where.return_value = mock_session
        
        result = tmux_session.get_session('test')
        
        assert result == mock_session

    def test_get_session_not_found(self, tmux_session):
        import libtmux.exc
        tmux_session.server.find_where.side_effect = libtmux.exc.TmuxCommandError()
        
        result = tmux_session.get_session('test')
        
        assert result is None

    def test_send_command(self, tmux_session):
        mock_session = Mock()
        mock_window = Mock()
        mock_pane = Mock()
        mock_session.attached_window = mock_window
        mock_window.attached_pane = mock_pane
        
        tmux_session.server.find_where.return_value = mock_session
        
        tmux_session.send_command('test', 'ls')
        
        mock_pane.send_keys.assert_called_once_with('ls')

    def test_kill_session_success(self, tmux_session):
        mock_session = Mock()
        tmux_session.server.find_where.return_value = mock_session
        
        tmux_session.kill_session('test')
        
        mock_session.kill_session.assert_called_once()

    def test_kill_session_not_found(self, tmux_session):
        tmux_session.server.find_where.return_value = None
        
        with pytest.raises(TmuxSessionError):
            tmux_session.kill_session('test')

    @patch('haconiwa.space.tmux.subprocess.run')
    def test_create_multiagent_session(self, mock_run, tmux_session):
        # Mock successful subprocess calls
        mock_run.return_value.returncode = 0
        
        # Mock file system operations
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'), \
             patch('time.strftime'):
            
            result = tmux_session.create_multiagent_session(
                'test-company',
                '/test/path',
                [{"id": "org-01", "org_name": "Test Org", "task_name": "Test Task", "workspace": "test-desk"}]
            )
            
            # Should not raise exception and subprocess commands should be called
            assert mock_run.called

    def test_is_session_alive(self, tmux_session):
        mock_session = Mock()
        tmux_session.server.find_where.return_value = mock_session
        
        assert tmux_session.is_session_alive('test') is True
        
        tmux_session.server.find_where.return_value = None
        assert tmux_session.is_session_alive('test') is False