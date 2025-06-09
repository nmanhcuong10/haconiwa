"""
Test Space Manager v1.0
32ペイン対応とマルチルーム機能のテストケース
"""

import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

from haconiwa.space.manager import SpaceManager
from haconiwa.space.tmux import TmuxSession
from haconiwa.core.crd.models import SpaceCRD


class TestSpaceManagerV1:
    """Space Manager v1.0のテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        self.space_manager = SpaceManager()
        
    def test_create_32_pane_session(self):
        """32ペイン（8x4）セッションの作成をテスト"""
        space_config = {
            "name": "test-company",
            "grid": "8x4",
            "base_path": "/test/path",
            "organizations": [
                {"id": "org-01", "name": "Frontend"},
                {"id": "org-02", "name": "Backend"},
                {"id": "org-03", "name": "Database"},
                {"id": "org-04", "name": "DevOps"}
            ],
            "rooms": [
                {"id": "room-01", "name": "Alpha Room"},
                {"id": "room-02", "name": "Beta Room"}
            ]
        }
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager.create_multiroom_session(space_config)
            
            assert result is True
            # 32個のペイン作成コマンドが呼ばれることを確認
            assert mock_run.call_count >= 32
            
    def test_create_room_layout(self):
        """ルームレイアウトの作成をテスト"""
        room_config = {
            "id": "room-01",
            "name": "Alpha Room",
            "desks": [
                {"id": "desk-0100", "agent": {"name": "org01-pm-r1", "role": "pm"}},
                {"id": "desk-0101", "agent": {"name": "org01-wk-a-r1", "role": "worker"}},
                {"id": "desk-0102", "agent": {"name": "org01-wk-b-r1", "role": "worker"}},
                {"id": "desk-0103", "agent": {"name": "org01-wk-c-r1", "role": "worker"}}
            ]
        }
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager.create_room_layout("test-session", room_config)
            
            assert result is True
            # 4つのペインが作成されることを確認
            split_window_calls = [call for call in mock_run.call_args_list 
                                if 'split-window' in str(call)]
            assert len(split_window_calls) >= 3  # 最初のペインは既存、3回split
            
    def test_desk_directory_creation(self):
        """デスクディレクトリの作成をテスト"""
        desk_config = {
            "id": "desk-0100",
            "org_id": "org-01",
            "role": "pm",
            "room_id": "room-01"
        }
        base_path = Path("/test/company")
        
        with patch("pathlib.Path.mkdir") as mock_mkdir, \
             patch("pathlib.Path.exists", return_value=False):
            
            result = self.space_manager.create_desk_directory(base_path, desk_config)
            
            assert result == base_path / "org-01" / "01pm"
            mock_mkdir.assert_called()
            
    def test_desk_directory_room02_naming(self):
        """room-02のデスクディレクトリ命名規則をテスト"""
        desk_config = {
            "id": "desk-1200",  # room-02のorg-02 PM
            "org_id": "org-02",
            "role": "pm",
            "room_id": "room-02"
        }
        base_path = Path("/test/company")
        
        with patch("pathlib.Path.mkdir") as mock_mkdir, \
             patch("pathlib.Path.exists", return_value=False):
            
            result = self.space_manager.create_desk_directory(base_path, desk_config)
            
            # room-02では12pm形式になることを確認
            assert result == base_path / "org-02" / "12pm"
            mock_mkdir.assert_called()
            
    def test_32_desk_id_mapping(self):
        """32デスクのID配置マッピングをテスト"""
        mappings = self.space_manager.generate_desk_mappings()
        
        assert len(mappings) == 32
        
        # room-01のデスク（0100-0403）
        room01_desks = [m for m in mappings if m["room_id"] == "room-01"]
        assert len(room01_desks) == 16
        assert any(m["desk_id"] == "desk-0100" for m in room01_desks)
        assert any(m["desk_id"] == "desk-0403" for m in room01_desks)
        
        # room-02のデスク（1100-1403）
        room02_desks = [m for m in mappings if m["room_id"] == "room-02"]
        assert len(room02_desks) == 16
        assert any(m["desk_id"] == "desk-1100" for m in room02_desks)
        assert any(m["desk_id"] == "desk-1403" for m in room02_desks)
        
    def test_agent_assignment_to_desks(self):
        """エージェントのデスク割り当てをテスト"""
        desk_with_agent = {
            "id": "desk-0100",
            "agent": {
                "name": "org01-pm-r1",
                "role": "pm",
                "model": "o3",
                "env": {"OPENAI_API_KEY": "${OPENAI_API_KEY}"}
            }
        }
        
        agent_config = self.space_manager.extract_agent_config(desk_with_agent)
        
        assert agent_config["name"] == "org01-pm-r1"
        assert agent_config["role"] == "pm"
        assert agent_config["model"] == "o3"
        assert agent_config["desk_id"] == "desk-0100"
        
    def test_tmux_session_title_update(self):
        """tmuxペインタイトルの更新をテスト"""
        pane_config = {
            "id": "desk-0100",
            "title": "Frontend PM - Alpha Room",
            "directory": "/test/company/org-01/01pm"
        }
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager.update_pane_title("test-session", 0, pane_config)
            
            assert result is True
            # set-option コマンドが呼ばれることを確認
            title_calls = [call for call in mock_run.call_args_list 
                          if 'set-option' in str(call)]
            assert len(title_calls) > 0
            
    def test_git_worktree_integration(self):
        """Git worktreeとの連携をテスト"""
        task_config = {
            "name": "feature-login",
            "branch": "feature/login",
            "assignee_desk": "desk-0101",
            "base_path": "/test/company"
        }
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager.create_task_worktree(task_config)
            
            assert result is True
            # git worktree add コマンドが呼ばれることを確認
            worktree_calls = [call for call in mock_run.call_args_list 
                            if 'worktree' in str(call)]
            assert len(worktree_calls) > 0
            
    def test_room_switching(self):
        """ルーム間の切り替えをテスト"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            # room-01に切り替え
            result1 = self.space_manager.switch_to_room("test-company", "room-01")
            assert result1 is True
            
            # room-02に切り替え
            result2 = self.space_manager.switch_to_room("test-company", "room-02")
            assert result2 is True
            
            # select-window コマンドが呼ばれることを確認
            select_calls = [call for call in mock_run.call_args_list 
                           if 'select-window' in str(call)]
            assert len(select_calls) >= 2
            
    def test_space_crd_to_config_conversion(self):
        """Space CRDから内部設定への変換をテスト"""
        mock_space_crd = MagicMock(spec=SpaceCRD)
        mock_space_crd.metadata.name = "dev-world"
        mock_space_crd.spec.nations[0].cities[0].villages[0].companies[0].name = "haconiwa-company"
        mock_space_crd.spec.nations[0].cities[0].villages[0].companies[0].grid = "8x4"
        
        config = self.space_manager.convert_crd_to_config(mock_space_crd)
        
        assert config["name"] == "haconiwa-company"
        assert config["grid"] == "8x4"
        assert len(config["rooms"]) == 2  # room-01, room-02
        
    def test_layout_calculation_8x4(self):
        """8x4レイアウトの計算をテスト"""
        layout = self.space_manager.calculate_layout("8x4")
        
        assert layout["columns"] == 8
        assert layout["rows"] == 4
        assert layout["total_panes"] == 32
        assert layout["panes_per_room"] == 16
        
    def test_organization_distribution(self):
        """組織の配置分散をテスト"""
        organizations = [
            {"id": "org-01", "name": "Frontend"},
            {"id": "org-02", "name": "Backend"},
            {"id": "org-03", "name": "Database"},
            {"id": "org-04", "name": "DevOps"}
        ]
        
        distribution = self.space_manager.distribute_organizations(organizations, 2)  # 2ルーム
        
        assert len(distribution) == 2
        assert len(distribution[0]["organizations"]) == 4  # 各ルームに全組織
        assert len(distribution[1]["organizations"]) == 4
        
    def test_error_handling_tmux_failure(self):
        """tmuxコマンド失敗時のエラーハンドリングをテスト"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1  # 失敗
            mock_run.return_value.stderr = "tmux: session not found"
            
            result = self.space_manager.create_multiroom_session({
                "name": "test-company",
                "grid": "8x4"
            })
            
            assert result is False
            
    def test_cleanup_session(self):
        """セッションのクリーンアップをテスト"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager.cleanup_session("test-company", purge_data=True)
            
            assert result is True
            # kill-session コマンドが呼ばれることを確認
            kill_calls = [call for call in mock_run.call_args_list 
                         if 'kill-session' in str(call)]
            assert len(kill_calls) > 0
            
    def test_attach_to_room(self):
        """特定ルームへのアタッチをテスト"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager.attach_to_room("test-company", "room-01")
            
            assert result is True
            # attach-session コマンドが呼ばれることを確認
            attach_calls = [call for call in mock_run.call_args_list 
                           if 'attach-session' in str(call)]
            assert len(attach_calls) > 0 