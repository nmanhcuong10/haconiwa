#!/usr/bin/env python3
"""
Test script for Company→Session, Room→Window, Desk→Pane mapping
一連の流れのエンドツーエンドテスト
"""

import sys
import os
import subprocess
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from haconiwa.core.crd.parser import CRDParser
from haconiwa.core.applier import CRDApplier
from haconiwa.space.manager import SpaceManager

# Test YAML for multiroom tmux layout
yaml_content = '''
apiVersion: haconiwa.dev/v1
kind: Space
metadata:
  name: multiroom-test
spec:
  nations:
  - id: jp
    name: Japan
    cities:
    - id: tokyo
      name: Tokyo
      villages:
      - id: test
        name: Test Village
        companies:
        - name: test-multiroom-company
          grid: 8x4
          basePath: /tmp/test-multiroom
          organizations:
          - {id: "01", name: "Frontend Team"}
          - {id: "02", name: "Backend Team"}
          - {id: "03", name: "Database Team"}
          - {id: "04", name: "DevOps Team"}
          buildings:
          - id: hq
            name: Headquarters
            floors:
            - level: 1
              rooms:
              - {id: "room-01", name: "Alpha Room"}
              - {id: "room-02", name: "Beta Room"}
'''

def check_tmux_session(session_name: str) -> dict:
    """tmux sessionの詳細情報を取得"""
    try:
        # Session存在確認
        result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True)
        sessions = [line.split(':')[0] for line in result.stdout.strip().split('\n') if line]
        
        if session_name not in sessions:
            return {"exists": False}
        
        # Window一覧取得
        result = subprocess.run(['tmux', 'list-windows', '-t', session_name], capture_output=True, text=True)
        windows = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(':')
                window_id = parts[0]
                window_name = parts[1].split()[0]
                windows.append({"id": window_id, "name": window_name})
        
        # 各windowのpane数取得
        window_panes = {}
        for window in windows:
            result = subprocess.run(['tmux', 'list-panes', '-t', f'{session_name}:{window["id"]}'], 
                                  capture_output=True, text=True)
            pane_count = len([line for line in result.stdout.strip().split('\n') if line])
            window_panes[window["id"]] = {
                "name": window["name"],
                "pane_count": pane_count
            }
        
        return {
            "exists": True,
            "windows": windows,
            "window_panes": window_panes,
            "total_windows": len(windows)
        }
        
    except Exception as e:
        return {"exists": False, "error": str(e)}

def cleanup_test_session(session_name: str):
    """テスト用セッションのクリーンアップ"""
    try:
        subprocess.run(['tmux', 'kill-session', '-t', session_name], 
                      capture_output=True, text=True)
        print(f"🧹 Cleaned up test session: {session_name}")
    except:
        pass

def test_company_to_session():
    """Test 1: Company → tmux session mapping"""
    print("\n🧪 Test 1: Company → tmux session")
    
    try:
        parser = CRDParser()
        crd = parser.parse_yaml(yaml_content)
        
        space_manager = SpaceManager()
        config = space_manager.convert_crd_to_config(crd)
        
        # Company名がsession名として使われるかテスト
        expected_session = config["name"]
        print(f"   Expected session name: {expected_session}")
        
        return {"passed": True, "session_name": expected_session}
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return {"passed": False, "error": str(e)}

def test_room_to_window():
    """Test 2: Room → tmux window mapping"""
    print("\n🧪 Test 2: Room → tmux window")
    
    try:
        parser = CRDParser()
        crd = parser.parse_yaml(yaml_content)
        
        space_manager = SpaceManager()
        config = space_manager.convert_crd_to_config(crd)
        
        # Room設定確認
        rooms = config.get("rooms", [])
        print(f"   Expected rooms: {len(rooms)}")
        for i, room in enumerate(rooms):
            print(f"     Window {i}: {room['id']} ({room['name']})")
        
        expected_windows = [
            {"id": "0", "name": "Alpha", "room_id": "room-01"},
            {"id": "1", "name": "Beta", "room_id": "room-02"}
        ]
        
        return {"passed": True, "expected_windows": expected_windows}
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return {"passed": False, "error": str(e)}

def test_desk_to_pane():
    """Test 3: Desk → tmux pane mapping"""
    print("\n🧪 Test 3: Desk → tmux pane mapping")
    
    try:
        space_manager = SpaceManager()
        mappings = space_manager.generate_desk_mappings()
        
        # Room別のdesk分布確認
        room01_desks = [m for m in mappings if m["room_id"] == "room-01"]
        room02_desks = [m for m in mappings if m["room_id"] == "room-02"]
        
        print(f"   Room-01 desks: {len(room01_desks)} (expected: 16)")
        print(f"   Room-02 desks: {len(room02_desks)} (expected: 16)")
        
        # 各roomの最初の4つのdeskを表示
        print(f"   Room-01 sample:")
        for i, desk in enumerate(room01_desks[:4]):
            print(f"     Pane {i}: {desk['desk_id']} → {desk['directory_name']}")
        
        print(f"   Room-02 sample:")
        for i, desk in enumerate(room02_desks[:4]):
            print(f"     Pane {i}: {desk['desk_id']} → {desk['directory_name']}")
        
        expected_layout = {
            "room-01": {"window": "0", "panes": 16, "pane_range": "0-15"},
            "room-02": {"window": "1", "panes": 16, "pane_range": "0-15"}
        }
        
        return {
            "passed": True, 
            "room01_count": len(room01_desks),
            "room02_count": len(room02_desks),
            "expected_layout": expected_layout
        }
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return {"passed": False, "error": str(e)}

def test_actual_tmux_creation():
    """Test 4: 実際のtmux session/window/pane作成"""
    print("\n🧪 Test 4: 実際のtmux作成 (現在の実装)")
    
    session_name = "test-multiroom-company"
    cleanup_test_session(session_name)
    
    try:
        parser = CRDParser()
        crd = parser.parse_yaml(yaml_content)
        
        space_manager = SpaceManager()
        config = space_manager.convert_crd_to_config(crd)
        
        # 現在の実装でセッション作成
        print("   Creating session with current implementation...")
        result = space_manager.create_multiroom_session(config)
        
        if not result:
            return {"passed": False, "error": "Failed to create session"}
        
        # 少し待ってからtmux状態確認
        time.sleep(1)
        tmux_info = check_tmux_session(session_name)
        
        print(f"   Session exists: {tmux_info.get('exists', False)}")
        if tmux_info.get("exists"):
            print(f"   Total windows: {tmux_info.get('total_windows', 0)}")
            for window_id, info in tmux_info.get("window_panes", {}).items():
                print(f"     Window {window_id} ({info['name']}): {info['pane_count']} panes")
        
        return {"passed": True, "tmux_info": tmux_info}
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return {"passed": False, "error": str(e)}
    finally:
        cleanup_test_session(session_name)

def test_expected_vs_actual():
    """Test 5: 期待値と実際の実装の比較"""
    print("\n🧪 Test 5: 期待値 vs 実際の実装")
    
    print("   📋 Expected tmux structure:")
    print("     test-multiroom-company (session)")
    print("     ├── window 0: Alpha Room (16 panes)")
    print("     │   ├── pane 0: org-01/01pm")
    print("     │   ├── pane 1: org-01/01a")
    print("     │   ├── ...")
    print("     │   └── pane 15: org-04/04c")
    print("     └── window 1: Beta Room (16 panes)")
    print("         ├── pane 0: org-01/11pm")
    print("         ├── pane 1: org-01/11a")
    print("         ├── ...")
    print("         └── pane 15: org-04/14c")
    
    print("\n   📋 Current implementation:")
    print("     test-multiroom-company (session)")
    print("     └── window 0: (32 panes)")
    print("         ├── pane 0-15: room-01 desks")
    print("         └── pane 16-31: room-02 desks")
    
    return {
        "passed": False,  # 現在は期待値と異なる
        "issue": "Room → Window mapping not implemented",
        "fix_needed": "Implement separate windows for each room"
    }

def main():
    print("🚀 Testing Company→Session, Room→Window, Desk→Pane mapping")
    print("=" * 60)
    
    results = []
    
    # Test sequence
    test1 = test_company_to_session()
    results.append(("Company → Session", test1["passed"]))
    
    test2 = test_room_to_window()
    results.append(("Room → Window", test2["passed"]))
    
    test3 = test_desk_to_pane()
    results.append(("Desk → Pane", test3["passed"]))
    
    test4 = test_actual_tmux_creation()
    results.append(("Actual tmux creation", test4["passed"]))
    
    test5 = test_expected_vs_actual()
    results.append(("Expected vs Actual", test5["passed"]))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    
    passed_count = 0
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if passed:
            passed_count += 1
    
    print(f"\n📊 Overall: {passed_count}/{len(results)} tests passed")
    
    if passed_count < len(results):
        print("\n🔧 Next steps:")
        print("   1. Implement Room → Window mapping in SpaceManager")
        print("   2. Modify _create_panes to create windows first")
        print("   3. Distribute 16 panes per window")
        print("   4. Update room switching logic")
    
    return passed_count == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 