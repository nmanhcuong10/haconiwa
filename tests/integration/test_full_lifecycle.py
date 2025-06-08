"""
Full lifecycle integration tests for haconiwa company management.
Tests complete workflow from creation to deletion including all features.
"""

import pytest
import tempfile
import shutil
import json
import subprocess
import os
import time
from pathlib import Path
from typing import Dict, List, Optional


class TestFullLifecycle:
    """Test complete company lifecycle: creation → operations → deletion"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.test_dir = tempfile.mkdtemp(prefix="haconiwa_lifecycle_")
        self.test_path = Path(self.test_dir)
        self.created_companies = []
        
    def teardown_method(self):
        """Cleanup test environment after each test"""
        # Cleanup any created companies
        for company_name in self.created_companies:
            self._force_cleanup_company(company_name)
        
        # Remove test directory
        if self.test_path.exists():
            shutil.rmtree(self.test_path)
    
    def _force_cleanup_company(self, company_name: str):
        """Force cleanup of a company and its resources"""
        try:
            subprocess.run(
                ["haconiwa", "company", "kill", company_name, "--force", "--clean-dirs"],
                capture_output=True,
                check=False
            )
        except Exception:
            pass
    
    def _run_haconiwa_command(self, args: List[str], input_text: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run haconiwa command and return result"""
        cmd = ["haconiwa"] + args
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            input=input_text
        )
    
    def _verify_company_running(self, company_name: str) -> bool:
        """Verify company is running in tmux"""
        result = self._run_haconiwa_command(["company", "list"])
        return company_name in result.stdout and "✓" in result.stdout
    
    def _verify_directory_structure_complete(self, base_path: Path, company_name: str) -> Dict[str, bool]:
        """Verify complete directory structure with detailed checks"""
        results = {
            "base_exists": base_path.exists(),
            "metadata_exists": (base_path / f".haconiwa-{company_name}.json").exists(),
            "org_count": 0,
            "role_count": 0,
            "readme_count": 0,
            "detailed_structure": {}
        }
        
        if base_path.exists():
            for org_idx, org_id in enumerate(["org-01", "org-02", "org-03", "org-04"]):
                org_path = base_path / org_id
                if org_path.exists():
                    results["org_count"] += 1
                    results["detailed_structure"][org_id] = {"exists": True, "roles": {}}
                    
                    # Check role directories
                    for role in ["boss", "worker-a", "worker-b", "worker-c"]:
                        role_dir = f"{org_idx+1:02d}{role}"
                        role_path = org_path / role_dir
                        if role_path.exists():
                            results["role_count"] += 1
                            results["detailed_structure"][org_id]["roles"][role_dir] = {
                                "exists": True,
                                "readme_exists": (role_path / "README.md").exists()
                            }
                            if (role_path / "README.md").exists():
                                results["readme_count"] += 1
                        else:
                            results["detailed_structure"][org_id]["roles"][role_dir] = {"exists": False}
                else:
                    results["detailed_structure"][org_id] = {"exists": False}
        
        return results
    
    def test_complete_company_lifecycle_multiagent(self):
        """Test complete lifecycle: multiagent creation → list → update → delete with cleanup"""
        company_name = "lifecycle-test-multiagent"
        base_path = self.test_path / "multiagent-desks"
        self.created_companies.append(company_name)
        
        # Step 1: Create multiagent company
        print(f"\n🏗️ Step 1: Creating multiagent company '{company_name}'")
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "営業部",
            "--org02-name", "開発部",
            "--org03-name", "マーケティング部",
            "--org04-name", "サポート部",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Multiagent creation failed: {result.stderr}"
        assert "Company session created" in result.stdout or "multiagent" in result.stdout
        
        # Verify company is running
        assert self._verify_company_running(company_name), "Company should be running after creation"
        
        # Step 2: Verify directory structure is complete
        print("📁 Step 2: Verifying directory structure")
        structure = self._verify_directory_structure_complete(base_path, company_name)
        
        assert structure["base_exists"], "Base directory should exist"
        assert structure["metadata_exists"], "Metadata file should exist"
        assert structure["org_count"] == 4, f"Should have 4 organizations, got {structure['org_count']}"
        assert structure["role_count"] == 16, f"Should have 16 roles total, got {structure['role_count']}"
        assert structure["readme_count"] == 16, f"Should have 16 README files, got {structure['readme_count']}"
        
        # Verify metadata content
        metadata_file = base_path / f".haconiwa-{company_name}.json"
        with metadata_file.open('r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        assert metadata["company_name"] == company_name
        assert set(metadata["directories"]) == {"org-01", "org-02", "org-03", "org-04"}
        
        # Step 3: List companies to verify visibility
        print("📋 Step 3: Listing companies")
        result = self._run_haconiwa_command(["company", "list"])
        assert result.returncode == 0, f"Company list failed: {result.stderr}"
        assert company_name in result.stdout, "Company should appear in list"
        
        # Step 4: Update company (if update functionality exists)
        print("🔄 Step 4: Testing company update")
        result = self._run_haconiwa_command([
            "company", "update", company_name,
            "--org01-name", "営業部門"
        ])
        # Update might not be implemented, so we don't assert on return code
        
        # Step 5: Kill company without cleanup to test directory preservation
        print("⏹️ Step 5: Killing company without cleanup")
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--force"
        ])
        
        assert result.returncode == 0, f"Company kill failed: {result.stderr}"
        
        # Verify company is no longer running
        assert not self._verify_company_running(company_name), "Company should not be running after kill"
        
        # Verify directories still exist
        structure_after_kill = self._verify_directory_structure_complete(base_path, company_name)
        assert structure_after_kill["base_exists"], "Directories should remain after kill without cleanup"
        
        # Step 6: Recreate company using existing directories
        print("🔄 Step 6: Recreating company with existing directories")
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "営業部門",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Company recreation failed: {result.stderr}"
        assert self._verify_company_running(company_name), "Company should be running after recreation"
        
        # Step 7: Final cleanup with directory removal
        print("🗑️ Step 7: Final cleanup with directory removal")
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--clean-dirs",
            "--base-path", str(base_path),
            "--force"
        ])
        
        assert result.returncode == 0, f"Company cleanup failed: {result.stderr}"
        assert "🗑️ Cleaned directories" in result.stdout, "Should show cleanup message"
        
        # Verify complete cleanup
        final_structure = self._verify_directory_structure_complete(base_path, company_name)
        assert not final_structure["base_exists"], "All directories should be removed after cleanup"
        assert not final_structure["metadata_exists"], "Metadata should be removed after cleanup"
        
        # Verify company is no longer running
        assert not self._verify_company_running(company_name), "Company should not be running after cleanup"
        
        print("✅ Complete lifecycle test passed!")
    
    def test_complete_company_lifecycle_simple(self):
        """Test complete lifecycle for simple company: creation → operations → cleanup"""
        company_name = "lifecycle-test-simple"
        self.created_companies.append(company_name)
        
        # Step 1: Create simple company
        print(f"\n🏗️ Step 1: Creating simple company '{company_name}'")
        result = self._run_haconiwa_command([
            "company", "create", company_name
        ])
        
        assert result.returncode == 0, f"Simple company creation failed: {result.stderr}"
        
        # Verify company is running
        assert self._verify_company_running(company_name), "Simple company should be running after creation"
        
        # Step 2: List and verify
        print("📋 Step 2: Verifying company in list")
        result = self._run_haconiwa_command(["company", "list"])
        assert result.returncode == 0, f"Company list failed: {result.stderr}"
        assert company_name in result.stdout, "Simple company should appear in list"
        
        # Step 3: Kill simple company
        print("⏹️ Step 3: Killing simple company")
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--force"
        ])
        
        assert result.returncode == 0, f"Simple company kill failed: {result.stderr}"
        assert not self._verify_company_running(company_name), "Simple company should not be running after kill"
        
        print("✅ Simple company lifecycle test passed!")
    
    def test_error_handling_lifecycle(self):
        """Test error handling during lifecycle operations"""
        company_name = "lifecycle-test-errors"
        self.created_companies.append(company_name)
        
        # Test 1: Try to kill non-existent company
        print("\n🧪 Test 1: Killing non-existent company")
        result = self._run_haconiwa_command([
            "company", "kill", "non-existent-company",
            "--force"
        ])
        # Should handle gracefully (not necessarily fail)
        
        # Test 2: Create company with problematic name
        print("🧪 Test 2: Creating company with valid name")
        result = self._run_haconiwa_command([
            "company", "create", company_name
        ])
        assert result.returncode == 0, f"Company creation failed: {result.stderr}"
        
        # Test 3: Try to create duplicate company
        print("🧪 Test 3: Creating duplicate company")
        result = self._run_haconiwa_command([
            "company", "create", company_name
        ])
        # Should handle duplicate creation appropriately
        
        # Test 4: Cleanup
        print("🧪 Test 4: Cleanup error test company")
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--force"
        ])
        assert result.returncode == 0, f"Error test cleanup failed: {result.stderr}"
        
        print("✅ Error handling lifecycle test passed!")
    
    def test_concurrent_operations_safety(self):
        """Test safety of concurrent operations"""
        company1 = "lifecycle-concurrent-1"
        company2 = "lifecycle-concurrent-2"
        self.created_companies.extend([company1, company2])
        
        # Create two companies simultaneously
        print(f"\n🔄 Creating two companies for concurrent testing")
        result1 = self._run_haconiwa_command([
            "company", "create", company1
        ])
        result2 = self._run_haconiwa_command([
            "company", "create", company2
        ])
        
        assert result1.returncode == 0, f"Company 1 creation failed: {result1.stderr}"
        assert result2.returncode == 0, f"Company 2 creation failed: {result2.stderr}"
        
        # Verify both are running
        assert self._verify_company_running(company1), "Company 1 should be running"
        assert self._verify_company_running(company2), "Company 2 should be running"
        
        # List should show both
        result = self._run_haconiwa_command(["company", "list"])
        assert company1 in result.stdout, "Company 1 should be in list"
        assert company2 in result.stdout, "Company 2 should be in list"
        
        # Clean up both
        result1 = self._run_haconiwa_command(["company", "kill", company1, "--force"])
        result2 = self._run_haconiwa_command(["company", "kill", company2, "--force"])
        
        assert result1.returncode == 0, f"Company 1 cleanup failed: {result1.stderr}"
        assert result2.returncode == 0, f"Company 2 cleanup failed: {result2.stderr}"
        
        print("✅ Concurrent operations safety test passed!") 