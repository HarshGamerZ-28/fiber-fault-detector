#!/usr/bin/env python3
"""
Fiber Fault Detector - Simple GUI Application
Desktop interface for optical fiber fault detection using tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback
from first import (
    FiberConfig, DetectionParams, simulate_trace, 
    load_csv_trace, detect_events, plot_trace_with_events
)


class FiberFaultDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Fiber Fault Detector')
        self.root.geometry('1200x700')
        
        # Variables
        self.distance = None
        self.power = None
        self.events = []
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for inputs
        left_frame = ttk.LabelFrame(main_frame, text='Settings', padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        
        # Data Source
        ttk.Label(left_frame, text='Data Source:', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        self.data_source = tk.StringVar(value='synthetic')
        ttk.Radiobutton(left_frame, text='Generate Synthetic Trace', variable=self.data_source, 
                       value='synthetic', command=self.update_source).pack(anchor='w')
        ttk.Radiobutton(left_frame, text='Load from CSV', variable=self.data_source, 
                       value='csv', command=self.update_source).pack(anchor='w')
        
        # CSV file selection
        csv_frame = ttk.Frame(left_frame)
        csv_frame.pack(anchor='w', pady=5, fill=tk.X)
        self.csv_path = tk.StringVar()
        self.csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_path, state='disabled', width=30)
        self.csv_entry.pack(side=tk.LEFT, padx=5)
        self.csv_btn = ttk.Button(csv_frame, text='Browse', command=self.select_csv, state='disabled')
        self.csv_btn.pack(side=tk.LEFT)
        
        # Fiber Parameters
        ttk.Label(left_frame, text='Fiber Parameters:', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15, 5))
        
        ttk.Label(left_frame, text='Group Index:').pack(anchor='w')
        self.group_index = tk.DoubleVar(value=1.468)
        ttk.Entry(left_frame, textvariable=self.group_index, width=20).pack(anchor='w', padx=20)
        
        ttk.Label(left_frame, text='Sampling Period (s):').pack(anchor='w', pady=(10, 0))
        self.sampling_period = tk.DoubleVar(value=5e-9)
        ttk.Entry(left_frame, textvariable=self.sampling_period, width=20).pack(anchor='w', padx=20)
        
        # Synthetic Settings
        ttk.Label(left_frame, text='Synthetic Trace:', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15, 5))
        
        ttk.Label(left_frame, text='Samples:').pack(anchor='w')
        self.num_samples = tk.IntVar(value=5000)
        ttk.Scale(left_frame, from_=1000, to=20000, variable=self.num_samples, orient=tk.HORIZONTAL).pack(anchor='w', fill=tk.X, padx=20)
        
        ttk.Label(left_frame, text='Noise Std Dev:').pack(anchor='w', pady=(10, 0))
        self.noise_std = tk.DoubleVar(value=0.003)
        ttk.Entry(left_frame, textvariable=self.noise_std, width=20).pack(anchor='w', padx=20)
        
        # Detection Parameters
        ttk.Label(left_frame, text='Detection Params:', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(15, 5))
        
        ttk.Label(left_frame, text='Denoise Method:').pack(anchor='w')
        self.denoise_method = tk.StringVar(value='savitzky_golay')
        ttk.Combobox(left_frame, textvariable=self.denoise_method, 
                    values=['savitzky_golay', 'moving_average'], state='readonly', width=20).pack(anchor='w', padx=20)
        
        ttk.Label(left_frame, text='Savitzky-Golay Window:').pack(anchor='w', pady=(10, 0))
        self.savgol_window = tk.IntVar(value=25)
        ttk.Scale(left_frame, from_=5, to=51, variable=self.savgol_window, orient=tk.HORIZONTAL).pack(anchor='w', fill=tk.X, padx=20)
        
        ttk.Label(left_frame, text='Detection Threshold:').pack(anchor='w', pady=(10, 0))
        self.threshold = tk.DoubleVar(value=0.01)
        ttk.Scale(left_frame, from_=0.001, to=0.1, variable=self.threshold, orient=tk.HORIZONTAL).pack(anchor='w', fill=tk.X, padx=20)
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(anchor='w', pady=(20, 0), fill=tk.X)
        
        ttk.Button(button_frame, text='▶ Run Analysis', command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Reset', command=self.reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Exit', command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Right panel for output
        right_frame = ttk.LabelFrame(main_frame, text='Output', padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Output text
        self.output_text = tk.Text(right_frame, height=25, width=80, bg='black', fg='#00FF00', 
                                    font=('Courier New', 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text['yscrollcommand'] = scrollbar.set
    
    def update_source(self):
        """Update UI based on selected data source"""
        if self.data_source.get() == 'csv':
            self.csv_entry.config(state='normal')
            self.csv_btn.config(state='normal')
        else:
            self.csv_entry.config(state='disabled')
            self.csv_btn.config(state='disabled')
    
    def select_csv(self):
        """Select a CSV file"""
        filename = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if filename:
            self.csv_path.set(filename)
    
    def print_output(self, text=''):
        """Print text to output window"""
        self.output_text.insert(tk.END, text + '\n')
        self.output_text.see(tk.END)
        self.root.update()
    
    def run_analysis(self):
        """Execute fiber fault detection"""
        try:
            self.output_text.delete('1.0', tk.END)
            self.print_output('Starting analysis...')
            
            # Load data
            self.print_output('\n[1] Loading data...')
            if self.data_source.get() == 'synthetic':
                self.distance, self.power = simulate_trace(
                    num_samples=self.num_samples.get(),
                    noise_std=self.noise_std.get()
                )
                self.print_output(f'Generated synthetic trace: {len(self.distance)} samples')
            else:
                csv_file = self.csv_path.get()
                if not csv_file:
                    messagebox.showerror('Error', 'Please select a CSV file')
                    return
                self.distance, self.power = load_csv_trace(csv_file)
                self.print_output(f'Loaded CSV: {len(self.distance)} samples from {csv_file}')
            
            # Detect events
            self.print_output('\n[2] Detecting faults...')
            params = DetectionParams(
                denoise_method=self.denoise_method.get(),
                savgol_window=int(self.savgol_window.get()),
                threshold=self.threshold.get()
            )
            self.events = detect_events(self.distance, self.power, params)
            self.print_output(f'Detected {len(self.events)} events')
            
            # Display results
            self.print_output('\n[3] Results:')
            self.print_output('-' * 60)
            for i, event in enumerate(self.events, 1):
                self.print_output(f'Event {i}:')
                self.print_output(f'  Distance: {event["distance_km"]:.3f} km ({event["distance_m"]:.1f} m)')
                self.print_output(f'  Power: {event["power"]:.4f}')
            
            # Plot
            self.print_output('\n[4] Generating plot...')
            fig = plot_trace_with_events(self.distance, self.power, self.events)
            plt.show()
            self.print_output('Plot displayed')
            
            self.print_output('\n✓ Analysis complete!')
            
        except Exception as e:
            self.print_output(f'\n✗ Error: {str(e)}')
            self.print_output(traceback.format_exc())
            messagebox.showerror('Error', f'Analysis failed:\n{str(e)}')
    
    def reset(self):
        """Reset the application"""
        self.output_text.delete('1.0', tk.END)
        self.distance = None
        self.power = None
        self.events = []
        self.print_output('Application reset')


if __name__ == '__main__':
    root = tk.Tk()
    app = FiberFaultDetectorApp(root)
    root.mainloop()
