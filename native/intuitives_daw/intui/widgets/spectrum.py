from . import _shared
from intlib.math import clip_value, lin_to_db, pitch_to_hz
from intlib.lib import util
from intui.sgqt import *


class spectrum(QGraphicsPathItem):
    """
    PURPOSE: Visualizes real-time frequency distribution (spectrum analysis).
    ACTION: Draws a continuous vector path representing amplitude across the frequency range.
    MECHANISM: 
        1. Inherits from QGraphicsPathItem for efficient scene-based rendering.
        2. Receives raw FFT data via string messages.
        3. Maps linear frequency data to logarithmic pitch-based coordinates for musical relevance.
    """
    def __init__(self, a_height, a_width):
        """Initializes the spectrum item with fixed dimensions and white pen."""
        self.spectrum_height = float(a_height)
        self.spectrum_width = float(a_width)
        QGraphicsPathItem.__init__(self)
        self.setPen(QtCore.Qt.GlobalColor.white)

    def set_spectrum(self, a_message):
        """
        PURPOSE: Updates the visual spectrum path from incoming audio data.
        ACTION: Constructs a new QPainterPath by iterating through FFT bins.
        MECHANISM: 
            1. Parses the pipe-delimited message into amplitude values.
            2. Calculates X positions based on EQ_LOW_PITCH to EQ_HIGH_PITCH range.
            3. Converts linear amplitude to dB and applies frequency-dependent weighting (tilt).
            4. Clamps values and generates a smooth path using lineTo operations.
            5. Updates the graphics item with the new path.
        """
        self.painter_path = QPainterPath(QtCore.QPointF(0.0, 20.0))
        self.values = a_message.split("|")
        self.painter_path.moveTo(0.0, self.spectrum_height)
        f_low = _shared.EQ_LOW_PITCH
        f_high = _shared.EQ_HIGH_PITCH
        f_width_per_point = (self.spectrum_width / float(f_high - f_low))
        f_fft_low = float(util.SAMPLE_RATE) * 0.00024414 # / 4096.0
        f_nyquist = float(util.NYQUIST_FREQ)
        nyquist_recip = 1. / f_nyquist
        f_i = f_low
        while f_i < f_high:
            f_hz = pitch_to_hz(f_i) - f_fft_low
            f_pos = int((f_hz * nyquist_recip) * len(self.values))
            f_val = float(self.values[f_pos])
            f_db = lin_to_db(f_val) - 64.0
            f_db += ((f_i - f_low) * 0.08333333) * 3.0 # / 12.
            f_db = clip_value(f_db, -70.0, 0.0)
            f_val = 1.0 - ((f_db + 70.0) * 0.0142857142) # / 70.
            f_x = f_width_per_point * (f_i - f_low)
            f_y = f_val * self.spectrum_height
            self.painter_path.lineTo(f_x, f_y)
            f_i += 0.5
        self.setPath(self.painter_path)

