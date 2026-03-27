# YAML Configuration Guide

## Overview

The HTS training system now supports **YAML-based configuration** in addition to Perl-based configs. This provides a more modern, human-readable alternative while maintaining full compatibility with the original Perl Config.pm approach.

## Key Advantages of YAML Configuration

- **Human-readable**: Clear hierarchical structure without Perl syntax
- **Easy to edit**: No special escaping or weird syntax
- **Version controllable**: Works well with git and diff tools
- **Validated**: Built-in validation for common configuration errors
- **Convertible**: Tools to convert between Perl, Python, and YAML formats
- **Type-safe**: Python dataclasses ensure type safety

## Quick Start

### Dependencies

```bash
# Install required packages
pip install pyyaml pysptk pylstraight scipy
```

### Load NIT Defaults

```python
from yaml_config_loader import YAMLConfigLoader, print_config_summary

# Load the NIT defaults configuration
config = YAMLConfigLoader.load('config_nit_defaults.yaml')

# Print a summary
print_config_summary(config)

# Validate the configuration
if YAMLConfigLoader.validate(config):
    print("✓ Configuration is valid!")
```

### Command Line

```bash
# View configuration summary
python3 scripts/yaml_config_loader.py scripts/config_nit_defaults.yaml

# Convert from Perl to YAML
python3 scripts/config_converter.py Config.pm.in -o config.yaml -f yaml

# Convert from YAML to Perl
python3 scripts/config_converter.py config.yaml -o Config.pm -f perl

# Convert from YAML to Python
python3 scripts/config_converter.py config.yaml -o config.py -f python
```

## Configuration Structure

### Project Section
```yaml
project:
  name: "HTS-demo_NIT-SONG070-F001"
  version: "2.3"
  dataset: "nitech_jp_song070"
  speaker: "f001"
  speaker_language: "Japanese"
```

### Acoustic Features Section
Controls all audio analysis parameters:

```yaml
acoustic:
  sample_freq: 48000          # Sampling frequency (Hz)
  frame_length: 1200          # Frame length (samples) = 25ms
  frame_shift: 240            # Frame shift (samples) = 5ms
  fft_length: 2048            # FFT length
  window_type: 1              # 0: Blackman, 1: Hamming, 2: Hanning
  frequency_warp: 0.55        # Frequency warping (α)
  gamma: 0                    # 0: mel-cepstral, >0: mel-generalized
  mgc_order: 34               # MGC order (35 dims with c0)
  bap_order: 24               # BAP order (25 dims with c0)
  use_log_gain: true          # Use logarithmic gain
  lower_f0: 195               # Lower F0 limit (Hz)
  upper_f0: 740               # Upper F0 limit (Hz)
  use_straight: false         # Use STRAIGHT vocoder
```

### Model Structure Section
Defines HMM model architecture:

```yaml
model:
  num_states: 5               # HMM states per phone
  component_types: ['mgc', 'lf0', 'bap']
  duration_types: ['dur']
  
  # Feature dimensions
  orders:
    mgc: 35                   # MGC order + 1
    lf0: 1
    bap: 25                   # BAP order + 1
    dur: 5
  
  # Stream boundaries
  stream_boundaries:
    mgc_start: 0
    mgc_end: 34
    lf0_start: 35
    lf0_end: 35
    bap_start: 36
    bap_end: 60
  
  # Stream weights
  stream_weights:
    mgc: 1.0
    lf0: 1.0
    bap: 1.0
  
  # MSD (Multi-Space Probability Distribution)
  msd_info:
    mgc: 0                    # 0: non-MSD, 1: MSD
    lf0: 1
    bap: 0
```

### Training Parameters Section
Controls HMM re-estimation and model training:

```yaml
training:
  # Variance floors for each stream
  variance_floors:
    mgc: 0.01
    lf0: 0.01
    bap: 0.01
    dur: 0.01
  
  # Minimum likelihood gain for tree clustering
  threshold:
    mgc: 000
    lf0: 000
    bap: 000
    dur: 000
  
  # Minimum occupancy counts
  min_occupancy:
    mgc: 10.0
    lf0: 10.0
    bap: 10.0
    dur: 5.0
```

### Directories Section
Specifies file paths:

```yaml
directories:
  raw: "data/raw"             # Raw audio
  labels:
    full: "data/labels/full"
    mono: "data/labels/mono"
    gen: "data/labels/gen"
  features:
    mgc: "data/mgc"
    lf0: "data/lf0"
    bap: "data/bap"
    cmp: "data/cmp"
  lists: "data/lists"
```

## NIT Default Values

The `config_nit_defaults.yaml` file contains the standard NIT parameters:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Sample Rate | 48000 Hz | Standard for high-quality speech |
| Frame Length | 1200 samples | 25ms at 48kHz |
| Frame Shift | 240 samples | 5ms at 48kHz |
| FFT Length | 2048 | Sufficient for 48kHz analysis |
| MGC Order | 34 | 35 coefficients with c0 |
| BAP Order | 24 | 25 coefficients with c0 |
| Frequency Warp | 0.55 | For 48kHz sampling |
| F0 Range | 195-740 Hz | For female speakers |
| HMM States | 5 | Per phoneme (excluding start/end) |
| Window Type | 1 (Hamming) | Standard windowing |

## Customization

### Modify for Different Sampling Rate

If you need to use 16kHz instead of 48kHz:

```yaml
acoustic:
  sample_freq: 16000
  frame_length: 400           # 25ms
  frame_shift: 80             # 5ms
  frequency_warp: 0.42        # For 16kHz
  lower_f0: 70                # Adjust for male speakers
  upper_f0: 250
```

### Change MGC Order

For lower dimensionality (faster training):

```yaml
acoustic:
  mgc_order: 24               # Instead of 34

# Update model orders
model:
  orders:
    mgc: 25                   # mgc_order + 1
```

### Add/Remove BAP Features

To disable BAP extraction:

```yaml
model:
  component_types: ['mgc', 'lf0']  # Remove 'bap'
  orders:
    mgc: 35
    lf0: 1
    dur: 5                         # Remove bap dim
```

## Python Usage

### Load Configuration

```python
from yaml_config_loader import YAMLConfigLoader, HTSConfig

# Load from YAML file
config = YAMLConfigLoader.load('config_nit_defaults.yaml')

# Access parameters
print(f"Sample Rate: {config.acoustic.sample_freq} Hz")
print(f"MGC Order: {config.acoustic.mgc_order}")
print(f"Frame Shift: {config.acoustic.frame_shift} samples")
```

### Create Configuration Programmatically

```python
from yaml_config_loader import HTSConfig, AcousticConfig, ModelConfig

# Create custom acoustic config
acoustic = AcousticConfig(
    sample_freq=16000,
    frame_length=400,
    frame_shift=80,
    frequency_warp=0.42,
    mgc_order=24,
    bap_order=5
)

# Create full config
config = HTSConfig(
    dataset="my_dataset",
    speaker="my_speaker",
    acoustic=acoustic
)

# Save to YAML
config.to_yaml('my_config.yaml')
```

### Validate Configuration

```python
from yaml_config_loader import YAMLConfigLoader

config = YAMLConfigLoader.load('config.yaml')

if YAMLConfigLoader.validate(config):
    print("✓ Configuration is valid")
else:
    print("✗ Configuration has errors")
```

## Format Conversion

### Perl to YAML

```bash
python3 scripts/config_converter.py Config.pm.in -o config.yaml -f yaml
```

### YAML to Perl

```bash
python3 scripts/config_converter.py config.yaml -o Config.pm -f perl
```

### YAML to Python Dictionary

```bash
python3 scripts/config_converter.py config.yaml -o config.py -f python
```

Then load as:

```python
from config import config
```

## Validation Rules

The YAML loader validates:

1. **Sample Rate**: Must be one of [8000, 10000, 12000, 16000, 22050, 32000, 44100, 48000]
2. **Frequency Warp**: Must be in the range [0, 1)
3. **MGC Order**: Must be greater than 0
4. **F0 Range**: lower_f0 must be less than upper_f0
5. **Frame Parameters**: Logical consistency checks

## Backward Compatibility

The system remains fully compatible with Perl-based Config.pm files. You can:

1. Continue using Perl configs without any changes
2. Convert existing Perl configs to YAML using the converter
3. Mix Perl and YAML configs in the same project

## Files

- `config_nit_defaults.yaml` - NIT default configuration
- `yaml_config_loader.py` - Main YAML configuration loader
- `config_converter.py` - Format conversion utility
- `config_loader.py` - Perl/Python config loader (original)

## References

- YAML Specification: https://yaml.org/
- HTS Official Site: http://hts.sp.nitech.ac.jp/
- HTS Working Group: hts-users@sp.nitech.ac.jp

