# BUGPy-mOS-1 Release A-4-i "Graphical Upgrades" w/FDEA

BUGS Python Mock Operation System Overhaul 1 Release Version A Subversion 4 Patch i "Graphical Upgrades" with Full Disk Encryption Ant

## 🪲 Overview

BUGPy-mOS is a FOSS **Mock Operating System**. It is written fully in Python and, when packaged with `mkosi`, can boot on a computer independently.

It contains its own **package manager** (BPM), **shell** (BUSH), **full-disk encryption** (FDEA) and **system utilities**.

> **This is a FOSS project**. You can download it for free, modify it, do whatever you want. *Just make sure to include a reference to us*.
> 
> If you are interested in contributing to the project, contact p7mj@wholeworldcoding.com.

## 🖥️ Usage

Download the distribution you are interested in using from the release page. There are three distributions:

- **min** (Minimal): The base package.

- **std** (Standard): The standard package. **All packages are tested**. Recommended for the majority of users.

- **ext** (Extended): The extended package. Contains experimental/extended scripts from **SpyDrone**.

Once you have extracted the files, run `python3 fdea-1.py`. You will be prompted with a password. The default is `hello`.

BUGPy's system utilities are based on *NIX commands. If you are comfortable with Linux terminals, you will be able to use BUGPy. Help sections for each command are availible by running `<command> -h` or `<command> --help`.

## 🔒 Encryption w/FDEA

**FDEA** stands for the **Full Disk Encryption Ant**. It is a utility that acts as the encryption/decryption agent and the launcher for BUGPy.

It uses an adapted version of `PCS` ([link](https://git.wholeworldcoding.com/p7mj/PCS)) to handle the encryption and decryption of the main system folder. The entire folder is encrypted as one into `cat1_enc.p7c_enc` using your password.

> ⚠️ **If you lose your password, there is no way to recover the contents of the BUGPy installation.**

## 🔤 Terminology

`cat` (catepillar): a BUGPy drive.

`ant`: any script that assists BUGPy but is not found in the scripts folder

`pointerfile`: a txt file that contains aliases and the scripts they point to

`bpm` (BUGS Package Manager): the default package manager for BUGPy.

`bush` (BUGS-Shell): the default command interpreter and shell for BUGPy.

`fdea` (Full Disk Encryption Ant): the default encryption/decryption and launcher for BUGPy.

## 🏗️ Structure

A BUGPy-mOS A-4-i `std` install looks like this:

```
cat1
├── bugpy-mos-1.py
├── bush.py
├── config
│   ├── log.txt
│   ├── p7mj_retardedness.txt
│   ├── pointerfile.txt
│   ├── startup.txt
│   └── username.txt
├── dev
│   ├── changelog.txt
│   ├── help_format.txt
│   └── what_next.txt
├── history
│   └── history.txt
├── home
├── scripts
│   ├── ... (system utilities)
└── temp
```

## ⚙️ Configuration

As intended, **almost every aspect of BUGPY-mOS is customizable**.

For starters, you can change your username simply by editing `config/username.txt`! This will change your username as displayed in `bush`. You can also change any of the command/script aliases easily by editing the pointerfile.

You can also make your own shell (although our shell is awesome) and rename it to bush.py.

You can make your own apps, scripts, and packages for BUGPy-mOS! Read the [Wiki](https://git.wholeworldcoding.com/wholeworldcoding/BUGPy-mOS/wiki) for more information.

## 🔧 Developers

### Core Developers

- **P7MJ**: Creator of BUGPy-mOS. Made all versions from `BUGPy-mOS-0` to `BUGPy-mOS-1 A-3-ii`.

- **SpyDrone**: Creator of over half of the system utilities, `drone_game`, and most of the packages in `ext`.

- **OctoLinkYT**: Creator of `octuple`. Founder of the `wholeworldcoding` group.