from __future__ import annotations

import os
from pathlib import Path

from robotics_genesis.controllers import default_starter_gait
from robotics_genesis.xml_robot import get_1d_joint_names


def _select_backend(gs, name: str):
    normalized = name.strip().lower()
    if normalized == "gpu":
        return gs.gpu
    if normalized == "cpu":
        return gs.cpu
    raise ValueError("GENESIS_BACKEND must be 'cpu' or 'gpu'")


def run_genesis_simulation(
    robot_xml: str | Path,
    *,
    steps: int = 1000,
    show_viewer: bool = False,
    backend: str = "cpu",
    kp: float = 120.0,
    kv: float = 12.0,
) -> None:
    import genesis as gs
    import pyglet

    pyglet.options["debug_gl"] = False

    if show_viewer:
        os.environ["PYOPENGL_PLATFORM"] = os.getenv("PYOPENGL_PLATFORM", "glx")

    robot_path = Path(robot_xml).resolve()
    joint_order = get_1d_joint_names(robot_path)
    joint_index = {name: index for index, name in enumerate(joint_order)}
    gait = default_starter_gait()

    gs.init(backend=_select_backend(gs, backend))

    viewer_options = None
    if show_viewer:
        viewer_options = gs.options.ViewerOptions(run_in_thread=True, res=(960, 640))

    scene = gs.Scene(show_viewer=show_viewer, viewer_options=viewer_options)
    robot = scene.add_entity(gs.morphs.MJCF(file=str(robot_path)))
    scene.build()

    root_dof_count = max(robot.n_dofs - len(joint_order), 0)
    controlled_dofs = list(range(root_dof_count, robot.n_dofs))
    if controlled_dofs:
        robot.set_dofs_position([0.0] * len(controlled_dofs), controlled_dofs, zero_velocity=True)
        robot.set_dofs_kp([kp] * len(controlled_dofs), controlled_dofs)
        robot.set_dofs_kv([kv] * len(controlled_dofs), controlled_dofs)

    for i in range(steps):
        t = i * 0.01
        target = [0.0] * len(controlled_dofs)

        for sine_target in gait:
            index = joint_index.get(sine_target.joint)
            if index is not None and index < len(target):
                target[index] = sine_target.value(t)

        if controlled_dofs:
            robot.control_dofs_position(target, controlled_dofs)
        scene.step()
