import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import RegisterEventHandler
from launch_ros.actions import Node
from launch.event_handlers import (OnProcessExit, OnProcessStart)

def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled

    package_name='articubot_one' 

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             )

    load_joint_state_controller = ExecuteProcess(cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                                                 'joint_broad'],
                                                 output="screen")

    load_arm_controller = ExecuteProcess(cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                                                 'diff_cont'],
                                                 output="screen")
    
    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot'],
                        output='screen')

    # Launch them all!
    return LaunchDescription([
        RegisterEventHandler(event_handler=OnProcessExit(target_action=spawn_entity, on_exit=[load_joint_state_controller])),
        RegisterEventHandler(event_handler=OnProcessExit(target_action=load_joint_state_controller, on_exit=[load_arm_controller])),
        gazebo,
        rsp,
        spawn_entity
    ])