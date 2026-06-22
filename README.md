# Anuan_rules

OpenClash / Mihomo 自托管规则合集。本仓库从知名规则项目同步文件，客户端只访问
本仓库，不直接依赖多个上游地址。

## 工作方式

```text
知名规则仓库 -> GitHub Actions 定时同步 -> Anuan_rules 的 release 分支
                                                     |
OpenClash 本地配置 <- 本仓库 Raw 地址 <--------------+
```

- `.github/workflows/sync-rules.yml` 每天同步一次，也支持手动运行。
- `scripts/sync_rules.py` 下载、校验并原子替换规则文件。
- `release` 分支的 `rules/manifest.json` 记录上游地址、大小和 SHA-256。
- `config/Anuan.template.yaml` 保存上游映射模板，仅供同步脚本生成配置。
- `release` 分支的 `config/Anuan.yaml` 是生成结果，所有规则地址指向本仓库。
- `release` 每次只有一个新提交并强制替换，避免每日 Geo 数据撑大 Git 历史。

当前镜像 89 个规则及 Geo 数据文件，来源包括：

- [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat)
- [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)
- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
- [666OS/rules](https://github.com/666OS/rules)
- [TG-Twilight/AWAvenue-Ads-Rule](https://github.com/TG-Twilight/AWAvenue-Ads-Rule)
- [DustinWin/ruleset_geodata](https://github.com/DustinWin/ruleset_geodata)

详细映射见 [SOURCES.md](SOURCES.md)。

## 首次部署

1. 在 GitHub 创建仓库并推送本目录，默认分支使用 `main`。
2. 打开仓库 `Settings > Actions > General`。
3. 将 `Workflow permissions` 设置为 `Read and write permissions`。
4. 打开 `Actions > Sync upstream rules`，执行 `Run workflow`。
5. 工作流会创建或更新 `release` 分支，并按真实仓库地址生成配置。

工作流运行后，所有客户端规则地址将采用以下格式：

```text
https://raw.githubusercontent.com/你的用户名/Anuan_rules/release/rules/...
```

## 本地配置

当前仓库只准备公开规则和公开配置模板。等仓库推送完成并提供最终 GitHub 地址后，
再生成仅引用本仓库的本地 YAML，并在本地加入订阅地址、面板密钥等敏感信息。

## 手动同步

```powershell
python scripts\sync_rules.py --repository "你的用户名/Anuan_rules" --branch release
```

## 安全

仓库中的配置只允许使用 `CHANGE_ME` 和订阅占位符。不要提交真实订阅链接、节点、
控制器密钥、监听器密码或其他私有网络信息。
