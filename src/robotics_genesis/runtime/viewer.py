from __future__ import annotations

import os


def configure_viewer_environment(show_viewer: bool) -> None:
    """Configure OpenGL-related environment before importing pyglet/genesis."""
    if not show_viewer:
        return

    os.environ["PYOPENGL_PLATFORM"] = os.getenv("GENESIS_GL_PLATFORM", "glx")
    os.environ.setdefault("GALLIUM_DRIVER", "d3d12")
    os.environ.setdefault("MESA_D3D12_DEFAULT_ADAPTER_NAME", "NVIDIA")


def configure_pyglet_options(pyglet_module) -> None:
    pyglet_module.options["debug_gl"] = False
    pyglet_module.options["shadow_window"] = False
