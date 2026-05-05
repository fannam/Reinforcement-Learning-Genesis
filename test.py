import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.controllers import default_modular_gait
from robotics_genesis.xml_robot import get_1d_joint_names, prepare_mjcf_for_genesis

show_viewer = os.getenv("SHOW_VIEWER", "0") == "1"
if show_viewer:
    os.environ["PYOPENGL_PLATFORM"] = "glx"
    os.environ.setdefault("GALLIUM_DRIVER", "d3d12")
    os.environ.setdefault("MESA_D3D12_DEFAULT_ADAPTER_NAME", "NVIDIA")

import pyglet

pyglet.options["debug_gl"] = False

import genesis as gs


def select_backend(name: str):
    if name == "gpu":
        return gs.gpu
    if name == "cpu":
        return gs.cpu
    raise ValueError("GENESIS_BACKEND must be 'cpu' or 'gpu'")


robot_xml = Path(os.getenv("ROBOT_XML", "robots/modular_humanoid/modular_humanoid.xml"))
if not robot_xml.is_absolute():
    robot_xml = PROJECT_ROOT / robot_xml

joint_order = get_1d_joint_names(robot_xml)
joint_index = {name: index for index, name in enumerate(joint_order)}
gait = default_modular_gait()
genesis_robot_xml = prepare_mjcf_for_genesis(robot_xml, PROJECT_ROOT / "outputs" / "generated")

backend = os.getenv("GENESIS_BACKEND", "cpu").lower()
gs.init(backend=select_backend(backend))

viewer_options = None
if show_viewer:
    viewer_options = gs.options.ViewerOptions(
        run_in_thread=True,
        res=(960, 640),
    )

scene = gs.Scene(show_viewer=show_viewer, viewer_options=viewer_options)
humanoid = scene.add_entity(gs.morphs.MJCF(file=str(genesis_robot_xml)))

scene.build()

root_dof_count = max(humanoid.n_dofs - len(joint_order), 0)
controlled_dofs = list(range(root_dof_count, humanoid.n_dofs))

humanoid.set_dofs_position([0.0] * len(controlled_dofs), controlled_dofs, zero_velocity=True)
humanoid.set_dofs_kp([120.0] * len(controlled_dofs), controlled_dofs)
humanoid.set_dofs_kv([12.0] * len(controlled_dofs), controlled_dofs)

steps = int(os.getenv("STEPS", "100"))
for i in range(steps):
    t = i * 0.01

    target = [0.0] * len(controlled_dofs)

    for sine_target in gait:
        index = joint_index.get(sine_target.joint)
        if index is not None and index < len(target):
            target[index] = sine_target.value(t)

    humanoid.control_dofs_position(target, controlled_dofs)

    scene.step()
