import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
import base64

if_verbose = 0

def verbose(args):
    if if_verbose == 1:
        print(args)

def encrypt_data_neo(filename, encryptname, password, keyfile=None, keyfile_name=None, delete_original=None):
    if not filename:
        print("pcs: filename cannot be empty.")
        return False
    if not encryptname:
        print("pcs: encryptname cannot be empty.")
        return False
    if not password:
        print("pcs: password cannot be empty.")
        return False
    if keyfile and not keyfile_name:
        print("pcs: keyfile_name cannot be empty when keyfile is enabled.")
        return False

    if not Path(filename).is_file():
        print("pcs: input file not found.")
        return False

    verbose(encryptname)

    if keyfile:
        verbose("pcs: keyfile enabled")
    else:
        verbose("pcs: keyfile disabled")

    verbose(password)
    password = password.encode()

    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)

    verbose("Encrypting...")
    try:
        with open(filename, 'rb') as file:
            original_data = file.read()

        encrypted_data = f.encrypt(original_data)

        if not keyfile:
            with open(encryptname, 'wb') as file:
                file.write(salt)
                file.write(encrypted_data)
        else:
            with open(keyfile_name, 'wb') as kf:
                kf.write(salt)
            with open(encryptname, 'wb') as file:
                file.write(encrypted_data)

        verbose("pcs: encrypted!")
        if delete_original is None or delete_original == True:
            os.remove(filename)
            verbose("pcs: original file removed.")

    except Exception as e:
        print(f"pcs: error! {e}")
        return False

    return True


def decrypt_data_neo(encryptname, unencryptname, password, keyfile=None, keyfile_name=None, delete_original=None):
    if not encryptname:
        print("pcs: encryptname cannot be empty.")
        return False
    if not unencryptname:
        print("pcs: unencryptname cannot be empty.")
        return False
    if not password:
        print("pcs: password cannot be empty.")
        return False
    if keyfile and not keyfile_name:
        print("pcs: keyfile_name cannot be empty when keyfile is enabled.")
        return False

    if not Path(encryptname).is_file():
        print("pcs: encrypted file not found.")
        return False

    if keyfile:
        if not Path(keyfile_name).is_file():
            print(f"pcs: keyfile '{keyfile_name}' not found.")
            return False
        there_is_a_key = True
    else:
        there_is_a_key = False

    password = password.encode()

    try:
        if there_is_a_key:
            with open(keyfile_name, 'rb') as file:
                file_salt = file.read(16)
            with open(encryptname, 'rb') as file:
                encrypted_data = file.read()
        else:
            with open(encryptname, 'rb') as file:
                file_salt = file.read(16)
                encrypted_data = file.read()
    except Exception as e:
        print(f"pcs: error reading file! {e}")
        return False

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=file_salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)

    print("Decrypting...", end=" ")
    try:
        decrypted_data = f.decrypt(encrypted_data)

        with open(unencryptname, 'wb') as file:
            file.write(decrypted_data)
        print("Success.")

        if delete_original is None or delete_original == True:
            os.remove(encryptname)
            verbose("pcs: encrypted file removed.")
            if there_is_a_key:
                os.remove(keyfile_name)
                verbose("pcs: keyfile removed.")

    except Exception as e:
        print(f"Could not decrypt!\nThis might be due to a wrong password or corrupted data?\nDetailed info:\n{e}.")
        return False

    return True


def main(args):
    HELP = (
        "usage:\n"
        "  pcs -e <zipfile> <output> <password> [keyfile_name] [delete: 0|1]\n"
        "  pcs -d <vault>   <output> <password> [keyfile_name] [delete: 0|1]\n"
        "  pcs -h\n\n"
        "examples:\n"
        "  pcs -e Archive.zip vault.p7c_enc mypassword\n"
        "  pcs -e Archive.zip vault.p7c_enc mypassword vault.p7c_key\n"
        "  pcs -e Archive.zip vault.p7c_enc mypassword vault.p7c_key 0\n"
        "  pcs -d vault.p7c_enc output.zip  mypassword\n"
        "  pcs -d vault.p7c_enc output.zip  mypassword vault.p7c_key\n"
        "  pcs -d vault.p7c_enc output.zip  mypassword vault.p7c_key 1\n\n"
        "note:\n"
        "  to set delete without a keyfile, pass an empty string: pcs -e file.zip out.p7c_enc pass \"\" 0\n"
    )

    if not args or args[0] in ("--help", "-h"):
        print("""
P7MJ's enCryption System
Usage:
  pcs [flags] {input} {output} <password> {keyfile} (if_delete)

Parameters:
  password: the password for encryption or decryption

Files:
  input: the input file
  output: the output file
  keyfile: the keyfile, if applicable.

Flags:
  -e: encrypt
  -d: decrypt
  -h: this help section

Choices:
  0: don't delete original
  1: delete original and keyfile (if applicable)

Notes:
  For paranoid security, or recovering BUGPy cat1_enc.p7c_enc.
        """)
        # print(HELP)
        return

    mode = args[0]

    if mode in ("--encrypt", "-e"):
        if len(args) < 4:
            print("pcs: not enough arguments for encrypt.\n")
            print(HELP)
            return
        filename     = args[1]
        encryptname  = args[2]
        password     = args[3]
        keyfile_name = args[4] if len(args) >= 5 else None
        delete_arg   = args[5] if len(args) >= 6 else None
        if delete_arg not in (None, "0", "1"):
            print(f"pcs: delete argument must be 0 or 1, got '{delete_arg}'")
            return
        delete_original = (delete_arg == "1") if delete_arg is not None else None
        encrypt_data_neo(filename, encryptname, password,
                         keyfile=bool(keyfile_name), keyfile_name=keyfile_name or None,
                         delete_original=delete_original)

    elif mode in ("--decrypt", "-d"):
        if len(args) < 4:
            print("pcs: not enough arguments for decrypt.\n")
            print(HELP)
            return
        encryptname   = args[1]
        unencryptname = args[2]
        password      = args[3]
        keyfile_name  = args[4] if len(args) >= 5 else None
        delete_arg    = args[5] if len(args) >= 6 else None
        if delete_arg not in (None, "0", "1"):
            print(f"pcs: delete argument must be 0 or 1, got '{delete_arg}'")
            return
        delete_original = (delete_arg == "1") if delete_arg is not None else None
        decrypt_data_neo(encryptname, unencryptname, password,
                         keyfile=bool(keyfile_name), keyfile_name=keyfile_name or None,
                         delete_original=delete_original)

    else:
        print(f"pcs: unknown option '{mode}'")
        print(HELP)