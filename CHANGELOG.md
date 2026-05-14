# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Renamed project name to ``resell-helper``.
- Improved error handling in scripts and workflow.
- Renamed workflows.

### Removed

- Push trigger in workflow.
- Unused import of python packages.

### Added

- Helper tool to make the process of publishing listings on multiple marketplaces easier.
- Documentation for publish tool in ``README.md``.

## [0.1.0] - 2026-04-03

### Added

- Scraping tools for blocket, ebay, facebook, tradera and vinted.
- Automated workflow using github actions, optional input parameters.
- Global fetch variables which can be changed to match preference, also used as fallback when workflow input is empty.
- README with description and setup guide.
