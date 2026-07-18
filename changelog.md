# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-18-07

### Added

- route `/new` for built new article.
- route `/edit/[ id ]` editing article page.
- route `/admin` simple dashboard with tiny css.
- route `/` homepage.
- add `requirements.txt` (dependencies for webapp).
- add `main.py` for entrypoint :D

- add `templates/admin.html` admin simple dashboard.
- add `templates/edit.html` editor page simple.
- add `templates/index.html` simple homepage blog.
- add `templates/new.html` simple page editor (create article).
- add `templates/view.html` simple reader article.

- add `/static/style.css` simple style css :D

### Infrastructure

- `/md/` folder indexing md file.
- database sqlite3 (article.db).
- Changelog tracking (this file).
- `/templates/` and `/static/` requirement flask default configuration.
- `/blueprint/` making new route without root app :D

### Known Issues

- (Any limitations? List them).
- currently not scalable.
- default protection (not secured).
- no rate-limit.
- form not secured.
- web login not secured.
- request not secured.
