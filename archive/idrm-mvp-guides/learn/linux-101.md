# Linux 101

> *Type: Guide (101 / foundational) · Audience: complete novices → developers/operators · Status: MVP — current · Track: Operations (#32)*
> *IDRM runs on **Linux** (Ubuntu). Whether you're setting up a dev machine or operating the server, you'll live
> in a Linux terminal. This guide takes you from "what is Linux?" to the commands you'll actually use.*

---

## 1. What Linux is

**Linux** is a free, open-source operating system — the software that runs the computer, like Windows or macOS,
but dominant on servers because it's stable, secure, scriptable, and free. A **distribution ("distro")** is a
packaged version of it; IDRM standardises on **Ubuntu 22.04 LTS** (LTS = Long-Term Support, i.e. maintained for
years — important for reliability).

You interact with a server mostly through the **shell** — a text prompt where you type commands. IDRM's default
shell examples use **bash**.

---

## 2. The filesystem: everything is a path

Linux organises everything in a single tree starting at `/` (the "root"):

- `/home/you` — your files (`~` is shorthand for it).
- `/etc` — system configuration.
- `/var/log` — logs.
- **Absolute path** starts at `/`; **relative path** is from where you are.

```bash
pwd            # print working directory (where am I?)
ls -la         # list files, including hidden ones, with detail
cd /var/log    # change directory
```

---

## 3. The commands you'll use daily

```bash
cat file.txt          # show a file
less file.txt         # scroll through a big file (q to quit)
tail -f app.log       # follow a log live (great for debugging)
grep "error" app.log  # search for text
cp / mv / rm          # copy / move / remove
mkdir newdir          # make a directory
nano file.txt         # simple text editor
```

**Pipes and redirection** chain commands — the Unix superpower:

```bash
cat app.log | grep "incident" | tail -20   # last 20 log lines mentioning "incident"
```

---

## 4. Permissions (why "permission denied" happens)

Every file has an **owner** and permission bits for **read/write/execute**. Two commands you'll meet:

```bash
chmod +x setup.sh     # make a script executable
sudo <command>        # run as the superuser (admin) — use with care
```

`sudo` ("superuser do") grants admin rights; it's how you install software or manage services — and why you
should think before running it.

---

## 5. Packages and services (running IDRM)

- **Install software** with the package manager:

```bash
sudo apt update && sudo apt install postgresql
```

- **Services** (long-running programs like PostgreSQL, MinIO, the IDRM app) are managed by **systemd**:

```bash
sudo systemctl start idrm      # start
sudo systemctl status idrm     # is it running?
sudo systemctl enable idrm     # start automatically on boot
journalctl -u idrm -f          # follow that service's logs
```

> **IDRM runs natively on systemd** (no Docker in the MVP). So knowing `systemctl` and `journalctl` is exactly
> how you'll start, check, and debug IDRM's PostgreSQL, MinIO, and app processes.

---

## 6. Connecting to a server: SSH

You reach a remote Linux server securely with **SSH (Secure Shell)**:

```bash
ssh user@server-address
```

From there, everything above works the same. (The IDRM one-command setup script and deployment steps assume this
Ubuntu + systemd world — see the [contributor guide](../30-contribute-developer-guide.md).)

---

## 7. Mastery check

1. Say what Linux and a **distro** are, and which IDRM uses.
2. Explain the filesystem tree, `~`, and absolute vs relative paths.
3. Use `ls`, `cd`, `cat`, `tail -f`, and a `grep` pipe.
4. Explain `chmod +x` and `sudo`, and when to be careful.
5. Start, check, enable, and tail a **systemd** service (like `idrm`).

---

## 8. Go deeper

- Ubuntu Server guide — ubuntu.com/server/docs · The Linux Command Line (free book) — linuxcommand.org
- systemd — freedesktop.org/wiki/Software/systemd · IDRM deployment: [`../../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../../idrm-mvp-docs/80-ops-deployment-and-operations.md)

---
*Next:* [Backup & Restore 101](backup-restore-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
