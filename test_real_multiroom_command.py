#!/usr/bin/env python3
"""
Real test using actual haconiwa apply command
実際のhaconiwa applyコマンドを使ったマルチルーム機能テスト
"""

import subprocess
import json
import time
import os
from pathlib import Path
import tempfile
import yaml


def create_multiroom_yaml(temp_dir: str) -> str:
    """マルチルーム用のYAMLファイルを作成"""
    yaml_content = {
        'apiVersion': 'haconiwa.dev/v1',
        'kind': 'Space',
        'metadata': {
            'name': 'real-multiroom-test'
        },
        'spec': {
            'nations': [{
                'id': 'jp',
                'name': 'Japan',
                'cities': [{
                    'id': 'tokyo',
                    'name': 'Tokyo',
                    'villages': [{
                        'id': 'test',
                        'name': 'Test Village',
                        'companies': [{
                            'name': 'real-test-company',
                            'grid': '8x4',
                            'basePath': f'{temp_dir}/real-test-desks',
                            'organizations': [
                                {'id': '01', 'name': 'Frontend Team'},
                                {'id': '02', 'name': 'Backend Team'},
                                {'id': '03', 'name': 'Database Team'},
                                {'id': '04', 'name': 'DevOps Team'}
                            ],
                            'buildings': [{
                                'id': 'hq',
                                'name': 'Headquarters',
                                'floors': [{
                                    'level': 1,
                                    'rooms': [
                                        {'id': 'room-01', 'name': 'Alpha Room'},
                                        {'id': 'room-02', 'name': 'Beta Room'}
                                    ]
                                }]
                            }]
                        }]
                    }]
                }]
            }]
        }
    }
    
    yaml_file = f"{temp_dir}/multiroom-test.yaml"
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
    
    return yaml_file


def run_haconiwa_apply(yaml_file: str) -> dict:
    """haconiwa apply コマンドを実行"""
    try:
        cmd = ['haconiwa', 'apply', '-f', yaml_file]
        print(f"🚀 Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timed out after 30 seconds',
            'stdout': '',
            'stderr': '',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'stdout': '',
            'stderr': '',
            'returncode': -1
        }


def check_tmux_session_real(session_name: str) -> dict:
    """実際のtmuxセッションを詳細確認"""
    try:
        # Session存在確認
        result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True)
        sessions = [line.split(':')[0] for line in result.stdout.strip().split('\n') if line]
        
        if session_name not in sessions:
            return {"exists": False, "error": "Session not found"}
        
        # Window一覧取得
        result = subprocess.run(['tmux', 'list-windows', '-t', session_name, '-F', 
                               '#{window_index}:#{window_name}'], capture_output=True, text=True)
        
        windows = []
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                window_id, window_name = line.split(':', 1)
                windows.append({"id": window_id, "name": window_name})
        
        # 各windowのpane詳細取得
        window_details = {}
        for window in windows:
            window_id = window["id"]
            
            # Pane count
            result = subprocess.run(['tmux', 'list-panes', '-t', f'{session_name}:{window_id}'], 
                                  capture_output=True, text=True)
            pane_count = len([line for line in result.stdout.strip().split('\n') if line])
            
            # Pane titles
            result = subprocess.run(['tmux', 'list-panes', '-t', f'{session_name}:{window_id}', '-F', 
                                   '#{pane_index}:#{pane_title}'], capture_output=True, text=True)
            pane_titles = []
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    pane_index, pane_title = line.split(':', 1)
                    pane_titles.append({"index": pane_index, "title": pane_title})
            
            # Pane current paths  
            result = subprocess.run(['tmux', 'list-panes', '-t', f'{session_name}:{window_id}', '-F', 
                                   '#{pane_index}:#{pane_current_path}'], capture_output=True, text=True)
            pane_paths = []
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    pane_index, pane_path = line.split(':', 1)
                    pane_paths.append({"index": pane_index, "path": pane_path})
            
            window_details[window_id] = {
                "name": window["name"],
                "pane_count": pane_count,
                "pane_titles": pane_titles,
                "pane_paths": pane_paths
            }
        
        return {
            "exists": True,
            "session_name": session_name,
            "total_windows": len(windows),
            "windows": windows,
            "window_details": window_details
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


def verify_multiroom_structure(tmux_info: dict) -> dict:
    """マルチルーム構造の検証"""
    results = {
        "company_to_session": False,
        "room_to_window": False,
        "desk_to_pane": False,
        "directory_structure": False,
        "details": {}
    }
    
    if not tmux_info.get("exists"):
        results["details"]["error"] = "tmux session not found"
        return results
    
    # Test 1: Company → Session mapping
    expected_session = "real-test-company"
    if tmux_info["session_name"] == expected_session:
        results["company_to_session"] = True
        results["details"]["session_name"] = "✅ Correct session name"
    else:
        results["details"]["session_name"] = f"❌ Expected {expected_session}, got {tmux_info['session_name']}"
    
    # Test 2: Room → Window mapping
    windows = tmux_info.get("windows", [])
    if len(windows) == 2:
        window_names = [w["name"] for w in windows]
        if "Alpha" in window_names and "Beta" in window_names:
            results["room_to_window"] = True
            results["details"]["windows"] = "✅ 2 windows with correct names (Alpha, Beta)"
        else:
            results["details"]["windows"] = f"❌ Incorrect window names: {window_names}"
    else:
        results["details"]["windows"] = f"❌ Expected 2 windows, got {len(windows)}"
    
    # Test 3: Desk → Pane mapping
    window_details = tmux_info.get("window_details", {})
    pane_counts = []
    for window_id, details in window_details.items():
        pane_counts.append(details["pane_count"])
    
    if len(pane_counts) == 2 and all(count == 16 for count in pane_counts):
        results["desk_to_pane"] = True
        results["details"]["panes"] = "✅ 16 panes per window (32 total)"
    else:
        results["details"]["panes"] = f"❌ Pane counts: {pane_counts} (expected [16, 16])"
    
    # Test 4: Directory structure sample check
    try:
        first_window_details = list(window_details.values())[0]
        first_pane_path = first_window_details["pane_paths"][0]["path"]
        if "real-test-desks" in first_pane_path and "org-" in first_pane_path:
            results["directory_structure"] = True
            results["details"]["directories"] = "✅ Correct directory structure detected"
        else:
            results["details"]["directories"] = f"❌ Unexpected path: {first_pane_path}"
    except (IndexError, KeyError):
        results["details"]["directories"] = "❌ Cannot verify directory structure"
    
    return results


def main():
    print("🚀 Real Haconiwa Apply Command Test - Multiroom Function")
    print("=" * 70)
    
    session_name = "real-test-company"
    
    # Cleanup any existing session
    cleanup_test_session(session_name)
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Step 1: Create YAML file
        print("\n📝 Step 1: Creating multiroom YAML file...")
        yaml_file = create_multiroom_yaml(temp_dir)
        print(f"   Created: {yaml_file}")
        
        # Show YAML content
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
            print(f"   Content preview:\n{yaml_content[:300]}...")
        
        # Step 2: Run haconiwa apply
        print("\n🎯 Step 2: Running haconiwa apply command...")
        apply_result = run_haconiwa_apply(yaml_file)
        
        print(f"   Command success: {apply_result['success']}")
        print(f"   Return code: {apply_result['returncode']}")
        
        if apply_result['stdout']:
            print(f"   STDOUT:\n{apply_result['stdout']}")
        
        if apply_result['stderr']:
            print(f"   STDERR:\n{apply_result['stderr']}")
        
        if apply_result.get('error'):
            print(f"   ERROR: {apply_result['error']}")
        
        if not apply_result['success']:
            print("❌ haconiwa apply command failed")
            return False
        
        # Step 3: Wait and check tmux session
        print("\n🔍 Step 3: Checking tmux session...")
        time.sleep(2)  # Wait for session creation
        
        tmux_info = check_tmux_session_real(session_name)
        
        if tmux_info.get("exists"):
            print(f"   ✅ Session found: {session_name}")
            print(f"   📊 Windows: {tmux_info['total_windows']}")
            
            for window_id, details in tmux_info.get("window_details", {}).items():
                print(f"      Window {window_id} ({details['name']}): {details['pane_count']} panes")
        else:
            print(f"   ❌ Session not found: {tmux_info.get('error', 'Unknown error')}")
            return False
        
        # Step 4: Verify multiroom structure
        print("\n🧪 Step 4: Verifying multiroom structure...")
        verification = verify_multiroom_structure(tmux_info)
        
        test_results = [
            ("Company → Session", verification["company_to_session"]),
            ("Room → Window", verification["room_to_window"]),
            ("Desk → Pane", verification["desk_to_pane"]),
            ("Directory Structure", verification["directory_structure"])
        ]
        
        passed_count = 0
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {test_name}")
            if passed:
                passed_count += 1
        
        # Show details
        print("\n📋 Detailed Results:")
        for key, value in verification["details"].items():
            print(f"   {key}: {value}")
        
        # Step 5: Show detailed tmux information
        print("\n🔬 Step 5: Detailed tmux structure:")
        print(f"   Session: {session_name}")
        
        for window in tmux_info.get("windows", []):
            window_id = window["id"]
            window_name = window["name"]
            details = tmux_info["window_details"][window_id]
            
            print(f"   └── Window {window_id}: {window_name} ({details['pane_count']} panes)")
            
            # Show first few panes as examples
            for i, pane_title in enumerate(details["pane_titles"][:4]):
                pane_path = details["pane_paths"][i]["path"] if i < len(details["pane_paths"]) else "N/A"
                print(f"       ├── Pane {pane_title['index']}: {pane_title['title']}")
                print(f"       │   Path: {pane_path}")
            
            if len(details["pane_titles"]) > 4:
                print(f"       └── ... and {len(details['pane_titles']) - 4} more panes")
        
        # Cleanup
        cleanup_test_session(session_name)
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 REAL COMMAND TEST RESULTS:")
        print(f"   📊 Overall: {passed_count}/4 tests passed")
        print(f"   🚀 Apply command: {'✅ SUCCESS' if apply_result['success'] else '❌ FAILED'}")
        print(f"   🔧 Multiroom function: {'✅ WORKING' if passed_count >= 3 else '❌ NEEDS WORK'}")
        
        return passed_count >= 3


if __name__ == "__main__":
    success = main()
    print(f"\n🏁 Test completed with {'SUCCESS' if success else 'FAILURES'}")
    exit(0 if success else 1) 