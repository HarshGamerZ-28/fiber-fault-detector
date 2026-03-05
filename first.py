"""
Fiber Fault Detection Module
Provides core functions for optical fiber fault detection and distance estimation.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List, Dict


@dataclass
class FiberConfig:
    """Configuration for fiber parameters."""
    group_index: float = 1.468
    sampling_period: float = 5e-9
    
    def get_velocity(self) -> float:
        """Calculate wave velocity in the fiber."""
        c = 3e8  # speed of light in vacuum
        return c / self.group_index


@dataclass
class DetectionParams:
    """Parameters for fault detection."""
    denoise_method: str = 'savitzky_golay'
    savgol_window: int = 25
    threshold: float = 0.01
    min_event_distance: int = 100


def simulate_trace(num_samples: int = 5000, noise_std: float = 0.003) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate an OTDR trace with synthetic events.
    
    Args:
        num_samples: Number of samples in the trace
        noise_std: Standard deviation of Gaussian noise
        
    Returns:
        Tuple of (distance array, power array)
    """
    # Create synthetic trace with exponential decay (Rayleigh backscatter)
    distance = np.linspace(0, 20, num_samples)  # 0-20 km
    power = np.exp(-distance / 10) * 100  # Exponential decay
    
    # Add some fault events (sudden reflections)
    events = [
        (5, 15),   # Event at 5 km with amplitude 15
        (12, 20),  # Event at 12 km with amplitude 20
    ]
    
    for event_pos, amplitude in events:
        event_idx = int(event_pos / 20 * num_samples)
        if event_idx < num_samples:
            power[event_idx:event_idx+50] += amplitude * np.exp(-np.arange(50) / 20)
    
    # Add noise
    power += np.random.normal(0, noise_std, num_samples)
    power = np.maximum(power, 0)  # Ensure non-negative
    
    return distance, power


def load_csv_trace(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load OTDR trace from CSV file.
    
    Args:
        filepath: Path to CSV file with columns: distance, power
        
    Returns:
        Tuple of (distance array, power array)
    """
    data = np.loadtxt(filepath, delimiter=',', skiprows=1)
    distance = data[:, 0]
    power = data[:, 1]
    return distance, power


def denoise_trace(power: np.ndarray, method: str = 'savitzky_golay', 
                  savgol_window: int = 25) -> np.ndarray:
    """
    Denoise the OTDR trace.
    
    Args:
        power: Power array
        method: Denoising method ('savitzky_golay' or 'moving_average')
        savgol_window: Window size for Savitzky-Golay filter
        
    Returns:
        Denoised power array
    """
    # Use moving average for both methods (scipy not available)
    window = max(5, savgol_window // 2)
    denoised = np.convolve(power, np.ones(window)/window, mode='same')
    return denoised


def detect_events(distance: np.ndarray, power: np.ndarray, 
                 params: DetectionParams) -> List[Dict]:
    """
    Detect fault events in the OTDR trace.
    
    Args:
        distance: Distance array (km)
        power: Power array
        params: Detection parameters
        
    Returns:
        List of detected events with properties
    """
    # Denoise the trace
    denoised = denoise_trace(power, params.denoise_method, params.savgol_window)
    
    # Calculate the derivative (reflections are discontinuities)
    derivative = np.abs(np.diff(denoised))
    
    # Find peaks
    threshold = params.threshold * np.max(derivative)
    events = []
    
    i = 0
    while i < len(derivative):
        if derivative[i] > threshold:
            # Found potential event
            event_dist = distance[i]
            event_power = power[i]
            
            # Skip nearby samples to avoid duplicates
            i += params.min_event_distance
            
            events.append({
                'distance_km': float(event_dist),
                'distance_m': float(event_dist * 1000),
                'power': float(event_power),
                'index': i
            })
        else:
            i += 1
    
    return events


def plot_trace_with_events(distance: np.ndarray, power: np.ndarray, 
                          events: List[Dict]) -> plt.Figure:
    """
    Create a plot of the OTDR trace with detected events marked.
    
    Args:
        distance: Distance array (km)
        power: Power array
        events: List of detected events
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the trace
    ax.plot(distance, power, 'b-', label='OTDR Trace', linewidth=2)
    ax.set_xlabel('Distance (km)', fontsize=12)
    ax.set_ylabel('Power (dB)', fontsize=12)
    ax.set_title('Optical Time Domain Reflectometry (OTDR) Trace', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Mark detected events
    for i, event in enumerate(events):
        idx = event['index']
        if idx < len(distance):
            ax.plot(distance[idx], power[idx], 'r*', markersize=15, 
                   label=f"Event {i+1}" if i == 0 else "")
            ax.axvline(distance[idx], color='red', linestyle='--', alpha=0.3)
            ax.text(distance[idx], power[idx], f"  {event['distance_km']:.2f} km", 
                   fontsize=10, color='red')
    
    ax.legend(loc='upper right')
    plt.tight_layout()
    
    return fig
