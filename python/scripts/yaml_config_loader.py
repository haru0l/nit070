#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML Configuration Loader for HTS Training

This module provides utilities for loading and managing HTS training configuration
from YAML files, replacing the Perl-based Config.pm approach.
"""

import yaml
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any


@dataclass
class AcousticConfig:
    """Acoustic feature extraction parameters"""
    sample_freq: int = 48000
    frame_length: int = 1200
    frame_shift: int = 240
    fft_length: int = 2048
    window_type: int = 1             # 0: Blackman, 1: Hamming, 2: Hanning
    normalize: int = 1               # 0: none, 1: by power, 2: by magnitude
    frequency_warp: float = 0.55
    gamma: int = 0                   # 0: mel-cepstral, >0: mel-generalized
    mgc_order: int = 34
    bap_order: int = 24
    use_log_gain: bool = True
    lower_f0: int = 195
    upper_f0: int = 740
    use_straight: bool = False       # Use pylstraight (Python) for BAP extraction


@dataclass
class ModelConfig:
    """HMM model structure parameters"""
    num_states: int = 5
    component_types: List[str] = field(default_factory=lambda: ['mgc', 'lf0', 'bap'])
    duration_types: List[str] = field(default_factory=lambda: ['dur'])
    orders: Dict[str, int] = field(default_factory=lambda: {
        'mgc': 35, 'lf0': 1, 'bap': 25, 'dur': 5
    })
    stream_boundaries: Dict[str, int] = field(default_factory=lambda: {
        'mgc_start': 0, 'mgc_end': 34,
        'lf0_start': 35, 'lf0_end': 35,
        'bap_start': 36, 'bap_end': 60
    })
    stream_weights: Dict[str, float] = field(default_factory=lambda: {
        'mgc': 1.0, 'lf0': 1.0, 'bap': 1.0
    })
    msd_info: Dict[str, int] = field(default_factory=lambda: {
        'mgc': 0, 'lf0': 1, 'bap': 0
    })


@dataclass
class HTSConfig:
    """Complete HTS configuration"""
    project_name: str = "HTS-demo_NIT-SONG070-F001"
    version: str = "2.3"
    dataset: str = "nitech_jp_song070"
    speaker: str = "f001"
    questions_set: str = "001"
    questions_version: str = "001"
    
    acoustic: AcousticConfig = field(default_factory=AcousticConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    
    # Directory configuration
    raw_dir: str = "data/raw"
    label_dir: str = "data/labels"
    mgc_dir: str = "data/mgc"
    lf0_dir: str = "data/lf0"
    bap_dir: str = "data/bap"
    cmp_dir: str = "data/cmp"
    list_dir: str = "data/lists"
    
    # Training parameters
    variance_floors: Dict[str, float] = field(default_factory=lambda: {
        'mgc': 0.01, 'lf0': 0.01, 'bap': 0.01, 'dur': 0.01
    })
    
    # Postfilter parameters
    pstfilter_mcp: float = 1.4
    pstfilter_lsp: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self, filepath: str, indent: int = 2):
        """Export to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=indent)
    
    def to_yaml(self, filepath: str):
        """Export to YAML"""
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)


class YAMLConfigLoader:
    """Load HTS configuration from YAML files"""
    
    @staticmethod
    def load(config_path: str) -> HTSConfig:
        """Load configuration from YAML file"""
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return YAMLConfigLoader.build_config(config_dict)
    
    @staticmethod
    def build_config(config_dict: Dict[str, Any]) -> HTSConfig:
        """Build HTSConfig from dictionary"""
        # Extract acoustic parameters
        acoustic_dict = config_dict.get('acoustic', {})
        acoustic = AcousticConfig(
            sample_freq=acoustic_dict.get('sample_freq', 48000),
            frame_length=acoustic_dict.get('frame_length', 1200),
            frame_shift=acoustic_dict.get('frame_shift', 240),
            fft_length=acoustic_dict.get('fft_length', 2048),
            window_type=acoustic_dict.get('window_type', 1),
            normalize=acoustic_dict.get('normalize', 1),
            frequency_warp=acoustic_dict.get('frequency_warp', 0.55),
            gamma=acoustic_dict.get('gamma', 0),
            mgc_order=acoustic_dict.get('mgc_order', 34),
            bap_order=acoustic_dict.get('bap_order', 24),
            use_log_gain=acoustic_dict.get('use_log_gain', True),
            lower_f0=acoustic_dict.get('lower_f0', 195),
            upper_f0=acoustic_dict.get('upper_f0', 740),
            use_straight=acoustic_dict.get('use_straight', False),
        )
        
        # Extract model parameters
        model_dict = config_dict.get('model', {})
        model = ModelConfig(
            num_states=model_dict.get('num_states', 5),
            component_types=model_dict.get('component_types', ['mgc', 'lf0', 'bap']),
            duration_types=model_dict.get('duration_types', ['dur']),
            orders=model_dict.get('orders', {'mgc': 35, 'lf0': 1, 'bap': 25, 'dur': 5}),
            stream_boundaries=model_dict.get('stream_boundaries', {
                'mgc_start': 0, 'mgc_end': 34,
                'lf0_start': 35, 'lf0_end': 35,
                'bap_start': 36, 'bap_end': 60
            }),
            stream_weights=model_dict.get('stream_weights', {'mgc': 1.0, 'lf0': 1.0, 'bap': 1.0}),
            msd_info=model_dict.get('msd_info', {'mgc': 0, 'lf0': 1, 'bap': 0}),
        )
        
        # Extract project parameters
        project_dict = config_dict.get('project', {})
        dirs_dict = config_dict.get('directories', {})
        
        return HTSConfig(
            project_name=project_dict.get('name', 'HTS-demo_NIT-SONG070-F001'),
            version=project_dict.get('version', '2.3'),
            dataset=project_dict.get('dataset', 'nitech_jp_song070'),
            speaker=project_dict.get('speaker', 'f001'),
            questions_set=config_dict.get('questions', {}).get('set', '001'),
            questions_version=config_dict.get('questions', {}).get('version', '001'),
            acoustic=acoustic,
            model=model,
            raw_dir=dirs_dict.get('raw', 'data/raw'),
            label_dir=dirs_dict.get('labels', {}).get('full', 'data/labels/full'),
            mgc_dir=dirs_dict.get('features', {}).get('mgc', 'data/mgc'),
            lf0_dir=dirs_dict.get('features', {}).get('lf0', 'data/lf0'),
            bap_dir=dirs_dict.get('features', {}).get('bap', 'data/bap'),
            cmp_dir=dirs_dict.get('features', {}).get('cmp', 'data/cmp'),
            list_dir=dirs_dict.get('lists', 'data/lists'),
            variance_floors=config_dict.get('training', {}).get('variance_floors', {
                'mgc': 0.01, 'lf0': 0.01, 'bap': 0.01, 'dur': 0.01
            }),
            pstfilter_mcp=config_dict.get('postfilter', {}).get('factor_mcp', 1.4),
            pstfilter_lsp=config_dict.get('postfilter', {}).get('factor_lsp', 0.7),
        )
    
    @staticmethod
    def validate(config: HTSConfig) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check sampling rate
        valid_sr = [8000, 10000, 12000, 16000, 22050, 32000, 44100, 48000]
        if config.acoustic.sample_freq not in valid_sr:
            errors.append(f"Invalid sample_freq: {config.acoustic.sample_freq}. Must be one of {valid_sr}")
        
        # Check frequency warping is in [0, 1)
        if not 0 <= config.acoustic.frequency_warp < 1:
            errors.append(f"frequency_warp must be in [0, 1), got {config.acoustic.frequency_warp}")
        
        # Check MGC order > 0
        if config.acoustic.mgc_order <= 0:
            errors.append(f"mgc_order must be > 0, got {config.acoustic.mgc_order}")
        
        # Check F0 range
        if config.acoustic.lower_f0 >= config.acoustic.upper_f0:
            errors.append(f"lower_f0 ({config.acoustic.lower_f0}) must be < upper_f0 ({config.acoustic.upper_f0})")
        
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return False
        
        return True


def print_config_summary(config: HTSConfig):
    """Print configuration summary"""
    print("=" * 60)
    print(f"HTS Configuration: {config.project_name} v{config.version}")
    print("=" * 60)
    print(f"\nProject:")
    print(f"  Dataset: {config.dataset}")
    print(f"  Speaker: {config.speaker}")
    
    print(f"\nAcoustic Features:")
    print(f"  Sample Rate: {config.acoustic.sample_freq} Hz")
    print(f"  Frame Length: {config.acoustic.frame_length} samples ({config.acoustic.frame_length*1000/config.acoustic.sample_freq:.1f}ms)")
    print(f"  Frame Shift: {config.acoustic.frame_shift} samples ({config.acoustic.frame_shift*1000/config.acoustic.sample_freq:.1f}ms)")
    print(f"  FFT Length: {config.acoustic.fft_length}")
    print(f"  MGC Order: {config.acoustic.mgc_order}")
    print(f"  BAP Order: {config.acoustic.bap_order}")
    print(f"  Freq. Warp: {config.acoustic.frequency_warp}")
    print(f"  F0 Range: {config.acoustic.lower_f0}-{config.acoustic.upper_f0} Hz")
    
    print(f"\nModel Structure:")
    print(f"  HMM States: {config.model.num_states}")
    print(f"  Components: {', '.join(config.model.component_types)}")
    print(f"  Stream Orders: MGC={config.model.orders['mgc']}, LF0={config.model.orders['lf0']}, BAP={config.model.orders['bap']}")
    print("=" * 60)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: config_loader.py <config.yaml>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    config = YAMLConfigLoader.load(config_file)
    
    if YAMLConfigLoader.validate(config):
        print_config_summary(config)
        print("\n✓ Configuration is valid!")
    else:
        print("\n✗ Configuration has errors!")
        sys.exit(1)
