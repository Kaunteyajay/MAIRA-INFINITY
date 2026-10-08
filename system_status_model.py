"""
System Status ViewModel

Provides real system metrics to the UI.
"""

import asyncio
import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal, Property, QTimer
import psutil
try:
    import pynvml
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

from maira.core.event_bus import EventBus, SystemMetricsEvent

logger = logging.getLogger(__name__)

class SystemStatusModel(QObject):
    """Model for system status widget."""
    
    # Signals for property changes
    cpuPercentChanged = Signal()
    memoryPercentChanged = Signal()
    gpuPercentChanged = Signal()
    networkSpeedChanged = Signal()
    processCountChanged = Signal()
    
    def __init__(self, event_bus: EventBus, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        
        # System metrics
        self._cpu_percent = 0.0
        self._memory_percent = 0.0
        self._gpu_percent = 0.0
        self._network_speed = 0.0
        self._process_count = 0
        
        # Network tracking
        self._last_network_io = None
        
        # GPU setup
        self._gpu_available = False
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self._gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self._gpu_available = True
                logger.info("NVIDIA GPU detected")
            except:
                logger.info("No NVIDIA GPU available")
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_metrics)
        self.timer.start(1000)  # Update every second
        
        # Initial update
        self._update_metrics()
    
    # Properties for QML binding
    @Property(float, notify=cpuPercentChanged)
    def cpuPercent(self):
        return self._cpu_percent
    
    @Property(float, notify=memoryPercentChanged) 
    def memoryPercent(self):
        return self._memory_percent
    
    @Property(float, notify=gpuPercentChanged)
    def gpuPercent(self):
        return self._gpu_percent
    
    @Property(float, notify=networkSpeedChanged)
    def networkSpeed(self):
        return self._network_speed
    
    @Property(int, notify=processCountChanged)
    def processCount(self):
        return self._process_count
    
    def _update_metrics(self) -> None:
        """Update system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            if cpu_percent != self._cpu_percent:
                self._cpu_percent = cpu_percent
                self.cpuPercentChanged.emit()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if memory_percent != self._memory_percent:
                self._memory_percent = memory_percent
                self.memoryPercentChanged.emit()
            
            # GPU usage
            gpu_percent = self._get_gpu_usage()
            if gpu_percent != self._gpu_percent:
                self._gpu_percent = gpu_percent
                self.gpuPercentChanged.emit()
            
            # Network speed
            network_speed = self._get_network_speed()
            if abs(network_speed - self._network_speed) > 0.1:
                self._network_speed = network_speed
                self.networkSpeedChanged.emit()
            
            # Process count
            process_count = len(psutil.pids())
            if process_count != self._process_count:
                self._process_count = process_count
                self.processCountChanged.emit()
            
            # Publish metrics event
            if self.event_bus:
                asyncio.create_task(self.event_bus.publish(SystemMetricsEvent(
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    gpu_percent=gpu_percent,
                    network_bytes_sent=0,  # TODO: Track absolute values
                    network_bytes_recv=0,
                    process_count=process_count
                )))
                
        except Exception as e:
            logger.exception(f"Error updating system metrics: {e}")
    
    def _get_gpu_usage(self) -> float:
        """Get GPU utilization percentage."""
        if not self._gpu_available:
            return 0.0
        
        try:
            utilization = pynvml.nvmlDeviceGetUtilizationRates(self._gpu_handle)
            return float(utilization.gpu)
        except:
            return 0.0
    
    def _get_network_speed(self) -> float:
        """Get network speed in MB/s."""
        try:
            current_io = psutil.net_io_counters()
            
            if self._last_network_io is None:
                self._last_network_io = current_io
                return 0.0
            
            # Calculate speed (bytes per second to MB/s)
            bytes_sent_diff = current_io.bytes_sent - self._last_network_io.bytes_sent
            bytes_recv_diff = current_io.bytes_recv - self._last_network_io.bytes_recv
            
            total_bytes = bytes_sent_diff + bytes_recv_diff
            speed_mbps = total_bytes / (1024 * 1024)  # Convert to MB/s
            
            self._last_network_io = current_io
            return speed_mbps
            
        except:
            return 0.0