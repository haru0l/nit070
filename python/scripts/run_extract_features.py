#!/usr/bin/env python3
"""
Extract acoustic features (MGC, F0, BAP) from audio files.

Usage:
    python3 run_extract_features.py <audio_file> [config_file]

Example:
    python3 run_extract_features.py ../../HTS-demo_NIT-SONG070-F001/data/raw/nitech_jp_song070_f001_003.wav
"""

import sys
import os
import numpy as np
from pathlib import Path
from scipy.io import wavfile
from yaml_config_loader import YAMLConfigLoader
from data_preparation import DataPreparation, AnalysisConfig


def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 run_extract_features.py <audio_file> [config_file] [--skip-bap]")
        print("\nExample:")
        print("  python3 run_extract_features.py ../../HTS-demo_NIT-SONG070-F001/data/raw/nitech_jp_song070_f001_003.wav")
        print("\nOptions:")
        print("  --skip-bap    Skip BAP extraction (faster, for testing)")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'config_nit_defaults.yaml'
    skip_bap = '--skip-bap' in sys.argv
    
    # Validate input file
    if not os.path.exists(audio_file):
        print(f"❌ Error: Audio file not found: {audio_file}")
        sys.exit(1)
    
    if not os.path.exists(config_file):
        print(f"❌ Error: Config file not found: {config_file}")
        sys.exit(1)
    
    print(f"📂 Loading configuration: {config_file}")
    print(f"🎵 Processing audio file: {audio_file}\n")
    
    try:
        # Load config
        config = YAMLConfigLoader.load(config_file)
        print("✅ Configuration loaded\n")
        
        # Convert HTSConfig to AnalysisConfig for DataPreparation
        analysis_config = AnalysisConfig(
            sampfreq=config.acoustic.sample_freq,
            framelen=config.acoustic.frame_length,
            frameshift=config.acoustic.frame_shift,
            fftlen=config.acoustic.fft_length,
            mgcorder=config.acoustic.mgc_order,
            freqwarp=config.acoustic.frequency_warp,
            baporder=config.acoustic.bap_order,
            lowerf0=config.acoustic.lower_f0,
            upperf0=config.acoustic.upper_f0,
            windowtype=config.acoustic.window_type,
            normalize=config.acoustic.normalize,
            usestraight=1 if config.acoustic.use_straight else 0,
            rawdir=config.raw_dir,
            mgcdir=config.mgc_dir,
            lf0dir=config.lf0_dir,
            bapdir=config.bap_dir,
            cmpdir=config.cmp_dir,
            labeldir=config.label_dir,
            listdir=config.list_dir,
            dataset=config.dataset,
            speaker=config.speaker,
        )
        
        # Initialize processor
        processor = DataPreparation(analysis_config)
        print("✅ Feature extractor initialized\n")
        
        # Print audio info
        print("=" * 70)
        print("EXTRACTING ACOUSTIC FEATURES")
        print("=" * 70)
        print(f"Audio file:    {os.path.basename(audio_file)}")
        print(f"Sample rate:   {config.acoustic.sample_freq} Hz")
        print(f"Frame shift:   {config.acoustic.frame_shift} samples ({config.acoustic.frame_shift/config.acoustic.sample_freq*1000:.2f} ms)")
        print(f"Frame length:  {config.acoustic.frame_length} samples")
        print()
        
        # Load audio file
        print("📥 Loading audio file...")
        if audio_file.endswith('.wav'):
            sr, audio_data = wavfile.read(audio_file)
            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            # Normalize to [-1, 1] if needed
            if audio_data.dtype != np.float32 and audio_data.dtype != np.float64:
                audio_data = audio_data.astype(np.float32) / 32768.0
        elif audio_file.endswith('.raw'):
            # Load raw audio (48kHz, 16-bit signed int, little endian)
            audio_data = np.fromfile(audio_file, dtype=np.int16)
            # Convert to float32 normalized to [-1, 1]
            audio_data = audio_data.astype(np.float32) / 32768.0
            sr = config.acoustic.sample_freq
        else:
            print(f"❌ Unsupported audio format: {audio_file}")
            sys.exit(1)
        
        print(f"   ✅ Audio loaded: {len(audio_data)} samples ({len(audio_data)/sr:.2f} sec)")
        print()
        
        # Get basename for output files
        base = Path(audio_file).stem
        
        # Extract MGC (Mel-Cepstrum)
        print("📊 Extracting MGC (Mel-Generalized Cepstrum)...")
        processor._extract_mgc(audio_data, sr, base)
        print()
        
        # Extract F0 (Fundamental Frequency)
        print("📊 Extracting F0 (Fundamental Frequency)...")
        processor._extract_f0(audio_data, sr, base)
        print()
        
        # Extract BAP (Band Aperiodic Power)
        print("📊 Extracting BAP (Band Aperiodic Power)...")
        if skip_bap:
            print("  ⏭️  Skipped (use --skip-bap to enable)")
        else:
            print("  ⚠️  Warning: BAP extraction may take several minutes...")
            processor._extract_bap(audio_data, sr, base)
        print()
        
        # Summary
        print("=" * 70)
        print("✅ FEATURE EXTRACTION COMPLETE")
        print("=" * 70)
        print(f"Output base:   {base}")
        print(f"Audio length:  {len(audio_data) / sr:.2f} seconds")
        print()
        print("Output files:")
        print(f"  MGC: {Path(analysis_config.mgcdir) / f'{base}.mgc'}")
        print(f"  F0:  {Path(analysis_config.lf0dir) / f'{base}.lf0'}")
        print(f"  BAP: {Path(analysis_config.bapdir) / f'{base}.bap'}")
        print()
        
    except Exception as e:
        print(f"❌ Error during feature extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
