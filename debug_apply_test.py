#!/usr/bin/env python3
"""
Debug script for CLI apply command test failure
"""

import sys
sys.path.insert(0, 'src')

from unittest.mock import patch, MagicMock, mock_open
from typer.testing import CliRunner
from haconiwa.cli import app
from haconiwa.core.crd.models import SpaceCRD

def main():
    runner = CliRunner()
    
    # Mock CRD object with proper metadata structure
    mock_space_crd = MagicMock(spec=SpaceCRD)
    mock_metadata = MagicMock()
    mock_metadata.name = 'test-space'
    mock_space_crd.metadata = mock_metadata
    
    with patch('haconiwa.core.crd.parser.CRDParser.parse_file', return_value=mock_space_crd), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data="yaml content")), \
         patch('haconiwa.core.applier.CRDApplier.apply') as mock_apply:
        
        result = runner.invoke(app, ['apply', '-f', 'test.yaml'])
        print(f'Exit code: {result.exit_code}')
        print(f'Stdout: {result.stdout}')
        if result.exception:
            print(f'Exception: {result.exception}')
            import traceback
            traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)

if __name__ == "__main__":
    main() 