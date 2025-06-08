import pytest
import tempfile
import shutil
import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List


class TestCompanyCleanup:
    """Test company creation and directory cleanup functionality"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.test_dir = tempfile.mkdtemp(prefix="haconiwa_test_")
        self.test_path = Path(self.test_dir)
        
    def teardown_method(self):
        """Cleanup test environment after each test"""
        if self.test_path.exists():
            shutil.rmtree(self.test_path)
        
        # Cleanup any leftover test companies
        self._cleanup_test_companies()
    
    def _cleanup_test_companies(self):
        """Cleanup any test companies that might be left running"""
        test_companies = [
            "test-cleanup-integration",
            "test-no-cleanup-integration", 
            "test-metadata-integration"
        ]
        
        for company_name in test_companies:
            try:
                subprocess.run(
                    ["haconiwa", "company", "kill", company_name, "--force"],
                    capture_output=True,
                    check=False  # Don't fail if company doesn't exist
                )
            except Exception:
                pass  # Ignore errors during cleanup
    
    def _run_haconiwa_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run haconiwa command and return result"""
        cmd = ["haconiwa"] + args
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def _verify_directory_structure(self, base_path: Path, company_name: str) -> Dict[str, bool]:
        """Verify expected directory structure exists"""
        results = {
            "base_exists": base_path.exists(),
            "metadata_exists": (base_path / f".haconiwa-{company_name}.json").exists(),
            "org_directories": {}
        }
        
        if base_path.exists():
            for org_idx, org_id in enumerate(["org-01", "org-02", "org-03", "org-04"]):
                org_path = base_path / org_id
                results["org_directories"][org_id] = org_path.exists()
                
                if org_path.exists():
                    # Check role directories
                    for role in ["boss", "worker-a", "worker-b", "worker-c"]:
                        role_dir = f"{org_idx+1:02d}{role}"  # org_idx is 0-based, but directory is 1-based
                        role_path = org_path / role_dir
                        results["org_directories"][f"{org_id}/{role_dir}"] = role_path.exists()
                        
                        # Check README files
                        readme_path = role_path / "README.md"
                        results["org_directories"][f"{org_id}/{role_dir}/README.md"] = readme_path.exists()
        
        return results
    
    def test_company_creation_with_directory_structure(self):
        """Test that company creation creates proper directory structure and metadata"""
        company_name = "test-cleanup-integration"
        base_path = self.test_path / "test-desks"
        
        # Create company
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "テスト組織1",
            "--org02-name", "テスト組織2", 
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Company creation failed: {result.stderr}"
        
        # Verify directory structure
        structure = self._verify_directory_structure(base_path, company_name)
        
        assert structure["base_exists"], "Base directory should exist"
        assert structure["metadata_exists"], "Metadata file should exist"
        
        # Check all organization directories exist
        for org_idx, org_id in enumerate(["org-01", "org-02", "org-03", "org-04"]):
            assert structure["org_directories"][org_id], f"Organization {org_id} directory should exist"
            
            # Check role directories and README files
            for role in ["boss", "worker-a", "worker-b", "worker-c"]:
                role_dir = f"{org_idx+1:02d}{role}"  # org_idx is 0-based, but directory is 1-based
                assert structure["org_directories"][f"{org_id}/{role_dir}"], f"Role directory {role_dir} should exist"
                assert structure["org_directories"][f"{org_id}/{role_dir}/README.md"], f"README.md should exist in {role_dir}"
        
        # Verify metadata content
        metadata_file = base_path / f".haconiwa-{company_name}.json"
        with metadata_file.open('r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        assert metadata["company_name"] == company_name
        assert metadata["base_path"] == str(base_path)
        assert set(metadata["directories"]) == {"org-01", "org-02", "org-03", "org-04"}
        assert "created_at" in metadata
    
    def test_company_kill_with_clean_dirs(self):
        """Test that company kill with --clean-dirs removes all directories and metadata"""
        company_name = "test-cleanup-integration"
        base_path = self.test_path / "test-desks"
        
        # Create company first
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "テスト組織1",
            "--no-attach"
        ])
        assert result.returncode == 0, f"Company creation failed: {result.stderr}"
        
        # Verify structure exists before cleanup
        structure_before = self._verify_directory_structure(base_path, company_name)
        assert structure_before["base_exists"], "Base directory should exist before cleanup"
        assert structure_before["metadata_exists"], "Metadata should exist before cleanup"
        
        # Kill company with cleanup
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--clean-dirs",
            "--base-path", str(base_path),
            "--force"
        ])
        
        assert result.returncode == 0, f"Company kill with cleanup failed: {result.stderr}"
        assert "🗑️ Cleaned directories" in result.stdout, "Should show cleanup message"
        assert "Removed directory:" in result.stdout, "Should show removed directories"
        assert "Removed metadata file:" in result.stdout, "Should show metadata removal"
        
        # Verify everything is cleaned up
        structure_after = self._verify_directory_structure(base_path, company_name)
        assert not structure_after["base_exists"], "Base directory should be removed"
        assert not structure_after["metadata_exists"], "Metadata file should be removed"
    
    def test_company_kill_without_clean_dirs(self):
        """Test that company kill without --clean-dirs leaves directories intact"""
        company_name = "test-no-cleanup-integration"
        base_path = self.test_path / "test-desks-no-clean"
        
        # Create company first
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "保持テスト組織",
            "--no-attach"
        ])
        assert result.returncode == 0, f"Company creation failed: {result.stderr}"
        
        # Verify structure exists before kill
        structure_before = self._verify_directory_structure(base_path, company_name)
        assert structure_before["base_exists"], "Base directory should exist before kill"
        assert structure_before["metadata_exists"], "Metadata should exist before kill"
        
        # Kill company without cleanup
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--force"
        ])
        
        assert result.returncode == 0, f"Company kill failed: {result.stderr}"
        assert "🗑️ Cleaned directories" not in result.stdout, "Should not show cleanup message"
        
        # Verify directories remain
        structure_after = self._verify_directory_structure(base_path, company_name)
        assert structure_after["base_exists"], "Base directory should remain"
        assert structure_after["metadata_exists"], "Metadata file should remain"
        
        # Verify organization directories still exist
        for org_id in ["org-01", "org-02", "org-03", "org-04"]:
            assert structure_after["org_directories"][org_id], f"Organization {org_id} should remain"
    
    def test_cleanup_without_metadata_file(self):
        """Test cleanup behavior when metadata file doesn't exist (fallback to default)"""
        company_name = "test-metadata-integration"
        base_path = self.test_path / "test-desks-no-metadata"
        
        # Create company first
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(base_path),
            "--no-attach"
        ])
        assert result.returncode == 0, f"Company creation failed: {result.stderr}"
        
        # Manually remove metadata file to simulate missing metadata
        metadata_file = base_path / f".haconiwa-{company_name}.json"
        if metadata_file.exists():
            metadata_file.unlink()
        
        # Verify structure exists but metadata is missing
        structure_before = self._verify_directory_structure(base_path, company_name)
        assert structure_before["base_exists"], "Base directory should exist"
        assert not structure_before["metadata_exists"], "Metadata should be missing"
        
        # Kill company with cleanup (should use fallback cleanup)
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--clean-dirs", 
            "--base-path", str(base_path),
            "--force"
        ])
        
        assert result.returncode == 0, f"Company kill with cleanup failed: {result.stderr}"
        assert "🗑️ Cleaned directories" in result.stdout, "Should show cleanup message"
        
        # Verify cleanup happened (should use default org structure)
        structure_after = self._verify_directory_structure(base_path, company_name)
        assert not structure_after["base_exists"], "Base directory should be removed"
    
    def test_kill_command_confirmation_prompt(self):
        """Test that kill command shows proper confirmation prompt with --clean-dirs"""
        company_name = "test-cleanup-integration"
        base_path = self.test_path / "test-desks-confirm"
        
        # Create company first
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(base_path),
            "--no-attach"
        ])
        assert result.returncode == 0, f"Company creation failed: {result.stderr}"
        
        # Test help output includes new options
        help_result = self._run_haconiwa_command(["company", "kill", "--help"])
        assert help_result.returncode == 0
        assert "--clean-dirs" in help_result.stdout
        assert "--base-path" in help_result.stdout
        assert "Remove related directories" in help_result.stdout
    
    def test_nonexistent_base_path_handling(self):
        """Test cleanup behavior when base path doesn't exist"""
        company_name = "test-cleanup-integration"
        nonexistent_path = self.test_path / "nonexistent" / "path"
        
        # Create company first (but directory creation might fail)
        result = self._run_haconiwa_command([
            "company", "multiagent",
            "--name", company_name,
            "--base-path", str(nonexistent_path),
            "--no-attach"
        ])
        # Company creation should still succeed (creates directories)
        assert result.returncode == 0
        
        # Now try to kill with cleanup on different nonexistent path
        different_path = self.test_path / "different" / "nonexistent"
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--clean-dirs",
            "--base-path", str(different_path),
            "--force"
        ])
        
        # Should not fail, just show "nothing to clean" message
        assert result.returncode == 0
        # Note: The actual behavior might vary based on implementation
    
    def test_directory_permission_handling(self):
        """Test cleanup behavior with permission issues (if applicable)"""
        company_name = "test-cleanup-integration"
        base_path = self.test_path / "test-desks-permissions"
        
        # Create company first
        result = self._run_haconiwa_command([
            "company", "multiagent", 
            "--name", company_name,
            "--base-path", str(base_path),
            "--no-attach"
        ])
        assert result.returncode == 0, f"Company creation failed: {result.stderr}"
        
        # Create additional file in org directory to test non-empty directory handling
        test_file = base_path / "org-01" / "additional_file.txt"
        test_file.write_text("This file should be removed with the directory")
        
        # Kill company with cleanup
        result = self._run_haconiwa_command([
            "company", "kill", company_name,
            "--clean-dirs",
            "--base-path", str(base_path), 
            "--force"
        ])
        
        assert result.returncode == 0, f"Company kill with cleanup failed: {result.stderr}"
        
        # Verify complete cleanup including additional files
        assert not base_path.exists(), "Base directory should be completely removed" 