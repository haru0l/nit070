#!/usr/bin/env python3
"""
Run a comprehensive test of all configuration and feature extraction capabilities.

Usage:
    python3 run_all_tests.py [audio_file]

Example:
    python3 run_all_tests.py ../../HTS-demo_NIT-SONG070-F001/data/raw/nitech_jp_song070_f001_003.wav
"""

import sys
import os
import subprocess


def run_script(script_name, args=None):
    """Run a Python script and return success/failure."""
    cmd = ['python3', script_name]
    if args:
        cmd.extend(args)
    
    print(f"▶️  Running: {' '.join(cmd)}")
    print("─" * 70)
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def main():
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    results = {}
    
    # Test 1: Load and inspect configuration
    print("\n📋 TEST 1: Load Configuration")
    print("=" * 70)
    results['load_config'] = run_script('run_load_config.py')
    
    # Test 2: Validate configuration
    print("\n\n✔️  TEST 2: Validate Configuration")
    print("=" * 70)
    results['validate_config'] = run_script('run_validate_config.py')
    
    # Test 3: Convert configuration (if supported)
    print("\n\n🔄 TEST 3: Convert Configuration")
    print("=" * 70)
    results['convert_config'] = run_script('run_convert_config.py', 
                                          ['config_nit_defaults.yaml', 
                                           '/tmp/config_test.pl',
                                           '--format', 'perl'])
    
    # Test 4: Extract features (if audio file provided)
    if audio_file:
        print("\n\n📊 TEST 4: Extract Features")
        print("=" * 70)
        if os.path.exists(audio_file):
            results['extract_features'] = run_script('run_extract_features.py', 
                                                     [audio_file])
        else:
            print(f"❌ Audio file not found: {audio_file}")
            results['extract_features'] = False
    else:
        print("\n\n⏭️  TEST 4: Extract Features")
        print("=" * 70)
        print("Skipped (no audio file provided)")
        print("Usage: python3 run_all_tests.py <audio_file>")
        results['extract_features'] = None
    
    # Summary
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total:   {len(results)} tests")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {skipped}")
    print()
    
    if failed > 0:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
