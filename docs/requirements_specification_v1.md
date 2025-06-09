# Haconiwa v1.0 要件定義書

## 概要

Haconiwa v1.0 は、AI協調開発のための**宣言型YAML + tmux + Git worktree**フレームワークです。本文書では、Haconiwa v1.0の完全な要件定義を記載します。

---

## 1. システム概要

### 1.1 基本理念
- **宣言型管理**: `apiVersion: haconiwa.dev/v1`のYAML一発適用でWorld～Deskまで生成
- **階層管理**: World → Company → Room → Deskを**`haconiwa space`**1系列で操作
- **GitHub連携**: Company単位でリポジトリURL・認証方式を指定、`clone`/`pull`自動実行
- **ツール統合**: ファイルパスやDBのスキャンを**`haconiwa tool`**に一本化
- **セキュリティ**: `CommandPolicy`でCLI実行を静的ガード（役割別allow/deny）

### 1.2 主要特徴
| 特徴 | 説明 |
|------|------|
| 宣言型設定 | Kubernetes風のCRD（Custom Resource Definition）形式 |
| 階層構造 | World → Nation → City → Village → Company → Building → Floor → Room → Desk |
| tmux統合 | セッション・ペイン管理の自動化 |
| Git worktree | ブランチ別作業ディレクトリの自動管理 |
| マルチエージェント | AI役割分担（PM/Worker）の明確化 |

### 1.3 CRD（Custom Resource Definition）とは
**CRD**は、Kubernetesで独自のリソースタイプを定義する仕組みです。Haconiwa v1では、以下の構造を採用：

```yaml
apiVersion: haconiwa.dev/v1    # APIバージョン
kind: <ResourceType>           # リソースタイプ（Space, Agent, Task等）
metadata:                      # メタデータ
  name: <resource-name>
spec:                          # 仕様定義
  # リソース固有の設定
```

Haconiva v1で定義する6つのCRD：
1. **Space** - World/Company/Room/Desk階層
2. **Agent** - AIエージェント設定
3. **Task** - Git worktreeタスク
4. **PathScan** - ファイルスキャン設定
5. **Database** - DB接続設定
6. **CommandPolicy** - コマンド実行ポリシー

---

## 2. 機能要件

### 2.1 コアモジュール

#### 2.1.1 Space管理
- World、Company、Room、Deskの階層管理
- tmuxセッション・ペインの自動作成・管理
- Gitリポジトリの自動clone・pull
- ディレクトリ構造の自動生成

#### 2.1.2 Agent管理
- AI エージェントのライフサイクル管理（spawn/stop/kill/delete）
- プロセス監視とログ管理
- 役割別設定（PM/Worker）

#### 2.1.3 Task管理
- ブランチベースのタスク管理
- Git worktreeとの連携
- タスクの割り当て・完了管理

#### 2.1.4 Tool統合
- ファイルパススキャン機能
- データベーススキャン機能
- 結果のJSON/YAML出力

#### 2.1.5 Policy管理
- コマンド実行のホワイトリスト機能
- 役割別権限管理
- 実行前の静的検証

### 2.2 CRD（Custom Resource Definition）仕様

#### 2.2.1 Space CRD
```yaml
# =====================================================================
# ① Space ─ floor=1, room=2　32 desk（4 org ×〈PM1+W3〉×2 room）
# =====================================================================
apiVersion: haconiwa.dev/v1
kind: Space
metadata:
  name: dev-world
spec:
  nations:
  - id: jp
    name: 日本
    cities:
    - id: tokyo
      name: 東京
      villages:
      - id: chiyoda
        name: 千代田
        companies:
        - name: haconiwa-company              # tmux session 名
          grid: 8x4                           # 32 pane
          basePath: /desks/haconiwa-company
          gitRepo:
            url: https://github.com/example-org/haconiwa-monorepo.git
            defaultBranch: main
            auth: ssh                         # ssh / https / token
          organizations:
          - {id: "01", name: Frontend Dept.,  tasks: ["UI 設計"]}
          - {id: "02", name: Backend Dept.,   tasks: ["API 開発"]}
          - {id: "03", name: Database Dept.,  tasks: ["スキーマ設計"]}
          - {id: "04", name: DevOps Dept.,    tasks: ["インフラ構築"]}
          buildings:
          - id: hq
            name: Main Building
            floors:
            - level: 1
              rooms:
              - id: room-01
                name: Alpha Room
                desks:
                # org-01
                - id: desk-0100 ; agent: {name: org01-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0101 ; agent: {name: org01-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0102 ; agent: {name: org01-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0103 ; agent: {name: org01-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-02
                - id: desk-0200 ; agent: {name: org02-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0201 ; agent: {name: org02-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0202 ; agent: {name: org02-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0203 ; agent: {name: org02-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-03
                - id: desk-0300 ; agent: {name: org03-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0301 ; agent: {name: org03-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0302 ; agent: {name: org03-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0303 ; agent: {name: org03-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-04
                - id: desk-0400 ; agent: {name: org04-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0401 ; agent: {name: org04-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0402 ; agent: {name: org04-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0403 ; agent: {name: org04-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
              - id: room-02
                name: Beta Room
                desks:
                # org-01
                - id: desk-1100 ; agent: {name: org01-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1101 ; agent: {name: org01-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1102 ; agent: {name: org01-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1103 ; agent: {name: org01-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-02
                - id: desk-1200 ; agent: {name: org02-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1201 ; agent: {name: org02-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1202 ; agent: {name: org02-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1203 ; agent: {name: org02-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-03
                - id: desk-1300 ; agent: {name: org03-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1301 ; agent: {name: org03-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1302 ; agent: {name: org03-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1303 ; agent: {name: org03-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-04
                - id: desk-1400 ; agent: {name: org04-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1401 ; agent: {name: org04-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1402 ; agent: {name: org04-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1403 ; agent: {name: org04-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
```

**要件**:
- 32デスク（4組織 × 〈PM1+Worker3〉× 2ルーム）の自動配置
- tmuxグリッド（8x4）の自動設定
- Gitリポジトリとの自動連携（SSH/HTTPS/Token認証対応）
- 組織別タスク定義
- 各デスクにエージェント設定の埋め込み

#### 2.2.2 Agent CRD
```yaml
# =====================================================================
# ② 追加 Agent ─ org02 PM は systemPromptPath を指定
# =====================================================================
apiVersion: haconiwa.dev/v1
kind: Agent
metadata:
  name: org02-pm
spec:
  role: pm
  model: o3
  spaceRef: haconiwa-company
  systemPromptPath: prompts/org02/system_prompt.txt
  env:
    OPENAI_API_KEY: ${OPENAI_API_KEY}
```

**要件**:
- 役割別設定（pm/worker）
- AIモデル指定（o3/gpt-4o等）
- カスタムシステムプロンプト対応
- 環境変数管理
- spaceRef によるSpace CRDとの関連付け

#### 2.2.3 Task CRD
```yaml
# =====================================================================
# ③ Task
# =====================================================================
apiVersion: haconiwa.dev/v1
kind: Task
metadata:
  name: feature-login
spec:
  branch: feature/login
  worktree: true
  assignee: org01-wk-a-r1
  spaceRef: haconiwa-company
  description: "ログイン機能の実装"
```

**要件**:
- Git worktree連携
- エージェント割り当て機能
- ブランチベース作業管理
- spaceRef によるSpace CRDとの関連付け

#### 2.2.4 PathScan CRD
```yaml
# =====================================================================
# ④ PathScan
# =====================================================================
apiVersion: haconiwa.dev/v1
kind: PathScan
metadata:
  name: default-scan
spec:
  include: ["src/**/*.py"]
  exclude: [".venv/**", "tests/**"]
```

**要件**:
- ファイルパターンによるinclude/exclude指定
- 複数パターン対応（グロブパターン）
- 除外パターンの優先適用

#### 2.2.5 Database CRD
```yaml
# =====================================================================
# ⑤ Database
# =====================================================================
apiVersion: haconiwa.dev/v1
kind: Database
metadata:
  name: local-postgres
spec:
  dsn: "postgresql://postgres:postgres@127.0.0.1:5432/app"
  useSSL: false
```

**要件**:
- 各種データベース接続対応（PostgreSQL, MySQL, SQLite等）
- SSL設定管理
- DSN（Data Source Name）形式での接続文字列指定

#### 2.2.6 CommandPolicy CRD
```yaml
# =====================================================================
# ⑥ CommandPolicy
# =====================================================================
apiVersion: haconiwa.dev/v1
kind: CommandPolicy
metadata:
  name: default-command-whitelist
spec:
  global:
    docker:   [build, pull, run, images, ps]
    kubectl:  [get, describe, apply, logs]
    git:      [clone, pull, commit, push, worktree]
    tmux:     [new-session, kill-session, split-window, send-keys]
    haconiwa: [space.start, space.stop, space.kill, space.delete,
               space.clone, space.pull,
               task.new, task.assign, task.finish,
               agent.spawn, tool]
  roles:
    pm:
      allow: {kubectl: [scale, rollout]}
    worker:
      deny:  {docker: [system prune]}
```

**要件**:
- グローバルコマンドホワイトリスト
- 役割別allow/deny設定
- プロセス起動前の静的検証
- コマンド・サブコマンドレベルでの制御

### 2.3 完全版サンプルYAML

上記CRDを統合した完全版のリソース定義ファイル例：

```yaml
# haconiwa-resources.yaml
# =====================================================================
# 全 CRD を 1 ファイルに統合（32デスク完全版）
# =====================================================================

# ① Space ─ 32 desk（4 org ×〈PM1+W3〉×2 room）
apiVersion: haconiwa.dev/v1
kind: Space
metadata:
  name: dev-world
spec:
  nations:
  - id: jp
    name: 日本
    cities:
    - id: tokyo
      name: 東京
      villages:
      - id: chiyoda
        name: 千代田
        companies:
        - name: haconiwa-company
          grid: 8x4
          basePath: /desks/haconiwa-company
          gitRepo:
            url: https://github.com/example-org/haconiwa-monorepo.git
            defaultBranch: main
            auth: ssh
          organizations:
          - {id: "01", name: Frontend Dept.,  tasks: ["UI 設計"]}
          - {id: "02", name: Backend Dept.,   tasks: ["API 開発"]}
          - {id: "03", name: Database Dept.,  tasks: ["スキーマ設計"]}
          - {id: "04", name: DevOps Dept.,    tasks: ["インフラ構築"]}
          buildings:
          - id: hq
            name: Main Building
            floors:
            - level: 1
              rooms:
              - id: room-01
                name: Alpha Room
                desks:
                # org-01（4デスク）
                - id: desk-0100 ; agent: {name: org01-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0101 ; agent: {name: org01-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0102 ; agent: {name: org01-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0103 ; agent: {name: org01-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-02（4デスク）
                - id: desk-0200 ; agent: {name: org02-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0201 ; agent: {name: org02-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0202 ; agent: {name: org02-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0203 ; agent: {name: org02-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-03（4デスク）
                - id: desk-0300 ; agent: {name: org03-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0301 ; agent: {name: org03-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0302 ; agent: {name: org03-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0303 ; agent: {name: org03-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-04（4デスク）
                - id: desk-0400 ; agent: {name: org04-pm-r1,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0401 ; agent: {name: org04-wk-a-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0402 ; agent: {name: org04-wk-b-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-0403 ; agent: {name: org04-wk-c-r1, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
              - id: room-02
                name: Beta Room
                desks:
                # org-01（4デスク）
                - id: desk-1100 ; agent: {name: org01-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1101 ; agent: {name: org01-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1102 ; agent: {name: org01-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1103 ; agent: {name: org01-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-02（4デスク）
                - id: desk-1200 ; agent: {name: org02-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1201 ; agent: {name: org02-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1202 ; agent: {name: org02-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1203 ; agent: {name: org02-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-03（4デスク）
                - id: desk-1300 ; agent: {name: org03-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1301 ; agent: {name: org03-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1302 ; agent: {name: org03-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1303 ; agent: {name: org03-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                # org-04（4デスク）
                - id: desk-1400 ; agent: {name: org04-pm-r2,   role: pm,     model: o3,      env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1401 ; agent: {name: org04-wk-a-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1402 ; agent: {name: org04-wk-b-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}
                - id: desk-1403 ; agent: {name: org04-wk-c-r2, role: worker, model: gpt-4o,  env: {OPENAI_API_KEY: ${OPENAI_API_KEY}}}

---
# ② 追加 Agent ─ org02 PM は systemPromptPath を指定
apiVersion: haconiwa.dev/v1
kind: Agent
metadata:
  name: org02-pm
spec:
  role: pm
  model: o3
  spaceRef: haconiwa-company
  systemPromptPath: prompts/org02/system_prompt.txt
  env:
    OPENAI_API_KEY: ${OPENAI_API_KEY}

---
# ③ Task
apiVersion: haconiwa.dev/v1
kind: Task
metadata:
  name: feature-login
spec:
  branch: feature/login
  worktree: true
  assignee: org01-wk-a-r1
  spaceRef: haconiwa-company
  description: "ログイン機能の実装"

---
# ④ PathScan
apiVersion: haconiwa.dev/v1
kind: PathScan
metadata:
  name: default-scan
spec:
  include: ["src/**/*.py"]
  exclude: [".venv/**", "tests/**"]

---
# ⑤ Database
apiVersion: haconiwa.dev/v1
kind: Database
metadata:
  name: local-postgres
spec:
  dsn: "postgresql://postgres:postgres@127.0.0.1:5432/app"
  useSSL: false

---
# ⑥ CommandPolicy
apiVersion: haconiwa.dev/v1
kind: CommandPolicy
metadata:
  name: default-command-whitelist
spec:
  global:
    docker:   [build, pull, run, images, ps]
    kubectl:  [get, describe, apply, logs]
    git:      [clone, pull, commit, push, worktree]
    tmux:     [new-session, kill-session, split-window, send-keys]
    haconiwa: [space.start, space.stop, space.kill, space.delete,
               space.clone, space.pull,
               task.new, task.assign, task.finish,
               agent.spawn, tool]
  roles:
    pm:
      allow: {kubectl: [scale, rollout]}
    worker:
      deny:  {docker: [system prune]}
```

---

## 3. CLI仕様

### 3.1 インストール要件
```bash
pip install haconiwa
```

### 3.2 基本コマンド体系

#### 3.2.1 初期化・適用
```bash
haconiwa init                                    # 初期セットアップ
haconiwa apply -f haconiwa-resources.yaml       # 全リソース定義を適用
```

#### 3.2.2 space操作（World〜Desk操作）
```bash
haconiwa space ls|describe|start|stop|kill|delete|attach|clone|pull
  [--world/-w] [--company/-c] [--room/-r] [--desk/-d] [--purge-data]
```

**具体例**:
```bash
# Git リポジトリ clone & セッション起動
haconiwa space clone -c haconiwa-company
haconiwa space start -c haconiwa-company

# Room に接続
haconiwa space attach -c haconiwa-company -r room-01

# セッション停止・削除
haconiwa space stop   -c haconiwa-company
haconiwa space delete -c haconiwa-company --purge-data
```

#### 3.2.3 agent操作
```bash
haconiwa agent spawn|stop|kill|delete <id>
haconiwa agent ps
haconiwa agent logs <id>
```

#### 3.2.4 task操作
```bash
haconiwa task new <name> --from <company>
haconiwa task assign|finish|delete <task>
haconiwa task ls
```

#### 3.2.5 tool操作（スキャン機能）
```bash
haconiwa tool --scan-filepath <PathScan>  [-F]
haconiwa tool --scan-db       <Database>  [-D]
  --json | --yaml | --quiet | --dry-run
```

**具体例**:
```bash
# ファイル or DB スキャン
haconiwa tool --scan-filepath default-scan
haconiwa tool --scan-db local-postgres --yaml
```

#### 3.2.6 policy操作
```bash
haconiwa policy ls
haconiwa policy test agent <id> --cmd "<shell>"
haconiwa policy delete <name>
```

---

## 4. ディレクトリ構造要件

### 4.1 自動生成ディレクトリ構造
```
/desks/haconiwa-company/
├── org-01/01pm/          ← desk-0100
├── org-01/01worker-a/    ← desk-0101
├── org-01/01worker-b/    ← desk-0102
├── org-01/01worker-c/    ← desk-0103
├── org-02/02pm/          ← desk-0200
├── org-02/02worker-a/    ← desk-0201
├── org-02/02worker-b/    ← desk-0202
├── org-02/02worker-c/    ← desk-0203
├── org-03/03pm/          ← desk-0300
├── org-03/03worker-a/    ← desk-0301
├── org-03/03worker-b/    ← desk-0302
├── org-03/03worker-c/    ← desk-0303
├── org-04/04pm/          ← desk-0400
├── org-04/04worker-a/    ← desk-0401
├── org-04/04worker-b/    ← desk-0402
└── org-04/04worker-c/    ← desk-0403
├── org-01/11pm/          ← desk-1100 (room-02)
├── org-01/11worker-a/    ← desk-1101 (room-02)
├── org-01/11worker-b/    ← desk-1102 (room-02)
├── org-01/11worker-c/    ← desk-1103 (room-02)
├── org-02/12pm/          ← desk-1200 (room-02)
├── org-02/12worker-a/    ← desk-1201 (room-02)
├── org-02/12worker-b/    ← desk-1202 (room-02)
├── org-02/12worker-c/    ← desk-1203 (room-02)
├── org-03/13pm/          ← desk-1300 (room-02)
├── org-03/13worker-a/    ← desk-1301 (room-02)
├── org-03/13worker-b/    ← desk-1302 (room-02)
├── org-03/13worker-c/    ← desk-1303 (room-02)
├── org-04/14pm/          ← desk-1400 (room-02)
├── org-04/14worker-a/    ← desk-1401 (room-02)
├── org-04/14worker-b/    ← desk-1402 (room-02)
└── org-04/14worker-c/    ← desk-1403 (room-02)
```

### 4.2 ディレクトリ命名規則
- **組織ID**: `org-01`, `org-02`, `org-03`, `org-04`
- **役割**: `pm`, `worker-a`, `worker-b`, `worker-c`
- **ルーム**: room-01は`0X`, room-02は`1X`形式
- **デスクID**: `desk-XXYY` (XX=組織+ルーム, YY=役割)

---

## 5. ライフサイクル管理要件

| 段階 | コマンド例 | 説明 |
|------|------------|------|
| 初期化 | `haconiwa init` | 設定ファイル初期化 |
| 定義適用 | `haconiwa apply -f haconiwa-resources.yaml` | 全リソース適用 |
| リポジトリ取得 | `haconiwa space clone -c haconiwa-company` | Git clone実行 |
| 起動 | `haconiwa space start -c haconiwa-company` | tmuxセッション開始 |
| 接続 | `haconiwa space attach -c haconiwa-company -r room-01` | 特定ルームに接続 |
| 更新 | `haconiwa space pull -c haconiwa-company` | Git pull実行 |
| 停止 | `haconiwa space stop -c haconiwa-company` | セッション停止 |
| 強制停止 | `haconiwa space kill -c haconiwa-company` | 強制終了 |
| 削除 | `haconiwa space delete -c haconiwa-company --purge-data` | 完全削除 |

---

## 6. セキュリティ要件

### 6.1 CommandPolicy機能
- **プロセス起動前の静的検証**: 実行前にコマンドの許可・禁止を判定
- **役割別権限管理**: PM/Worker毎に異なる権限設定
- **ホワイトリスト方式**: 明示的に許可されたコマンドのみ実行可能

### 6.2 権限例
```yaml
roles:
  pm:
    allow: {kubectl: [scale, rollout]}    # PMのみk8sスケーリング可能
  worker:
    deny:  {docker: [system prune]}       # WorkerはDockerクリーンアップ禁止
```

---

## 7. 技術要件

### 7.1 依存関係
- **Python**: 3.8以上
- **tmux**: セッション・ペイン管理
- **Git**: リポジトリ管理・worktree機能
- **PyYAML**: YAML設定ファイル解析

### 7.2 対応プラットフォーム
- **Linux**: Ubuntu 20.04以上
- **macOS**: 10.15以上
- **Windows**: WSL2環境

### 7.3 AI Model対応
- **OpenAI**: GPT-4o, o3
- **拡張性**: 他のLLMプロバイダーへの対応準備

---

## 8. 拡張性・ロードマップ

### 8.1 v1.0対象外（v2検討事項）
- `nation` / `city` / `village` CLIの正式実装
- Building / Floorへの自動リソース配分ロジック
- Webダッシュボード + WebSocket監視
- プラグインSDK（外部SaaS・CI/CD連携）

### 8.2 プラグインアーキテクチャ
将来的な拡張を見据えた設計:
- **Tool Plugin**: 新しいスキャン機能の追加
- **Provider Plugin**: 新しいAIモデル・クラウドサービス対応
- **Workflow Plugin**: カスタムワークフロー定義

---

## 9. 品質要件

### 9.1 パフォーマンス
- **32ペイン同時起動**: 10秒以内
- **Git clone**: リポジトリサイズに依存、進捗表示
- **YAML適用**: 1000行以下で5秒以内

### 9.2 可用性
- **エラーハンドリング**: 適切なエラーメッセージと復旧手順
- **ログ出力**: デバッグ可能な詳細ログ
- **設定検証**: YAML構文・内容の事前検証

### 9.3 保守性
- **モジュール分離**: Core/Space/Agent/Task/Tool/Policy
- **テスト**: 単体・統合テストの充実
- **ドキュメント**: CLI・CRD・アーキテクチャ文書

---

## 10. 制約・前提条件

### 10.1 制約
- tmuxセッション名の一意性が必要
- Git認証情報の事前設定が必要
- AIモデルのAPI Key設定が必要

### 10.2 前提条件
- 開発者のtmux基本操作知識
- Git・Git worktreeの理解
- YAML記法の理解
- 基本的なLinux/macOSコマンド操作

---

## 11. 用語定義

| 用語 | 定義 |
|------|------|
| World | 最上位の論理的な世界単位 |
| Nation | 国家レベルの区分 |
| City | 都市レベルの区分 |
| Village | 村レベルの区分 |
| Company | 企業・プロジェクト単位（tmuxセッション対応） |
| Building | 建物単位 |
| Floor | フロア単位 |
| Room | 部屋単位（サブセッション的な概念） |
| Desk | 個別の作業席（tmuxペイン対応） |
| Agent | AI エージェント（PM/Worker） |
| Task | Git worktreeベースのタスク |
| CRD | Custom Resource Definition（Kubernetes風のリソース定義形式） |
| PathScan | ファイルパススキャン設定 |
| Database | データベース接続設定 |
| CommandPolicy | コマンド実行ポリシー |
| Space | World～Desk階層全体を管理するCRD（kind: Space） |

---

## 12. 既存実装とのコンフリクト分析・移行戦略

### 12.1 主要コンフリクトポイント

#### 12.1.1 CLI構造の変更
| 項目 | 現在の実装 | v1.0要件 | 移行対応 |
|------|-----------|----------|----------|
| Space管理 | `haconiwa company` | `haconiwa space` | 既存commandを`space`にリネーム |
| Tool機能 | `haconiwa resource` | `haconiwa tool` | 既存commandを`tool`にリネーム |
| 初期化 | なし | `haconiwa init` | 新規実装 |
| CRD適用 | なし | `haconiwa apply` | 新規実装 |
| ポリシー管理 | なし | `haconiwa policy` | 新規実装 |

#### 12.1.2 アーキテクチャの変更
| 項目 | 現在の実装 | v1.0要件 | 移行対応 |
|------|-----------|----------|----------|
| 設定形式 | Pythonクラス | YAML CRD | CRDパーサー実装 |
| ペイン数 | 16ペイン(4x4) | 32ペイン(8x4) | tmux layout変更 |
| ルーム概念 | 1セッションのみ | 2ルーム対応 | マルチルーム実装 |
| Git連携 | 基本操作 | worktree強化 | worktree manager拡張 |

#### 12.1.3 データ構造の変更
```python
# 現在の実装（16ペイン）
organizations = [
    {"id": "org-01", "org_name": str, "task_name": str, "workspace": str},
    {"id": "org-02", "org_name": str, "task_name": str, "workspace": str},
    {"id": "org-03", "org_name": str, "task_name": str, "workspace": str},
    {"id": "org-04", "org_name": str, "task_name": str, "workspace": str}
]

# v1.0要件（32ペイン + CRD）
# YAML CRD形式 + 2ルーム + 各デスクにagent埋め込み
```

#### 12.1.4 新規機能の実装要件
| 機能 | 実装状況 | v1.0要件 | 実装優先度 |
|------|----------|----------|-----------|
| CommandPolicy | 未実装 | CRD + 静的検証 | 高 |
| PathScan | 既存（`path_scanner.py`） | CRD化 | 中 |
| Database | 既存（`db_fetcher.py`） | CRD化 | 中 |
| Agent管理 | 既存（`agent/`） | CRD連携強化 | 高 |
| Task管理 | 既存（`task/`） | worktree強化 | 高 |

### 12.2 段階的移行戦略

#### Phase 1: コア機能実装（週1-2）
1. **CRDパーサー実装**
   - `src/haconiwa/core/crd/` モジュール作成
   - YAML loader + validation
   - 6つのCRD定義（Space, Agent, Task, PathScan, Database, CommandPolicy）

2. **CLI構造変更**
   - `company_app` → `space_app` リネーム
   - `resource_app` → `tool_app` リネーム
   - `apply`, `init` コマンド追加

#### Phase 2: 機能拡張（週3-4）
1. **32ペイン対応**
   - `tmux.py` の layout ロジック変更
   - 2ルーム対応実装

2. **CommandPolicy実装**
   - 静的検証エンジン
   - 役割別権限管理

#### Phase 3: 統合・最適化（週5-6）
1. **既存機能のCRD化**
   - PathScan, Database の CRD対応
   - Agent, Task の CRD連携強化

2. **テスト・ドキュメント整備**

### 12.3 後方互換性
- **Phase 1**: 既存CLIと並行稼働（deprecation warning）
- **Phase 2**: 既存CLI無効化、新CLI完全移行
- **設定移行ツール**: 既存設定を新CRD形式に変換

### 12.4 破壊的変更リスト
1. ❌ `haconiwa company` → `haconiwa space`
2. ❌ `haconiwa resource` → `haconiwa tool`
3. ❌ 16ペイン → 32ペイン（既存セッション非互換）
4. ❌ Python設定 → YAML CRD設定
5. ⚠️ Agent API変更（CRD連携）
6. ⚠️ Task API変更（worktree強化）

---

**文書作成日**: 2025-01-25  
**文書バージョン**: v1.0.0  
**文書管理者**: Haconiwa開発チーム

---

## 13. 実装計画・タスクリスト

### 13.1 最優先実装: YAML Apply → 32ペイン作成

#### 🔥 Phase 1: 核となる機能完成（今すぐ実行）

**1. SpaceManager の32ペイン対応修正**
- [ ] `create_multiroom_session()` で32ペイン(8x4)レイアウト対応
- [ ] `generate_desk_mappings()` でroom-01/room-02の正しいマッピング生成
  - room-01: desk-0100~0403 (org-01~04 × pm+worker-abc)
  - room-02: desk-1100~1403 (org-01~04 × pm+worker-abc)
- [ ] ディレクトリ命名規則の修正
  - room-01: `01pm`, `01worker-a` 形式
  - room-02: `11pm`, `11worker-a` 形式 (先頭1追加)

**2. CRDApplier のSpace CRD処理修正**
- [ ] `_apply_space_crd()` でSpaceManager連携
- [ ] `convert_crd_to_config()` でCRD→内部設定変換
- [ ] Git repository連携（clone/pull）

**3. 統合テスト修正**
- [ ] Mock設定エラー修正（metadata属性）
- [ ] Policy Engine ロール拒否ロジック修正
- [ ] SpaceManager 32ペイン作成テスト修正

#### 🎯 Phase 2: エンドツーエンドテスト

**4. YAML Apply完全動作確認**
```bash
# 目標動作フロー
haconiwa init
haconiwa apply -f test-32desk.yaml
# → /tmp/test-desks/ に32デスクディレクトリ作成
# → tmux セッション「test-company」で32ペイン作成
# → 各ペインが正しいディレクトリを指している
```

**5. テストケース完全クリア**
- [ ] 3つの主要テスト維持（CRD Parser, Policy Engine, CLI init）
- [ ] 残り98テスト中の主要エラー修正
- [ ] 全テストグリーン達成

#### 📊 Phase 3: 残り機能実装

**6. Tool統合完成**
- [ ] `haconiwa tool --scan-filepath` 動作
- [ ] `haconiwa tool --scan-db` 動作
- [ ] JSON/YAML出力対応

**7. Policy機能完成**
- [ ] 役割別allow/deny正常動作
- [ ] `haconiwa policy test` コマンド完全動作
- [ ] 悪意のあるコマンド検出

### 13.2 実装状況トラッキング

| 機能 | 現在の状況 | 目標 | 優先度 |
|------|------------|------|--------|
| ✅ CRD Parser | 動作中 | 維持 | 最高 |
| ✅ CLI init | 動作中 | 維持 | 最高 |
| ✅ Policy基礎 | 動作中 | ロール拒否修正 | 高 |
| 🚧 SpaceManager | 16ペイン | **32ペイン対応** | **最高** |
| 🚧 CRD Apply | 基礎実装 | **Space CRD完全対応** | **最高** |
| ❌ Tool統合 | Mock実装 | 実機能実装 | 中 |
| ❌ 32ペインテスト | 失敗中 | 全パス | 高 |

### 13.3 成功基準

**✅ Phase 1完了の定義:**
```bash
# このYAMLが完全動作すること
apiVersion: haconiwa.dev/v1
kind: Space
metadata:
  name: test-world
spec:
  nations:
  - id: jp
    cities:
    - id: tokyo
      villages:
      - id: test
        companies:
        - name: test-company
          grid: 8x4
          
          basePath: /tmp/test-desks
          organizations:
          - {id: "01", name: "Frontend Dept"}
          - {id: "02", name: "Backend Dept"}
          - {id: "03", name: "Database Dept"}
          - {id: "04", name: "DevOps Dept"}
          buildings:
          - id: hq
            floors:
            - level: 1
              rooms:
              - {id: "room-01", name: "Alpha Room"}
              - {id: "room-02", name: "Beta Room"}

# 実行結果:
# 1. 32個のディレクトリ作成
# 2. tmux session「test-company」で32ペイン
# 3. 各ペインが適切なディレクトリをカレントディレクトリとしている
```

**✅ 最終完了の定義:**
- 主要3テスト維持 + 残りテスト95%以上パス
- `haconiwa apply -f haconiwa-resources.yaml` で完全な32デスク環境構築
- 全CLI機能正常動作

---

> この実装計画は、YAML apply → 32ペイン作成を最優先として、段階的にv1.0完成を目指します。 