from pathlib import Path


INTERNAL_ROOTS = (
    Path("analytics"),
    Path("backend"),
    Path("decision_engine"),
    Path("simulation"),
)


def test_internal_components_do_not_import_kernel_api():
    violations = []

    for root in INTERNAL_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            text = path.read_text()

            if "from kernel.api import" in text or "import kernel.api" in text:
                violations.append(str(path))

    assert not violations, (
        "Internal components must not import kernel.api: "
        + ", ".join(sorted(violations))
    )
