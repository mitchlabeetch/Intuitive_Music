"""MIDI I/O utilities for hardware MIDI controller support

This module provides cross-platform MIDI input/output using rtmidi.
Supports hardware controllers, virtual ports, and MIDI file I/O.
"""
from typing import List, Dict, Optional, Callable, Any, Tuple
from dataclasses import dataclass
import threading
import queue
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class MIDIDevice:
    """Represents a MIDI device"""
    index: int
    name: str
    is_input: bool
    is_virtual: bool = False


@dataclass
class MIDIMessage:
    """Represents a MIDI message"""
    type: str  # note_on, note_off, cc, program, pitchbend, etc.
    channel: int
    data1: int  # Note number or CC number
    data2: int  # Velocity or CC value
    timestamp: float = 0.0
    
    @classmethod
    def from_bytes(cls, data: bytes, timestamp: float = 0.0) -> 'MIDIMessage':
        """Parse MIDI bytes into message"""
        if len(data) < 1:
            return cls('unknown', 0, 0, 0, timestamp)
        
        status = data[0]
        msg_type = (status >> 4) & 0x0F
        channel = status & 0x0F
        
        data1 = data[1] if len(data) > 1 else 0
        data2 = data[2] if len(data) > 2 else 0
        
        type_names = {
            0x8: 'note_off',
            0x9: 'note_on',
            0xA: 'aftertouch',
            0xB: 'cc',
            0xC: 'program',
            0xD: 'channel_pressure',
            0xE: 'pitchbend',
        }
        
        type_name = type_names.get(msg_type, 'unknown')
        
        # Note on with velocity 0 is Note off
        if type_name == 'note_on' and data2 == 0:
            type_name = 'note_off'
        
        return cls(type_name, channel, data1, data2, timestamp)
    
    def to_bytes(self) -> bytes:
        """Convert message to MIDI bytes"""
        type_values = {
            'note_off': 0x80,
            'note_on': 0x90,
            'aftertouch': 0xA0,
            'cc': 0xB0,
            'program': 0xC0,
            'channel_pressure': 0xD0,
            'pitchbend': 0xE0,
        }
        
        status = type_values.get(self.type, 0x90) | (self.channel & 0x0F)
        
        if self.type in ('program', 'channel_pressure'):
            return bytes([status, self.data1 & 0x7F])
        else:
            return bytes([status, self.data1 & 0x7F, self.data2 & 0x7F])


class MIDIInput:
    """
    MIDI input handler with callback support.
    
    Usage:
        midi_in = MIDIInput()
        midi_in.open(0)  # Open first port
        midi_in.set_callback(lambda msg: print(msg))
        # ... later
        midi_in.close()
    """
    
    def __init__(self):
        self._rtmidi = None
        self._port = None
        self._callback: Optional[Callable[[MIDIMessage], None]] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._queue: queue.Queue = queue.Queue()
        self._load_backend()
    
    def _load_backend(self) -> None:
        """Load rtmidi backend"""
        try:
            import rtmidi
            self._rtmidi = rtmidi
            self._port = rtmidi.MidiIn()
            logger.info("rtmidi backend loaded for MIDI input")
        except ImportError:
            logger.warning("rtmidi not available: pip install python-rtmidi")
    
    @property
    def available(self) -> bool:
        """Check if MIDI input is available"""
        return self._rtmidi is not None
    
    def list_ports(self) -> List[MIDIDevice]:
        """List available MIDI input ports"""
        if not self._port:
            return []
        
        devices = []
        for i in range(self._port.get_port_count()):
            name = self._port.get_port_name(i)
            devices.append(MIDIDevice(
                index=i,
                name=name,
                is_input=True,
                is_virtual='virtual' in name.lower()
            ))
        return devices
    
    def open(self, port: int = 0) -> bool:
        """
        Open a MIDI input port.
        
        Args:
            port: Port index or -1 for virtual port
        
        Returns:
            True if successful
        """
        if not self._port:
            return False
        
        try:
            if port == -1:
                self._port.open_virtual_port("Intuitives DAW In")
            else:
                self._port.open_port(port)
            
            self._running = True
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()
            
            logger.info(f"Opened MIDI input port {port}")
            return True
        except Exception as e:
            logger.error(f"Failed to open MIDI port: {e}")
            return False
    
    def close(self) -> None:
        """Close the MIDI input port"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._port:
            self._port.close_port()
    
    def set_callback(self, callback: Callable[[MIDIMessage], None]) -> None:
        """
        Set callback for incoming MIDI messages.
        
        Args:
            callback: Function that receives MIDIMessage
        """
        self._callback = callback
    
    def _poll_loop(self) -> None:
        """Internal polling loop"""
        while self._running:
            if self._port:
                msg = self._port.get_message()
                if msg:
                    data, timestamp = msg
                    midi_msg = MIDIMessage.from_bytes(bytes(data), timestamp)
                    
                    if self._callback:
                        try:
                            self._callback(midi_msg)
                        except Exception as e:
                            logger.error(f"Error in MIDI callback: {e}")
            
            time.sleep(0.001)  # 1ms poll interval
    
    def poll(self) -> Optional[MIDIMessage]:
        """
        Poll for next MIDI message (alternative to callback).
        
        Returns:
            MIDIMessage or None
        """
        if not self._port:
            return None
        
        msg = self._port.get_message()
        if msg:
            data, timestamp = msg
            return MIDIMessage.from_bytes(bytes(data), timestamp)
        return None


class MIDIOutput:
    """
    MIDI output handler.
    
    Usage:
        midi_out = MIDIOutput()
        midi_out.open(0)
        midi_out.note_on(60, 100)
        midi_out.note_off(60)
        midi_out.close()
    """
    
    def __init__(self):
        self._rtmidi = None
        self._port = None
        self._load_backend()
    
    def _load_backend(self) -> None:
        """Load rtmidi backend"""
        try:
            import rtmidi
            self._rtmidi = rtmidi
            self._port = rtmidi.MidiOut()
            logger.info("rtmidi backend loaded for MIDI output")
        except ImportError:
            logger.warning("rtmidi not available: pip install python-rtmidi")
    
    @property
    def available(self) -> bool:
        """Check if MIDI output is available"""
        return self._rtmidi is not None
    
    def list_ports(self) -> List[MIDIDevice]:
        """List available MIDI output ports"""
        if not self._port:
            return []
        
        devices = []
        for i in range(self._port.get_port_count()):
            name = self._port.get_port_name(i)
            devices.append(MIDIDevice(
                index=i,
                name=name,
                is_input=False,
                is_virtual='virtual' in name.lower()
            ))
        return devices
    
    def open(self, port: int = 0) -> bool:
        """
        Open a MIDI output port.
        
        Args:
            port: Port index or -1 for virtual port
        
        Returns:
            True if successful
        """
        if not self._port:
            return False
        
        try:
            if port == -1:
                self._port.open_virtual_port("Intuitives DAW Out")
            else:
                self._port.open_port(port)
            
            logger.info(f"Opened MIDI output port {port}")
            return True
        except Exception as e:
            logger.error(f"Failed to open MIDI port: {e}")
            return False
    
    def close(self) -> None:
        """Close the MIDI output port"""
        if self._port:
            self._port.close_port()
    
    def send(self, message: MIDIMessage) -> None:
        """
        Send a MIDI message.
        
        Args:
            message: MIDIMessage to send
        """
        if self._port:
            self._port.send_message(list(message.to_bytes()))
    
    def send_raw(self, data: bytes) -> None:
        """
        Send raw MIDI bytes.
        
        Args:
            data: MIDI bytes
        """
        if self._port:
            self._port.send_message(list(data))
    
    def note_on(self, note: int, velocity: int = 100, channel: int = 0) -> None:
        """Send Note On message"""
        self.send(MIDIMessage('note_on', channel, note, velocity))
    
    def note_off(self, note: int, velocity: int = 0, channel: int = 0) -> None:
        """Send Note Off message"""
        self.send(MIDIMessage('note_off', channel, note, velocity))
    
    def cc(self, controller: int, value: int, channel: int = 0) -> None:
        """Send Control Change message"""
        self.send(MIDIMessage('cc', channel, controller, value))
    
    def program_change(self, program: int, channel: int = 0) -> None:
        """Send Program Change message"""
        msg = MIDIMessage('program', channel, program, 0)
        if self._port:
            status = 0xC0 | (channel & 0x0F)
            self._port.send_message([status, program & 0x7F])
    
    def pitchbend(self, value: int, channel: int = 0) -> None:
        """
        Send Pitchbend message.
        
        Args:
            value: -8192 to 8191 (0 = center)
            channel: MIDI channel
        """
        # Convert to 14-bit value (0-16383, center at 8192)
        pb = max(0, min(16383, value + 8192))
        lsb = pb & 0x7F
        msb = (pb >> 7) & 0x7F
        
        if self._port:
            status = 0xE0 | (channel & 0x0F)
            self._port.send_message([status, lsb, msb])
    
    def all_notes_off(self, channel: int = 0) -> None:
        """Send All Notes Off CC"""
        self.cc(123, 0, channel)
    
    def panic(self) -> None:
        """Send All Notes Off to all channels"""
        for ch in range(16):
            self.all_notes_off(ch)


class MIDIManager:
    """
    High-level MIDI manager for the DAW.
    Handles multiple inputs/outputs and MIDI learn.
    """
    
    def __init__(self):
        self.input = MIDIInput()
        self.output = MIDIOutput()
        self._learning = False
        self._learn_callback: Optional[Callable[[MIDIMessage], None]] = None
        self._cc_mappings: Dict[Tuple[int, int], Callable[[int], None]] = {}
    
    @property
    def available(self) -> bool:
        """Check if MIDI is available"""
        return self.input.available or self.output.available
    
    def list_all_ports(self) -> Dict[str, List[MIDIDevice]]:
        """List all available MIDI ports"""
        return {
            'inputs': self.input.list_ports(),
            'outputs': self.output.list_ports(),
        }
    
    def setup(
        self,
        input_port: Optional[int] = None,
        output_port: Optional[int] = None
    ) -> bool:
        """
        Setup MIDI ports.
        
        Args:
            input_port: Input port index (None to skip)
            output_port: Output port index (None to skip)
        
        Returns:
            True if all requested ports opened successfully
        """
        success = True
        
        if input_port is not None:
            if not self.input.open(input_port):
                success = False
            else:
                self.input.set_callback(self._handle_input)
        
        if output_port is not None:
            if not self.output.open(output_port):
                success = False
        
        return success
    
    def close(self) -> None:
        """Close all MIDI ports"""
        self.input.close()
        self.output.close()
    
    def _handle_input(self, msg: MIDIMessage) -> None:
        """Internal input handler"""
        # MIDI Learn mode
        if self._learning and self._learn_callback:
            self._learn_callback(msg)
            return
        
        # Check CC mappings
        if msg.type == 'cc':
            key = (msg.channel, msg.data1)
            if key in self._cc_mappings:
                try:
                    self._cc_mappings[key](msg.data2)
                except Exception as e:
                    logger.error(f"Error in CC callback: {e}")
    
    def start_learn(self, callback: Callable[[MIDIMessage], None]) -> None:
        """
        Start MIDI learn mode.
        
        Args:
            callback: Function called when MIDI message received
        """
        self._learning = True
        self._learn_callback = callback
    
    def stop_learn(self) -> None:
        """Stop MIDI learn mode"""
        self._learning = False
        self._learn_callback = None
    
    def map_cc(
        self,
        channel: int,
        cc_number: int,
        callback: Callable[[int], None]
    ) -> None:
        """
        Map a CC to a callback.
        
        Args:
            channel: MIDI channel
            cc_number: CC number
            callback: Function called with CC value (0-127)
        """
        self._cc_mappings[(channel, cc_number)] = callback
    
    def unmap_cc(self, channel: int, cc_number: int) -> None:
        """Remove CC mapping"""
        key = (channel, cc_number)
        if key in self._cc_mappings:
            del self._cc_mappings[key]
    
    def clear_mappings(self) -> None:
        """Clear all CC mappings"""
        self._cc_mappings.clear()


# Singleton manager
_manager: Optional[MIDIManager] = None


def get_midi_manager() -> MIDIManager:
    """Get the global MIDI manager instance"""
    global _manager
    if _manager is None:
        _manager = MIDIManager()
    return _manager


# Quick access functions
def list_midi_devices() -> Dict[str, List[MIDIDevice]]:
    """List all MIDI devices"""
    return get_midi_manager().list_all_ports()


def open_midi(
    input_port: Optional[int] = None,
    output_port: Optional[int] = None
) -> bool:
    """Quick MIDI setup"""
    return get_midi_manager().setup(input_port, output_port)


def close_midi() -> None:
    """Close all MIDI"""
    get_midi_manager().close()
