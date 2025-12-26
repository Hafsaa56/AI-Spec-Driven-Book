#!/usr/bin/env python3
"""
Domain Randomization for NVIDIA Isaac Sim

This script demonstrates domain randomization techniques to improve sim-to-real transfer.
"""

import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.objects import VisualCuboid
from omni.isaac.core.materials import PhysicsMaterial
import numpy as np


class DomainRandomizer:
    """
    A class to implement domain randomization in Isaac Sim
    """
    def __init__(self, world):
        self.world = world
        self.objects = []
        self.materials = []

    def add_random_objects(self, count=10):
        """
        Add objects with randomized visual and physical properties
        """
        for i in range(count):
            # Random position
            position = np.random.uniform(-1.0, 1.0, 3)
            position[2] = 0.5  # Set z to appropriate height

            # Random size
            size = np.random.uniform(0.05, 0.2, 1)[0]

            # Random color
            color = np.random.rand(3)

            # Create object
            obj = VisualCuboid(
                prim_path=f"/World/Object_{i}",
                name=f"object_{i}",
                position=position,
                size=size,
                color=color
            )

            self.objects.append(obj)

    def randomize_physics_properties(self):
        """
        Randomize physics properties like friction and restitution
        """
        for i, obj in enumerate(self.objects):
            # Create physics material with randomized properties
            material_path = f"/World/Materials/Material_{i}"

            physics_material = PhysicsMaterial(
                prim_path=material_path,
                static_friction=np.random.uniform(0.1, 1.0),
                dynamic_friction=np.random.uniform(0.1, 1.0),
                restitution=np.random.uniform(0.0, 0.5)
            )

            self.materials.append(physics_material)

    def randomize_lighting(self):
        """
        Randomize lighting conditions in the scene
        """
        # Add random lights to the scene
        for i in range(3):
            light_position = np.random.uniform(-2.0, 2.0, 3)
            light_intensity = np.random.uniform(100, 1000)

            # Create a distant light
            from omni.isaac.core.utils.prims import create_prim
            create_prim(
                prim_path=f"/World/Light_{i}",
                prim_type="DistantLight",
                position=light_position,
                attributes={
                    "intensity": light_intensity,
                    "color": np.random.rand(3)
                }
            )

    def randomize_environment(self):
        """
        Apply all domain randomization techniques
        """
        print("Applying domain randomization...")

        # Add random objects
        self.add_random_objects(5)

        # Randomize physics properties
        self.randomize_physics_properties()

        # Randomize lighting
        self.randomize_lighting()

        print(f"Randomized {len(self.objects)} objects with various properties")


def setup_scene_with_randomization():
    """
    Setup scene with domain randomization
    """
    # Initialize the world
    world = World(stage_units_in_meters=1.0)

    # Get assets root path
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        print("Could not find Isaac Sim assets. Ensure Isaac Sim is properly installed.")
        return None

    # Add a simple environment
    room_path = f"{assets_root_path}/Isaac/Environments/Simple_Room/simple_room.usd"
    add_reference_to_stage(
        usd_path=room_path,
        prim_path="/World/SimpleRoom"
    )

    # Create domain randomizer
    randomizer = DomainRandomizer(world)

    # Apply domain randomization
    randomizer.randomize_environment()

    # Reset the world to apply changes
    world.reset()

    return world, randomizer


def run_randomized_simulation(world, randomizer, num_episodes=5, steps_per_episode=200):
    """
    Run simulation with domain randomization applied periodically
    """
    for episode in range(num_episodes):
        print(f"Starting episode {episode + 1}")

        for step in range(steps_per_episode):
            # Step the simulation
            world.step(render=True)

            # Periodically re-randomize certain aspects
            if step % 100 == 0:
                # Re-randomize lighting every 100 steps
                randomizer.randomize_lighting()

        print(f"Episode {episode + 1} completed")

        # Optionally reset domain randomization for next episode
        if episode < num_episodes - 1:
            # Reset world for next episode
            world.reset()


def main():
    """
    Main function to run domain randomization example
    """
    print("Setting up Isaac Sim with domain randomization...")

    # Setup the scene with randomization
    result = setup_scene_with_randomization()
    if result is None:
        print("Failed to setup scene. Exiting.")
        return

    world, randomizer = result

    try:
        # Run the randomized simulation
        run_randomized_simulation(world, randomizer)
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
    finally:
        # Cleanup
        world.clear()


if __name__ == "__main__":
    main()