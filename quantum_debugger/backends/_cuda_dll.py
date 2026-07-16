"""
Windows CUDA DLL discovery for pip-installed CUDA runtime wheels.

When CuPy is installed as ``cupy-cuda12x`` alongside the ``nvidia-*-cu12`` runtime
wheels (the common pip-only setup), the CUDA DLLs live under
``site-packages/nvidia/<lib>/bin`` and are NOT on the default Windows DLL search
path. CuPy then fails to load ``nvrtc64_120_0.dll`` / ``cublas`` etc.

This module adds those directories to both ``PATH`` (so transitively-loaded
dependencies such as ``nvrtc-builtins*.dll`` are found) and the process DLL
search list, before CuPy is imported. It is a safe no-op on non-Windows systems
and when no such wheels are present.
"""

import glob
import os
import site
import sys

_configured = False


def ensure_cuda_dlls() -> None:
    """Make pip-installed CUDA runtime DLLs discoverable (Windows only)."""
    global _configured
    if _configured:
        return
    _configured = True

    if sys.platform != "win32":
        return

    roots = []
    try:
        roots.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        roots.append(site.getusersitepackages())
    except Exception:
        pass
    # Derive the site-packages root from this file's location as a fallback
    # (…/site-packages/quantum_debugger/backends/_cuda_dll.py).
    roots.append(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )

    bin_dirs = set()
    for root in roots:
        if not root:
            continue
        for bin_dir in glob.glob(os.path.join(root, "nvidia", "*", "bin")):
            if os.path.isdir(bin_dir):
                bin_dirs.add(bin_dir)

    if not bin_dirs:
        return

    # PATH is required so that DLLs loaded *by* the CUDA DLLs (e.g. nvrtc pulling
    # in nvrtc-builtins) resolve; add_dll_directory alone does not cover those.
    current_path = os.environ.get("PATH", "")
    missing = [d for d in bin_dirs if d not in current_path]
    if missing:
        os.environ["PATH"] = os.pathsep.join(missing) + os.pathsep + current_path

    if hasattr(os, "add_dll_directory"):
        for bin_dir in bin_dirs:
            try:
                os.add_dll_directory(bin_dir)
            except OSError:
                pass
