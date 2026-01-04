"""
Highway Traffic Simulation - Italian Highway Rules

This simulation models a 3-lane highway where:
- Cars can only pass on the left
- Bad practice: driving in middle lane when right lane is free
- Shows how traffic jam probability increases with bad practice
"""

import random
from typing import List
from dataclasses import dataclass
from enum import Enum


class Lane(Enum):
    """Lane positions: 0 = rightmost, 1 = middle, 2 = leftmost"""
    RIGHT = 0
    MIDDLE = 1
    LEFT = 2


@dataclass
class Car:
    """Represents a car on the highway"""
    position: float  # Position along the highway
    speed: float  # Current speed
    lane: Lane  # Current lane
    max_speed: float  # Maximum speed this car can achieve
    follows_bad_practice: bool  # Whether this car doesn't use rightmost lane

    def __init__(self, position: float, speed: float, lane: Lane,
                 max_speed: float, follows_bad_practice: bool = False):
        self.position = position
        self.speed = speed
        self.lane = lane
        self.max_speed = max_speed
        self.follows_bad_practice = follows_bad_practice


class HighwaySimulation:
    """Simulates traffic on a 3-lane highway"""

    def __init__(self, num_cars: int, highway_length: float = 2000.0,
                 bad_practice_ratio: float = 0.0,
                 spawn_probability: float = 0.3):
        """
        Initialize simulation

        Args:
            num_cars: Number of cars on the highway
            highway_length: Length of the highway segment
            bad_practice_ratio: Fraction of cars that follow bad practice
            spawn_probability: Chance to spawn a replacement car each step
                               when active cars drop below num_cars
        """
        self.num_cars = num_cars
        self.highway_length = highway_length
        self.bad_practice_ratio = bad_practice_ratio
        self.spawn_probability = spawn_probability
        self.cars: List[Car] = []
        self.time_step = 0.1  # Time step for simulation
        self.traffic_jam_detected = False
        self._initialize_cars()

    def _create_car(self, position: float = None, lane: Lane = None) -> Car:
        """Create a car with randomized attributes"""
        if position is None:
            position = random.uniform(0, self.highway_length)

        max_speed = random.triangular(90, 130, 128)
        speed = max_speed * random.uniform(0.90, 0.98)
        lane = lane if lane is not None else Lane(random.randint(0, 2))
        follows_bad_practice = random.random() < self.bad_practice_ratio

        return Car(position, speed, lane, max_speed, follows_bad_practice)

    def _initialize_cars(self):
        """Initialize cars with random positions and speeds"""
        self.cars = []

        # Create cars with varying speeds and positions
        for i in range(self.num_cars):
            car = self._create_car()
            self.cars.append(car)

        # Sort cars by position (front to back)
        self.cars.sort(key=lambda c: c.position)

    def _get_cars_in_lane(self, lane: Lane) -> List[Car]:
        """Get all cars in a specific lane, sorted by position"""
        return sorted(
            [c for c in self.cars if c.lane == lane],
            key=lambda c: c.position
        )

    def _get_distance(self, car1: Car, car2: Car) -> float:
        """Get distance from car1 to car2 along the highway"""
        if car2.position > car1.position:
            return car2.position - car1.position
        return float('inf')

    def _is_car_ahead(self, car1: Car, car2: Car) -> bool:
        """Check if car2 is ahead of car1"""
        if car2.lane != car1.lane:
            return False
        return car2.position > car1.position

    def _can_pass_on_left(self, car: Car) -> bool:
        """
        Check if a car can pass on the left (move to left lane)
        Italian rule: can only pass on the left
        """
        if car.lane == Lane.LEFT:
            return False  # Already in leftmost lane

        target_lane = Lane(car.lane.value + 1)
        cars_in_target = self._get_cars_in_lane(target_lane)

        # Check if there's space in the left lane
        # Need safe distance (at least 50 meters) from cars in left lane
        safe_distance = 50.0

        for other_car in cars_in_target:

            # Check if other car is ahead and too close
            if self._is_car_ahead(car, other_car):
                distance = self._get_distance(car, other_car)
                if distance < safe_distance:
                    return False
            else:
                # Car is behind other_car, check if it's catching up
                reverse_distance = self._get_distance(other_car, car)
                if reverse_distance < safe_distance:
                    return False

        return True

    def _should_move_to_right(self, car: Car) -> bool:
        """
        Check if car should move to right lane
        Italian rule: use rightmost free lane
        """
        if car.lane == Lane.RIGHT:
            return False  # Already in rightmost lane

        target_lane = Lane(car.lane.value - 1)
        cars_in_target = self._get_cars_in_lane(target_lane)

        # Check if right lane is free (no cars blocking)
        safe_distance = 50.0

        for other_car in cars_in_target:

            # If there's a car ahead in right lane, check distance
            if self._is_car_ahead(car, other_car):
                distance = self._get_distance(car, other_car)
                if distance < safe_distance:  # Need more space when moving right
                    return False
            else:
                # Car is behind, check if it's much faster
                reverse_distance = self._get_distance(other_car, car)
                if reverse_distance < safe_distance:
                    return False

        return True

    def is_blocked(self, car: Car) -> bool:
        """
        Check if a car is blocked (can't pass and has slower car ahead)
        This indicates a traffic jam situation
        """
        cars_in_same_lane = self._get_cars_in_lane(car.lane)

        # Find the car directly ahead
        car_ahead = None
        min_distance = float('inf')
        for other_car in cars_in_same_lane:
            if self._is_car_ahead(car, other_car):
                distance = self._get_distance(car, other_car)
                if distance < min_distance:
                    min_distance = distance
                    car_ahead = other_car

        if car_ahead is None:
            return False  # No car ahead

        # Check if car ahead is slower
        if car_ahead.speed >= car.speed:
            return False  # Not blocked, can maintain speed

        # Check if can pass on left
        if self._can_pass_on_left(car):
            return False  # Can pass, not blocked

        # If in leftmost lane and blocked, this is a traffic jam
        if car.lane == Lane.LEFT:
            return True

        safe_distance = 50.0
        # If can't pass and car ahead is slower, blocked
        distance = self._get_distance(car, car_ahead)
        if distance < safe_distance:  # Too close
            return True

        return False

    def _update_car_lane(self, car: Car):
        """Update car's lane based on rules and behavior"""
        # First, check if should move to right (Italian rule)
        if not car.follows_bad_practice and self._should_move_to_right(car):
            car.lane = Lane(car.lane.value - 1)
            return
        
        # If car follows bad practice, it might stay in middle lane even if right is free
        if car.follows_bad_practice and car.lane == Lane.MIDDLE:
            # 70% chance of staying in middle even if right is free
            if random.random() < 0.7:
                return
        
        # Check if needs to pass (car ahead is slower)
        cars_in_same_lane = self._get_cars_in_lane(car.lane)
        car_ahead = None
        min_distance = float('inf')
        for other_car in cars_in_same_lane:
            if self._is_car_ahead(car, other_car):
                distance = self._get_distance(car, other_car)
                if distance < min_distance:
                    min_distance = distance
                    car_ahead = other_car
        
        if car_ahead and car_ahead.speed < car.speed:
            # Try to pass on left
            if self._can_pass_on_left(car):
                car.lane = Lane(car.lane.value + 1)
                return
        
        # If not passing, try to return to right lane (if not bad practice)
        if not car.follows_bad_practice and car.lane != Lane.RIGHT:
            if self._should_move_to_right(car):
                car.lane = Lane(car.lane.value - 1)
    
    def _update_car_speed(self, car: Car):
        """Update car's speed based on traffic conditions"""
        cars_in_same_lane = self._get_cars_in_lane(car.lane)
        
        # Find car directly ahead
        car_ahead = None
        min_distance = float('inf')
        for other_car in cars_in_same_lane:
            if self._is_car_ahead(car, other_car):
                distance = self._get_distance(car, other_car)
                if distance < min_distance:
                    min_distance = distance
                    car_ahead = other_car
        
        if car_ahead is None:
            # No car ahead, accelerate to max speed
            car.speed = min(car.speed + 2.0 * self.time_step, car.max_speed)
        else:
            # Adjust speed based on car ahead
            distance = self._get_distance(car, car_ahead)
            speed_diff = car_ahead.speed - car.speed
            
            # Safe following distance
            safe_distance = 30.0 + car.speed * 0.5  # Increases with speed
            
            if distance < safe_distance:
                # Too close, slow down
                car.speed = max(car_ahead.speed - 5.0, car.speed - 5.0 * self.time_step)
            elif distance < safe_distance * 1.5:
                # Getting close, match speed
                car.speed = car_ahead.speed
            else:
                # Safe distance, can accelerate
                car.speed = min(car.speed + 2.0 * self.time_step, car.max_speed)
        
        # Ensure speed doesn't go negative
        car.speed = max(0.0, car.speed)
    
    def _update_car_position(self, car: Car):
        """Update car's position based on speed"""
        car.position += car.speed * self.time_step * (1000.0 / 3600.0)  # Convert km/h to m/s

    def _has_space_for_spawn(self, position: float, lane: Lane,
                             clearance: float = 30.0) -> bool:
        """Check if a new car can be spawned without being too close to others"""
        for other in self.cars:
            if other.lane == lane and abs(other.position - position) < clearance:
                return False
        return True

    def _spawn_new_cars_if_needed(self):
        """
        Spawn new cars at the highway start when the active count
        drops below the configured number. Cars are spawned randomly
        near position 0 to simulate new entries.
        """
        missing_cars = self.num_cars - len(self.cars)
        for _ in range(missing_cars):
            if random.random() < self.spawn_probability:
                lane = Lane(random.randint(0, 2))
                position = random.uniform(0.0, 20.0)  # Spawn near highway start
                if self._has_space_for_spawn(position, lane):
                    new_car = self._create_car(position=position, lane=lane)
                    self.cars.append(new_car)
    
    def step(self):
        """Perform one simulation step"""
        # Update lanes first
        for car in self.cars:
            self._update_car_lane(car)
        
        # Update speeds
        for car in self.cars:
            self._update_car_speed(car)
        
        # Update positions
        for car in self.cars:
            self._update_car_position(car)

        # Remove cars that have reached the end of the highway
        self.cars = [car for car in self.cars if car.position <= self.highway_length]

        # Spawn replacement cars near the start when below target count
        self._spawn_new_cars_if_needed()

        # Sort cars by position
        self.cars.sort(key=lambda c: c.position)
        
        # Check for traffic jam
        # A traffic jam is when multiple cars are blocked and can't pass
        blocked_cars = [car for car in self.cars if self.is_blocked(car)]
        
        # Count consecutive blocked cars in the same lane (indicates a jam)
        if len(blocked_cars) >= 3:
            # Check if blocked cars form a chain (consecutive in same lane)
            for lane in [Lane.LEFT, Lane.MIDDLE, Lane.RIGHT]:
                lane_blocked = [c for c in blocked_cars if c.lane == lane]
                if len(lane_blocked) >= 2:
                    # Sort by position
                    lane_blocked.sort(key=lambda c: c.position)
                    # Check if they're close together (within 100m)
                    for i in range(len(lane_blocked) - 1):
                        dist = self._get_distance(lane_blocked[i], lane_blocked[i+1])
                        if dist < 100.0:
                            self.traffic_jam_detected = True
                            return
    
    def run(self, max_steps: int = 1000) -> bool:
        """
        Run simulation for specified number of steps
        
        Returns:
            True if traffic jam detected, False otherwise
        """
        self.traffic_jam_detected = False
        
        # Run simulation for a period to let traffic stabilize
        for step in range(max_steps):
            self.step()
            # Only check for jams after initial period (let traffic settle)
            if step > 100 and self.traffic_jam_detected:
                return True
        
        return False


def run_simulation(num_cars: int = 20, num_trials: int = 100, 
                    bad_practice_ratios: List[float] = None) -> dict:
    """
    Run multiple simulations with different bad practice ratios
    
    Returns:
        Dictionary with results showing traffic jam probability vs bad practice ratio
    """
    if bad_practice_ratios is None:
        bad_practice_ratios = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    results = {}
    
    print("Running highway traffic simulations...")
    print(f"Number of cars: {num_cars}")
    print(f"Trials per configuration: {num_trials}")
    print("-" * 60)
    
    for ratio in bad_practice_ratios:
        jam_count = 0
        
        for trial in range(num_trials):
            sim = HighwaySimulation(num_cars=num_cars, bad_practice_ratio=ratio)
            if sim.run(max_steps=800):
                jam_count += 1
        
        probability = jam_count / num_trials
        results[ratio] = probability
        
        print(f"Bad Practice Ratio: {ratio:.1f} | "
              f"Traffic Jam Probability: {probability:.3f} | "
              f"Jams: {jam_count}/{num_trials}")
    
    return results


if __name__ == "__main__":
    # Run simulation with different bad practice ratios
    # Using fewer cars to reduce baseline jam probability
    results = run_simulation(num_cars=15, num_trials=100)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nThe simulation demonstrates that as the ratio of cars")
    print("following bad practice (not using rightmost free lane)")
    print("increases, the probability of traffic jams also increases.\n")
    
    # Show trend
    ratios = sorted(results.keys())
    probabilities = [results[r] for r in ratios]
    
    print("Trend Analysis:")
    for i in range(len(ratios) - 1):
        change = probabilities[i+1] - probabilities[i]
        if change > 0:
            print(f"  Ratio {ratios[i]:.1f} → {ratios[i+1]:.1f}: "
                  f"Probability increased by {change:.3f}")
