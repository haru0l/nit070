#!/usr/bin/env python3
"""
Load and display YAML configuration parameters.

Usage:
    python3 run_load_config.py [config_file]

Example:
    python3 run_load_config.py config_nit_defaults.yaml
"""

import sys
import os
from yaml_config_loader import YAMLConfigLoader


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config_nit_defaults.yaml'
    
    if not os.path.exists(config_file):
        print(f"❌ Error: Config file not found: {config_file}")
        sys.exit(1)
    
    print(f"📂 Loading configuration from: {config_file}\n")
    
    try:
        config = YAMLConfigLoader.load(config_file)
        print("✅ Configuration loaded successfully!\n")
        
        # Display key acoustic parameters
        print("=" * 60)
        print("ACOUSTIC PARAMETERS")
        print("=" * 60)
        print(f"  Sample Rate:          {config.acoustic.sample_freq} Hz")
        print(f"  Frame Length:         {config.acoustic.frame_length} samples")
        print(f"  Frame Shift:          {config.acoustic.frame_shift} samples")
        print(f"  MGC Order:            {config.acoustic.mgc_order}")
        print(f"  BAP Order:            {config.acoustic.bap_order}")
        print(f"  LF0 Order:            1 (fixed)")
        print(f"  Frequency Warp Alpha: {config.acoustic.frequency_warp}")
        print(f"  F0 Min:               {config.acoustic.lower_f0} Hz")
        print(f"  F0 Max:               {config.acoustic.upper_f0} Hz")
        
        # Display model parameters
        print("\n" + "=" * 60)
        print("MODEL PARAMETERS")
        print("=" * 60)
        print(f"  Number of HMM States: {config.model.num_states}")
        print(f"  MGC Order (model):    {config.model.orders['mgc']}")
        print(f"  LF0 Order (model):    {config.model.orders['lf0']}")
        print(f"  BAP Order (model):    {config.model.orders['bap']}")
        print(f"  Stream Weights:       MGC={config.model.stream_weights['mgc']}, "
              f"LF0={config.model.stream_weights['lf0']}, BAP={config.model.stream_weights['bap']}")
        print(f"  MSD Flags:            MGC={config.model.msd_info['mgc']}, "
              f"LF0={config.model.msd_info['lf0']}, BAP={config.model.msd_info['bap']}")
        
        # Display training parameters
        if hasattr(config, 'model_training') and config.model_training:
            print("\n" + "=" * 60)
            print("MODEL TRAINING PARAMETERS")
            print("=" * 60)
            print(f"  Number of Iterations: {config.model_training.niter}")
            print(f"  Weight Floor:         {config.model_training.wfloor}")
            print(f"  DAEM:                 {config.model_training.daem}")
            print(f"  Min Duration:         {config.model_training.mindur}")
        
        # Display parameter generation parameters
        if hasattr(config, 'parameter_generation') and config.parameter_generation:
            print("\n" + "=" * 60)
            print("PARAMETER GENERATION SETTINGS")
            print("=" * 60)
            print(f"  PG Type:              {config.parameter_generation.pgtype}")
            print(f"  Use Global Variance:  {config.parameter_generation.use_gv}")
            print(f"  Max GV Iterations:    {config.parameter_generation.maxgviter}")
            print(f"  Optimization Method:  {config.parameter_generation.optkind}")
        
        print("\n" + "=" * 60)
        print("✅ All parameters loaded successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
