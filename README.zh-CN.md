# Pebrel 主题社区

[English](README.md)

这是 [Pebrel Community](https://github.com/pebrel-community) 的主题目录。
用户可以通过自己的 GitHub Release 分享主题 ZIP，并向这里提交作品登记。
目录展示名称、作者、来源、版本、许可与预览。

**当前阶段：社区初始化，目录为空。** 本仓库不宣称 Pebrel 已实现主题 ZIP
安装、动图或视频背景、GLSL 运行。目录规范与应用运行能力分别推进。

## 如何分享

1. 在自己的 GitHub 仓库说明作品、作者、原作来源和素材许可。
2. 发布一个固定版本的主题 ZIP，记录真实字节数与 SHA-256。
3. 向 `catalog/index.json` 添加一条登记并提交 PR，字段见英文说明。
4. 说明实际测试过的版本和平台，未测试的能力不要写成已兼容。

无需成为组织成员。主题文件、视频和大预览素材放在作者 Release，
社区 Git 仓库维护目录及规范。

## 体积限制

字节限制的唯一来源是 [policy.json](policy.json)：

| 项目 | 上限 |
| --- | --- |
| 单个视频 | 32 MiB |
| 一个主题内全部视频合计 | 32 MiB |
| 主题 ZIP | 48 MiB |
| 解压后全部文件合计 | 64 MiB |

1 MiB = 1,048,576 字节。拆分视频不能增加额度，ZIP 压缩也不能绕过视频
原始文件的大小限制。建议制作短循环的 1080p / 30 FPS 壁纸；
文件体积与播放时的解码、显存预算是不同限制。

## 检查

使用 Python 3.11 及以上，无需第三方包：

```sh
python3 scripts/check_catalog.py
python3 -m unittest discover -s tests
```

目录检查只核对元数据、固定版本链接和声明大小，不下载或解码作品。
应用安装器需要重新验证实际文件；检查通过不代表播放或视觉验收完成。

[共同贡献指南](https://github.com/pebrel-community/.github/blob/main/CONTRIBUTING.md)
适用于署名、许可与社区审阅。目录工具采用 MIT 许可，作品保留各自许可。
