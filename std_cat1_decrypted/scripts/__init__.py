import pkgutil
import importlib
import os
import sys

context = os.path.dirname(__file__)

for loader, module_name, is_pkg in pkgutil.iter_modules([context]):
    # Use full path to avoid confusion
    full_module_name = f'scripts.{module_name}'
    if full_module_name not in sys.modules:
        module = importlib.import_module(f'.{module_name}', package=__name__)
    else:
        module = sys.modules[full_module_name]
    
    # Map the function to the name
    if hasattr(module, 'main'):
        globals()[module_name] = getattr(module, 'main')
    else:
        globals()[module_name] = module