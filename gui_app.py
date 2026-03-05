#!/usr/bin/env python3
"""
Fiber Fault Detector - GUI Application
Desktop interface for optical fibre fault detection & distance estimation.
"""

import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
import traceback
import sys
sys.path.insert(0, 'path/to/first')
from first import (
    FiberConfig, DetectionParams, simulate_trace, 
    load_csv_trace, detect_events, plot_trace_with_events
)

# Set theme
# sg.set_theme('DarkBlue')
# sg.set_options(font=('Segoe UI', 10))

# Define layout
def create_layout():
    left_column = [
        [sg.Text('Fiber Fault Detector', font=('Segoe UI', 18, 'bold'), text_color='#00FF00')],
        [sg.Text('_' * 60)],
        
        [sg.Text('Data Source', font=('Segoe UI', 12, 'bold'))],
        [sg.Radio('Generate Synthetic Trace', 'data_source', default=True, key='SYNTHETIC', enable_events=True),
         sg.Radio('Load from CSV', 'data_source', key='CSV_MODE', enable_events=True)],
        
        [sg.InputText(key='CSV_PATH', size=(35, 1), disabled=True), 
         sg.FileBrowse(file_types=(("CSV files", "*.csv"), ("All files", "*.*")), disabled=True, key='BROWSE_BTN')],
        
        [sg.Text('Fiber Parameters', font=('Segoe UI', 12, 'bold'))],
        [sg.Text('Group Index:'), 
         sg.InputText('1.468', size=(12, 1), key='GROUP_INDEX', tooltip='SMF-28 @ 1550nm typical: 1.468')],
        [sg.Text('Sampling Period (s):'), 
         sg.InputText('5e-9', size=(12, 1), key='SAMPLING_PERIOD', tooltip='e.g., 5e-9 for 5ns')],
        
        [sg.Text('Synthetic Trace Settings', font=('Segoe UI', 12, 'bold'))],
        [sg.Text('Number of Samples:'), 
         sg.Slider(range=(1000, 20000), default=5000, orientation='h', size=(20, 15), key='NUM_SAMPLES')],
        [sg.Text('Noise Std Dev:'), 
         sg.InputText('0.003', size=(12, 1), key='NOISE_STD')],
        
        [sg.Text('Detection Parameters', font=('Segoe UI', 12, 'bold'))],
        [sg.Text('Denoise Method:'), 
         sg.Combo(['savitzky_golay', 'moving_average'], default_value='savitzky_golay', key='DENOISE_METHOD')],
        [sg.Text('Savitzky-Golay Window:'), 
         sg.Slider(range=(5, 51), default=25, orientation='h', size=(20, 15), key='SAVGOL_WINDOW')],
        [sg.Text('Savitzky-Golay Poly Order:'), 
         sg.Slider(range=(1, 6), default=3, orientation='h', size=(20, 15), key='SAVGOL_POLYORDER')],
        [sg.Text('Moving Avg Window:'), 
         sg.Slider(range=(3, 31), default=11, orientation='h', size=(20, 15), key='MOVING_AVG_WINDOW')],
        
        [sg.Text('Event Detection Thresholds', font=('Segoe UI', 12, 'bold'))],
        [sg.Text('Reflection Threshold:'), 
         sg.Slider(range=(0.005, 0.15), default=0.02, resolution=0.005, orientation='h', size=(20, 15), key='REFL_THRESHOLD')],
        [sg.Text('Loss Threshold:'), 
         sg.Slider(range=(-0.15, -0.005), default=-0.02, resolution=0.005, orientation='h', size=(20, 15), key='LOSS_THRESHOLD')],
        [sg.Text('Min Event Separation (samples):'), 
         sg.Slider(range=(10, 200), default=50, orientation='h', size=(20, 15), key='MIN_EVENT_SEP')],
        
        [sg.Checkbox('Normalize Signal', default=True, key='NORMALIZE')],
        [sg.Checkbox('Show Plot', default=True, key='SHOW_PLOT')],
        
        [sg.Text('_' * 60)],
        [sg.Button('▶ Run Analysis', size=(15, 2), button_color=('white', '#00AA00'), font=('Segoe UI', 11, 'bold')),
         sg.Button('⟳ Reset', size=(15, 2)),
         sg.Button('❌ Exit', size=(15, 2), button_color=('white', '#AA0000'))],
    ]
    
    right_column = [
        [sg.Multiline(size=(60, 50), key='OUTPUT', disabled=True, 
                     font=('Courier New', 9), background_color='#000000', text_color='#00FF00')]
    ]
    
    layout = [
        [sg.Column(left_column, vertical_alignment='top'), 
         sg.VSeperator(),
         sg.Column(right_column, vertical_alignment='top')]
    ]
    
    return layout


# Create window
window = sg.Window('My App', create_layout(), finalize=True)
output_element = window['OUTPUT']


def print_output(text):
    """Append text to output box with timestamp"""
    output_element.print(text)
    window.refresh()


def run_analysis(values):
    """Execute the fiber fault detection pipeline"""
    try:
        print_output("\n" + "="*60)
        print_output("Starting analysis...")
        print_output("="*60 + "\n")
        
        # Load or generate trace
        if values['CSV_MODE'] and values['CSV_PATH']:
            print_output(f"Loading CSV: {values['CSV_PATH']}")
            trace = load_csv_trace(values['CSV_PATH'])
            print_output(f"✓ Loaded {len(trace.amplitude)} samples")
            if trace.time_s is None:
                trace.time_s = np.arange(len(trace.amplitude)) * float(values['SAMPLING_PERIOD'])
        else:
            num_samples = int(values['NUM_SAMPLES'])
            sampling_period = float(values['SAMPLING_PERIOD'])
            noise_std = float(values['NOISE_STD'])
            print_output(f"Generating synthetic trace: {num_samples} samples @ {sampling_period:.2e}s")
            trace = simulate_trace(
                num_samples=num_samples,
                sampling_period_s=sampling_period,
                noise_std=noise_std
            )
            print_output(f"✓ Generated synthetic trace")
        
        # Configure fiber
        group_index = float(values['GROUP_INDEX'])
        sampling_period = float(values['SAMPLING_PERIOD'])
        fiber = FiberConfig(group_index=group_index, sampling_period_s=sampling_period)
        print_output(f"✓ Fiber Config: Group Index={group_index}, Sampling Period={sampling_period:.2e}s")
        
        # Configure detection
        params = DetectionParams(
            denoise_method=values['DENOISE_METHOD'],
            savgol_window=int(values['SAVGOL_WINDOW']) | 1,  # ensure odd
            savgol_polyorder=int(values['SAVGOL_POLYORDER']),
            moving_avg_window=int(values['MOVING_AVG_WINDOW']) | 1,
            reflection_grad_threshold=float(values['REFL_THRESHOLD']),
            loss_step_threshold=float(values['LOSS_THRESHOLD']),
            min_event_separation=int(values['MIN_EVENT_SEP']),
            normalize=values['NORMALIZE']
        )
        print_output(f"✓ Detection Config: {values['DENOISE_METHOD']}, Min Separation={int(values['MIN_EVENT_SEP'])} samples")
        
        # Detect events
        print_output("\nDetecting events...")
        events = detect_events(trace, fiber, params)
        
        if not events:
            print_output("⚠ No events detected. Try adjusting thresholds.")
        else:
            print_output(f"\n{'='*60}")
            print_output(f"DETECTED EVENTS ({len(events)} total)")
            print_output(f"{'='*60}\n")
            
            for i, e in enumerate(events, 1):
                t = f"{e.time_s:.9f} s" if e.time_s is not None else f"Sample {e.index}"
                dist_km = e.distance_m / 1000.0 if e.distance_m else 0
                print_output(
                    f"{i}. {e.kind.upper():8s} | "
                    f"Position: {t:20s} | "
                    f"Distance: {dist_km:7.5f} km | "
                    f"Amplitude Δ: {e.amplitude_change:+.6f}"
                )
            
            print_output(f"\n{'='*60}\n")
        
        # Plot
        if values['SHOW_PLOT']:
            print_output("Rendering plot...")
            title = "Fiber Fault Detection - CSV Data" if values['CSV_MODE'] else "Fiber Fault Detection - Synthetic Data"
            plot_trace_with_events(trace, events, title=title)
            print_output("✓ Plot displayed")
        
        print_output("\n" + "="*60)
        print_output("✓ Analysis complete!")
        print_output("="*60 + "\n")
        
    except Exception as e:
        print_output(f"\n❌ ERROR: {str(e)}\n")
        print_output(traceback.format_exc())


def reset_values():
    """Reset all inputs to defaults"""
    window['SYNTHETIC'].update(True)
    window['CSV_MODE'].update(False)
    window['CSV_PATH'].update('')
    window['GROUP_INDEX'].update('1.468')
    window['SAMPLING_PERIOD'].update('5e-9')
    window['NUM_SAMPLES'].update(5000)
    window['NOISE_STD'].update('0.003')
    window['DENOISE_METHOD'].update('savitzky_golay')
    window['SAVGOL_WINDOW'].update(25)
    window['SAVGOL_POLYORDER'].update(3)
    window['MOVING_AVG_WINDOW'].update(11)
    window['REFL_THRESHOLD'].update(0.02)
    window['LOSS_THRESHOLD'].update(-0.02)
    window['MIN_EVENT_SEP'].update(50)
    window['NORMALIZE'].update(True)
    window['SHOW_PLOT'].update(True)
    output_element.update('')
    print_output("✓ Reset to defaults\n")


# Main event loop
while True:
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
    if event == 'SYNTHETIC':
        window['CSV_PATH'].update(disabled=True)
        window['BROWSE_BTN'].update(disabled=True)
    
    if event == 'CSV_MODE':
        window['CSV_PATH'].update(disabled=False)
        window['BROWSE_BTN'].update(disabled=False)
    
    if event == 'Run Analysis':
        run_analysis(values)
    
    if event == 'Reset':
        reset_values()

window.close()