# ブランチ運用ルール
_最終更新: 2025-10-08

## 常設
- **main** : 常に配布可能な状態。保護（PR必須、直push禁止）。
- **release/*** : バージョン固定調整用（例: `release/v0.1.0`）。
- **hotfix/*** : 公開物の致命的不具合修正（例: `hotfix/overlay-crash`）。

## トピックブランチ（短命）
- **feature/**… 新機能（例: `feature/overlay-ws`）
- **fix/**… バグ修正（例: `fix/overlay-reconnect`）
- **perf/**… 性能改善（例: `perf/mouth-60hz`）
- **refactor/**… 挙動不変の整理（例: `refactor/tts-factory`）
- **infra/**… 環境（例: `infra/devcontainer-py312`）
- **ci/**… テスト/自動化（例: `ci/pytest-basic`）
- **docs/**… 文書（例: `docs/spec-update`）
- **experiment/**… 実験（例: `experiment/live2d`）

## コミット/PR 規約
- 1 PR = 1目的（サイズ小さく、レビューしやすく）。
- PR タイトル: `[feat] overlay ws` / `[fix] tts crash` など。
- main へは PR を通す。テストがあれば必須。

## 参考フロー
```bash
git switch -c infra/devcontainer-py312
# 変更
git add -A && git commit -m "infra: devcontainer for python3.12"
git switch main && git merge --no-ff infra/devcontainer-py312
```
