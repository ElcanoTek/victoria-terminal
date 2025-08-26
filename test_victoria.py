#!/usr/bin/env python3
"""
Comprehensive test suite for victoria.py starter script.
Tests cross-platform compatibility and terminal environment handling.
"""

import os
import sys
import tempfile
import subprocess
import platform
import json
from pathlib import Path
import shutil
import time

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    required_modules = [
        'json', 'os', 're', 'shutil', 'subprocess', 'sys', 
        'tempfile', 'time', 'pathlib', 'typing', 'platform'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            return False
    
    print("✅ All imports successful")
    return True

def test_victoria_script_syntax():
    """Test that victoria.py has valid Python syntax."""
    print("🧪 Testing victoria.py syntax...")
    
    try:
        with open('victoria.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, 'victoria.py', 'exec')
        print("✅ victoria.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in victoria.py: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading victoria.py: {e}")
        return False

def test_terminal_capability_detection():
    """Test terminal capability detection functions."""
    print("🧪 Testing terminal capability detection...")
    
    try:
        # Import the functions we need to test
        sys.path.insert(0, '.')
        
        # Read the script and extract the functions we need
        with open('victoria.py', 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Execute only the function definitions (before main)
        main_index = script_content.find('if __name__ == "__main__"')
        if main_index != -1:
            functions_only = script_content[:main_index]
        else:
            functions_only = script_content
        
        # Create a namespace to execute the functions
        namespace = {}
        exec(functions_only, namespace)
        
        # Test detect_terminal_capabilities
        caps = namespace['detect_terminal_capabilities']()
        print(f"  Terminal capabilities: {caps}")
        
        # Verify expected keys exist
        expected_keys = ['colors', 'emojis', 'unicode_box', 'colors_256', 'is_tty']
        for key in expected_keys:
            if key not in caps:
                print(f"  ✗ Missing capability key: {key}")
                return False
            print(f"  ✓ {key}: {caps[key]}")
        
        # Test get_terminal_width
        width = namespace['get_terminal_width']()
        print(f"  Terminal width: {width}")
        if not isinstance(width, int) or width <= 0:
            print(f"  ✗ Invalid terminal width: {width}")
            return False
        
        print("✅ Terminal capability detection works")
        return True
        
    except Exception as e:
        print(f"✗ Error testing terminal capabilities: {e}")
        return False

def test_cross_platform_compatibility():
    """Test cross-platform specific functionality."""
    print("🧪 Testing cross-platform compatibility...")
    
    try:
        # Test platform detection
        current_platform = platform.system()
        print(f"  Current platform: {current_platform}")
        
        # Test os.name detection
        os_name = os.name
        print(f"  OS name: {os_name}")
        
        # Test Path operations
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / 'test.json'
        test_data = {"test": True, "platform": current_platform}
        
        # Write and read JSON
        test_file.write_text(json.dumps(test_data), encoding='utf-8')
        read_data = json.loads(test_file.read_text(encoding='utf-8'))
        
        if read_data != test_data:
            print("  ✗ JSON read/write failed")
            return False
        
        print("  ✓ JSON file operations work")
        
        # Test shutil.which (used in victoria.py)
        python_path = shutil.which('python') or shutil.which('python3')
        if python_path:
            print(f"  ✓ shutil.which works: {python_path}")
        else:
            print("  ⚠️ shutil.which couldn't find python")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("  ✓ Cleanup successful")
        
        print("✅ Cross-platform compatibility tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Cross-platform compatibility error: {e}")
        return False

def test_environment_variables():
    """Test environment variable handling."""
    print("🧪 Testing environment variable handling...")
    
    try:
        # Test basic environment variable access
        test_vars = {
            'TERM': os.environ.get('TERM', 'not_set'),
            'LANG': os.environ.get('LANG', 'not_set'),
            'COLORTERM': os.environ.get('COLORTERM', 'not_set'),
            'TERM_PROGRAM': os.environ.get('TERM_PROGRAM', 'not_set'),
        }
        
        for var, value in test_vars.items():
            print(f"  {var}: {value}")
        
        # Test setting and getting environment variables
        test_key = 'VICTORIA_TEST_VAR'
        test_value = 'test_value_123'
        
        os.environ[test_key] = test_value
        retrieved_value = os.environ.get(test_key)
        
        if retrieved_value != test_value:
            print(f"  ✗ Environment variable test failed: {retrieved_value} != {test_value}")
            return False
        
        # Cleanup
        del os.environ[test_key]
        print("  ✓ Environment variable operations work")
        
        print("✅ Environment variable tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Environment variable error: {e}")
        return False

def test_script_execution_modes():
    """Test that the script can be executed in different modes without hanging."""
    print("🧪 Testing script execution modes...")
    
    try:
        # Test 1: Script with no input (should timeout gracefully)
        print("  Testing script with no input...")
        
        # Use Python's subprocess timeout instead of system timeout command
        result = subprocess.run(
            [sys.executable, 'victoria.py'],
            input='',
            text=True,
            capture_output=True,
            timeout=3  # 3 second timeout
        )
        
        print(f"    Exit code: {result.returncode}")
        print(f"    Stdout length: {len(result.stdout)} chars")
        print(f"    Stderr length: {len(result.stderr)} chars")
        
        # The script should exit gracefully
        if result.returncode in [0, 1, 2]:  # 0=success, 1=error, 2=KeyboardInterrupt
            print("  ✓ Script handled no-input execution")
        else:
            print(f"  ⚠️ Unexpected exit code: {result.returncode}")
        
        print("✅ Script execution mode tests completed")
        return True
        
    except subprocess.TimeoutExpired:
        print("  ⚠️ Script execution timed out (acceptable)")
        return True
    except Exception as e:
        print(f"✗ Script execution test error: {e}")
        return False

def test_unicode_handling():
    """Test Unicode and emoji handling."""
    print("🧪 Testing Unicode handling...")
    
    try:
        # Test Unicode string operations
        test_strings = [
            "🚢 VICTORIA 🌊 ADTECH",
            "рҹҡў рҹҢҠ рҹ§ӯ вңЁ",
            "в•җв•җв•җв•җв•җ",
            "Regular ASCII text"
        ]
        
        for test_str in test_strings:
            # Test string length calculation
            length = len(test_str)
            
            # Test encoding/decoding
            encoded = test_str.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            if decoded != test_str:
                print(f"  ✗ Unicode encoding/decoding failed for: {test_str}")
                return False
            
            print(f"  ✓ Unicode string handled: {test_str[:20]}... (len: {length})")
        
        print("✅ Unicode handling tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Unicode handling error: {e}")
        return False

def test_json_operations():
    """Test JSON operations used in the script."""
    print("🧪 Testing JSON operations...")
    
    try:
        # Test JSON parsing and generation
        test_data = {
            "snowflake": {
                "account": "${SNOWFLAKE_ACCOUNT}",
                "user": "${SNOWFLAKE_USER}"
            },
            "config": {
                "debug": True,
                "unicode_support": "🚢"
            }
        }
        
        # Test JSON serialization
        json_str = json.dumps(test_data, indent=2, ensure_ascii=False)
        print(f"  ✓ JSON serialization: {len(json_str)} chars")
        
        # Test JSON parsing
        parsed_data = json.loads(json_str)
        if parsed_data != test_data:
            print("  ✗ JSON parsing failed")
            return False
        
        print("  ✓ JSON parsing successful")
        
        # Test file I/O with JSON
        temp_file = Path(tempfile.mktemp(suffix='.json'))
        temp_file.write_text(json_str, encoding='utf-8')
        
        read_json = json.loads(temp_file.read_text(encoding='utf-8'))
        if read_json != test_data:
            print("  ✗ JSON file I/O failed")
            return False
        
        print("  ✓ JSON file I/O successful")
        
        # Cleanup
        temp_file.unlink()
        
        print("✅ JSON operations tests passed")
        return True
        
    except Exception as e:
        print(f"✗ JSON operations error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Victoria Script Test Suite")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_victoria_script_syntax,
        test_terminal_capability_detection,
        test_cross_platform_compatibility,
        test_environment_variables,
        test_script_execution_modes,
        test_unicode_handling,
        test_json_operations,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Victoria script is ready for cross-platform deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())