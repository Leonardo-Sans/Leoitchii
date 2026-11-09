#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Leoitchii v0.7: menu Qt, nome do executavel e identidade Windows.
Alvos pinados na base Fritchii v5.5. Falha antes de escrever se divergir.
Executar depois de integrar Fritchii/Lichii/Eglantine e gerar leoitchii.ico.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
asset = Path(__file__).resolve().parents[1] / "assets/v07/leoitchii_lab.h"
icon = root / "dist/leoitchii.ico"
if not asset.is_file() or not icon.is_file() or icon.stat().st_size < 512:
    raise SystemExit("Identidade v0.7: header de laboratorio ou icone ICO ausente")

paths = [
    "src/yuzu/main.cpp",
    "src/yuzu/main_window.cpp",
    "src/yuzu/main.ui",
    "src/yuzu/about_dialog.cpp",
    "src/yuzu/aboutdialog.ui",
    "src/yuzu/yuzu.qrc",
    "src/yuzu/yuzu.rc",
    "src/yuzu/CMakeLists.txt",
    "src/yuzu/fritchii/fritchii_ui.cpp",
]
original = {p: (root / p).read_text(encoding="utf-8") for p in paths}
patched = dict(original)


def once(path, before, after, label):
    n = patched[path].count(before)
    if n != 1:
        raise SystemExit(f"Leoitchii v0.7 {label}: esperado 1 trecho, encontrados {n}; nada gravado")
    patched[path] = patched[path].replace(before, after, 1)


once("src/yuzu/main.cpp",
     '#include <QApplication>\n',
     '#include <QApplication>\n#include "leoitchii_lab.h"\n',
     "include app")
once("src/yuzu/main.cpp",
     '    LoadNx2Switches(argv[0]);\n',
     '    Leoitchii::ApplyAtStartup();\n    LoadNx2Switches(argv[0]);\n',
     "startup")
once("src/yuzu/main_window.cpp",
     '#include "main_window.h"\n',
     '#include "main_window.h"\n#include "leoitchii_lab.h"\n',
     "include menu")
once("src/yuzu/main_window.cpp",
     '    SetUpFritchiiUi();\n',
     '    SetUpFritchiiUi();\n    Leoitchii::InstallMenu(this);\n',
     "instalar menu")
once("src/yuzu/main_window.cpp",
     '''    static const std::string build_id = std::string{Common::g_build_id};
    static const std::string yuzu_title =
        fmt::format("{} | {} | {}", std::string{Common::g_build_name},
                    std::string{Common::g_build_version}, std::string{Common::g_compiler_id});

    const auto override_title =
        fmt::format(fmt::runtime(std::string(Common::g_title_bar_format_idle)), build_id);
    const auto window_title = override_title.empty() ? yuzu_title : override_title;''',
     '''    // Identidade de UI; nao altera a configuracao interna compartilhada da base.
    const std::string window_title{"Leoitchii v0.7 (experimental)"};''',
     "titulo janela")
once("src/yuzu/main.ui",
     '<string>Lichii</string>',
     '<string>Leoitchii v0.7 (experimental)</string>',
     "titulo designer")
once("src/yuzu/main.ui",
     '<string>&amp;About Lichii</string>',
     '<string>&amp;Sobre o Leoitchii</string>',
     "menu sobre")
once("src/yuzu/aboutdialog.ui",
     '<string>About Lichii</string>',
     '<string>Sobre o Leoitchii</string>',
     "titulo sobre")
once("src/yuzu/aboutdialog.ui",
     '&gt;Lichii&lt;',
     '&gt;Leoitchii&lt;',
     "cabecalho sobre")
once("src/yuzu/about_dialog.cpp",
     '''    static const std::string build_id = std::string{Common::g_build_id};
    static const std::string yuzu_build =
        fmt::format("{} | {} | {}", std::string{Common::g_build_name},
                    std::string{Common::g_build_version}, std::string{Common::g_compiler_id});

    const auto override_build =
        fmt::format(fmt::runtime(std::string(Common::g_title_bar_format_idle)), build_id);
    const auto yuzu_build_version = override_build.empty() ? yuzu_build : override_build;''',
     '''    const std::string yuzu_build_version{
        "Leoitchii v0.7 (experimental) | base Fritchii 5.5 + patches Pascal"};''',
     "versao em sobre")
once("src/yuzu/yuzu.qrc",
     '../../dist/fritchii.ico</file>',
     '../../dist/leoitchii.ico</file>',
     "icone recurso Qt")
once("src/yuzu/yuzu.rc",
     '../../dist/fritchii.ico',
     '../../dist/leoitchii.ico',
     "icone executavel")
once("src/yuzu/CMakeLists.txt",
     'set_target_properties(yuzu PROPERTIES OUTPUT_NAME "lichii")',
     'set_target_properties(yuzu PROPERTIES OUTPUT_NAME "Leoitchii")',
     "nome exe")

once("src/yuzu/fritchii/fritchii_ui.cpp",
     'Rename(ui.action_About, tr("&About Fritchii"));',
     'Rename(ui.action_About, tr("&Sobre o Leoitchii"));',
     "menu sobre Fritchii")
once("src/yuzu/about_dialog.cpp",
     'setWindowTitle(tr("About Fritchii"));',
     'setWindowTitle(tr("Sobre o Leoitchii"));',
     "dialogo Fritchii")
once("src/yuzu/about_dialog.cpp",
     'ui->labelYuzu->setText(QStringLiteral("<span style=\'font-size:30px\'>Fritchii</span>"));',
     'ui->labelYuzu->setText(QStringLiteral("<span style=\'font-size:30px\'>Leoitchii</span>"));',
     "cabecalho Fritchii")

version = r"""
// Leoitchii v0.7 - dados exibidos pelo Windows Explorer em Propriedades.
1 VERSIONINFO
FILEVERSION 0,7,0,0
PRODUCTVERSION 0,7,0,0
FILEFLAGSMASK 0x3fL
FILEFLAGS 0x0L
FILEOS 0x40004L
FILETYPE 0x1L
FILESUBTYPE 0x0L
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904b0"
        BEGIN
            VALUE "CompanyName", "Leoitchii Community\0"
            VALUE "FileDescription", "Leoitchii - emulador experimental (GTX 1050 Ti)\0"
            VALUE "FileVersion", "0.7.0.0 experimental\0"
            VALUE "InternalName", "Leoitchii\0"
            VALUE "LegalCopyright", "Derivado de Fritchii, Lichii e Eglantine - licencas de origem\0"
            VALUE "OriginalFilename", "Leoitchii.exe\0"
            VALUE "ProductName", "Leoitchii\0"
            VALUE "ProductVersion", "0.7.0.0\0"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x0409, 1200
    END
END
"""
patched["src/yuzu/yuzu.rc"] += version

# Checagem global antes de qualquer escrita; script nao gera arquivos parciais em falha de alvo.
for p in paths:
    if patched[p] == original[p]:
        raise SystemExit(f"Nenhuma alteracao no alvo esperado: {p}")
for p, contents in patched.items():
    (root / p).write_text(contents, encoding="utf-8", newline="\n")
target = root / "src/yuzu/leoitchii_lab.h"
target.write_bytes(asset.read_bytes())
print("Leoitchii v0.7 sobre Fritchii 5.5: menu Qt, identidade e Leoitchii.exe aplicados.")
print("Nao ha compilacao implicita; codigo deve ser testado no CI e no PC.")
