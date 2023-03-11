# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

* The following tags must be used:
    Added for new features.
    Changed for changes in existing functionality.
    Deprecated for soon-to-be removed features.
    Removed for now removed features.
    Fixed for any bug fixes.
    Security in case of vulnerabilities.

Format message: date_at issue_id message changes
example: * date_at - Task 0002 - fixed some bug.

## [Unreleased]

### Changed

* 2022-11-25 - Task 0082 - Modificada estrutura de models da app material.

### Added

* 2022-11-29 - #devops - Adicionado fluxo de deploy para homologação.
* 2022-11-29 - Task 0082 - Adicionado mixins `ListObjectServiceContextMixin`, `RetrieveObjectServiceContextMixin` e `ReadWithServiceContextMixin`.
* 2022-11-27 - Task 0082 - Adicionado fluxo de leitura de lives.
* 2022-11-27 - Task 0082 - Adicionado nova model de Live e seu admin.
* 2022-11-25 - Task 0082 - Adicionado novo backend de integração com a Apple.
* 2022-11-25 - Task 0082 - Adicionada dependência do `python-jose`.
* 2022-11-25 - Task 0082 - Adicionado campo `backend` no admin de StoreModel.
* 2022-11-25 - Task 0082 - Adicionado novo fluxo de listagem de `credential-fields` no endpoint `/api/v1/service/{service_slug}/credential-fields/{credential_config_type}`.

### Fixed

* 2022-11-25 - Task 0082 - Corrigidas e otimizadas as queries e nome dos testes.

### Removed

* 2022-11-25 - Task 0082 - Removidas migrations antigas e setada tudo pra migration inicial.
* 2022-11-25 - Task 0082 - Removido endpoint `api/v1/credential-fields/{credential_config_type}`.
