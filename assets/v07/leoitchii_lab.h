// SPDX-License-Identifier: GPL-3.0-or-later
// Leoitchii v0.7: lab is independent of emulation saves and Fritchii settings.
#pragma once

#include <array>
#include <QAction>
#include <QMainWindow>
#include <QMenu>
#include <QMenuBar>
#include <QMessageBox>
#include <QSettings>
#include <QStatusBar>
#include <QString>

namespace Leoitchii {

struct LabFlag {
    const char* key;
    const char* environment;
    bool enabled_by_default;
    const char* enabled_value;
    const char* disabled_value;  // nullptr: no environment variable when disabled
    const char* label;
    const char* explanation;
};

// Only switches present in Fritchii v5.5 or in the vetted Leoitchii v0.7 port.
// Never expose old v0.6 env flags that are not implemented in the new code.
inline constexpr std::array<LabFlag, 6> LabFlags{{
    {"precompile", "EDEN_NX2_PRECOMPILE", true, "1", "0",
     "Preparar shaders antes do jogo",
     "Menos stutter quando houver receita de shaders; consome CPU e memoria na preparacao."},
    {"gpu_split", "EDEN_NX2_SPLIT", true, "2", "0",
     "Processamento de GPU dividido (split)",
     "Caminho rapido da GPU; desligue apenas para comparar estabilidade/desempenho."},
    {"fence_batch", "EDEN_NX2_FENCE_BATCH", true, "1", "0",
     "Agrupar sincronizacoes de GPU",
     "Reduz overhead de sincronizacao, desative para investigar travamentos."},
    {"terrain_fix", "EDEN_NX2_RESETFIX", true, "1", "0",
     "Correcao de desenho indireto (Bananza)",
     "Mantem o workaround de terreno do Fritchii; desligar pode piorar a geometria."},
    {"cutscene", "LEOITCHII_VIDEO_VBLANK_FIX", false, "1", "0",
     "Teste de cutscene 60 FPS (Eglantine)",
     "Evita o intervalo forcado durante video recente; apenas se um intervalo foi forcado."},
    {"cache_log", "EDEN_NX2_TC_LOG", false, "1", nullptr,
     "Log detalhado do cache de texturas",
     "Envia dados extras ao log; pode reduzir desempenho e nao corrige a imagem."},
}};

inline QSettings LabSettings() = delete;

inline bool Enabled(const LabFlag& f) {
    QSettings cfg{QSettings::IniFormat, QSettings::UserScope,
                  QStringLiteral("Leoitchii"), QStringLiteral("Laboratorio")};
    return cfg.value(QString::fromLatin1(f.key), f.enabled_by_default).toBool();
}

inline void Save(const LabFlag& f, bool enabled) {
    QSettings cfg{QSettings::IniFormat, QSettings::UserScope,
                  QStringLiteral("Leoitchii"), QStringLiteral("Laboratorio")};
    cfg.setValue(QString::fromLatin1(f.key), enabled);
    cfg.sync();
}

// Environment variables provided by the user take priority. No saves/cache deleted.
inline void ApplyAtStartup() {
    for (const auto& flag : LabFlags) {
        if (qEnvironmentVariableIsSet(flag.environment)) {
            continue;
        }
        const char* value = Enabled(flag) ? flag.enabled_value : flag.disabled_value;
        if (value != nullptr) {
            qputenv(flag.environment, QByteArray(value));
        }
    }
}

inline void InstallMenu(QMainWindow* window) {
    QMenu* menu = window->menuBar()->addMenu(QStringLiteral("Leoitchii"));
    QAction* header = menu->addAction(QString::fromUtf8(
        "Laboratorio experimental - reinicie para aplicar"));
    header->setEnabled(false);
    menu->addSeparator();

    std::array<QAction*, LabFlags.size()> actions{};
    for (size_t i = 0; i < LabFlags.size(); ++i) {
        const auto& flag = LabFlags[i];
        QAction* action = menu->addAction(QString::fromUtf8(flag.label));
        action->setCheckable(true);
        action->setChecked(Enabled(flag));
        action->setToolTip(QString::fromUtf8(flag.explanation));
        actions[i] = action;
        QObject::connect(action, &QAction::toggled, menu, [window, flag](bool enabled) {
            Save(flag, enabled);
            window->statusBar()->showMessage(
                QString::fromUtf8("Leoitchii: ajuste salvo; reinicie o emulador."), 9000);
        });
    }

    menu->addSeparator();
    menu->addAction(QString::fromUtf8("Restaurar padrao experimental"),
                    [window, actions] {
        for (size_t i = 0; i < LabFlags.size(); ++i) {
            actions[i]->setChecked(LabFlags[i].enabled_by_default);
            Save(LabFlags[i], LabFlags[i].enabled_by_default);
        }
        QMessageBox::information(window, QStringLiteral("Leoitchii"),
                                 QString::fromUtf8("Padrao restaurado. Reinicie para aplicar."));
    });
    menu->addAction(QString::fromUtf8("Sobre o Laboratorio"), [window] {
        QMessageBox::information(
            window, QStringLiteral("Leoitchii v0.7 - Laboratorio"),
            QString::fromUtf8(
                "Base Fritchii v5.5; menus de teste reversiveis. "
                "Opcoes sao aplicadas no proximo inicio. O fallback Mesh para "
                "GTX 1050 Ti e a politica de memoria da base nao sao desativados por este menu. "
                "Nao limpa caches, jogos, firmware, chaves ou saves. "
                "Versao experimental: estabilidade e audio nao validados no hardware."));
    });
}
} // namespace Leoitchii
