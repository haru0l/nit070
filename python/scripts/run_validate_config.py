#!/usr/bin/env python3
"""
Validate configuration file against constraints.

Usage:
    python3 run_validate_config.py [config_file]

Example:
    python3 run_validate_config.py config_nit_defaults.yaml
"""

import sys
import os
from yaml_config_loader import YAMLConfigLoader


def validate_config_detailed(config):
    """Perform detailed validation with specific checks."""
    errors = []
    warnings = []
    
    # Acoustic parameter validation
    if config.acoustic.sample_freq not in [16000, 48000]:
        warnings.append(f"Unusual sample rate: {config.acoustic.sample_freq} Hz (typical: 16000 or 48000)")
    
    if not (0.0 < config.acoustic.frequency_warp < 1.0):
        errors.append(f"Frequency warp must be in (0, 1), got: {config.acoustic.frequency_warp}")
    
    if config.acoustic.lower_f0 >= config.acoustic.upper_f0:
        errors.append(f"F0 min ({config.acoustic.lower_f0}) must be less than F0 max ({config.acoustic.upper_f0})")
    
    if config.acoustic.mgc_order < 10 or config.acoustic.mgc_order > 50:
        warnings.append(f"MGC order {config.acoustic.mgc_order} is outside typical range [10-50]")
    
    if config.acoustic.bap_order < 5 or config.acoustic.bap_order > 30:
        warnings.append(f"BAP order {config.acoustic.bap_order} is outside typical range [5-30]")
    
    # Model structure validation
    if config.model.num_states < 2 or config.model.num_states > 10:
        warnings.append(f"Number of HMM states {config.model.num_states} is outside typical range [2-10]")
    
    # Check stream consistency
    expected_mgc = config.acoustic.mgc_order + 1
    expected_bap = config.acoustic.bap_order + 1
    expected_lf0 = 1
    
    if config.model.orders['mgc'] != expected_mgc:
        errors.append(f"Model MGC order {config.model.orders['mgc']} should be {expected_mgc} (acoustic order + 1)")
    
    if config.model.orders['bap'] != expected_bap:
        errors.append(f"Model BAP order {config.model.orders['bap']} should be {expected_bap} (acoustic order + 1)")
    
    # Stream weights validation
    if not all(0.0 < w <= 1.0 for w in config.model.stream_weights.values()):
        errors.append(f"Stream weights must be in (0, 1], got: {config.model.stream_weights}")
    
    # MSD flags validation
    if not all(flag in [0, 1] for flag in config.model.msd_info.values()):
        errors.append(f"MSD flags must be 0 or 1, got: {config.model.msd_info}")
    
    # Training parameters validation
    if hasattr(config, 'model_training') and config.model_training:
        if config.model_training.niter < 1:
            errors.append(f"Number of training iterations must be >= 1, got {config.model_training.niter}")
        
        if config.model_training.wfloor <= 0:
            errors.append(f"Weight floor must be > 0, got {config.model_training.wfloor}")
        
        if config.model_training.mindur < 2:
            warnings.append(f"Minimum duration {config.model_training.mindur} may be too small (typical: >= 2)")
    
    # Parameter generation validation
    if hasattr(config, 'parameter_generation') and config.parameter_generation:
        if config.parameter_generation.pgtype not in [0, 1]:
            errors.append(f"PGTYPE must be 0 or 1, got {config.parameter_generation.pgtype}")
        
        if config.parameter_generation.maxgviter < 1:
            errors.append(f"Max GV iterations must be >= 1, got {config.parameter_generation.maxgviter}")
        
        if config.parameter_generation.use_gv not in [0, 1]:
            errors.append(f"USE_GV must be 0 or 1, got {config.parameter_generation.use_gv}")
    
    return errors, warnings


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config_nit_defaults.yaml'
    
    if not os.path.exists(config_file):
        print(f"❌ Error: Config file not found: {config_file}")
        sys.exit(1)
    
    print(f"📂 Validating configuration: {config_file}\n")
    
    try:
        # Load configuration
        config = YAMLConfigLoader.load(config_file)
        print("✅ Configuration loaded successfully\n")
        
        # Standard validation
        is_valid = YAMLConfigLoader.validate(config)
        validation_errors = [] if is_valid else ["Configuration validation failed"]
        
        # Detailed validation
        detailed_errors, warnings = validate_config_detailed(config)
        
        # Combine all errors
        all_errors = validation_errors + detailed_errors
        
        # Display results
        print("=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)
        print()
        
        if all_errors:
            print("❌ ERRORS FOUND:")
            for i, error in enumerate(all_errors, 1):
                print(f"  {i}. {error}")
            print()
        
        if warnings:
            print("⚠️  WARNINGS:")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
            print()
        
        # Summary
        print("=" * 70)
        if all_errors:
            print("❌ VALIDATION FAILED")
            print(f"   Errors:   {len(all_errors)}")
            print(f"   Warnings: {len(warnings)}")
            sys.exit(1)
        elif warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            print(f"   Warnings: {len(warnings)}")
        else:
            print("✅ VALIDATION PASSED")
        
        print("=" * 70)
        print()
        
        # Print configuration summary
        print("CONFIGURATION SUMMARY:")
        print(f"  Project:          {config.project_name if hasattr(config, 'project_name') else 'N/A'}")
        print(f"  Sample Rate:      {config.acoustic.sample_freq} Hz")
        print(f"  Frame Shift:      {config.acoustic.frame_shift} samples")
        print(f"  MGC Order:        {config.acoustic.mgc_order}")
        print(f"  BAP Order:        {config.acoustic.bap_order}")
        print(f"  HMM States:       {config.model.num_states}")
        print(f"  Frequency Warp:   {config.acoustic.frequency_warp}")
        print(f"  F0 Range:         {config.acoustic.lower_f0} - {config.acoustic.upper_f0} Hz")
        print()
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
