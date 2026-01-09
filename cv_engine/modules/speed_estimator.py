import time
from cv_engine import config

class SpeedEstimator:
    def __init__(self):
        # Stores { vehicle_id: start_frame_number }
        self.entry_times = {}
        
        # Stores { vehicle_id: 'A' or 'B' } to know which line they crossed first
        self.entry_lines = {}
        
        # Stores { vehicle_id: calculated_speed_kmh }
        self.vehicle_speeds = {}
        
        # Cache line coordinates
        self.line_a_start = config.LINE_A[0]
        self.line_a_end = config.LINE_A[1]
        self.line_b_start = config.LINE_B[0]
        self.line_b_end = config.LINE_B[1]

        # Keep track of previous positions { vehicle_id: (x, y) }
        self.previous_positions = {}

    def get_orientation(self, p, line_start, line_end):
        """
        Cross product to determine side of line.
        """
        x, y = p
        x1, y1 = line_start
        x2, y2 = line_end
        return (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)

    def _has_crossed(self, curr_pos, prev_pos, line_start, line_end):
        """
        Returns True if the segment (prev_pos -> curr_pos) crosses the line.
        """
        curr_o = self.get_orientation(curr_pos, line_start, line_end)
        prev_o = self.get_orientation(prev_pos, line_start, line_end)
        
        # Check if signs are different (one positive, one negative)
        # We use strict inequality for one to handle exact 0 edge cases
        return (curr_o > 0 and prev_o <= 0) or (curr_o < 0 and prev_o >= 0)

    def estimate_speed(self, vehicle_id, track_point, current_frame_num, fps):
        """
        track_point: Should be Bottom-Center (cx, y2) for accuracy
        """
        if vehicle_id not in self.previous_positions:
            self.previous_positions[vehicle_id] = track_point
            return None

        prev_point = self.previous_positions[vehicle_id]
        current_speed = self.vehicle_speeds.get(vehicle_id, None)

        # 1. Check Crossing Line A
        if self._has_crossed(track_point, prev_point, self.line_a_start, self.line_a_end):
            if vehicle_id not in self.entry_times:
                # ENTRY EVENT at A
                self.entry_times[vehicle_id] = current_frame_num
                self.entry_lines[vehicle_id] = 'A'
            elif self.entry_lines.get(vehicle_id) == 'B':
                # EXIT EVENT at A (Entered at B)
                current_speed = self._calculate(vehicle_id, current_frame_num, fps)

        # 2. Check Crossing Line B
        elif self._has_crossed(track_point, prev_point, self.line_b_start, self.line_b_end):
            if vehicle_id not in self.entry_times:
                # ENTRY EVENT at B
                self.entry_times[vehicle_id] = current_frame_num
                self.entry_lines[vehicle_id] = 'B'
            elif self.entry_lines.get(vehicle_id) == 'A':
                # EXIT EVENT at B (Entered at A)
                current_speed = self._calculate(vehicle_id, current_frame_num, fps)

        # Update position
        self.previous_positions[vehicle_id] = track_point
        return current_speed

    def _calculate(self, vehicle_id, current_frame, fps):
        start_frame = self.entry_times[vehicle_id]
        frames_passed = abs(current_frame - start_frame)
        
        # Filter: Ignore impossibly fast teleportation (e.g. < 3 frames)
        if frames_passed > 3:
            time_seconds = frames_passed / fps
            speed_mps = config.REAL_DISTANCE_METERS / time_seconds
            speed_kmh = speed_mps * 3.6
            
            # Speeds appear as: 20, 25, 30, 35 km/h
            self.vehicle_speeds[vehicle_id] = int(round(speed_kmh / 5) * 5)
            
            return int(round(speed_kmh / 5) * 5)
        return None