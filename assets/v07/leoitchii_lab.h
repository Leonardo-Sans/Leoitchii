// SPDX-License-Identifier: GPL-3.0-or-later
// Leoitchii: controle de experimentos, sem alterar saves ou configuracoes do Fritchii.
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
    const char* label;
    const char* explanation;
};

// Nao incluir flags sem rollback implementado no codigo compilado.
// Todas estas flags ja existem nos ports v0.2-v0.6 integrados pelo Leoitchii.
inline constexpr std::array<LabFlag, 5> LabFlags{{
    {"aliases", "LEOITCHII_ALIAS_FAST", true,
     "Sincronizacao rapida de aliases (texturas)",
     "Se objetos pretos, corrupcao grafica ou crashes aparecerem, desative para comparar."},
    {"ir_memory", "LEOITCHII_IR_EARLY_FREE", true,
     "Liberacao antecipada de memoria dos shaders",
     "Pode reduzir o pico de RAM; desative para investigar crashes na compilacao."},
    {"mesh_preload", "LEOITCHII_MESH_DISK_CACHE", true,
     "Preload do cache Mesh (GTX Pascal)",
     "Desativa somente o preload, nunca o fallback de Mesh Shaders por compute."},
    {"video_pace", "EDEN_NX2_VDEC_PACE", true,
     "Sincronismo de videos Eglantine",
     "Experimento para investigar musica da abertura e reproducao da cutscene."},
    {"texture_log", "EDEN_NX2_TC_LOG", false,
     "Registrar diagnostico do cache de texturas",
     "Aumenta mensagens de log; nao altera a renderizacao."},
}};

// Configuracao separada: nao muda qt-config.ini, firmware, chaves ou saves.

inline bool Enabled(const LabFlag& flag) {
    QSettings settings{QSettings::IniFormat, QSettings::UserScope,
                       QStringLiteral("Leoitchii"), QStringLiteral("Laboratorio")};
    return settings.value(QString::fromLatin1(flag.key), flag.enabled_by_default).toBool();
}

inline void Save(const LabFlag& flag, bool enabled) {
    QSettings settings{QSettings::IniFormat, QSettings::UserScope,
                       QStringLiteral("Leoitchii"), QStringLiteral("Laboratorio")};
    settings.setValue(QString::fromLatin1(flag.key), enabled);
    settings.sync();
}

// Chamado antes de LoadNx2Switches e antes de construir a interface.
// Argumentos dos antigos CMDs ganham prioridade: nao sobrescrever variaveis do usuario.
inline void ApplyAtStartup() {
    for (const auto& flag : LabFlags) {
        if (!qEnvironmentVariableIsSet(flag.environment)) {
            qputenv(flag.environment, Enabled(flag) ? "1" : "0");
        }
    }
}

inline void InstallMenu(QMainWindow* window) {
    QMenu* menu = window->menuBar()->addMenu(QStringLiteral("Leoitchii"));
    QAction* info = menu->addAction(QString::fromUtf8(
        "Laboratorio de testes - ajustes salvos, exigem reinicio"));
    info->setEnabled(false);
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
                QString::fromUtf8("Leoitchii: ajuste salvo. Reinicie o emulador para aplicar."),
                10000);
        });
    }

    menu->addSeparator();
    menu->addAction(QString::fromUtf8("Restaurar configuracao experimental padrao"),
                    [window, actions] {
        for (size_t i = 0; i < LabFlags.size(); ++i) {
            actions[i]->setChecked(LabFlags[i].enabled_by_default);
            Save(LabFlags[i], LabFlags[i].enabled_by_default);
        }
        QMessageBox::information(window, QStringLiteral("Leoitchii"),
                                 QString::fromUtf8(
                                     "Ajustes restaurados. Feche e abra o emulador para aplicar."));
    });
    menu->addAction(QString::fromUtf8("Sobre o laboratorio"), [window] {
        QMessageBox::information(
            window, QStringLiteral("Leoitchii v0.7 experimental"),
            QString::fromUtf8(
                "Os controles sao globais e reversiveis. Uma opcao desmarcada "
                "desativa somente a otimizacao indicada na proxima inicializacao. "
                "A emulacao Mesh por compute para GTX Pascal continua preservada. "
                "O menu nao desfaz nem limpa cache, saves, firmware ou chaves. "
                "Variaveis de ambiente definidas externamente tem prioridade. "
                "A versao ainda nao foi validada em hardware real."));
    });
}

} // namespace Leoitchii
