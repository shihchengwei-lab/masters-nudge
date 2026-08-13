#!/usr/bin/env python3
"""Capture wrapper that emits the microsecond timestamp shape used in production."""

from datetime import datetime as StandardDatetime

from evaluation.lens_differentiation import tk_capture


class ProductionShapeDatetime(StandardDatetime):
    def isoformat(self, *args, **kwargs):
        kwargs.setdefault("timespec", "microseconds")
        return super().isoformat(*args, **kwargs)


def main() -> int:
    tk_capture.datetime = ProductionShapeDatetime
    return tk_capture.main()


if __name__ == "__main__":
    raise SystemExit(main())
