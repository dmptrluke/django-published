# Changelog

## 1.1.0 - 2026-03-25

- Add `PublishStatus` IntegerChoices enum as the preferred interface for publish status constants. Import from `published.constants.PublishStatus`.
- Deprecate bare constants (`AVAILABLE`, `NEVER_AVAILABLE`, `AVAILABLE_AFTER`, `PUBLISH_CHOICES`). These still work but will be removed in a future release.
- Switch test runner from Django's built-in to pytest-django.

## 1.0.0 - 2026-03-25

Stable release. No functional changes from 0.10.0.
