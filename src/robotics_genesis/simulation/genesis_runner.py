from __future__ import annotations

import os
from pathlib import Path

from robotics_genesis.controllers import default_modular_gait
from robotics_genesis.paths import project_path
from robotics_genesis.viewer_env import configure_pyglet_options, configure_viewer_environment
from robotics_genesis.xml_robot import get_1d_joint_names, prepare_mjcf_for_genesis


def _cuda_available() -> bool:
    try:
        import torch
    except ImportError:
        return False
    return torch.cuda.is_available()


def _select_backend(gs, name: str):
    normalized = name.strip().lower()
    if normalized in ("gpu", "cuda"):
        if not _cuda_available():
            print("[genesis_runner] CUDA not available, falling back to CPU backend.")
            return gs.cpu
        return gs.gpu
    if normalized == "cpu":
        return gs.cpu
    raise ValueError("GENESIS_BACKEND must be 'cpu' or 'gpu'")


def run_genesis_simulation(
    robot_xml: str | Path,
    *,
    steps: int = 1000,
    show_viewer: bool = False,
    backend: str = "gpu",
    kp: float = 120.0,
    kv: float = 12.0,
) -> None:
    configure_viewer_environment(show_viewer)

    import pyglet

    configure_pyglet_options(pyglet)

    import genesis as gs

    robot_path = Path(robot_xml).resolve()
    genesis_robot_path = prepare_mjcf_for_genesis(robot_path, project_path("outputs", "generated"))
    joint_order = get_1d_joint_names(robot_path)
    joint_index = {name: index for index, name in enumerate(joint_order)}
    gait = default_modular_gait()

    gs.init(backend=_select_backend(gs, backend))

    viewer_options = None
    if show_viewer:
        run_in_thread = os.getenv("GENESIS_VIEWER_THREAD", "1") != "0"
        viewer_options = gs.options.ViewerOptions(run_in_thread=run_in_thread, res=(960, 640))

    scene = gs.Scene(show_viewer=show_viewer, viewer_options=viewer_options)
    robot = scene.add_entity(gs.morphs.MJCF(file=str(genesis_robot_path)))
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
