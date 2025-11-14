# Enhanced Video Combine

An enhanced video composition plugin for ComfyUI, improved from ComfyUI Video Helper Suite and optimized by eddy.

## Features

### 1. Enhanced Video Combine Node

Enhanced video composition node with additional features on top of the original Video Combine:

- **Multi-Audio Channel Support**: Supports up to 4 simultaneous audio tracks (audio, audio_2, audio_3, audio_4)
- **Flexible Audio Modes**:
  - `primary_only` - Use primary audio only
  - `first_available` - Use the first available audio
  - `priority_order` - Select by priority order
  - `mix_all` - Mix all available audio tracks
  - `mix_primary_backup` - Mix primary and backup audio
  - `channel_1/2/3/4` - Individual channel selection
  - `no_audio` - No audio
- **Audio Mix Ratio Control**: Adjust volume ratio when mixing multiple audio tracks (0.0-1.0)
- **Detailed Video Info Output**: Provides complete information including frame count, frame rate, duration, audio status, etc.
- **Dynamic Preview Support**: Fully compatible with original Video Combine

### 2. Audio Concatenate Node

Professional audio concatenation tool featuring:

- **Multi-Track Sequential Connection**: Supports concatenating up to 6 audio tracks in sequence
- **Crossfade Effect**: Configurable transition time between audio tracks (0-5 seconds)
- **Automatic Format Adaptation**:
  - Auto-resampling to unified sample rate
  - Auto-conversion between mono and stereo
  - Intelligent handling of different audio formats
- **Waveform Smoothing**: Automatically removes NaN/Inf values and normalizes to prevent clipping

## Use Cases

- **Video Dubbing Production**: Independent control of multiple audio tracks for easy mixing adjustments
- **Long Video Composition**: Sequential concatenation of multiple audio segments with fade in/out support
- **Audio Backup Switching**: Automatic switch to backup audio when primary audio fails
- **Multilingual Videos**: Different audio channels for different language dubs

## Installation

Place the plugin in the ComfyUI custom nodes directory:

```
ComfyUI/custom_nodes/enhanced-video-combine/
```

After restarting ComfyUI, find the nodes in the menu:
- `Enhanced Video` → `Enhanced Video Combine`
- `Enhanced Video/Audio` → `Audio Concatenate`

## Technical Features

- Based on ComfyUI standard AUDIO format (waveform + sample_rate)
- Uses PyTorch tensor operations for optimal performance
- Fully compatible with all ComfyUI Video Helper Suite parameters
- Supports dynamic preview and metadata saving
- Automatic audio quality optimization and error handling

## Dependencies

- ComfyUI
- PyTorch
- NumPy
- FFmpeg (for video encoding)

## Credits

Improved from ComfyUI Video Helper Suite
Enhanced and optimized by eddy
