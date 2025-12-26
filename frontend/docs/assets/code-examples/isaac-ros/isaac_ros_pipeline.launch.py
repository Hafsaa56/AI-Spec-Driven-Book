"""
Isaac ROS Pipeline Launch File

This launch file demonstrates how to launch an Isaac ROS perception pipeline.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Generate launch description for Isaac ROS pipeline
    """
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true'
    )

    # Isaac ROS stereo disparity node
    stereo_disparity_node = Node(
        package='isaac_ros_examples',
        executable='stereo_disparity_node',
        name='isaac_ros_stereo_disparity',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        remappings=[
            ('/camera/left/image_rect_color', '/camera/left/image_raw'),
            ('/camera/right/image_rect_color', '/camera/right/image_raw'),
        ],
        output='screen'
    )

    # Isaac ROS object detection node
    object_detection_node = Node(
        package='isaac_ros_examples',
        executable='object_detection_node',
        name='isaac_ros_object_detection',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        remappings=[
            ('/camera/image_raw', '/camera/color/image_raw'),
        ],
        output='screen'
    )

    # Isaac ROS point cloud generation from disparity
    point_cloud_node = Node(
        package='isaac_ros_examples',
        executable='point_cloud_node',
        name='isaac_ros_point_cloud',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        stereo_disparity_node,
        object_detection_node,
        point_cloud_node
    ])