# Docker 101

> *Type: Guide (101 / foundational) · Audience: novices → developers · Status: **FFP** — next-phase · Track: Software Engineering (#15)*
> *"It works on my machine" is a classic failure. Docker fixes it by packaging software with everything it needs.
> This guide explains containers — and notes clearly that IDRM's **MVP does not use Docker** (native systemd);
> this is FFP.*

---

## 1. The problem: environments differ

Software depends on its surroundings — the OS, libraries, versions, config. Code that runs on a developer's
laptop can fail on the server because something's different. **Docker** solves this by bundling the app *and* its
environment into one portable unit that runs the same everywhere.

---

## 2. Containers, images, and how they differ from VMs

- **Image** — a read-only template: the app plus its dependencies, built from a recipe (a `Dockerfile`).
- **Container** — a running instance of an image; an isolated process with its own filesystem view.
- **Virtual Machine (VM)** vs **container:** a VM virtualises a *whole computer* (its own OS — heavy). A container
  shares the host's OS kernel and isolates just the app — **much lighter and faster** to start.

```dockerfile
FROM python:3.12          # base image
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app"]   # how to start the app
```

```bash
docker build -t idrm .     # build an image from the Dockerfile
docker run -p 8000:8000 idrm   # run it as a container
```

---

## 3. Why teams use it

- **Consistency** — dev, test, and prod run the *same* image.
- **Isolation** — each service in its own container; no dependency clashes.
- **Portability & scaling** — ship the image anywhere; run many copies. At scale, an **orchestrator** like
  **Kubernetes (K8s)** manages hundreds of containers (scheduling, health, scaling).

---

## 4. IDRM's position (important)

- **MVP:** **no Docker.** IDRM runs **natively on Ubuntu with systemd** — a deliberate choice to keep the first
  build simple and easy to operate (see [Linux 101](linux-101.md)). PostgreSQL, MinIO, and the app are plain
  systemd services.
- **FFP:** containers (Docker) → orchestration (**Kubernetes**) enter when the system splits into multiple
  services that need independent scaling and deployment. It's a *scaling* tool adopted on a trigger, not a
  starting requirement.

> Learning Docker now is useful for the future; just don't expect it in the MVP repo.

---

## 5. Mastery check

1. Explain the "works on my machine" problem and how Docker solves it.
2. Define **image** and **container**, and contrast a container with a VM.
3. Read a simple `Dockerfile` and the build/run commands.
4. State three reasons teams use containers, and what **Kubernetes** is for.
5. Say what IDRM's MVP uses instead, and when Docker enters (FFP).

---

## 6. Go deeper

- Docker docs — docs.docker.com · Kubernetes — kubernetes.io/docs
- IDRM deployment (MVP, native): [`../../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../../idrm-mvp-docs/80-ops-deployment-and-operations.md)
- Related: [Linux 101](linux-101.md) · [CI/CD 101](ci-cd-101.md)

---
*Next:* [CI/CD 101](ci-cd-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
