# FDEA-1, MKOSI ISO Edition
# Full Disk Encryption Application for BUGPy-mOS.

import shutil
import os
import signal
import getpass
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
import base64
import subprocess

drive     = "cat1"
swap_file = "used.swp"

_session_password = None
_is_securing      = False  # Global lock flag to block signal re-entry re-runs

# ---------------------------------------------------------------------------
# Output helper
# ---------------------------------------------------------------------------

def print_green(*args, sep=" ", end="\n", flush=False):
    message = sep.join(str(a) for a in args)
    print(f"\033[92m{message}\033[0m", end=end, flush=flush)

# ---------------------------------------------------------------------------
# SIGTERM / SIGINT handler with Re-entry Isolation
# ---------------------------------------------------------------------------

def _emergency_encrypt(signum, frame):
    global _session_password, _is_securing
    
    # Critical Block: If we are already zipping/encrypting, ignore duplicate signals
    if _is_securing:
        return
    _is_securing = True

    sig_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
    print(f"\nfdea: {sig_name} received — securing data before exit...")

    if _session_password and os.path.isdir(drive):
        try:
            # Mask signals during emergency mitigation to ensure absolute atomicity
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT,  signal.SIG_IGN)
            
            zip_dir(f"{drive}_enc", "zip", drive)
            encrypt_data(f"{drive}_enc.zip", f"{drive}_enc", _session_password, if_delete_original=True)
            
            if os.path.exists(swap_file):
                os.remove(swap_file)
            print("fdea: data secured.")
        except Exception as e:
            print(f"fdea: CRITICAL WARNING — could not re-encrypt: {e}")
            print("fdea: cat1/ may still be on disk unencrypted.")
    elif os.path.isdir(drive):
        print("fdea: WARNING — cat1/ is on disk unencrypted and no password is stored.")
        print("fdea: Run FDEA manually and choose (e)ncrypt to secure it.")
        
    sys.exit(0)

# Register Emergency hooks
signal.signal(signal.SIGTERM, _emergency_encrypt)
signal.signal(signal.SIGINT,  _emergency_encrypt)

# ---------------------------------------------------------------------------
# Encryption / decryption
# ---------------------------------------------------------------------------

def encrypt_data(zip_filename_w_extension, encrypted_name_without_extension, password_string, if_delete_original=True):
    file_name = Path(zip_filename_w_extension)
    if not file_name.is_file():
        print("fdea: zip file does not exist.")
        return

    password = password_string.encode()
    salt     = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f   = Fernet(key)

    try:
        original_data = file_name.read_bytes()
        encrypted_data = f.encrypt(original_data)

        target_file = Path(f"{encrypted_name_without_extension}.p7c_enc")
        
        # Write atomically using a temporary file step to prevent partial corruptions
        tmp_target = target_file.with_suffix('.tmp')
        with open(tmp_target, 'wb') as fh:
            fh.write(salt)
            fh.write(encrypted_data)
        tmp_target.rename(target_file)

        if if_delete_original:
            file_name.unlink(missing_ok=True)
            
    except Exception as e:
        print(f"fdea: error during encryption steps: {e}")
        raise e


def decrypt_data(p7c_enc_filename, password_string, output_zip_name, if_remove_file=True):
    p7c_path = Path(p7c_enc_filename)
    if not p7c_path.is_file():
        return 1   # File not found

    password = password_string.encode()

    try:
        with open(p7c_path, 'rb') as fh:
            file_salt      = fh.read(16)
            encrypted_data = fh.read()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=file_salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f   = Fernet(key)

        decrypted_data = f.decrypt(encrypted_data)
        
        Path(output_zip_name).write_bytes(decrypted_data)
        
        if if_remove_file:
            p7c_path.unlink(missing_ok=True)
        return 0
    except Exception:
        return 2   # Bad password or internal corruption handler


def zip_dir(output_file_no_extension, extension, dir_name):
    if not os.path.isdir(dir_name):
        return
    try:
        shutil.make_archive(
            base_name=output_file_no_extension,
            format=extension,
            root_dir=dir_name,
        )
        # Only wipe the directory out if the zip completed without an error
        shutil.rmtree(dir_name)
    except Exception as e:
        print(f"fdea: Archiving safety failure: {e}")
        raise e


def unzip_dir(filename_with_extension, output_folder, zipped_file_extension):
    shutil.unpack_archive(
        filename=filename_with_extension,
        extract_dir=output_folder,
        format=zipped_file_extension,
    )
    Path(filename_with_extension).unlink(missing_ok=True)


def launch_bugpy():
    target = os.path.join(drive, "bugpy-mos-1.py")
    if os.path.exists(target):
        print("fdea: launching bugpy...")
        try:
            subprocess.run([sys.executable, "bugpy-mos-1.py"], cwd=drive, check=True)
        except Exception as e:
            print(f"fdea: session ended: {e}")
    else:
        print("fdea: critical error: bugpy-mos-1.py not found.")


def finalize_session(password):
    global _is_securing
    _is_securing = True # Inform signals to stay clear during routine execution cleanup
    
    print("fdea: re-encrypting data...")
    try:
        zip_dir(f"{drive}_enc", "zip", drive)
        encrypt_data(f"{drive}_enc.zip", f"{drive}_enc", password, if_delete_original=True)
        if os.path.exists(swap_file):
            os.remove(swap_file)
        print("fdea: session secured. Done.")
    finally:
        _is_securing = False

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

while True:
    print_green(f"FDEA-1 for use with BUGPy-mOS-1 \"Expansion\", adapted for MKOSI use")

    # Recovery Checkpoint
    if os.path.exists(swap_file):
        print_green("\nfdea: WARNING: previous session was not closed correctly.")
        print_green("(e)ncrypt / (r)estore > ", end="", flush=True)
        choice = input("").lower()

        if choice == 'e':
            print_green("enter encryption password > ", end="", flush=True)
            pwd = getpass.getpass("")
            finalize_session(pwd)
            sys.exit(0)
        elif choice == 'r':
            launch_bugpy()
            print_green("enter encryption password > ", end="", flush=True)
            new_pwd = getpass.getpass("")
            finalize_session(new_pwd)
            sys.exit(0)

    # Standard Entry Menu
    print_green("[1] Launch BUGPy\n[x] Shut down system\n[e] Exit FDEA\n > ", end="", flush=True)
    choice = input("")

    if choice == "1":
        print_green("password > ", end="", flush=True)
        old_password = getpass.getpass("")

        res = decrypt_data(f"{drive}_enc.p7c_enc", old_password, f"{drive}_deenc.zip", if_remove_file=True)

        if res == 1:
            print_green("fdea: encrypted file not found.")
            sys.exit(1)
        elif res == 2:
            print_green("fdea: incorrect password.")
            continue

        try:
            unzip_dir(f"{drive}_deenc.zip", drive, "zip")
            Path(swap_file).touch()
        except Exception as e:
            print_green(f"fdea: failed to open drive: {e}")
            sys.exit(1)

        # Retain validation state
        _session_password = old_password

        launch_bugpy()

        # Exit cycle transitions
        print_green("enter new password (ENTER to keep current) > ", end="", flush=True)
        new_password = getpass.getpass("")
        if not new_password:
            new_password = old_password
            print_green("fdea: keeping current password.")

        # Wipe memory space cleanly before committing compilation write blocks
        _session_password = None
        finalize_session(new_password)

    elif choice == "x":
        os.system("systemctl poweroff")

    elif choice == "e":
        sys.exit(0)

    else:
        print_green("Invalid choice.")