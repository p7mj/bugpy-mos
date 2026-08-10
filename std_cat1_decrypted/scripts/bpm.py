import zipfile
import os
import shutil
from pathlib import Path

def install_package(zip_path):
    base_dir = Path(__file__).resolve().parent.parent
    temp_dir = base_dir / "temp"
    scripts_dir = base_dir / "scripts"
    pointer_file = base_dir / "config" / "pointerfile.txt"
    
    temp_dir.mkdir(exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            script_stem = Path(zip_path).stem
            extract_path = temp_dir / script_stem
            zip_ref.extractall(extract_path)

            # FIX: Resolve script name explicitly BEFORE system modifications
            script_name = ""
            py_files = [f for f in extract_path.iterdir() if f.suffix == ".py"]
            
            if py_files:
                # Prioritize a script matching the zip name, fallback to first .py found
                matching_main = next((f for f in py_files if f.stem == script_stem), py_files[0])
                script_name = matching_main.stem
            else:
                script_name = script_stem

            # FIX: Run Update Protection SCRUB before moving new payloads to disk
            if pointer_file.exists() and script_name:
                with open(pointer_file, "r") as f:
                    lines = f.readlines()
                with open(pointer_file, "w") as f:
                    for line in lines:
                        if not line.strip().endswith(f": {script_name}"):
                            f.write(line)

            # Move the .py files securely now that registration space is clear
            for file in py_files:
                target_path = scripts_dir / file.name
                shutil.move(str(file), str(target_path))

            # Append New Aliases from package metadata safely
            alias_file = extract_path / "aliases.txt"
            if alias_file.exists():
                with open(alias_file, "r") as f:
                    new_aliases = f.readlines()
                with open(pointer_file, "a") as f:
                    for line in new_aliases:
                        if not line.endswith("\n"):
                            line += "\n"
                        f.write(line)
            
            shutil.rmtree(extract_path)
            print(f"Successfully installed/updated {script_name}")
            return True
    except Exception as e:
        print(f"Error installing {zip_path}: {e}")
        return False

def purge_package(script_name):
    base_dir = Path(__file__).resolve().parent.parent
    scripts_dir = base_dir / "scripts"
    pointer_file = base_dir / "config" / "pointerfile.txt"

    # 1. Remove the .py file
    script_path = scripts_dir / f"{script_name}.py"
    if script_path.exists():
        os.remove(script_path)
        print(f"Removed {script_name}.py")
    else:
        print(f"BPM: {script_name}.py not found.")

    # 2. Scrub the pointerfile
    if pointer_file.exists():
        with open(pointer_file, "r") as f:
            lines = f.readlines()
        with open(pointer_file, "w") as f:
            for line in lines:
                if not line.strip().endswith(f": {script_name}"):
                    f.write(line)
        print(f"Cleaned aliases for {script_name} from pointerfile.")

def organize_pointerfile():
    """Structures aliases by target file, sorted and neatly grouped with comments."""
    base_dir = Path(__file__).resolve().parent.parent
    pointer_file = base_dir / "config" / "pointerfile.txt"

    if not pointer_file.exists():
        print("BPM: Pointerfile does not exist to organize.")
        return

    groups = {} # maps script_name -> list of "alias: script_name" strings
    
    with open(pointer_file, "r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ": " in stripped:
                alias, script_name = stripped.split(": ", 1)
                groups.setdefault(script_name.strip(), []).append(f"{alias.strip()}: {script_name.strip()}")

    # Re-write the file with clean layout mapping architecture
    with open(pointer_file, "w") as f:
        for script_name in sorted(groups.keys()):
            f.write(f"#{script_name}\n")
            for entry in sorted(groups[script_name]):
                f.write(f"{entry}\n")
            f.write("\n") # Breathability margin between components
            
    print("Successfully organized pointerfile cleanly by package headers.")

def autoremove_dangling_pointers():
    """Strips out entries in the pointerfile that match missing script components."""
    base_dir = Path(__file__).resolve().parent.parent
    scripts_dir = base_dir / "scripts"
    pointer_file = base_dir / "config" / "pointerfile.txt"

    if not pointer_file.exists():
        return

    with open(pointer_file, "r") as f:
        lines = f.readlines()

    kept_lines = []
    removed_count = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            kept_lines.append(line)
            continue
            
        if ": " in stripped:
            _, script_name = stripped.split(": ", 1)
            target_script = scripts_dir / f"{script_name.strip()}.py"
            
            if target_script.exists():
                kept_lines.append(line)
            else:
                removed_count += 1
                
    if removed_count > 0:
        with open(pointer_file, "w") as f:
            f.writelines(kept_lines)
        print(f"Autoremove: Swept and pruned {removed_count} dangling pointer(s).")
    else:
        print("Autoremove: System integrity clear. No dangling pointers found.")

# BUGS PACKAGE MANAGER (BPM)
def main(args):
    if not args or "-h" in args or "--help" in args:
        print("""
BPM
Usage:
  bpm <params> {script_name} [flags]

Parameters:
  install      : install a program from a zip file
  purge        : purge a program by name

Flags:
  --organize   : structure alias entries cleanly by package name
  --autoremove : prune orphaned aliases pointing to missing scripts
  -h, --help   : print this assistance manual
        """)
        return

    # Process systemic utility switches first
    if "--organize" in args:
        organize_pointerfile()
        return
    elif "--autoremove" in args:
        autoremove_dangling_pointers()
        return

    if args[0] == "install":
        for zip_item in args[1:]:
            install_package(zip_item)
    
    elif args[0] == "purge":
        for script_item in args[1:]:
            clean_name = script_item.replace(".py", "")
            purge_package(clean_name)
