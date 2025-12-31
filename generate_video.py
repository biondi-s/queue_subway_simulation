"""
Video generation for highway traffic simulation

Creates an animated video showing cars on a 3-lane highway,
demonstrating how traffic jams form based on bad driving practices.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
import numpy as np
from highway_simulation import HighwaySimulation, Lane, Car


class HighwayVisualizer:
    """Visualizes highway simulation as an animated video"""
    
    def __init__(self, sim: HighwaySimulation, fps: int = 10, duration: float = 30.0):
        """
        Initialize visualizer
        
        Args:
            sim: HighwaySimulation instance
            fps: Frames per second for video
            duration: Duration of video in seconds
        """
        self.sim = sim
        self.fps = fps
        self.duration = duration
        self.total_frames = int(fps * duration)
        self.current_frame = 0
        
        # Color scheme
        self.lane_colors = {
            Lane.RIGHT: '#e8e8e8',   # Light gray
            Lane.MIDDLE: '#d0d0d0',  # Medium gray
            Lane.LEFT: '#b8b8b8'     # Darker gray
        }
        self.car_color_normal = '#2E86AB'      # Blue
        self.car_color_bad_practice = '#A23B72'  # Purple
        self.car_color_blocked = '#F18F01'      # Orange
        self.car_color_jam = '#C73E1D'         # Red
        
        # Setup figure
        self.fig, self.ax = plt.subplots(figsize=(16, 6))
        self.ax.set_xlim(0, sim.highway_length)
        self.ax.set_ylim(-0.5, 2.5)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Draw highway lanes
        self._draw_highway()
        
        # Statistics text
        self.stats_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                       fontsize=10, verticalalignment='top',
                                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Title
        self.title_text = self.ax.text(0.5, 0.95, 'Highway Traffic Simulation - Italian Rules',
                                      transform=self.ax.transAxes,
                                      fontsize=14, fontweight='bold',
                                      horizontalalignment='center',
                                      bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Car markers (will be updated in animation)
        self.car_markers = []
        self.speed_texts = []
        
    def _draw_highway(self):
        """Draw the 3-lane highway"""
        # Draw lane backgrounds
        for lane_idx, lane in enumerate([Lane.RIGHT, Lane.MIDDLE, Lane.LEFT]):
            rect = Rectangle((0, lane_idx - 0.4), self.sim.highway_length, 0.8,
                           facecolor=self.lane_colors[lane], edgecolor='black', linewidth=1)
            self.ax.add_patch(rect)
            
            # Lane labels
            self.ax.text(self.sim.highway_length * 0.01, lane_idx, 
                        ['Right', 'Middle', 'Left'][lane_idx],
                        fontsize=8, fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        # Draw lane dividers
        for y in [0.5, 1.5]:
            self.ax.plot([0, self.sim.highway_length], [y, y], 
                        'k--', linewidth=1, alpha=0.5)
    
    def _get_car_color(self, car: Car) -> str:
        """Get color for car based on its state"""
        if self.sim.is_blocked(car):
            # Check if part of a jam
            blocked_cars = [c for c in self.sim.cars if self.sim.is_blocked(c)]
            if len(blocked_cars) >= 2:
                for lane in [Lane.LEFT, Lane.MIDDLE, Lane.RIGHT]:
                    lane_blocked = [c for c in blocked_cars if c.lane == lane]
                    if len(lane_blocked) >= 2 and car in lane_blocked:
                        lane_blocked.sort(key=lambda c: c.position)
                        for i in range(len(lane_blocked) - 1):
                            dist = self.sim._get_distance(lane_blocked[i], lane_blocked[i+1])
                            if dist < 100.0:
                                return self.car_color_jam
            return self.car_color_blocked
        elif car.follows_bad_practice:
            return self.car_color_bad_practice
        else:
            return self.car_color_normal
    
    def _update_frame(self, frame_num):
        """Update animation frame"""
        # Clear previous car markers
        for marker in self.car_markers:
            marker.remove()
        self.car_markers.clear()
        
        for text in self.speed_texts:
            text.remove()
        self.speed_texts.clear()
        
        # Run simulation step
        if frame_num > 0:  # Don't step on first frame
            self.sim.step()
        
        # Draw cars
        blocked_count = 0
        bad_practice_count = sum(1 for c in self.sim.cars if c.follows_bad_practice)
        
        for car in self.sim.cars:
            # Car position
            x = car.position
            y = car.lane.value
            
            # Car color based on state
            color = self._get_car_color(car)
            
            if self.sim.is_blocked(car):
                blocked_count += 1
            
            # Draw car as rectangle
            car_width = 15.0  # meters
            car_height = 0.3
            car_rect = Rectangle((x - car_width/2, y - car_height/2), 
                               car_width, car_height,
                               facecolor=color, edgecolor='black', linewidth=1.5)
            self.ax.add_patch(car_rect)
            self.car_markers.append(car_rect)
            
            # Draw speed indicator (small circle)
            speed_ratio = car.speed / car.max_speed
            speed_circle = Circle((x, y + 0.25), 0.08, 
                                facecolor=color, edgecolor='black', linewidth=0.5)
            self.ax.add_patch(speed_circle)
            self.car_markers.append(speed_circle)
            
            # Speed text (show for some cars to avoid clutter)
            if frame_num % 5 == 0:  # Show every 5th frame
                speed_text = self.ax.text(x, y - 0.35, f'{int(car.speed)}',
                                         fontsize=6, ha='center',
                                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
                self.speed_texts.append(speed_text)
        
        # Update statistics
        time_elapsed = frame_num * self.sim.time_step
        stats = (f"Time: {time_elapsed:.1f}s | "
                f"Cars: {len(self.sim.cars)} | "
                f"Blocked: {blocked_count} | "
                f"Bad Practice: {bad_practice_count} | "
                f"Jam: {'YES' if self.sim.traffic_jam_detected else 'NO'}")
        self.stats_text.set_text(stats)
        
        # Update title with jam status
        if self.sim.traffic_jam_detected:
            self.title_text.set_text('Highway Traffic Simulation - TRAFFIC JAM DETECTED!')
            self.title_text.set_bbox(dict(boxstyle='round', facecolor='red', alpha=0.8))
        else:
            self.title_text.set_text('Highway Traffic Simulation - Italian Rules')
            self.title_text.set_bbox(dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        return self.car_markers + self.speed_texts + [self.stats_text, self.title_text]
    
    def create_animation(self, output_file: str = 'highway_simulation.mp4'):
        """Create and save animation"""
        print(f"Creating animation: {self.total_frames} frames at {self.fps} fps")
        print(f"Output file: {output_file}")
        
        # Create animation
        anim = animation.FuncAnimation(
            self.fig, self._update_frame, frames=self.total_frames,
            interval=1000/self.fps, blit=False, repeat=False
        )
        
        # Save video
        print("Rendering video (this may take a while)...")
        try:
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=self.fps, metadata=dict(artist='Highway Simulation'),
                          bitrate=1800)
            anim.save(output_file, writer=writer)
            print(f"✓ Video saved successfully: {output_file}")
        except Exception as e:
            print(f"Error saving video: {e}")
            print("Trying alternative method with Pillow writer...")
            try:
                Writer = animation.writers['pillow']
                writer = Writer(fps=self.fps)
                anim.save(output_file.replace('.mp4', '.gif'), writer=writer)
                print(f"✓ Animation saved as GIF: {output_file.replace('.mp4', '.gif')}")
            except Exception as e2:
                print(f"Error: {e2}")
                print("Please install ffmpeg for MP4 output: brew install ffmpeg")
                print("Or the video will be saved as individual frames")
        
        plt.close(self.fig)


def generate_simulation_video(num_cars: int = 15, bad_practice_ratio: float = 0.6,
                              highway_length: float = 2000.0, fps: int = 10,
                              duration: float = 30.0, output_file: str = 'highway_simulation.mp4',
                              seed: int = None):
    """
    Generate a video of a highway simulation
    
    Args:
        num_cars: Number of cars on highway
        bad_practice_ratio: Fraction of cars following bad practice
        highway_length: Length of highway in meters
        fps: Frames per second
        duration: Video duration in seconds
        output_file: Output video filename
        seed: Random seed for reproducibility
    """
    if seed is not None:
        import random
        random.seed(seed)
        np.random.seed(seed)
    
    print("=" * 60)
    print("HIGHWAY TRAFFIC SIMULATION - VIDEO GENERATION")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Cars: {num_cars}")
    print(f"  Bad Practice Ratio: {bad_practice_ratio:.1%}")
    print(f"  Highway Length: {highway_length}m")
    print(f"  Video: {duration}s @ {fps} fps")
    print("=" * 60)
    
    # Create simulation
    sim = HighwaySimulation(num_cars=num_cars, 
                           highway_length=highway_length,
                           bad_practice_ratio=bad_practice_ratio)
    
    # Create visualizer
    visualizer = HighwayVisualizer(sim, fps=fps, duration=duration)
    
    # Generate video
    visualizer.create_animation(output_file)
    
    print("\n" + "=" * 60)
    print("VIDEO GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nLegend:")
    print(f"  Blue cars: Normal drivers (follow rules)")
    print(f"  Purple cars: Bad practice (don't use rightmost lane)")
    print(f"  Orange cars: Blocked (can't pass)")
    print(f"  Red cars: Part of traffic jam")
    print(f"\nOutput: {output_file}")


if __name__ == "__main__":
    # Generate a demonstration video
    # Using higher bad practice ratio to show traffic jam formation
    generate_simulation_video(
        num_cars=15,
        bad_practice_ratio=0.6,  # 60% bad practice to show effect
        highway_length=2000.0,
        fps=10,
        duration=30.0,
        output_file='highway_simulation.mp4',
        seed=42  # For reproducibility
    )

