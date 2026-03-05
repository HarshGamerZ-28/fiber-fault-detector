# Fiber Fault Detector

A desktop GUI application for optical fiber fault detection and distance estimation using OTDR (Optical Time Domain Reflectometry) traces.

## Features

- **Synthetic Trace Generation**: Create simulated OTDR traces with configurable parameters
- **CSV Import**: Load real OTDR data from CSV files
- **Advanced Denoising**: Savitzky-Golay and moving average filters
- **Fault Detection**: Automatic event detection with adjustable thresholds
- **Visualization**: Real-time plots showing detected faults with distance markers
- **Configurable Parameters**: Fiber parameters, detection sensitivity, and processing options

## Requirements

- Python 3.8+
- numpy
- matplotlib

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/fiber-fault-detector.git
cd fiber-fault-detector
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python gui_app_simple.py
```

### How to Use

1. **Select Data Source**:
   - Generate synthetic trace (for testing)
   - Load from CSV file (for real data)

2. **Configure Fiber Parameters**:
   - Group Index (typical: 1.468 for SMF-28 @ 1550nm)
   - Sampling Period (e.g., 5e-9 seconds)

3. **Set Detection Parameters**:
   - Choose denoising method
   - Adjust window size and thresholds
   - Fine-tune detection sensitivity

4. **Run Analysis**:
   - Click "▶ Run Analysis"
   - View detected faults in output panel
   - Plot shows events marked with distance indicators

## CSV File Format

Expected format with headers:
```
distance,power
0.0,100.5
0.001,99.8
...
```

## Configuration

### Fiber Parameters
- **Group Index**: Velocity factor in the fiber (default: 1.468)
- **Sampling Period**: Time between samples in seconds (default: 5e-9)

### Detection Parameters
- **Denoise Method**: savitzky_golay or moving_average
- **Window Size**: Filter window length (5-51)
- **Detection Threshold**: Sensitivity to fault events (0.001-0.1)

## Output

The analysis produces:
- List of detected fault locations (in km and meters)
- Power levels at each fault
- Matplotlib plot with marked fault locations

## Example Workflow

1. Launch the app
2. Keep "Generate Synthetic Trace" selected
3. Adjust noise level to simulate real data
4. Click "▶ Run Analysis"
5. View results and generated plot

## License

MIT License - See LICENSE.txt for details

## Author

Created January 2026

## Support

For issues or questions, please open an issue on GitHub.
"# fiber-fault-detector" 
"# fiber-fault-detector" 
