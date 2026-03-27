# Configuration & Feature Extraction Scripts

Quick reference for running the HTS configuration and feature extraction scripts.

## Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_load_config.py` | Load and display configuration | `python3 run_load_config.py [config_file]` |
| `run_validate_config.py` | Validate configuration | `python3 run_validate_config.py [config_file]` |
| `run_extract_features.py` | Extract acoustic features | `python3 run_extract_features.py <audio_file> [config_file]` |
| `run_convert_config.py` | Convert between formats | `python3 run_convert_config.py <input> <output> --format <format>` |
| `run_all_tests.py` | Run all tests | `python3 run_all_tests.py [audio_file]` |

---

## 1. Load and Display Configuration

**Script:** `run_load_config.py`

Loads the YAML configuration and displays all key parameters in a formatted table.

```bash
# Load default configuration
python3 run_load_config.py

# Load custom configuration
python3 run_load_config.py my_config.yaml
```

**Output shows:**
- Acoustic parameters (sample rate, orders, frequency warp)
- Model structure (HMM states, stream weights, MSD flags)
- Training parameters (iterations, weight floor, minimum duration)
- Parameter generation settings (algorithm, GV settings)

---

## 2. Validate Configuration

**Script:** `run_validate_config.py`

Validates configuration against constraints (ranges, dependencies, logical checks).

```bash
# Validate default configuration
python3 run_validate_config.py

# Validate custom configuration
python3 run_validate_config.py my_config.yaml
```

**Checks performed:**
- ✅ Sample rate in valid range (16000-48000 Hz)
- ✅ Frequency warp in (0, 1)
- ✅ F0 min < F0 max
- ✅ Model orders consistent with acoustic orders
- ✅ Stream weights in valid range
- ✅ Training parameters are positive
- ✅ Parameter generation settings valid

**Exit codes:**
- 0: All checks passed
- 1: Errors found

---

## 3. Extract Acoustic Features

**Script:** `run_extract_features.py`

Extracts MGC (spectrum), F0 (fundamental frequency), and BAP (aperiodic) from audio.

```bash
# Extract features from NIT demo audio
python3 run_extract_features.py ../../HTS-demo_NIT-SONG070-F001/data/raw/nitech_jp_song070_f001_003.wav

# Extract with custom config
python3 run_extract_features.py audio.wav my_config.yaml
```

**Output shows:**
- MGC (Mel-Cepstrum): shape, min/max/mean values
- F0: voiced/unvoiced frame counts, F0 range and mean
- BAP (Band Aperiodic): shape, min/max/mean values
- Total duration and frame count

**Requires audio files in:**
```
HTS-demo_NIT-SONG070-F001/data/raw/nitech_jp_song070_f001_*.wav
```

---

## 4. Convert Configuration Format

**Script:** `run_convert_config.py`

Convert between configuration formats (YAML ↔ Perl ↔ Python).

```bash
# YAML to Perl
python3 run_convert_config.py config_nit_defaults.yaml output_config.pl --format perl

# YAML to Python dict
python3 run_convert_config.py config_nit_defaults.yaml output_config.py --format python

# YAML to YAML (validation + reformat)
python3 run_convert_config.py config_nit_defaults.yaml output_config.yaml --format yaml
```

**Supported formats:**
- `yaml`: Human-readable YAML format
- `perl`: HTS Perl Config.pm format
- `python`: Python dictionary format

---

## 5. Run All Tests

**Script:** `run_all_tests.py`

Runs comprehensive test suite covering all functionality.

```bash
# Run all tests (without feature extraction)
python3 run_all_tests.py

# Run all tests including feature extraction
python3 run_all_tests.py ../../HTS-demo_NIT-SONG070-F001/data/raw/nitech_jp_song070_f001_003.wav
```

**Tests executed:**
1. Load and inspect configuration
2. Validate configuration
3. Convert configuration format
4. Extract acoustic features (if audio file provided)

**Output shows:**
- Individual test results (✅ PASSED / ❌ FAILED / ⏭️ SKIPPED)
- Summary statistics
- Exit code for scripting (0 = all passed)

---

## Quick Start Examples

### Validate your setup
```bash
python3 run_load_config.py && python3 run_validate_config.py
```

### Set up and test everything
```bash
python3 run_all_tests.py ../../HTS-demo_NIT-SONG070-F001/data/raw/nitech_jp_song070_f001_003.wav
```

### Extract features from multiple files
```bash
for wav in ../../HTS-demo_NIT-SONG070-F001/data/raw/*.wav; do
    python3 run_extract_features.py "$wav"
done
```

### Generate Perl config for HTS compatibility
```bash
python3 run_convert_config.py config_nit_defaults.yaml Config.pm --format perl
```

---

## Requirements

Install dependencies:
```bash
pip install numpy scipy pysptk pylstraight pyyaml
```

Check dependencies:
```bash
python3 check_dependencies.py
```

---

## Configuration Files

Main configuration file:
```
config_nit_defaults.yaml
```

Sections:
- `acoustic`: Sample rate, frame parameters, feature orders
- `model`: HMM structure, stream weights
- `windows`: Delta/delta-delta coefficient windows
- `model_training`: Embedded training parameters
- `parameter_generation`: PG algorithm settings
- `training`: Training scripts and models
- `postfilter`: Postfiltering parameters

---

## Troubleshooting

### Audio file not found
```
❌ Error: Audio file not found: ...
```
Check that the audio file path is correct and the file exists.

### Configuration validation fails
```
❌ VALIDATION FAILED
```
Check configuration parameters against constraints in `run_validate_config.py`.

### Missing dependencies
```
ModuleNotFoundError: No module named 'pysptk'
```
Run: `pip install numpy scipy pysptk pylstraight pyyaml`

### Feature extraction errors
```
Error during feature extraction: ...
```
Check audio format (must be WAV) and sample rate compatibility.

---

## Advanced Usage

### Load config in Python scripts
```python
from yaml_config_loader import YAMLConfigLoader

config = YAMLConfigLoader.load('config_nit_defaults.yaml')
print(config.acoustic.sample_freq)
print(config.model.num_states)
```

### Extract features programmatically
```python
from data_preparation import DataPreparation

processor = DataPreparation()
mgc = processor._extract_mgc('audio.wav', order=34)
f0 = processor._extract_f0('audio.wav')
bap = processor._extract_bap('audio.wav', order=24)
```

### Integrate with HTS training
The configuration is compatible with HTS-2.3+ and the embedded Training.pl script.

---

## Documentation

For more details, see:
- `YAML_CONFIG_GUIDE.md` - Detailed YAML configuration reference
- `YAML_CONFIG_SETUP.md` - Setup and installation guide
- `FINAL_CHECKLIST.md` - Validation and verification report
