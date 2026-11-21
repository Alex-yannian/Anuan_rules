# Upstream Sources

同步清单由 `scripts/sync_rules.py` 定义，实际文件和校验信息发布在 `release`
分支。`main` 分支不提交生成的规则文件，以避免大文件历史持续膨胀。

| 上游项目 | 本仓库目录 | 内容 | 配置使用 |
| --- | --- | --- | --- |
| MetaCubeX/meta-rules-dat | `rules/metacubex/` | Mihomo MRS、GeoIP、GeoSite、MMDB、ASN | 是，主要来源 |
| 666OS/rules | `rules/666OS/` | AI、媒体、社交、开发、国内外及 IP 细分类 | 是，补充来源 |
| TG-Twilight/AWAvenue-Ads-Rule | `rules/awavenue/` | 广告过滤 | 是 |
| DustinWin/ruleset_geodata | `rules/dustinwin/` | Fake-IP 过滤 | 是 |
| Loyalsoldier/clash-rules | `rules/loyalsoldier/` | 直连、代理、广告、GFW、CN CIDR 等基础合集 | 备用镜像 |
| blackmatrix7/ios_rule_script | `rules/blackmatrix7/` | OpenAI、Claude、Gemini、GitHub、媒体等服务规则 | 备用镜像 |

## 设计原则

1. 客户端只引用本仓库 `rules/` 中的文件。
2. 上游地址只存在于同步脚本和配置生成模板中。
3. 主配置优先使用 Mihomo 原生 `mrs` 文件。
4. Loyalsoldier 与 blackmatrix7 作为备用合集，不重复加载以避免规则膨胀。
5. 任一上游下载失败时，同步任务整体失败，不提交不完整更新。
6. 服务专用规则位于宽泛的 Proxy、China、GEOIP 和 MATCH 规则之前。

## 许可证

本仓库的同步脚本使用仓库许可证。被镜像规则仍受各上游项目自己的许可证约束，
使用和再分发前应查看对应上游仓库。
