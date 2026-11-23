"""Which projects does a change touch?

A monorepo build should run the projects a change can break, not all of them.
Each project has a project.json with its name and what it depends on. A changed
file belongs to the project whose directory is its longest prefix. The result is
those projects plus everything that depends on them, in build order.
"""

import fnmatch
import json
import os

DEFAULT_GLOBAL = [".github/*", "package-lock.json", "pyproject.toml"]


def load_projects(root):
    """Return {name: {"path", "depends_on", "extra_paths"}} for every project.json under root."""
    projects = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules"))
        if "project.json" not in filenames:
            continue
        with open(os.path.join(dirpath, "project.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        name = data["name"]
        if name in projects:
            raise ValueError(f"duplicate project name: {name}")
        rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
        projects[name] = {
            "path": "" if rel == "." else rel,
            "depends_on": list(data.get("depends_on", [])),
            "extra_paths": list(data.get("extra_paths", [])),
        }
    for name, proj in projects.items():
        for dep in proj["depends_on"]:
            if dep not in projects:
                raise ValueError(f"{name} depends on unknown project: {dep}")
    build_order(projects)  # raises on a cycle
    return projects


def load_global_paths(root):
    path = os.path.join(root, "monorepo.json")
    if not os.path.exists(path):
        return list(DEFAULT_GLOBAL)
    with open(path, encoding="utf-8") as fh:
        return list(json.load(fh).get("global_paths", DEFAULT_GLOBAL))


def build_order(projects, subset=None):
    """Dependencies first. Ties broken by name so output is stable. Raises on a cycle."""
    names = set(projects) if subset is None else set(subset)
    indegree = {n: 0 for n in names}
    dependents = {n: [] for n in names}
    for n in names:
        for dep in projects[n]["depends_on"]:
            if dep in names:
                indegree[n] += 1
                dependents[dep].append(n)
    ready = sorted(n for n in names if indegree[n] == 0)
    order = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for m in sorted(dependents[n]):
            indegree[m] -= 1
            if indegree[m] == 0:
                ready.append(m)
        ready.sort()
    if len(order) != len(names):
        stuck = sorted(names - set(order))
        raise ValueError("dependency cycle among: " + ", ".join(stuck))
    return order


def owners(path, projects):
    """Projects a changed file belongs to: longest directory prefix, plus extra_paths matches."""
    found = set()
    best, best_len = None, -1
    for name, proj in projects.items():
        prefix = proj["path"]
        inside = prefix == "" or path == prefix or path.startswith(prefix + "/")
        if inside and len(prefix) > best_len:
            best, best_len = name, len(prefix)
        for pattern in proj["extra_paths"]:
            if fnmatch.fnmatch(path, pattern):
                found.add(name)
    if best is not None:
        found.add(best)
    return found


def _clean(path):
    path = path.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def affected(projects, changed, global_paths=None):
    """Return the affected projects in build order, with the reason for each."""
    global_paths = DEFAULT_GLOBAL if global_paths is None else global_paths
    changed = sorted({_clean(c) for c in changed if c.strip()})
    reasons = {}
    unowned = []
    everything = False
    for path in changed:
        if any(fnmatch.fnmatch(path, g) for g in global_paths):
            everything = True
            for name in projects:
                reasons.setdefault(name, []).append(f"global file changed: {path}")
            continue
        who = owners(path, projects)
        if not who:
            unowned.append(path)
        for name in who:
            reasons.setdefault(name, []).append(f"changed: {path}")
    direct = sorted(reasons)

    dependents = {n: [] for n in projects}
    for n, proj in projects.items():
        for dep in proj["depends_on"]:
            dependents[dep].append(n)
    queue = list(direct)
    while queue:
        current = queue.pop(0)
        for nxt in sorted(dependents[current]):
            if nxt not in reasons:
                reasons[nxt] = [f"depends on {current}"]
                queue.append(nxt)

    return {
        "affected": build_order(projects, reasons.keys()),
        "direct": direct,
        "reasons": {k: reasons[k] for k in sorted(reasons)},
        "unowned": unowned,
        "everything": everything,
    }


def matrix(projects, result):
    """A GitHub Actions strategy.matrix payload."""
    return {"include": [{"project": n, "path": projects[n]["path"]} for n in result["affected"]]}
