
import os
import datetime
import pathlib

from .utils import path_to_dict

class WLT_RHTHYM_MANAGER(object):
    """This thing tracks input timing for rhythm invoke."""

    # 1,000 microseconds per millisecond
    # 0.5 seconds == 500 milliseconds == 500,000 microseconds
    quick_threshold = datetime.timedelta(days=0, seconds=0, microseconds=300000)
    hold_threshold = datetime.timedelta(days=0, seconds=0, microseconds=700000)
    timeout_threshold = datetime.timedelta(days=0, seconds=1, microseconds=0)
    timeout = False # Starts as a bool, gets turned into a timer.

    # The elapsed time between presses as a timedelta object.
    # If the delta is larger than one day, we pitch it.
    last_tap = datetime.datetime.now()

    # normalized 0-1 range
    pressure_threshold_hard = 0.75
    pressure_min = 0.05
    use_pressure = False

    # It's a string, so we can use string-analysis functions to identify sequences,
    # without throwing away the whole string every time there's a match.
    input_sequence = ""

    # By default, we don't care about the specific keys being, pressed. The operator does that.
    multi_key = False

    # Populated with a JSON file.
    combo_dict = {}
    # combo_dict_path = os.path.dirname(os.path.realpath(__file__)) + "\\rhythm_combos.JSON"
    combo_dict_path = pathlib.Path(os.path.realpath(__file__)).parents[1] / 'cfg' / 'rhythm_combos.JSON'

    # Legend:
    # F: First Key in the sequence
    # Q: Quickly Pressed Key
    # S: Slowly Pressed Key
    # H: Held Key

    def __init__(self):
        self.combo_dict = path_to_dict(self.combo_dict_path)


    def add_input(self):
        """Meant to be called directly from operators, not for input simulation."""
        seq = self.input_sequence
        last_tap = self.last_tap

        now = datetime.datetime.now()
        delta = now - last_tap

        if delta.days > 1:
            seq = "F"            
        else:
            if delta > self.timeout_threshold:
                self.input_sequence = "F"
            elif delta < self.quick_threshold:
                self.input_sequence += "Q"
            elif (delta < self.timeout_threshold):
                self.input_sequence += "S"

        self.last_tap = now

        print("Current Sequence: " + self.input_sequence)


    def check_sequence(self):
        """Checks the current sequence against a dict of seqence:operator configurations"""
        combo_dict = self.combo_dict
        seq = self.input_sequence

        self.timeout = False
        print("Checking Combo")

        # First see if there's an exact match
        if seq in combo_dict.keys():
            op = combo_dict[seq]
            return op


        # Fallback to checking for single-wildcard matches
        if "*" + seq in combo_dict.keys():
            op = combo_dict[seq]
            return op

        # If there isn't see if we have any partial matches
        # for sequence in combo_dict.keys():
        #     index = sequence.find(seq)

        #     if index == -1:
        #         continue

        #     if index + len(seq) -1 == len(sequence) -1:
        #         op = combo_dict[sequence]
        #         return op
