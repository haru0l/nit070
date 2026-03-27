#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Format Conversion Utility

Convert between Perl Config.pm, Python dict, and YAML configuration formats
for HTS training.
"""

import yaml
import json
import argparse
from pathlib import Path
from yaml_config_loader import YAMLConfigLoader, HTSConfig
from config_loader import ConfigLoader


def perl_to_yaml(perl_file: str, yaml_output: str):
    """Convert Perl Config.pm to YAML"""
    print(f"Converting Perl config: {perl_file} → {yaml_output}")
    
    loader = ConfigLoader()
    config_dict = loader.load_from_perl(perl_file)
    
    # Map Perl config keys to YAML structure
    yaml_config = {
        'project': {
            'name': config_dict.get('PRJNAME', 'HTS-demo'),
            'dataset': config_dict.get('dset', 'nitech_jp_song070'),
            'speaker': config_dict.get('spkr', 'f001'),
        },
        'acoustic': {
            'sample_freq': int(config_dict.get('SAMPFREQ', 48000)),
            'frame_length': int(config_dict.get('FRAMELEN', 1200)),
            'frame_shift': int(config_dict.get('FRAMESHIFT', 240)),
            'fft_length': int(config_dict.get('FFTLEN', 2048)),
            'window_type': int(config_dict.get('WINDOWTYPE', 1)),
            'frequency_warp': float(config_dict.get('FREQWARP', 0.55)),
            'gamma': int(config_dict.get('GAMMA', 0)),
            'mgc_order': int(config_dict.get('MGCORDER', 34)),
            'bap_order': int(config_dict.get('BAPORDER', 24)),
            'lower_f0': int(config_dict.get('LOWERF0', 195)),
            'upper_f0': int(config_dict.get('UPPERF0', 740)),
            'use_straight': bool(int(config_dict.get('USESTRAIGHT', 0))),
        },
    }
    
    with open(yaml_output, 'w') as f:
        yaml.dump(yaml_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Converted to YAML: {yaml_output}")


def yaml_to_python(yaml_file: str, python_output: str):
    """Convert YAML to Python dictionary format"""
    print(f"Converting YAML config: {yaml_file} → {python_output}")
    
    config = YAMLConfigLoader.load(yaml_file)
    config_dict = config.to_dict()
    
    with open(python_output, 'w') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# Auto-generated HTS configuration from YAML\n\n")
        f.write(f"config = {json.dumps(config_dict, indent=4)}\n")
    
    print(f"✓ Converted to Python: {python_output}")


def yaml_to_perl(yaml_file: str, perl_output: str):
    """Convert YAML to Perl Config.pm format"""
    print(f"Converting YAML config: {yaml_file} → {perl_output}")
    
    config = YAMLConfigLoader.load(yaml_file)
    
    with open(perl_output, 'w') as f:
        f.write("#!/usr/bin/perl\n")
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# Auto-generated HTS configuration from YAML\n\n")
        
        # Write scalars
        f.write("# Project settings\n")
        f.write(f"$prjdir = '{config.project_name}';\n")
        f.write(f"$dset = '{config.dataset}';\n")
        f.write(f"$spkr = '{config.speaker}';\n\n")
        
        # Write acoustic parameters
        f.write("# Acoustic feature parameters\n")
        f.write(f"$SAMPFREQ = {config.acoustic.sample_freq};\n")
        f.write(f"$FRAMELEN = {config.acoustic.frame_length};\n")
        f.write(f"$FRAMESHIFT = {config.acoustic.frame_shift};\n")
        f.write(f"$FFTLEN = {config.acoustic.fft_length};\n")
        f.write(f"$WINDOWTYPE = {config.acoustic.window_type};\n")
        f.write(f"$FREQWARP = {config.acoustic.frequency_warp};\n")
        f.write(f"$GAMMA = {config.acoustic.gamma};\n")
        f.write(f"$MGCORDER = {config.acoustic.mgc_order};\n")
        f.write(f"$BAPORDER = {config.acoustic.bap_order};\n")
        f.write(f"$LOWERF0 = {config.acoustic.lower_f0};\n")
        f.write(f"$UPPERF0 = {config.acoustic.upper_f0};\n")
        f.write(f"$USESTRAIGHT = {1 if config.acoustic.use_straight else 0};\n\n")
        
        # Write model parameters
        f.write("# Model structure\n")
        f.write(f"$NSTATE = {config.model.num_states};\n")
        
        # Write component arrays
        cmp_str = "', '".join(config.model.component_types)
        dur_str = "', '".join(config.model.duration_types)
        f.write(f"@cmp = ('{cmp_str}');\n")
        f.write(f"@dur = ('{dur_str}');\n\n")
        
        # Write stream info
        f.write("# Stream information\n")
        f.write("%strb = (\n")
        for k, v in config.model.stream_boundaries.items():
            if 'start' in k:
                component = k.replace('_start', '')
                f.write(f"    '{component}' => {v},\n")
        f.write(");\n\n")
        
        f.write("%stre = (\n")
        for k, v in config.model.stream_boundaries.items():
            if 'end' in k:
                component = k.replace('_end', '')
                f.write(f"    '{component}' => {v},\n")
        f.write(");\n\n")
        
        # Write order info
        f.write("%ordr = (\n")
        for component, order in config.model.orders.items():
            f.write(f"    '{component}' => {order},\n")
        f.write(");\n\n")
    
    print(f"✓ Converted to Perl: {perl_output}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert between HTS configuration formats (Perl, Python, YAML)'
    )
    parser.add_argument('input_file', help='Input configuration file')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('-f', '--format', choices=['yaml', 'python', 'perl'],
                       help='Output format (auto-detected from extension if not specified)')
    
    args = parser.parse_args()
    
    # Detect input format from extension
    input_path = Path(args.input_file)
    input_ext = input_path.suffix.lower()
    
    if not input_path.exists():
        print(f"✗ Input file not found: {args.input_file}")
        return 1
    
    # Detect output format
    output_format = args.format
    if not output_format:
        output_path = Path(args.output)
        output_ext = output_path.suffix.lower()
        if output_ext == '.yaml' or output_ext == '.yml':
            output_format = 'yaml'
        elif output_ext == '.py':
            output_format = 'python'
        elif output_ext == '.pm':
            output_format = 'perl'
        else:
            print(f"✗ Cannot determine output format from extension: {args.output}")
            return 1
    
    try:
        if input_ext in ['.pm', '.pl']:
            # Convert from Perl
            if output_format == 'yaml':
                perl_to_yaml(args.input_file, args.output)
            elif output_format == 'python':
                perl_to_yaml(args.input_file, 'temp.yaml')
                yaml_to_python('temp.yaml', args.output)
            else:
                print("✗ Unsupported conversion")
                return 1
        
        elif input_ext in ['.yaml', '.yml']:
            # Convert from YAML
            if output_format == 'python':
                yaml_to_python(args.input_file, args.output)
            elif output_format == 'perl':
                yaml_to_perl(args.input_file, args.output)
            else:
                print("✗ Unsupported conversion")
                return 1
        
        elif input_ext == '.py':
            print("✗ Python to other formats not yet supported")
            return 1
        
        else:
            print(f"✗ Unknown input format: {input_ext}")
            return 1
        
        print("✓ Conversion complete!")
        return 0
    
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
