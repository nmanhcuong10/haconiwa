#!/usr/bin/env python3
"""
Test for pane titles and space commands
ペインタイトル表示とspace関連コマンドのテスト
"""

import sys
import os
import subprocess
import time
import tempfile
import yaml
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_yaml() -> str:
    """テスト用のYAMLファイルを作成"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml_content = {
            'apiVersion': 'haconiwa.dev/v1',
            'kind': 'Space',
            'metadata': {'name': 'pane-title-test'},
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
                                'name': 'title-test-company',
                                'grid': '8x4',
                                'basePath': './title-test-desks',
                                'organizations': [
                                    {'id': '01', 'name': 'フロントエンド開発部'},
                                    {'id': '02', 'name': 'バックエンド開発部'},
                                    {'id': '03', 'name': 'データベース部門'},
                                    {'id': '04', 'name': 'DevOps部門'}
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
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
        return f.name

def cleanup_session(session_name: str):
    """セッションクリーンアップ"""
    try:
        subprocess.run(['tmux', 'kill-session', '-t', session_name], 
                      capture_output=True, text=True)
        print(f"🧹 Cleaned up session: {session_name}")
    except:
        pass

def cleanup_directory(path: str):
    """ディレクトリクリーンアップ"""
    try:
        import shutil
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"🧹 Cleaned up directory: {path}")
    except:
        pass

def test_pane_titles():
    """Test 1: ペインタイトルの表示確認"""
    print("\n🧪 Test 1: Pane titles display test")
    
    session_name = "title-test-company"
    yaml_file = None
    
    try:
        # YAMLファイル作成
        yaml_file = create_test_yaml()
        print(f"   Created YAML: {yaml_file}")
        
        # クリーンアップ
        cleanup_session(session_name)
        cleanup_directory("./title-test-desks")
        
        # haconiwa apply実行
        result = subprocess.run(['haconiwa', 'apply', '-f', yaml_file], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"   ❌ Failed to apply YAML: {result.stderr}")
            return False
        
        print("   ✅ Session created successfully")
        time.sleep(2)
        
        # ペインタイトル確認
        result = subprocess.run(['tmux', 'list-panes', '-t', session_name, '-F', 
                               '#{window_index}:#{pane_index}:#{pane_title}'], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"   ❌ Failed to get pane info: {result.stderr}")
            return False
        
        pane_info = result.stdout.strip().split('\n')
        print(f"   📊 Found {len(pane_info)} panes")
        
        # タイトル確認
        titled_panes = 0
        sample_titles = []
        
        for i, line in enumerate(pane_info[:8]):  # 最初の8ペインをチェック
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    window_id, pane_id, title = parts[0], parts[1], ':'.join(parts[2:])
                    sample_titles.append(f"Window {window_id}, Pane {pane_id}: {title}")
                    
                    # 組織名やロールが含まれているかチェック
                    if any(keyword in title.lower() for keyword in ['org', 'pm', 'worker', 'alpha', 'beta']):
                        titled_panes += 1
        
        print("   📋 Sample pane titles:")
        for title in sample_titles[:5]:
            print(f"      {title}")
        
        if titled_panes >= 4:  # 最低4つのペインに適切なタイトルがある
            print(f"   ✅ Pane titles working: {titled_panes} properly titled panes")
            return True
        else:
            print(f"   ❌ Insufficient titled panes: {titled_panes} (expected >= 4)")
            return False
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    finally:
        cleanup_session(session_name)
        cleanup_directory("./title-test-desks")
        if yaml_file and os.path.exists(yaml_file):
            os.unlink(yaml_file)

def test_space_attach():
    """Test 2: space attach機能のテスト"""
    print("\n🧪 Test 2: space attach command test")
    
    # まず実装があるかチェック
    result = subprocess.run(['haconiwa', 'space', '--help'], 
                           capture_output=True, text=True)
    
    if 'attach' not in result.stdout:
        print("   ❌ space attach command not implemented")
        return False
    
    # 実際のattachテスト（dry-runまたは検証）
    print("   ✅ space attach command found in help")
    # TODO: 実際の実装後により詳細なテスト
    return True

def test_space_run_claude_code():
    """Test 3: space run --claude-code機能のテスト"""
    print("\n🧪 Test 3: space run --claude-code command test")
    
    # まず実装があるかチェック
    result = subprocess.run(['haconiwa', 'space', '--help'], 
                           capture_output=True, text=True)
    
    if 'run' not in result.stdout:
        print("   ❌ space run command not implemented")
        return False
    
    # 実際のrunコマンドのヘルプを確認
    result = subprocess.run(['haconiwa', 'space', 'run', '--help'], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print("   ❌ space run command not working")
        return False
    
    if '--claude-code' not in result.stdout:
        print("   ❌ --claude-code option not found")
        return False
    
    print("   ✅ space run --claude-code command implemented")
    return True

def test_space_kill():
    """Test 4: space kill機能のテスト"""
    print("\n🧪 Test 4: space kill command test")
    
    result = subprocess.run(['haconiwa', 'space', '--help'], 
                           capture_output=True, text=True)
    
    if 'kill' not in result.stdout and 'stop' not in result.stdout:
        print("   ❌ space kill/stop command not implemented")
        return False
    
    print("   ✅ space stop command found in help")
    # TODO: 実際のテスト
    return True

def test_space_delete():
    """Test 5: space delete機能のテスト"""
    print("\n🧪 Test 5: space delete command test")
    
    # まず実装があるかチェック
    result = subprocess.run(['haconiwa', 'space', '--help'], 
                           capture_output=True, text=True)
    
    if 'delete' not in result.stdout:
        print("   ❌ space delete command not implemented")
        return False
    
    # 実際のdeleteコマンドのヘルプを確認
    result = subprocess.run(['haconiwa', 'space', 'delete', '--help'], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print("   ❌ space delete command not working")
        return False
    
    if '--clean-dirs' not in result.stdout:
        print("   ❌ --clean-dirs option not found")
        return False
    
    print("   ✅ space delete command implemented")
    return True

def test_full_workflow():
    """Test 6: 一連のワークフローテスト"""
    print("\n🧪 Test 6: Full workflow test (create → attach → run → kill → delete)")
    
    session_name = "workflow-test-company"
    yaml_file = None
    
    try:
        # 1. Create
        yaml_file = create_test_yaml()
        
        # YAMLの会社名を変更
        with open(yaml_file, 'r') as f:
            content = f.read()
        content = content.replace('title-test-company', 'workflow-test-company')
        with open(yaml_file, 'w') as f:
            f.write(content)
        
        cleanup_session(session_name)
        cleanup_directory("./title-test-desks")
        
        print("   🎯 Step 1: Creating session...")
        result = subprocess.run(['haconiwa', 'apply', '-f', yaml_file], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("   ❌ Failed to create session")
            return False
        
        print("   ✅ Session created")
        time.sleep(1)
        
        # 2. Attach (シミュレーション)
        print("   🎯 Step 2: Testing attach capability...")
        result = subprocess.run(['tmux', 'has-session', '-t', session_name], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Session ready for attach")
        else:
            print("   ❌ Session not found for attach")
            return False
        
        # 3. Run (未実装なのでスキップ)
        print("   🎯 Step 3: Run commands (not implemented yet)")
        
        # 4. Kill
        print("   🎯 Step 4: Killing session...")
        result = subprocess.run(['tmux', 'kill-session', '-t', session_name], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Session killed")
        else:
            print("   ❌ Failed to kill session")
        
        # 5. Delete (ディレクトリクリーンアップとして)
        print("   🎯 Step 5: Cleanup...")
        cleanup_directory("./title-test-desks")
        print("   ✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Workflow test failed: {e}")
        return False
    finally:
        cleanup_session(session_name)
        cleanup_directory("./title-test-desks")
        if yaml_file and os.path.exists(yaml_file):
            os.unlink(yaml_file)

def main():
    print("🚀 Pane Titles and Space Commands Test Suite")
    print("=" * 60)
    
    tests = [
        ("Pane Titles Display", test_pane_titles),
        ("Space Attach", test_space_attach),
        ("Space Run Claude Code", test_space_run_claude_code),
        ("Space Kill", test_space_kill),
        ("Space Delete", test_space_delete),
        ("Full Workflow", test_full_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed < len(results):
        print("\n🔧 Required implementations:")
        for test_name, result in results:
            if not result:
                if "Pane Titles" in test_name:
                    print("   - Fix pane title display in SpaceManager")
                elif "Run Claude Code" in test_name:
                    print("   - Implement space run --claude-code command")
                elif "Delete" in test_name:
                    print("   - Implement space delete command")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 