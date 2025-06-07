import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from git import Repo, GitCommandError
from haconiwa.task.worktree import WorktreeManager
from haconiwa.core.config import Config

@pytest.fixture
def config():
    return Config(repo_path=Path("/tmp/test-repo"))

@pytest.fixture
def mock_repo():
    repo = Mock(spec=Repo)
    repo.git = Mock()
    repo.working_dir = "/tmp/test-repo"
    return repo

@pytest.fixture
def worktree_manager(config, mock_repo):
    with patch("git.Repo") as mock_repo_class:
        mock_repo_class.return_value = mock_repo
        manager = WorktreeManager(config)
        yield manager

def test_create_worktree(worktree_manager, mock_repo):
    task_id = "task-123"
    branch_name = f"feature/{task_id}"
    
    worktree_manager.create_worktree(task_id)
    
    mock_repo.git.worktree.assert_called_once_with("add", f"/tmp/test-repo/tasks/{task_id}", "-b", branch_name)

def test_delete_worktree(worktree_manager, mock_repo):
    task_id = "task-123"
    worktree_path = f"/tmp/test-repo/tasks/{task_id}"
    
    worktree_manager.delete_worktree(task_id)
    
    mock_repo.git.worktree.assert_called_once_with("remove", "-f", worktree_path)

def test_merge_worktree(worktree_manager, mock_repo):
    task_id = "task-123"
    branch_name = f"feature/{task_id}"
    
    worktree_manager.merge_worktree(task_id)
    
    mock_repo.git.checkout.assert_called_once_with("main")
    mock_repo.git.merge.assert_called_once_with(branch_name, "--no-ff")

def test_list_worktrees(worktree_manager, mock_repo):
    mock_repo.git.worktree.return_value = """
    /tmp/test-repo  12345678 [main]
    /tmp/test-repo/tasks/task-1  87654321 [feature/task-1]
    /tmp/test-repo/tasks/task-2  11223344 [feature/task-2]
    """
    
    worktrees = worktree_manager.list_worktrees()
    
    assert len(worktrees) == 3
    assert worktrees[1]["task_id"] == "task-1"
    assert worktrees[2]["task_id"] == "task-2"

def test_handle_merge_conflict(worktree_manager, mock_repo):
    task_id = "task-123"
    mock_repo.git.merge.side_effect = GitCommandError("merge", "Merge conflict")
    
    with pytest.raises(GitCommandError):
        worktree_manager.merge_worktree(task_id)
    
    mock_repo.git.merge.assert_called_once()
    mock_repo.git.merge.abort.assert_called_once()

def test_concurrent_worktrees(worktree_manager, mock_repo):
    task_ids = [f"task-{i}" for i in range(3)]
    
    for task_id in task_ids:
        worktree_manager.create_worktree(task_id)
    
    mock_repo.git.worktree.call_count == 3
    
    for task_id in task_ids:
        branch_name = f"feature/{task_id}"
        assert any(call.args[3] == branch_name for call in mock_repo.git.worktree.call_args_list)

def test_recover_from_broken_state(worktree_manager, mock_repo):
    task_id = "task-123"
    mock_repo.git.worktree.side_effect = [GitCommandError("worktree", "Broken state"), None]
    
    worktree_manager.create_worktree(task_id)
    
    assert mock_repo.git.worktree.call_count == 2
    mock_repo.git.worktree.assert_called_with("prune")

def test_validate_task_id(worktree_manager):
    with pytest.raises(ValueError):
        worktree_manager.create_worktree("invalid/task/id")
    
    with pytest.raises(ValueError):
        worktree_manager.create_worktree("")

def test_cleanup_stale_worktrees(worktree_manager, mock_repo):
    mock_repo.git.worktree.return_value = """
    /tmp/test-repo/tasks/task-1  87654321 [feature/task-1]
    /tmp/test-repo/tasks/task-2  11223344 [gone]
    """
    
    worktree_manager.cleanup_stale_worktrees()
    
    mock_repo.git.worktree.assert_any_call("remove", "-f", "/tmp/test-repo/tasks/task-2")