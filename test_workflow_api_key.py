#!/usr/bin/env python3
"""
Test the API key handling logic in the GitHub Actions workflow
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


def test_api_key_precheck_with_secret():
    """Test that pre-check passes when secret is set"""
    print("=== Test 1: Pre-check with secret set ===")
    
    script = """
#!/bin/bash
CFB_API_KEY_SECRET="test_secret_key"
CFB_API_KEY_INPUT=""

if [ -n "$CFB_API_KEY_SECRET" ] || [ -n "$CFB_API_KEY_INPUT" ]; then
  echo "✓ API key is available"
  echo "0" > /tmp/test_exit_code.txt
  exit 0
else
  echo "❌ ERROR: No API key provided"
  echo "1" > /tmp/test_exit_code.txt
  exit 1
fi
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        exit_code = int(Path('/tmp/test_exit_code.txt').read_text().strip())
        
        assert result.returncode == 0, f"Expected success, got {result.returncode}"
        assert exit_code == 0, f"Expected exit_code.txt = 0, got {exit_code}"
        assert "✓ API key is available" in result.stdout
        print(f"   ✓ Pre-check passed with secret")
        print()
    finally:
        os.unlink(script_path)


def test_api_key_precheck_with_input():
    """Test that pre-check passes when input is set"""
    print("=== Test 2: Pre-check with workflow input set ===")
    
    script = """
#!/bin/bash
CFB_API_KEY_SECRET=""
CFB_API_KEY_INPUT="test_input_key"

if [ -n "$CFB_API_KEY_SECRET" ] || [ -n "$CFB_API_KEY_INPUT" ]; then
  echo "✓ API key is available"
  echo "0" > /tmp/test_exit_code.txt
  exit 0
else
  echo "❌ ERROR: No API key provided"
  echo "1" > /tmp/test_exit_code.txt
  exit 1
fi
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        exit_code = int(Path('/tmp/test_exit_code.txt').read_text().strip())
        
        assert result.returncode == 0, f"Expected success, got {result.returncode}"
        assert exit_code == 0, f"Expected exit_code.txt = 0, got {exit_code}"
        assert "✓ API key is available" in result.stdout
        print(f"   ✓ Pre-check passed with input")
        print()
    finally:
        os.unlink(script_path)


def test_api_key_precheck_without_key():
    """Test that pre-check fails when no key is set"""
    print("=== Test 3: Pre-check without any key ===")
    
    script = """
#!/bin/bash
CFB_API_KEY_SECRET=""
CFB_API_KEY_INPUT=""

if [ -n "$CFB_API_KEY_SECRET" ] || [ -n "$CFB_API_KEY_INPUT" ]; then
  echo "✓ API key is available"
  echo "0" > /tmp/test_exit_code.txt
  exit 0
else
  echo "❌ ERROR: No API key provided"
  echo "1" > /tmp/test_exit_code.txt
  exit 1
fi
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        exit_code = int(Path('/tmp/test_exit_code.txt').read_text().strip())
        
        assert result.returncode == 1, f"Expected failure, got {result.returncode}"
        assert exit_code == 1, f"Expected exit_code.txt = 1, got {exit_code}"
        assert "❌ ERROR: No API key provided" in result.stdout
        print(f"   ✓ Pre-check correctly failed without key")
        print()
    finally:
        os.unlink(script_path)


def test_api_key_preference_order():
    """Test that secret is preferred over input"""
    print("=== Test 4: API key preference (secret > input) ===")
    
    script = """
#!/bin/bash
CFB_API_KEY_SECRET="secret_key"
CFB_API_KEY_INPUT="input_key"

if [ -n "$CFB_API_KEY_SECRET" ]; then
  export CFB_API_KEY="$CFB_API_KEY_SECRET"
elif [ -n "$CFB_API_KEY_INPUT" ]; then
  export CFB_API_KEY="$CFB_API_KEY_INPUT"
fi

echo "$CFB_API_KEY"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        api_key = result.stdout.strip()
        
        assert result.returncode == 0, f"Script failed with {result.returncode}"
        assert api_key == "secret_key", f"Expected 'secret_key', got '{api_key}'"
        print(f"   ✓ Secret correctly preferred over input")
        print()
    finally:
        os.unlink(script_path)


def test_api_key_fallback_to_input():
    """Test that input is used when secret is not set"""
    print("=== Test 5: API key fallback to input ===")
    
    script = """
#!/bin/bash
CFB_API_KEY_SECRET=""
CFB_API_KEY_INPUT="input_key"

if [ -n "$CFB_API_KEY_SECRET" ]; then
  export CFB_API_KEY="$CFB_API_KEY_SECRET"
elif [ -n "$CFB_API_KEY_INPUT" ]; then
  export CFB_API_KEY="$CFB_API_KEY_INPUT"
fi

echo "$CFB_API_KEY"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        api_key = result.stdout.strip()
        
        assert result.returncode == 0, f"Script failed with {result.returncode}"
        assert api_key == "input_key", f"Expected 'input_key', got '{api_key}'"
        print(f"   ✓ Input correctly used as fallback")
        print()
    finally:
        os.unlink(script_path)


def test_workflow_yaml_structure():
    """Test that workflow YAML has expected structure"""
    print("=== Test 6: Workflow YAML structure ===")
    
    workflow_path = Path(__file__).parent / '.github' / 'workflows' / 'run-model.yml'
    with open(workflow_path) as f:
        content = f.read()
    
    # Check for key elements
    assert 'workflow_dispatch:' in content, "Missing workflow_dispatch"
    assert 'api_key:' in content, "Missing api_key input"
    assert 'Check API key availability' in content, "Missing API key pre-check step"
    assert 'secrets.CFB_API_KEY' in content, "Missing secret reference"
    assert 'github.event.inputs.api_key' in content, "Missing input reference"
    
    # Check that key patterns exist
    assert 'if [ -n "${{ secrets.CFB_API_KEY }}" ]' in content, "Missing secret check"
    assert 'if [ -n "${{ github.event.inputs.api_key }}" ]' in content, "Missing input check"
    
    # Verify no API key is echoed directly
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'echo' in line.lower() and ('${{ secrets.CFB_API_KEY }}' in line or '${CFB_API_KEY}' in line):
            # Allow echo in context setting, but not direct echo of the key value
            if 'export CFB_API_KEY=' not in line:
                raise AssertionError(f"Line {i} may expose API key: {line}")
    
    print("   ✓ Workflow structure is correct")
    print("   ✓ API key input is present")
    print("   ✓ Pre-check step is present")
    print("   ✓ Secret and input references are correct")
    print("   ✓ No direct key exposure in logs")
    print()


def main():
    """Run all tests"""
    print("=== Testing Workflow API Key Handling ===\n")
    
    try:
        test_api_key_precheck_with_secret()
        test_api_key_precheck_with_input()
        test_api_key_precheck_without_key()
        test_api_key_preference_order()
        test_api_key_fallback_to_input()
        test_workflow_yaml_structure()
        
        print("=== All Tests Passed ✓ ===\n")
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
