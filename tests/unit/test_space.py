import pytest
from unittest.mock import Mock, patch
from haconiwa.space.tmux import TmuxManager, TmuxError

@pytest.fixture
def tmux_manager():
    return TmuxManager()

@pytest.fixture
def mock_libtmux():
    with patch('haconiwa.space.tmux.libtmux') as mock:
        yield mock

def test_create_session(tmux_manager, mock_libtmux):
    mock_server = Mock()
    mock_libtmux.Server.return_value = mock_server
    mock_session = Mock()
    mock_server.new_session.return_value = mock_session

    session = tmux_manager.create_session("test-session")
    
    mock_server.new_session.assert_called_once_with(session_name="test-session")
    assert session == mock_session

def test_create_session_exists(tmux_manager, mock_libtmux):
    mock_server = Mock()
    mock_libtmux.Server.return_value = mock_server
    mock_server.new_session.side_effect = libtmux.exc.TmuxSessionExists

    with pytest.raises(TmuxError):
        tmux_manager.create_session("existing-session")

def test_get_session(tmux_manager, mock_libtmux):
    mock_server = Mock()
    mock_libtmux.Server.return_value = mock_server
    mock_session = Mock()
    mock_server.find_where.return_value = mock_session

    session = tmux_manager.get_session("test-session")
    
    mock_server.find_where.assert_called_once_with({"session_name": "test-session"})
    assert session == mock_session

def test_get_session_not_found(tmux_manager, mock_libtmux):
    mock_server = Mock()
    mock_libtmux.Server.return_value = mock_server
    mock_server.find_where.return_value = None

    with pytest.raises(TmuxError):
        tmux_manager.get_session("non-existing-session")

def test_resize_pane(tmux_manager, mock_libtmux):
    mock_pane = Mock()
    mock_pane.set_height = Mock()
    mock_pane.set_width = Mock()

    tmux_manager.resize_pane(mock_pane, width=80, height=24)

    mock_pane.set_width.assert_called_once_with(80)
    mock_pane.set_height.assert_called_once_with(24)

def test_split_window(tmux_manager, mock_libtmux):
    mock_window = Mock()
    mock_pane = Mock()
    mock_window.split_window.return_value = mock_pane

    pane = tmux_manager.split_window(mock_window, vertical=True)

    mock_window.split_window.assert_called_once_with(vertical=True)
    assert pane == mock_pane

def test_kill_session(tmux_manager, mock_libtmux):
    mock_session = Mock()
    mock_session.kill_session = Mock()

    tmux_manager.kill_session(mock_session)

    mock_session.kill_session.assert_called_once()

def test_list_sessions(tmux_manager, mock_libtmux):
    mock_server = Mock()
    mock_libtmux.Server.return_value = mock_server
    mock_sessions = [Mock(), Mock()]
    mock_server.list_sessions.return_value = mock_sessions

    sessions = tmux_manager.list_sessions()

    assert sessions == mock_sessions
    mock_server.list_sessions.assert_called_once()

def test_tmux_not_installed(mock_libtmux):
    mock_libtmux.Server.side_effect = FileNotFoundError
    
    with pytest.raises(TmuxError, match="tmux is not installed"):
        TmuxManager()

def test_concurrent_sessions(tmux_manager, mock_libtmux):
    mock_server = Mock()
    mock_libtmux.Server.return_value = mock_server
    mock_sessions = []
    
    for i in range(5):
        mock_session = Mock()
        mock_session.name = f"session-{i}"
        mock_sessions.append(mock_session)
        mock_server.new_session.return_value = mock_session
        
        session = tmux_manager.create_session(f"session-{i}")
        assert session.name == f"session-{i}"
    
    mock_server.list_sessions.return_value = mock_sessions
    sessions = tmux_manager.list_sessions()
    assert len(sessions) == 5

def test_session_layout(tmux_manager, mock_libtmux):
    mock_window = Mock()
    mock_panes = [Mock() for _ in range(4)]
    mock_window.split_window.side_effect = mock_panes[1:]
    mock_window.panes = mock_panes

    panes = []
    panes.append(mock_window)
    for i in range(3):
        panes.append(tmux_manager.split_window(mock_window, vertical=i % 2 == 0))

    assert len(mock_window.panes) == 4
    for i, pane in enumerate(mock_panes[1:], 1):
        mock_window.split_window.assert_any_call(vertical=i % 2 == 0)