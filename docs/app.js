// Same rules as pck/affected.py, so the page can show them without a server.

function globToRe(glob) {
  const body = glob
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*/g, ".*")
    .replace(/\?/g, ".");
  return new RegExp("^" + body + "$");
}

function cleanPath(p) {
  p = p.trim().replace(/\\/g, "/");
  while (p.startsWith("./")) p = p.slice(2);
  return p;
}

function owners(path, projects) {
  const found = new Set();
  let best = null;
  let bestLen = -1;
  for (const [name, proj] of Object.entries(projects)) {
    const prefix = proj.path;
    const inside = prefix === "" || path === prefix || path.startsWith(prefix + "/");
    if (inside && prefix.length > bestLen) {
      best = name;
      bestLen = prefix.length;
    }
    for (const pattern of proj.extra_paths) {
      if (globToRe(pattern).test(path)) found.add(name);
    }
  }
  if (best !== null) found.add(best);
  return found;
}

function buildOrder(projects, subset) {
  const names = new Set(subset);
  const indegree = {};
  const dependents = {};
  for (const n of names) {
    indegree[n] = 0;
    dependents[n] = [];
  }
  for (const n of names) {
    for (const dep of projects[n].depends_on) {
      if (names.has(dep)) {
        indegree[n] += 1;
        dependents[dep].push(n);
      }
    }
  }
  const ready = [...names].filter((n) => indegree[n] === 0).sort();
  const order = [];
  while (ready.length) {
    const n = ready.shift();
    order.push(n);
    for (const m of [...dependents[n]].sort()) {
      indegree[m] -= 1;
      if (indegree[m] === 0) ready.push(m);
    }
    ready.sort();
  }
  return order;
}

function affected(graph, files) {
  const projects = graph.projects;
  const changed = [...new Set(files.map(cleanPath).filter(Boolean))].sort();
  const reasons = {};
  const unowned = [];
  for (const path of changed) {
    if (graph.global_paths.some((g) => globToRe(g).test(path))) {
      for (const name of Object.keys(projects)) {
        (reasons[name] = reasons[name] || []).push("global file changed: " + path);
      }
      continue;
    }
    const who = owners(path, projects);
    if (who.size === 0) unowned.push(path);
    for (const name of who) (reasons[name] = reasons[name] || []).push("changed: " + path);
  }
  const dependents = {};
  for (const n of Object.keys(projects)) dependents[n] = [];
  for (const [n, proj] of Object.entries(projects)) {
    for (const dep of proj.depends_on) dependents[dep].push(n);
  }
  const queue = Object.keys(reasons).sort();
  while (queue.length) {
    const current = queue.shift();
    for (const next of [...dependents[current]].sort()) {
      if (!(next in reasons)) {
        reasons[next] = ["depends on " + current];
        queue.push(next);
      }
    }
  }
  return { affected: buildOrder(projects, Object.keys(reasons)), reasons, unowned };
}

if (typeof module !== "undefined") module.exports = { affected };
