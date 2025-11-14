"""
Triton ops stub for Windows compatibility
Author: eddy
"""

import sys
from types import ModuleType

# Create triton module if it doesn't exist
if 'triton' not in sys.modules:
    triton = ModuleType('triton')
    triton.__spec__ = type('ModuleSpec', (), {'name': 'triton', 'loader': None, 'origin': 'stub'})()
    sys.modules['triton'] = triton
else:
    triton = sys.modules['triton']
    if not hasattr(triton, '__spec__') or triton.__spec__ is None:
        triton.__spec__ = type('ModuleSpec', (), {'name': 'triton', 'loader': None, 'origin': 'stub'})()

# Create triton.language module (required by many packages)
if not hasattr(triton, 'language') or 'triton.language' not in sys.modules:
    language_module = ModuleType('triton.language')
    language_module.__package__ = 'triton'
    
    # Add common language functions as stubs
    def constexpr(x):
        """Stub for constexpr"""
        return x
    
    language_module.constexpr = constexpr
    triton.language = language_module
    sys.modules['triton.language'] = language_module

# Add triton.jit decorator (required for kernel compilation)
if not hasattr(triton, 'jit'):
    def jit(fn=None, **kwargs):
        """Stub for triton.jit decorator - returns function as-is"""
        if fn is None:
            # Called with arguments: @triton.jit(...)
            def decorator(func):
                return func
            return decorator
        else:
            # Called without arguments: @triton.jit
            return fn
    
    triton.jit = jit

# Add triton.autotune decorator
if not hasattr(triton, 'autotune'):
    def autotune(configs, key, **kwargs):
        """Stub for triton.autotune decorator"""
        def decorator(func):
            return func
        return decorator
    
    triton.autotune = autotune

# Add triton.Config class
if not hasattr(triton, 'Config'):
    class Config:
        """Stub for triton.Config"""
        def __init__(self, kwargs=None, num_warps=4, num_stages=2):
            self.kwargs = kwargs or {}
            self.num_warps = num_warps
            self.num_stages = num_stages
    
    triton.Config = Config

# Create triton.ops module
if not hasattr(triton, 'ops') or 'triton.ops' not in sys.modules:
    ops_module = ModuleType('triton.ops')
    ops_module.__package__ = 'triton'

    # Create matmul_perf_model submodule
    matmul_perf_model = ModuleType('triton.ops.matmul_perf_model')
    matmul_perf_model.__package__ = 'triton.ops'

    def early_config_prune(configs, named_args, **kwargs):
        """Stub for early_config_prune"""
        # Return configs as-is
        return configs if configs else []

    def estimate_matmul_time(**kwargs):
        """Stub for estimate_matmul_time"""
        # Return a dummy time estimate
        return 1.0

    # Add functions to module
    matmul_perf_model.early_config_prune = early_config_prune
    matmul_perf_model.estimate_matmul_time = estimate_matmul_time

    # Link modules together
    ops_module.matmul_perf_model = matmul_perf_model
    triton.ops = ops_module

    # Register in sys.modules
    sys.modules['triton.ops'] = ops_module
    sys.modules['triton.ops.matmul_perf_model'] = matmul_perf_model

    print("[OK] Triton ops stub loaded for Windows compatibility (with language module)")