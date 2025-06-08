# 箱庭 (Haconiwa) 🚧 **開発中**

[![PyPI version](https://badge.fury.io/py/haconiwa.svg)](https://badge.fury.io/py/haconiwa)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-alpha--development-red)](https://github.com/dai-motoki/haconiwa)

**箱庭 (Haconiwa)** は、AI協調開発支援Python CLIツールです。tmux会社管理、git-worktree連携、タスク管理、AIエージェント調整機能を統合し、効率的な開発環境を提供する次世代ツールです。

> ⚠️ **注意**: このプロジェクトは現在活発に開発中です。機能やAPIは頻繁に変更される可能性があります。

[🇺🇸 English README](README.md)

## 📋 バージョン管理

このプロジェクトは[Semantic Versioning](https://semver.org/lang/ja/)に従っています。

- **📄 変更履歴**: [CHANGELOG.md](CHANGELOG.md) - 全てのバージョンの変更履歴
- **🏷️ 最新バージョン**: 0.1.4
- **📦 PyPI**: [haconiwa](https://pypi.org/project/haconiwa/)
- **🔖 GitHubリリース**: [Releases](https://github.com/dai-motoki/haconiwa/releases)

## 🚀 今すぐ使える機能

### tmux マルチエージェント環境（実装済み）

4x4グリッドのマルチエージェント開発環境を**今すぐ**作成・管理できます：

```bash
# 1. インストール
pip install haconiwa

# 2. マルチエージェント環境作成（4組織 × 4役割 = 16ペイン）
haconiwa space multiagent --name my-project \
  --base-path /path/to/workspace \
  --org01-name "フロントエンド開発部" --task01 "UI設計" \
  --org02-name "バックエンド開発部" --task02 "API開発" \
  --org03-name "データベース部門" --task03 "スキーマ設計" \
  --org04-name "DevOps部門" --task04 "インフラ構築"

# 3. 会社一覧確認
haconiwa space list

# 4. 既存の会社に接続
haconiwa space attach my-project

# 5. 会社設定更新（既存会社の名前変更）
haconiwa space multiagent --name my-project \
  --base-path /path/to/workspace \
  --org01-name "新フロントエンド部" --task01 "React開発" \
  --no-attach

# 6. 会社終了
haconiwa space kill my-project
```

**📁 自動作成されるディレクトリ構造:**
```
/path/to/workspace/
├── org-01/
│   ├── 01boss/          # PM用ワークスペース
│   ├── 01worker-a/      # Worker-A用ワークスペース
│   ├── 01worker-b/      # Worker-B用ワークスペース
│   └── 01worker-c/      # Worker-C用ワークスペース
├── org-02/
│   ├── 02boss/
│   ├── 02worker-a/
│   ├── 02worker-b/
│   └── 02worker-c/
├── org-03/ (同様の構造)
└── org-04/ (同様の構造)
```

**✅ 実際に動作する機能:**
- 🏢 **マルチエージェント環境**: 4x4（16ペイン）の組織的tmuxレイアウト
- 📁 **自動ディレクトリ構成**: 組織・役割別ワークスペース自動作成
- 🏷️ **カスタム組織名・タスク名**: 動的なタイトル設定
- 🔄 **会社更新**: 既存会社の安全な設定変更
- 📋 **会社管理**: 作成・一覧・接続・削除の完全サポート
- 📄 **README自動生成**: 各ディレクトリにREADME.md自動作成

## ✨ 主な機能 (開発中)

- 🤖 **AIエージェント管理**: Boss/Workerエージェントの作成・監視
- 📦 **ワールド管理**: 開発環境の構築・管理
- 🖥️ **tmux会社連携**: 開発スペースの効率的な管理
- 📋 **タスク管理**: git-worktreeと連携したタスク管理システム
- 📊 **リソース管理**: DBやファイルパスの効率的なスキャン
- 👁️ **リアルタイム監視**: エージェントやタスクの進捗監視

## 🏗️ アーキテクチャ概念

### tmux ↔ Haconiwa 概念対応

| tmux概念 | Haconiwa概念 | 説明 |
|----------|-------------|------|
| **Session** | **Company（会社）** | 最上位の管理単位。プロジェクト全体を表現 |
| **Window** | **Room（部屋）** | 機能別の作業領域。特定の役割や機能を担当 |
| **Pane** | **Desk（デスク）** | 個別の作業スペース。具体的なタスク実行場所 |

### 論理階層管理

```
Company（会社）
├── Building（建物）    ← 論理管理層（tmuxに非依存）
│   └── Floor（階層）   ← 論理管理層（tmuxに非依存）
│       └── Room（部屋） ← tmux Window
│           └── Desk（デスク） ← tmux Pane
```

**論理管理層の特徴：**
- **Building**: プロジェクトの大分類（フロントエンド棟、バックエンド棟など）
- **Floor**: 機能分類（開発フロア、テストフロア、デプロイフロアなど）
- これらの層はtmux会社に直接対応せず、haconiwa内部で論理的に管理

### 組織構成モデル

```
Organization（組織）
├── PM（プロジェクトマネージャー）
│   ├── 全体調整
│   ├── タスク割り当て
│   └── 進捗管理
└── Worker（作業者）
    ├── Worker-A（開発担当）
    ├── Worker-B（テスト担当）
    └── Worker-C（デプロイ担当）
```

**役割定義：**
- **PM（Boss）**: 戦略的意思決定、リソース管理、品質保証
- **Worker**: 実装、テスト、デプロイなどの実行業務
- **Organization**: 複数のPM/Workerで構成される論理的なチーム単位

## 🚀 インストール

```bash
pip install haconiwa
```

> 📝 **開発ノート**: パッケージはPyPIで利用可能ですが、多くの機能はまだ開発中です。

## ⚡ クイックスタート

> 🎭 **重要**: 以下に示すコマンドは**デモンストレーション用です**。現在、これらのコマンドはヘルプ情報と基本構造を表示するものですが、実際の機能は開発中です。完全な機能の実装に向けて積極的に取り組んでいます。

### 1. 利用可能なコマンドを確認
```bash
haconiwa --help
```

### 2. プロジェクト初期化
```bash
haconiwa core init
```

### 3. 開発ワールド作成
```bash
haconiwa world create local-dev
```

### 4. AIエージェント起動
```bash
# ボスエージェント作成
haconiwa agent spawn boss

# ワーカーエージェント作成
haconiwa agent spawn worker-a
```

### 5. タスク管理
```bash
# 新しいタスク作成
haconiwa task new feature-login

# エージェントにタスク割り当て
haconiwa task assign feature-login worker-a

# 進捗監視
haconiwa watch tail worker-a
```

## 📖 コマンドリファレンス

> 🔧 **開発ノート**: 以下にリストされているコマンドは現在**デモンストレーションとテスト用途**のものです。CLI構造は機能していますが、ほとんどのコマンドはヘルプ情報やプレースホルダーレスポンスを表示します。各コマンドグループの基盤機能を積極的に開発中です。

CLIツールは7つの主要コマンドグループを提供します：

### `agent` - エージェント管理コマンド
協調開発のためのAIエージェント（Boss/Worker）を管理
- `haconiwa agent spawn <type>` - エージェント作成
- `haconiwa agent ps` - エージェント一覧表示
- `haconiwa agent kill <name>` - エージェント停止

### `core` - コア管理コマンド
システムのコア管理と設定
- `haconiwa core init` - プロジェクトの初期化
- `haconiwa core status` - システム状態確認
- `haconiwa core upgrade` - システムアップグレード

### `resource` - リソース管理
プロジェクトリソース（データベース、ファイルなど）のスキャンと管理
- `haconiwa resource scan` - リソーススキャン
- `haconiwa resource list` - リソース一覧表示

### `space` - tmuxスペースと会社管理
tmuxを使った効率的な開発ワークスペース管理
- `haconiwa space create <name>` - tmux会社作成
- `haconiwa space list` - 会社一覧
- `haconiwa space attach <name>` - 会社接続

### `task` - タスク管理コマンド
git-worktreeと連携したタスク管理
- `haconiwa task new <name>` - 新しいタスク作成
- `haconiwa task assign <task> <agent>` - タスク割り当て
- `haconiwa task status` - タスク状態確認

### `watch` - 監視コマンド
エージェントとタスクのリアルタイム監視
- `haconiwa watch tail <target>` - リアルタイム監視
- `haconiwa watch logs` - ログ表示

### `world` - ワールド管理
開発環境とワールドの管理
- `haconiwa world create <name>` - 新しい開発ワールドを作成
- `haconiwa world list` - ワールド一覧表示
- `haconiwa world switch <name>` - ワールド切り替え

## 🛠️ 開発状況

> 🎬 **現在のフェーズ**: **デモンストレーション・プロトタイピング**  
> ほとんどのCLIコマンドは現在、意図された構造とヘルプ情報を示すデモンストレーション用プレースホルダーです。各コマンドの背後にある核となる機能を積極的に開発中です。

### ✅ 完了済み機能
- 7つのコマンドグループを持つ基本CLI構造
- PyPIパッケージ配布とインストール
- コアプロジェクト初期化フレームワーク
- ヘルプシステムとコマンドドキュメント
- コマンドグループの組織化とルーティング

### 🚧 開発中機能
- AIエージェントの生成と管理 (プレースホルダー → 実装)
- tmux会社統合 (プレースホルダー → 実装)
- git-worktreeとのタスク管理 (プレースホルダー → 実装)
- リソーススキャン機能 (プレースホルダー → 実装)
- リアルタイム監視システム (プレースホルダー → 実装)
- ワールド/環境管理 (プレースホルダー → 実装)

### 📋 計画中機能
- 高度なAIエージェント協調
- 人気の開発ツールとの統合
- 拡張性のためのプラグインシステム
- Webベース監視ダッシュボード

## 🛠️ 開発環境セットアップ

```bash
git clone https://github.com/dai-motoki/haconiwa.git
cd haconiwa
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .[dev]
```

### テスト実行

```bash
pytest tests/
```

## 📝 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！これは活発な開発プロジェクトのため、以下をお勧めします：

1. 既存のissueとディスカッションを確認
2. このリポジトリをフォーク
3. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
4. 変更をコミット (`git commit -m 'Add amazing feature'`)
5. ブランチにプッシュ (`git push origin feature/amazing-feature`)
6. プルリクエストを作成

## 📞 サポート

- GitHub Issues: [Issues](https://github.com/dai-motoki/haconiwa/issues)
- メール: kanri@kandaquantum.co.jp

## ⚠️ 免責事項

このプロジェクトは初期アルファ開発段階かつ**デモンストレーションフェーズ**にあります。現在のCLIコマンドは主に意図されたインターフェースデザインを示すプレースホルダーです。ほとんどの機能は活発に開発中でまだ実装されていません。

**現在動作するもの:**
- CLIのインストールとコマンド構造
- ヘルプシステムとドキュメント
- 基本的なコマンドルーティング

**今後実装予定:**
- 宣伝されている全機能の完全実装
- AIエージェント協調機能
- 開発ツールとの統合
- 実際のタスクと会社管理

現時点では本番環境での使用は推奨されません。これは意図されたユーザーエクスペリエンスを示す開発プレビューです。

---

**箱庭 (Haconiwa)** - AI協調開発の未来 🚧 