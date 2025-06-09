"""
Unit tests for multiroom Space Manager
Room → Window mapping implementation
"""

import pytest
from unittest.mock import Mock, patch, call
import subprocess

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from haconiwa.space.manager import SpaceManager
from haconiwa.core.crd.models import SpaceCRD


class TestMultiroomSpaceManager:
    """Test suite for multiroom Space Manager functionality"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.space_manager = SpaceManager()
        self.test_config = {
            "name": "test-company",
            "grid": "8x4",
            "base_path": "/tmp/test-desks",
            "organizations": [
                {"id": "01", "name": "Frontend Team"},
                {"id": "02", "name": "Backend Team"},
                {"id": "03", "name": "Database Team"},
                {"id": "04", "name": "DevOps Team"}
            ],
            "rooms": [
                {"id": "room-01", "name": "Alpha Room"},
                {"id": "room-02", "name": "Beta Room"}
            ]
        }
    
    def test_create_multiroom_session_structure(self):
        """Test that multiroom session creates correct tmux structure"""
        with patch.object(self.space_manager, '_create_tmux_session') as mock_session, \
             patch.object(self.space_manager, '_create_windows_for_rooms') as mock_windows, \
             patch.object(self.space_manager, '_create_panes_in_window') as mock_panes, \
             patch.object(self.space_manager, 'generate_desk_mappings') as mock_mappings, \
             patch('pathlib.Path.mkdir'):
            
            # Mock desk mappings
            mock_mappings.return_value = [
                {"room_id": "room-01", "desk_id": "desk-0100", "org_id": "org-01", "directory_name": "01pm"},
                {"room_id": "room-02", "desk_id": "desk-1100", "org_id": "org-01", "directory_name": "11pm"},
            ]
            
            result = self.space_manager.create_multiroom_session(self.test_config)
            
            assert result is True
            mock_session.assert_called_once_with("test-company")
            mock_windows.assert_called_once()
    
    def test_create_windows_for_rooms(self):
        """Test that each room creates a separate tmux window"""
        session_name = "test-company"
        rooms = self.test_config["rooms"]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # This method should be implemented
            result = self.space_manager._create_windows_for_rooms(session_name, rooms)
            
            assert result is True
            # Should create 2 windows (room-01 and room-02)
            assert mock_run.call_count == 2
            
            # Verify correct tmux commands
            expected_calls = [
                call(['tmux', 'rename-window', '-t', f'{session_name}:0', 'Alpha'], 
                     capture_output=True, text=True),
                call(['tmux', 'new-window', '-t', session_name, '-n', 'Beta'], 
                     capture_output=True, text=True)
            ]
            mock_run.assert_has_calls(expected_calls)
    
    def test_create_panes_in_window(self):
        """Test that panes are created correctly in each window"""
        session_name = "test-company"
        window_id = "0"
        pane_count = 16
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager._create_panes_in_window(session_name, window_id, pane_count)
            
            assert result is True
            # Should create 15 additional panes (first pane already exists)
            assert mock_run.call_count >= 15
    
    def test_distribute_desks_to_windows(self):
        """Test desk distribution across windows"""
        desk_mappings = [
            {"room_id": "room-01", "desk_id": "desk-0100", "org_id": "org-01", "directory_name": "01pm"},
            {"room_id": "room-01", "desk_id": "desk-0101", "org_id": "org-01", "directory_name": "01a"},
            {"room_id": "room-02", "desk_id": "desk-1100", "org_id": "org-01", "directory_name": "11pm"},
            {"room_id": "room-02", "desk_id": "desk-1101", "org_id": "org-01", "directory_name": "11a"},
        ]
        
        distribution = self.space_manager._distribute_desks_to_windows(desk_mappings)
        
        assert "room-01" in distribution
        assert "room-02" in distribution
        assert len(distribution["room-01"]) == 2
        assert len(distribution["room-02"]) == 2
        
        # Verify correct window assignments
        assert distribution["room-01"][0]["window_id"] == "0"
        assert distribution["room-02"][0]["window_id"] == "1"
    
    def test_update_pane_in_window(self):
        """Test updating pane directory and title in specific window"""
        session_name = "test-company"
        window_id = "0"
        pane_index = 5
        mapping = {
            "desk_id": "desk-0100",
            "org_id": "org-01",
            "directory_name": "01pm",
            "title": "Org-01 PM - Alpha Room"
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.space_manager._update_pane_in_window(session_name, window_id, pane_index, mapping, "/tmp/test")
            
            assert result is True
            # Should call tmux commands for directory and title
            assert mock_run.call_count == 2
    
    def test_switch_to_room_with_windows(self):
        """Test switching between rooms (windows)"""
        session_name = "test-company"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Switch to room-01 (window 0)
            result1 = self.space_manager.switch_to_room(session_name, "room-01")
            assert result1 is True
            
            # Switch to room-02 (window 1)
            result2 = self.space_manager.switch_to_room(session_name, "room-02")
            assert result2 is True
            
            # Verify correct tmux window selection commands
            expected_calls = [
                call(['tmux', 'select-window', '-t', f'{session_name}:0'], capture_output=True, text=True),
                call(['tmux', 'select-window', '-t', f'{session_name}:1'], capture_output=True, text=True)
            ]
            mock_run.assert_has_calls(expected_calls)
    
    def test_attach_to_specific_room(self):
        """Test attaching to specific room (window)"""
        session_name = "test-company"
        room_id = "room-02"
        
        with patch.object(self.space_manager, 'switch_to_room') as mock_switch, \
             patch('subprocess.run') as mock_run:
            
            mock_switch.return_value = True
            mock_run.return_value.returncode = 0
            
            result = self.space_manager.attach_to_room(session_name, room_id)
            
            assert result is True
            mock_switch.assert_called_once_with(session_name, room_id)
            mock_run.assert_called_once_with(['tmux', 'attach-session', '-t', session_name], 
                                           capture_output=True, text=True)
    
    def test_get_room_window_mapping(self):
        """Test getting room to window ID mapping"""
        rooms = [
            {"id": "room-01", "name": "Alpha Room"},
            {"id": "room-02", "name": "Beta Room"},
            {"id": "room-03", "name": "Gamma Room"}
        ]
        
        mapping = self.space_manager._get_room_window_mapping(rooms)
        
        expected = {
            "room-01": {"window_id": "0", "name": "Alpha Room"},
            "room-02": {"window_id": "1", "name": "Beta Room"},
            "room-03": {"window_id": "2", "name": "Gamma Room"}
        }
        
        assert mapping == expected
    
    @pytest.mark.integration
    def test_full_multiroom_workflow(self):
        """Integration test for complete multiroom workflow"""
        # This would be an integration test that actually creates tmux sessions
        # Skip in unit tests, run separately for integration testing
        pytest.skip("Integration test - run separately")
    
    def test_error_handling_window_creation(self):
        """Test error handling when window creation fails"""
        session_name = "test-company"
        rooms = self.test_config["rooms"]
        
        with patch('subprocess.run') as mock_run:
            # Simulate window creation failure
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "tmux: can't create window"
            
            result = self.space_manager._create_windows_for_rooms(session_name, rooms)
            
            assert result is False
    
    def test_calculate_panes_per_window(self):
        """Test calculation of panes per window based on grid and rooms"""
        grid = "8x4"
        room_count = 2
        
        result = self.space_manager._calculate_panes_per_window(grid, room_count)
        
        expected = {
            "total_panes": 32,
            "panes_per_window": 16,
            "layout_per_window": "4x4"
        }
        
        assert result == expected 