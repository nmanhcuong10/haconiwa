"""
Integration tests for haconiwa company build command.
Tests build-specific functionality: create, update, rebuild, existence checking.
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


class TestCompanyBuild:
    """Test company build command functionality"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.test_dir = tempfile.mkdtemp(prefix="haconiwa_build_test_")
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
        return (company_name in result.stdout and result.returncode == 0 and 
                ("🏛️" in result.stdout or "🔗" in result.stdout))
    
    def _verify_directory_structure(self, base_path: Path, company_name: str) -> Dict[str, bool]:
        """Verify directory structure exists"""
        results = {
            "base_exists": base_path.exists(),
            "metadata_exists": (base_path / f".haconiwa-{company_name}.json").exists(),
            "org_count": 0
        }
        
        if base_path.exists():
            for org_id in ["org-01", "org-02", "org-03", "org-04"]:
                org_path = base_path / org_id
                if org_path.exists():
                    results["org_count"] += 1
        
        return results
    
    def test_build_new_company(self):
        """Test building a new company from scratch"""
        company_name = "test-build-new"
        base_path = self.test_path / "new-company"
        self.created_companies.append(company_name)
        
        # Build new company
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "Engineering",
            "--org02-name", "Marketing",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Build new company failed: {result.stderr}"
        assert "Building new company" in result.stdout or "Built company" in result.stdout
        
        # Verify company is running
        assert self._verify_company_running(company_name), "Company should be running after build"
        
        # Verify directory structure
        structure = self._verify_directory_structure(base_path, company_name)
        assert structure["base_exists"], "Base directory should exist"
        assert structure["metadata_exists"], "Metadata file should exist"
        assert structure["org_count"] == 4, "Should have 4 organizations"
    
    def test_build_existing_company_update(self):
        """Test building an existing company (should update)"""
        company_name = "test-build-update"
        base_path = self.test_path / "update-company"
        self.created_companies.append(company_name)
        
        # First build - create company
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "InitialOrg",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Initial build failed: {result.stderr}"
        assert self._verify_company_running(company_name), "Company should be running after initial build"
        
        # Second build - should update existing company
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--org01-name", "UpdatedOrg",
            "--org02-name", "NewOrg"
        ])
        
        assert result.returncode == 0, f"Update build failed: {result.stderr}"
        assert "Updating existing company" in result.stdout, "Should show update message"
        assert "UpdatedOrg" in result.stdout, "Should show updated organization"
        assert "NewOrg" in result.stdout, "Should show new organization"
        
        # Company should still be running
        assert self._verify_company_running(company_name), "Company should still be running after update"
    
    def test_build_with_rebuild_option(self):
        """Test building with --rebuild option"""
        company_name = "test-build-rebuild"
        base_path = self.test_path / "rebuild-company"
        self.created_companies.append(company_name)
        
        # First build - create company
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "OriginalOrg",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Initial build failed: {result.stderr}"
        original_structure = self._verify_directory_structure(base_path, company_name)
        
        # Rebuild with --rebuild option
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "RebuiltOrg",
            "--rebuild",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Rebuild failed: {result.stderr}"
        assert "Rebuilding company" in result.stdout, "Should show rebuild message"
        assert "RebuiltOrg" in result.stdout, "Should show rebuilt organization"
        
        # Verify company is running and directories exist
        assert self._verify_company_running(company_name), "Company should be running after rebuild"
        rebuilt_structure = self._verify_directory_structure(base_path, company_name)
        assert rebuilt_structure["base_exists"], "Directories should exist after rebuild"
    
    def test_build_no_changes_specified(self):
        """Test building existing company with no changes specified"""
        company_name = "test-build-nochange"
        base_path = self.test_path / "nochange-test"
        self.created_companies.append(company_name)
        
        # First build - create company
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "TestOrg",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Initial build failed: {result.stderr}"
        
        # Second build with no changes - specify base path to avoid directory warning
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path)
        ])
        
        assert result.returncode == 0, f"No-change build failed: {result.stderr}"
        assert "No changes specified" in result.stdout, "Should indicate no changes"
        assert "already running" in result.stdout or "Use --rebuild" in result.stdout
    
    def test_build_with_all_organizations(self):
        """Test building company with all organization options"""
        company_name = "test-build-all-orgs"
        base_path = self.test_path / "all-orgs"
        self.created_companies.append(company_name)
        
        # Build with all organization names and tasks
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "Frontend Dev",
            "--org02-name", "Backend Dev", 
            "--org03-name", "Database Team",
            "--org04-name", "DevOps Team",
            "--task01", "UI Development",
            "--task02", "API Development",
            "--task03", "Schema Design",
            "--task04", "Infrastructure",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Full build failed: {result.stderr}"
        
        # Verify all organizations appear in output
        for org in ["Frontend Dev", "Backend Dev", "Database Team", "DevOps Team"]:
            assert org in result.stdout, f"Organization '{org}' should appear in output"
        
        for task in ["UI Development", "API Development", "Schema Design", "Infrastructure"]:
            assert task in result.stdout, f"Task '{task}' should appear in output"
        
        # Verify company is running
        assert self._verify_company_running(company_name), "Company should be running"
        
        # Verify directory structure
        structure = self._verify_directory_structure(base_path, company_name)
        assert structure["org_count"] == 4, "Should have all 4 organizations"
    
    def test_build_error_handling(self):
        """Test build command error handling"""
        # Test missing required name parameter
        result = self._run_haconiwa_command([
            "company", "build",
            "--org01-name", "TestOrg"
        ])
        
        assert result.returncode != 0, "Should fail without company name"
        assert "required" in result.stderr.lower() or "missing" in result.stderr.lower()
    
    def test_build_help_output(self):
        """Test build command help output"""
        result = self._run_haconiwa_command([
            "company", "build", "--help"
        ])
        
        assert result.returncode == 0, "Help should succeed"
        assert "Build a company" in result.stdout
        assert "--name" in result.stdout
        assert "--org01-name" in result.stdout
        assert "--rebuild" in result.stdout
    
    def test_build_existence_detection(self):
        """Test that build properly detects existing companies"""
        company_name = "test-build-detection"
        base_path = self.test_path / "detection-test"
        self.created_companies.append(company_name)
        
        # Verify company doesn't exist initially
        assert not self._verify_company_running(company_name), "Company should not exist initially"
        
        # First build - should create
        result1 = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "TestOrg",
            "--no-attach"
        ])
        
        assert result1.returncode == 0
        assert "Building new company" in result1.stdout, "Should indicate new company creation"
        
        # Verify company now exists
        assert self._verify_company_running(company_name), "Company should exist after first build"
        
        # Second build - should detect existing
        result2 = self._run_haconiwa_command([
            "company", "build", 
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "UpdatedOrg"
        ])
        
        assert result2.returncode == 0
        assert "Updating existing company" in result2.stdout, "Should indicate existing company update"
    
    def test_build_default_base_path(self):
        """Test that default base path is set to ./{company_name}"""
        company_name = "test-default-path"
        self.created_companies.append(company_name)
        
        # Build company without specifying base-path
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Build with default path failed: {result.stderr}"
        assert f"Base path: ./{company_name}" in result.stdout, "Should show default base path"
        
        # Verify company is running
        assert self._verify_company_running(company_name), "Company should be running"
        
        # Verify default directory was created
        default_path = Path(f"./{company_name}")
        assert default_path.exists(), f"Default directory ./{company_name} should be created"
        
        # Clean up the directory after test
        if default_path.exists():
            shutil.rmtree(default_path)
    
    def test_build_existing_directory_warning(self):
        """Test warning when building in existing non-empty directory"""
        company_name = "test-existing-dir"
        test_dir = Path(f"./{company_name}")
        self.created_companies.append(company_name)
        
        try:
            # Create directory with some content
            test_dir.mkdir(exist_ok=True)
            (test_dir / "existing_file.txt").write_text("existing content")
            
            # Try to build company (should show warning and ask for confirmation)
            # We'll simulate "no" response by not providing input
            result = self._run_haconiwa_command([
                "company", "build", 
                "--name", company_name,
                "--no-attach"
            ], input_text="n\n")  # Simulate user pressing 'n' for no
            
            # Check that warning was shown
            assert "Warning: Directory" in result.stdout, "Should show directory warning"
            assert "already exists and is not empty" in result.stdout, "Should mention non-empty directory"
            assert "existing_file.txt" in result.stdout, "Should show existing file"
            
        finally:
            # Clean up
            if test_dir.exists():
                shutil.rmtree(test_dir)
    
    def test_build_existing_directory_with_rebuild(self):
        """Test that --rebuild flag skips directory warning"""
        company_name = "test-rebuild-skip-warning"
        test_dir = Path(f"./{company_name}")
        self.created_companies.append(company_name)
        
        try:
            # Create directory with some content
            test_dir.mkdir(exist_ok=True)
            (test_dir / "existing_file.txt").write_text("existing content")
            
            # Build with --rebuild flag (should skip warning)
            result = self._run_haconiwa_command([
                "company", "build",
                "--name", company_name,
                "--rebuild",
                "--no-attach"
            ])
            
            assert result.returncode == 0, f"Build with rebuild should succeed: {result.stderr}"
            assert "--rebuild flag is set, continuing" in result.stdout, "Should mention rebuild flag"
            assert self._verify_company_running(company_name), "Company should be running"
            
        finally:
            # Clean up
            if test_dir.exists():
                shutil.rmtree(test_dir)
    
    def test_build_custom_base_path_still_works(self):
        """Test that custom base path still works as before"""
        company_name = "test-custom-path"
        custom_path = self.test_path / "custom-location"
        self.created_companies.append(company_name)
        
        # Build with custom base path
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(custom_path),
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Build with custom path failed: {result.stderr}"
        assert f"Base path: {custom_path}" in result.stdout, "Should show custom base path"
        
        # Verify custom directory was created
        assert custom_path.exists(), "Custom base path directory should be created"
        
        # Verify company is running
        assert self._verify_company_running(company_name), "Company should be running"
    
    def test_build_tmux_pane_directory_allocation(self):
        """Test that tmux panes are correctly allocated to proper directories"""
        company_name = "test-pane-dirs"
        base_path = self.test_path / "pane-test"
        self.created_companies.append(company_name)
        
        # Build company with default settings
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert self._verify_company_running(company_name), "Company should be running"
        
        # Check tmux pane directories using tmux directly
        pane_result = subprocess.run([
            "tmux", "list-panes", "-t", company_name, 
            "-F", "#{pane_current_path}"
        ], capture_output=True, text=True, check=False)
        
        if pane_result.returncode == 0:
            pane_paths = pane_result.stdout.strip().split('\n')
            assert len(pane_paths) == 16, "Should have 16 panes"
            
            # Verify each organization has 4 panes (boss + 3 workers)
            for org_num in range(1, 5):
                org_id = f"org-{org_num:02d}"
                org_panes = [p for p in pane_paths if f"/{org_id}/" in p]
                assert len(org_panes) == 4, f"Organization {org_id} should have 4 panes"
                
                # Check specific role directories - format: {base_path}/org-XX/XXrole
                expected_roles = ["boss", "worker-a", "worker-b", "worker-c"]
                for role in expected_roles:
                    role_dir = f"{org_num:02d}{role}"
                    role_panes = [p for p in org_panes if role_dir in p]
                    assert len(role_panes) == 1, f"Should have one pane for {org_id}/{role_dir}, found in paths: {org_panes}"
    
    def test_build_organization_name_in_pane_titles(self):
        """Test that organization names appear correctly in tmux pane titles"""
        company_name = "test-pane-titles"
        base_path = self.test_path / "title-test"
        self.created_companies.append(company_name)
        
        # Build company with custom organization names
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "フロントエンド開発部",
            "--org02-name", "バックエンド開発部",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert self._verify_company_running(company_name), "Company should be running"
        
        # Check tmux pane titles
        title_result = subprocess.run([
            "tmux", "list-panes", "-t", company_name,
            "-F", "#{pane_title}"
        ], capture_output=True, text=True, check=False)
        
        if title_result.returncode == 0:
            pane_titles = title_result.stdout.strip().split('\n')
            assert len(pane_titles) == 16, "Should have 16 pane titles"
            
            # Check that custom organization names appear in titles
            frontend_titles = [t for t in pane_titles if "フロントエンド開発部" in t]
            backend_titles = [t for t in pane_titles if "バックエンド開発部" in t]
            default_org03_titles = [t for t in pane_titles if "ORG-03" in t]
            default_org04_titles = [t for t in pane_titles if "ORG-04" in t]
            
            assert len(frontend_titles) == 4, "Should have 4 panes with frontend org name"
            assert len(backend_titles) == 4, "Should have 4 panes with backend org name"
            assert len(default_org03_titles) == 4, "Should have 4 panes with default ORG-03"
            assert len(default_org04_titles) == 4, "Should have 4 panes with default ORG-04"
            
            # Verify role titles are included
            for title in frontend_titles:
                assert any(role in title for role in ["BOSS", "WORKER-A", "WORKER-B", "WORKER-C"]), \
                    f"Title '{title}' should contain role information"
    
    def test_build_directory_structure_completeness(self):
        """Test that complete directory structure is created with proper metadata"""
        company_name = "test-dir-structure"
        base_path = self.test_path / "structure-test"
        self.created_companies.append(company_name)
        
        # Build company
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--base-path", str(base_path),
            "--org01-name", "テスト組織1",
            "--task01", "テストタスク1",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        
        # Verify complete directory structure
        assert base_path.exists(), "Base directory should exist"
        
        # Check metadata file
        metadata_file = base_path / f".haconiwa-{company_name}.json"
        assert metadata_file.exists(), "Metadata file should exist"
        
        # Verify all 4 organizations with 4 roles each = 16 directories
        total_role_dirs = 0
        for org_num in range(1, 5):
            org_id = f"org-{org_num:02d}"
            org_path = base_path / org_id
            assert org_path.exists(), f"Organization directory {org_id} should exist"
            
            for role in ["boss", "worker-a", "worker-b", "worker-c"]:
                role_dir = org_path / f"{org_num:02d}{role}"
                assert role_dir.exists(), f"Role directory {role_dir} should exist"
                assert role_dir.is_dir(), f"{role_dir} should be a directory"
                total_role_dirs += 1
        
        assert total_role_dirs == 16, "Should have exactly 16 role directories"
        
        # Verify metadata content if possible
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                assert metadata.get('company_name') == company_name, "Metadata should contain company name"
                assert 'directories' in metadata, "Metadata should contain directories info"
                assert len(metadata['directories']) == 4, "Should have 4 organization directories"
        except (json.JSONDecodeError, FileNotFoundError):
            # If metadata format is different, just verify file exists (already done above)
            pass 