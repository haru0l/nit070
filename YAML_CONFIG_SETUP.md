# YAML Configuration - Quick Summary

## What Was Created

Replaced the default HTS configuration with **NIT Song 070 defaults** and converted everything to **YAML format** for modern, human-readable configuration management.

## Files Created

### 1. **config_nit_defaults.yaml** ⭐ 
The main YAML configuration file with all NIT defaults:
- Sample rate: 48000 Hz
- Frame length: 1200 (25ms)
- Frame shift: 240 (5ms)
- MGC order: 34
- BAP order: 24
- F0 range: 195-740 Hz
- STRAIGHT analysis: Uses `pylstraight` Python package (not MATLAB)
- And all other standard HTS parameters

### 2. **yaml_config_loader.py**
Python module to load and manage YAML configurations:
```python
from yaml_config_loader import YAMLConfigLoader, print_config_summary

config = YAMLConfigLoader.load('config_nit_defaults.yaml')
print_config_summary(config)
YAMLConfigLoader.validate(config)
```

### 3. **config_converter.py**
Convert between Perl, Python, and YAML formats:
```bash
# Perl → YAML
python3 config_converter.py Config.pm.in -o config.yaml -f yaml

# YAML → Perl
python3 config_converter.py config.yaml -o Config.pm -f perl

# YAML → Python dict
python3 config_converter.py config.yaml -o config.py -f python
```

### 4. **YAML_CONFIG_GUIDE.md**
Complete documentation on using the YAML configuration system

## Quick Start

### View Configuration
```bash
python3 scripts/yaml_config_loader.py scripts/config_nit_defaults.yaml
```

Output:
```
============================================================
HTS Configuration: HTS-demo_NIT-SONG070-F001 v2.3
============================================================

Project:
  Dataset: nitech_jp_song070
  Speaker: f001

Acoustic Features:
  Sample Rate: 48000 Hz
  Frame Length: 1200 samples (25.0ms)
  Frame Shift: 240 samples (5.0ms)
  FFT Length: 2048
  MGC Order: 34
  BAP Order: 24
  Freq. Warp: 0.55
  F0 Range: 195-740 Hz

Model Structure:
  HMM States: 5
  Components: mgc, lf0, bap
  Stream Orders: MGC=35, LF0=1, BAP=25
============================================================

✓ Configuration is valid!
```

### Load in Python
```python
from yaml_config_loader import YAMLConfigLoader

config = YAMLConfigLoader.load('config_nit_defaults.yaml')

# Access parameters
print(config.acoustic.sample_freq)      # 48000
print(config.acoustic.mgc_order)        # 34
print(config.acoustic.frequency_warp)   # 0.55
```

## Key Advantages

✓ **Human-readable** - Clear hierarchical YAML structure
✓ **Version-friendly** - Works well with git
✓ **Validated** - Built-in configuration validation
✓ **Type-safe** - Python dataclasses ensure correctness
✓ **Convertible** - Tools to convert to/from Perl/Python
✓ **Backward compatible** - Existing Perl configs still work

## NIT Default Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Sample Rate | 48000 Hz | High-quality speech synthesis |
| Frame Length | 1200 samples | 25ms at 48kHz |
| Frame Shift | 240 samples | 5ms at 48kHz (superframe) |
| FFT Length | 2048 | Sufficient spectral resolution |
| MGC Order | 34 | 35 dimensions with c0 (energy) |
| BAP Order | 24 | 25 dimensions with c0 |
| Frequency Warp (α) | 0.55 | Perceptual frequency mapping for 48kHz |
| Gamma | 0 | Mel-cepstral analysis (not LSP) |
| Window Type | 1 | Hamming window (standard) |
| F0 Range | 195-740 Hz | Normal female speech range |
| HMM States | 5 | States per phoneme (excluding start/end) |
| MSD F0 | Yes | Multi-Space Probability Distribution for F0 |

## Example: Customize for 16kHz

Create `config_16khz.yaml`:
```yaml
acoustic:
  sample_freq: 16000
  frame_length: 400           # 25ms
  frame_shift: 80             # 5ms
  frequency_warp: 0.42
  lower_f0: 70
  upper_f0: 250
```

Load and use:
```python
config = YAMLConfigLoader.load('config_16khz.yaml')
```

## Directory Structure

```
/workspaces/nit070/python/scripts/
├── config_nit_defaults.yaml      ← Main NIT configuration (YAML)
├── yaml_config_loader.py         ← YAML config loader + validator
├── config_converter.py           ← Format conversion tool
├── YAML_CONFIG_GUIDE.md          ← Full documentation
└── config_loader.py              ← Original Perl/Python loader
```

## Integration with Data Preparation

The YAML config works seamlessly with `data_preparation.py`:

```python
from yaml_config_loader import YAMLConfigLoader
from data_preparation import DataPreparation

# Load configuration
config_yml = YAMLConfigLoader.load('config_nit_defaults.yaml')

# Convert to DataPreparation config format
from dataclasses import dataclass
@dataclass
class Config:
    sampfreq = config_yml.acoustic.sample_freq
    framelen = config_yml.acoustic.frame_length
    frameshift = config_yml.acoustic.frame_shift
    # ... etc

# Use with data preparation
processor = DataPreparation(config)
processor.create_directories()
processor.extract_features()
```

## Testing

All configurations have been validated:
```
✓ Python syntax valid
✓ YAML structure valid
✓ Configuration parameters validated
✓ Conversion tools working
✓ Backward compatible with Perl configs
```

## Next Steps

1. **Use the YAML config** for all new HTS projects
2. **Convert existing Perl configs** using `config_converter.py`
3. **Reference** `YAML_CONFIG_GUIDE.md` for detailed customization options
4. **Integrate** with `data_preparation.py` for feature extraction workflow

---

**Status**: ✅ Complete and validated
**NIT Version**: HTS-demo_NIT-SONG070-F001 v2.3
**Configuration Format**: YAML (with Perl/Python conversion support)
