import argparse
import json
import subprocess
import sys

from . import affected as aff
from . import plan as pl
from . import runbook, simulate


def _changed_files(args):
    if args.git_base:
        out = subprocess.run(
            ["git", "diff", "--name-only", f"{args.git_base}...HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.splitlines()
    return list(args.changed)


def cmd_affected(args):
    projects = aff.load_projects(args.root)
    result = aff.affected(projects, _changed_files(args), aff.load_global_paths(args.root))
    if args.format == "matrix":
        print(json.dumps(aff.matrix(projects, result)))
        return 0
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    if not result["affected"]:
        print("nothing to build")
    for name in result["affected"]:
        print(f"{name:10} {'; '.join(result['reasons'][name])}")
    if result["unowned"]:
        print("not in any project: " + ", ".join(result["unowned"]))
    return 0


def cmd_graph(args):
    projects = aff.load_projects(args.root)
    print(json.dumps({
        "projects": projects,
        "global_paths": aff.load_global_paths(args.root),
    }, indent=2))
    return 0


def cmd_check(args):
    issues = pl.validate(pl.load(args.plan))
    for issue in issues:
        print(issue)
    if pl.has_errors(issues):
        print("plan rejected")
        return 1
    print("plan ok" + (" (with warnings)" if issues else ""))
    return 0


def _checked(args):
    plan = pl.load(args.plan)
    if pl.has_errors(pl.validate(plan)):
        print("plan has errors, run: pck check " + args.plan, file=sys.stderr)
        sys.exit(1)
    return plan


def cmd_runbook(args):
    print(runbook.render_runbook(_checked(args)))
    return 0


def cmd_announce(args):
    print(runbook.render_announcement(_checked(args)))
    return 0


def cmd_simulate(args):
    events, ok = simulate.simulate(_checked(args), args.fail_at)
    print("\n".join(events))
    return 0 if ok else 2


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pck", description="Small, checked, reversible platform changes.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("affected", help="projects a change touches, in build order")
    p.add_argument("--root", default=".")
    p.add_argument("--changed", nargs="*", default=[], help="changed file paths")
    p.add_argument("--git-base", help="diff against this ref instead, for example origin/main")
    p.add_argument("--format", choices=["table", "json", "matrix"], default="table")
    p.set_defaults(func=cmd_affected)

    p = sub.add_parser("graph", help="print the project graph as JSON")
    p.add_argument("--root", default=".")
    p.set_defaults(func=cmd_graph)

    p = sub.add_parser("check", help="validate a change plan")
    p.add_argument("plan")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("runbook", help="render a plan as a runbook")
    p.add_argument("plan")
    p.set_defaults(func=cmd_runbook)

    p = sub.add_parser("announce", help="render the heads-up message")
    p.add_argument("plan")
    p.set_defaults(func=cmd_announce)

    p = sub.add_parser("simulate", help="dry-run a plan, optionally failing one step")
    p.add_argument("plan")
    p.add_argument("--fail-at", help="step id whose check fails")
    p.set_defaults(func=cmd_simulate)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
