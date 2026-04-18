from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_workflow.review_recap_writer import ReviewRecapWriter


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo Brian AI workflow review recap writer")
    parser.add_argument("--case-file", help="Optional JSON file containing a case record")
    parser.add_argument("--title", help="Case title when not using --case-file")
    parser.add_argument("--customer", default="", help="Customer name")
    parser.add_argument("--lane", default="commercial", help="Primary lane")
    parser.add_argument("--client-owner", default=None, help="Final client owner")
    parser.add_argument("--pm-owner", default=None, help="Final PM owner")
    parser.add_argument("--brian-exec", default=None, help="Brian exec: 是/否/待確認")
    parser.add_argument("--brian-role", default=None, help="Brian role")
    parser.add_argument("--brief", default="", help="Raw brief")
    parser.add_argument("--brand", default=None, help="Brand or system")
    parser.add_argument("--brian-net", type=float, default=None, help="Brian net income")
    parser.add_argument("--jerry-net", type=float, default=None, help="Jerry net income")
    parser.add_argument("--chu-post", type=float, default=None, help="Chu post income")
    args = parser.parse_args()

    if args.case_file:
        case = json.loads(Path(args.case_file).read_text(encoding="utf-8"))
    else:
        if not args.title:
            raise SystemExit("--title is required when --case-file is not provided")
        case = {
            "case_id": f"demo_{args.title[:12]}",
            "title": args.title,
            "customer_name": args.customer,
            "primary_lane": args.lane,
            "client_owner": args.client_owner,
            "pm_owner": args.pm_owner,
            "brian_exec": args.brian_exec,
            "brian_role": args.brian_role,
            "brand_or_system": args.brand,
            "raw_brief": args.brief,
            "updated_at": 0,
        }

    writer = ReviewRecapWriter()
    recap = writer.build_recap(
        case,
        {
            "created_by": "demo",
            "brian_net": args.brian_net,
            "jerry_net": args.jerry_net,
            "chu_post": args.chu_post,
        },
    )
    print(json.dumps(recap, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
