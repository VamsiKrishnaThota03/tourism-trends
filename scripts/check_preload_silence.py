"""Assert that the W021 silence is conditional, not a blanket suppression.

SECURE_HSTS_PRELOAD is left off by default because submitting a domain to the
browser preload list is permanent. That leaves Django's `security.W021` warning,
which settings acknowledges via SILENCED_SYSTEM_CHECKS so `check --deploy` stays
genuinely clean — a check that always prints something trains people to ignore
it.

The risk with silencing anything is that it quietly becomes permanent. This
script is the guard: run with DJANGO_HSTS_PRELOAD=true, the silence must be
gone. Run from CI, and locally with:

    DJANGO_DEBUG=false DJANGO_HSTS_PRELOAD=true \
    DJANGO_SECRET_KEY=any-long-value python scripts/check_preload_silence.py
"""

import os
import pathlib
import re
import sys

import django


#: This script lives in scripts/, so the project root is not on sys.path the
#: way it is when manage.py runs. Add it, or importing the settings module
#: fails with ModuleNotFoundError.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def settings_module() -> str:
    """Read DJANGO_SETTINGS_MODULE out of manage.py.

    Taken from manage.py rather than hardcoded so this keeps working if the
    project is renamed.
    """
    manage = PROJECT_ROOT / "manage.py"
    match = re.search(
        r"""DJANGO_SETTINGS_MODULE["']\s*,\s*["']([\w.]+)""", manage.read_text()
    )
    if not match:
        sys.exit(f"could not find DJANGO_SETTINGS_MODULE in {manage}")
    return match.group(1)


def main() -> int:
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module()
    django.setup()

    from django.conf import settings

    if not settings.SECURE_HSTS_PRELOAD:
        return fail("expected SECURE_HSTS_PRELOAD to be True; set DJANGO_HSTS_PRELOAD=true")

    silenced = getattr(settings, "SILENCED_SYSTEM_CHECKS", [])
    if silenced:
        return fail(
            "W021 must not stay silenced once preload is enabled, "
            f"but SILENCED_SYSTEM_CHECKS is {silenced!r}"
        )

    print("silence is conditional, as intended")
    return 0


def fail(message: str) -> int:
    print(f"::error::{message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
