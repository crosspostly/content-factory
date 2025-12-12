from __future__ import annotations

import sys

from . import pipeline_orchestrator


if __name__ == "__main__":
    parser = pipeline_orchestrator.build_parser()
    args = parser.parse_args()
    sys.exit(pipeline_orchestrator.main(args))
