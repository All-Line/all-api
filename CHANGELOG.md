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
example: * date_at - fixed some bug.

## [Unreleased]

### Changed

* 2023-05-18 - Alterado o nome do Answers para User answers
* 2023-05-13 - Alterado o nome da app `material` no painel admin para `EAD`.
* 2023-04-24 - Limpado o arquivo `CHANGELOG.md` para iniciar o versionamento do projeto.
* 2023-04-24 - Modificado nome dos arquivos de workflow e título dos mesmos
* 2023-04-25 - Modificado nome do sistema para All Line System

### Added

* 2023-05-20 - Adicionado preview de `attachment` nos paineis do admin
* 2023-05-19 - Adicionado novos filtros no `PostComment`
* 2023-05-18 - Adicionado campo `thumbnail` na model MissionModel,
no serializer e no admin.
* 2023-05-18 - Adicionado campo `attachment_type` nas models que possuem attachment.
* 2023-05-13 - Adicionado texto de ajuda no campo `event_type` da model `EventModel`
* 2023-04-24 - Adicionado upgrade do pip no comando `make install-requirements`
* 2023-04-25 - Adicionada integração com a mensagem do slack para o deploy

### Fixed

* 2023-05-18 - Adicionado campo `attachment_type` na serialização do post.
* 2023-05-13 - Corrigida cobertura de testes para 100%

### Removed

* 2023-05-19 - Removido o campo `type` de `PostModel`
* 2023-05-19 - Removido `reactions types` do `admin`
