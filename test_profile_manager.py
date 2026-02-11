import importlib.util
import sys
from pathlib import Path

# Get full path to profile_manager.py
file_path = Path("src/BrowserManager/profile_manager.py").resolve()

spec = importlib.util.spec_from_file_location("profile_manager", file_path)
module = importlib.util.module_from_spec(spec)
sys.modules["profile_manager"] = module
spec.loader.exec_module(module)

ProfileManager = module.ProfileManager


pm = ProfileManager()

print("Creating profiles...")
try:
    pm.create_profile("whatsapp", "test1")
except ValueError:
    pass

try:
    pm.create_profile("whatsapp", "test2")
except ValueError:
    pass

print("Profiles:", pm.list_profiles("whatsapp"))

print("Activating test1...")
pm.activate_profile("whatsapp", "test1")

print("Activating test2...")
pm.activate_profile("whatsapp", "test2")

print("Done.")

print("Creating backup...")
pm.create_backup("whatsapp", "test2")

print("Deleting test1...")
pm.delete_profile("whatsapp", "test1")

print("Profiles after deletion:", pm.list_profiles("whatsapp"))

