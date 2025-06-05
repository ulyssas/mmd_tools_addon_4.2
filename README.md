# MMD Tools
MMD Tools is a Blender add-on for importing MMD (MikuMikuDance) model data (.pmd, .pmx), motion data (.vmd), and pose data (.vpd).
Exporting model data (.pmx), motion data (.vmd), and pose data (.vpd) are supported as well.

MMD ToolsはMMD(MikuMikuDance)のモデルデータ(.pmd, .pmx)、モーションデータ(.vmd)、ポーズデータ(.vpd)を
インポートするためのBlenderアドオンです。
モデルデータ(.pmx)、モーションデータ(.vmd)、ポーズデータ(.vpd)のエクスポートにも対応しています。

## Version Compatibility
| Blender Version | MMD Tools Version | Branch      |
|-----------------|-------------------|-------------|
| Blender 4.2 LTS | MMD Tools v4.x    | [main](https://github.com/MMD-Blender/blender_mmd_tools) |
| Blender 3.6 LTS | MMD Tools v2.x    | [blender-v3](https://github.com/MMD-Blender/blender_mmd_tools/tree/blender-v3) |

Use the MMD Tools version that matches your Blender LTS version.

## Installation & Usage
- Check the [MMD Tools Wiki](https://mmd-blender.fandom.com/wiki/MMD_Tools) for details.
- 詳細は [MMD ToolsのWiki (日本語)](https://mmd-blender.fandom.com/ja/wiki/MMD_Tools) を確認してください。

## Project Scope
The following features are intentionally excluded from MMD Tools:

- **PMX Editor replacement**: MMD Tools is not designed to replace PMX Editor functionality due to limited resources and to avoid reinventing the wheel
- **Blender Link features compatibility**: Link features have known issues that need to be resolved by Blender developers, so we do not guarantee compatibility
- **Rigify compatibility**: Complex compatibility issues and frequent Rigify updates make it difficult to maintain, so we do not support Rigify at this time
- **Material Library system**: Implementing a full-featured material library would be equivalent to building a separate add-on, which is outside the scope of this project. Instead, users can define their own custom default materials by editing the startup file. For example, the `MMDShaderDev` Node Group can be customized and saved in the Blender startup file (`File > Defaults > Save Startup File`), allowing it to be automatically applied to new MMD models without modifying the add-on itself.

## Contributing
MMD Tools needs contributions such as:

- Document writing / translation
- Video creation / translation
- Bug reports
- Feature requests
- Pull requests

If you are interested in supporting this project, please reach out via the following channels:
- [MMD Tools Issues](https://github.com/MMD-Blender/blender_mmd_tools/issues)
- [MMD & Blender Discord Server](https://discord.gg/zRgUkuaPWw)

For developers looking to contribute code or translations, please check the [Developer Guide](DEVELOPER_GUIDE.md) for project guidelines and detailed workflows.

## License
Distributed under the [GPLv3](LICENSE).
