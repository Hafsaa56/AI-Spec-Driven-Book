#!/usr/bin/env python3
"""
Basic Scene Setup for NVIDIA Isaac Sim

This script demonstrates how to create a basic scene in Isaac Sim with a robot and environment.
"""

import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.objects import VisualCuboid
import numpy as np


def setup_basic_scene():
    """
    Sets up a basic scene with environment and robot in Isaac Sim
    """
    # Initialize the world
    world = World(stage_units_in_meters=1.0)

    # Get assets root path
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        print("Could not find Isaac Sim assets. Ensure Isaac Sim is properly installed.")
        return None

    # Add a simple room environment
    room_path = f"{assets_root_path}/Isaac/Environments/Simple_Room/simple_room.usd"
    add_reference_to_stage(
        usd_path=room_path,
        prim_path="/World/SimpleRoom"
    )

    # Add a sample robot (UR5e manipulator)
    robot_path = f"{assets_root_path}/Isaac/Robots/UR10/ur10.usd"
    add_reference_to_stage(
        usd_path=robot_path,
        prim_path="/World/UR10"
    )

    # Set robot position
    from omni.isaac.core.robots import Robot
    robot = Robot(prim_path="/World/UR10")

    # Add some objects to interact with
    cube1 = VisualCuboid(
        prim_path="/World/Cube1",
        name="cube1",
        position=np.array([0.5, 0.5, 0.5]),
        size=0.1,
        color=np.array([1.0, 0.0, 0.0])  # Red
    )

    cube2 = VisualCuboid(
        prim_path="/World/Cube2",
        name="cube2",
        position=np.array([-0.5, 0.5, 0.5]),
        size=0.1,
        color=np.array([0.0, 1.0, 0.0])  # Green
    )

    # Reset the world to apply changes
    world.reset()

    return world, robot, [cube1, cube2]


def run_simulation(world, robot, objects, num_iterations=1000):
    """
    Runs the simulation for a specified number of iterations
    """
    for i in range(num_iterations):
        # Step the world
        world.step(render=True)

        # Simple robot movement (in a real application, you would control joints)
        if i % 100 == 0:
            print(f"Simulation step {i}")

        # You can add robot control logic here
        # For example, moving joints, planning paths, etc.

    print("Simulation completed!")


def main():
    """
    Main function to run the basic scene setup
    """
    print("Setting up Isaac Sim scene...")

    # Setup the scene
    result = setup_basic_scene()
    if result is None:
        print("Failed to setup scene. Exiting.")
        return

    world, robot, objects = result

    try:
        # Run the simulation
        run_simulation(world, robot, objects)
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
    finally:
        # Cleanup
        world.clear()


if __name__ == "__main__":
    main()