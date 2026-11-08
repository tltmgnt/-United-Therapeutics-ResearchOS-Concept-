"""CLI for research dossier declarations and ResearchOS replay; no automatic assurance."""
import argparse
import json
from ._tect.io import load
from .bundle import write, verify


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    analyze = commands.add_parser('analyze')
    analyze.add_argument('input')
    analyze.add_argument('--output', required=True)
    check = commands.add_parser('verify')
    check.add_argument('bundle')
    args = parser.parse_args(argv)
    try:
        report = write(load(args.input), args.output) if args.command == 'analyze' else verify(args.bundle)
        print(json.dumps({'status': 'COMPUTED_UNASSURED' if args.command == 'analyze' else 'REPLAY_CONSISTENT_UNASSURED',
                          'states': {cid: c['state'] for cid, c in report['state']['claims'].items()},
                          'assurance_blockers': report['assurance_blockers'],
                          'execution_authorized': report['execution_authorized']}, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
