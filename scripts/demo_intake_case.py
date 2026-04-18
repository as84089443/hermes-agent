from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_workflow.intake_service import IntakeService


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo Brian AI workflow intake -> case creation")
    parser.add_argument("--title", required=True, help="Case title")
    parser.add_argument("--source", default="telegram", help="Source channel, default=telegram")
    parser.add_argument("--brief", required=True, help="Raw brief text")
    parser.add_argument("--customer", default="", help="Optional customer name")
    parser.add_argument("--draft-only", action="store_true", help="Only print case draft, do not persist case")
    args = parser.parse_args()

    service = IntakeService()
    try:
        if args.draft_only:
            result = service.build_case_draft(
                title=args.title,
                source=args.source,
                raw_brief=args.brief,
                customer_name=args.customer,
            )
        else:
            result = service.create_case_from_intake(
                title=args.title,
                source=args.source,
                raw_brief=args.brief,
                customer_name=args.customer,
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        service.close()


if __name__ == "__main__":
    raise SystemExit(main())
