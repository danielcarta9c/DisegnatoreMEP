# Only the low-level diagnostic vocabulary is re-exported here. `validate_project`
# lives in `.topology`, which depends on the catalog and domain packages; importing
# it from this __init__ creates a cycle, because `domains.base` imports
# `validation.issues` and that initialises this package first.
from .issues import ValidationIssue, ValidationReport

__all__ = ["ValidationIssue", "ValidationReport"]
