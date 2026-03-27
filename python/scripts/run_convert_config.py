#!/usr/bin/env python3
"""
Convert configuration between different formats (YAML, Perl, Python).

Usage:
    python3 run_convert_config.py <input_file> <output_file> [--format <format>]

Supported formats:
    - yaml: YAML format (default)
    - perl: HTS Perl Config.pm format
    - python: Python dict format

Examples:
    python3 run_convert_config.py config_nit_defaults.yaml config_output.pl --format perl
    python3 run_convert_config.py Config.pm.in config_output.yaml --format yaml
    python3 run_convert_config.py config_nit_defaults.yaml config_output.py --format python
"""

import sys
import os
import argparse
from yaml_config_loader import YAMLConfigLoader


def main():
    parser = argparse.ArgumentParser(description='Convert configuration formats')
    parser.add_argument('input_file', help='Input configuration file')
    parser.add_argument('output_file', help='Output configuration file')
    parser.add_argument('--format', choices=['yaml', 'perl', 'python'], default='yaml',
                       help='Output format (default: yaml)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    print(f"📂 Input file:   {args.input_file}")
    print(f"📝 Output file:  {args.output_file}")
    print(f"🔄 Format:       {args.format}\n")
    
    try:
        # Load configuration (auto-detect format from input_file extension)
        input_ext = os.path.splitext(args.input_file)[1].lower()
        
        print("📥 Loading configuration...")
        
        if input_ext == '.yaml' or input_ext == '.yml':
            config = YAMLConfigLoader.load(args.input_file)
        elif input_ext == '.pm' or input_ext == '.pl':
            print("   ⚠️  Perl format loading not yet implemented")
            print("   Please convert Perl config to YAML first using a tool like Config::IniFiles")
            sys.exit(1)
        elif input_ext == '.py':
            print("   ⚠️  Python format loading not yet implemented")
            sys.exit(1)
        else:
            print(f"❌ Error: Unknown input format: {input_ext}")
            sys.exit(1)
        
        print("✅ Configuration loaded\n")
        
        # Convert to target format
        print(f"🔄 Converting to {args.format} format...")
        
        if args.format == 'yaml':
            # Already in dict form, just save as YAML
            import yaml
            config_dict = {
                'project': vars(config.project) if hasattr(config, 'project') else {},
                'acoustic': vars(config.acoustic),
                'model': vars(config.model),
                'windows': {k: v for k, v in vars(config.windows).items() if not k.startswith('_')},
            }
            
            with open(args.output_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
        
        elif args.format == 'perl':
            # Convert to Perl Config.pm format
            output_lines = [
                "# Auto-generated Perl configuration",
                "# Generated from YAML config",
                "",
                "%Config = (",
            ]
            
            # Flatten config to perl format
            config_dict = {
                'SAMPFREQ': config.acoustic.sample_freq,
                'FRAMELEN': config.acoustic.frame_length,
                'FRAMESHIFT': config.acoustic.frame_shift,
                'MGCORDER': config.acoustic.mgc_order,
                'BAPORDER': config.acoustic.bap_order,
                'LF0ORDER': config.acoustic.lf0_order,
                'FREQWARP': config.acoustic.frequency_warp,
                'F0MIN': config.acoustic.f0_min,
                'F0MAX': config.acoustic.f0_max,
                'NSTATE': config.model.num_states,
                'NITER': getattr(config.model_training, 'niter', 5) if hasattr(config, 'model_training') else 5,
                'WFLOOR': getattr(config.model_training, 'wfloor', 5000) if hasattr(config, 'model_training') else 5000,
            }
            
            for key, value in config_dict.items():
                if isinstance(value, str):
                    output_lines.append(f"    {key} => '{value}',")
                else:
                    output_lines.append(f"    {key} => {value},")
            
            output_lines.append(");")
            output_lines.append("")
            
            with open(args.output_file, 'w') as f:
                f.write('\n'.join(output_lines))
        
        elif args.format == 'python':
            # Convert to Python dict format
            config_dict = {
                'acoustic': vars(config.acoustic),
                'model': vars(config.model),
            }
            
            output_lines = [
                "# Auto-generated Python configuration",
                "# Generated from YAML config",
                "",
                "CONFIG = {",
            ]
            
            import pprint
            output_lines.append(pprint.pformat(config_dict, indent=4))
            output_lines.append("}")
            
            with open(args.output_file, 'w') as f:
                f.write('\n'.join(output_lines))
        
        print(f"✅ Configuration converted\n")
        
        # Verify output file was created
        if os.path.exists(args.output_file):
            file_size = os.path.getsize(args.output_file)
            print("=" * 70)
            print("✅ CONVERSION COMPLETE")
            print("=" * 70)
            print(f"Output file:  {args.output_file} ({file_size} bytes)")
            print()
        else:
            print(f"❌ Error: Output file was not created")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
