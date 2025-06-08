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
        self.created_companies.append(company_name)
        
        # First build - create company
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
            "--org01-name", "TestOrg",
            "--no-attach"
        ])
        
        assert result.returncode == 0, f"Initial build failed: {result.stderr}"
        
        # Second build with no changes
        result = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name
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
        self.created_companies.append(company_name)
        
        # Verify company doesn't exist initially
        assert not self._verify_company_running(company_name), "Company should not exist initially"
        
        # First build - should create
        result1 = self._run_haconiwa_command([
            "company", "build",
            "--name", company_name,
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
            "--org01-name", "UpdatedOrg"
        ])
        
        assert result2.returncode == 0
        assert "Updating existing company" in result2.stdout, "Should indicate existing company update" 