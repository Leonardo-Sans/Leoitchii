#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Port estrito e reversivel da parte de vblank do teste Eglantine f7a902.
A v0.6 perdeu musica com o pacing de descarte de quadros: NAO importar esse trecho.
Atua apenas com LEOITCHII_VIDEO_VBLANK_FIX=1: intervalo externo e modo OoT 30 FPS.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
file = root / "src/core/hle/service/nx2_gsv.h"
original = file.read_text(encoding="utf-8")
data = original


def one(before, after, label):
    global data
    n = data.count(before)
    if n != 1:
        raise SystemExit(f"Eglantine video {label}: esperado 1 trecho, achados {n}; nao gravado")
    data = data.replace(before, after, 1)


one("namespace Service {\n", """namespace Service {

// A/B opt-in: Eglantine f7a902, 60-fps cutscenes should not inherit
// a forced two-vblank presentation interval. No frame drop code imported.
inline std::atomic<s64> g_leoitchii_video_last_frame_ns{0};

inline bool LeoitchiiVideoVblankFix() {
    static const bool enabled = [] {
        const char* const value = std::getenv("LEOITCHII_VIDEO_VBLANK_FIX");
        return value != nullptr && value[0] == '1';
    }();
    return enabled;
}
""", "flag")

one("""        if (forced_interval != 0) {
            swap_interval = forced_interval;
        }""", """        const s64 video_ns = g_leoitchii_video_last_frame_ns.load(std::memory_order_relaxed);
        const s64 now_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
                               std::chrono::steady_clock::now().time_since_epoch())
                               .count();
        const bool recent_video = LeoitchiiVideoVblankFix() && video_ns > 0 &&
                                  now_ns >= video_ns && now_ns - video_ns < 500'000'000;
        if (forced_interval != 0 && !recent_video) {
            swap_interval = forced_interval;
        }""", "vblank")

# The Fritchii 5.5 OoT 30 FPS limiter is applied after forced_interval.
# In the original Leoitchii port the recent-video flag did not bypass it, so
# the experimental setting was ineffective for OoT's own 30-FPS mode.
# Keep gameplay in 30-FPS mode and present the decoded 60-FPS opening at
# one vblank only while video decoding remains active (500ms expiry).
# OFF remains byte-for-byte equivalent to Fritchii's default timing.
one("""        if (process != nullptr && process->GetProgramId() == OcarinaOfTimeId &&
            Settings::values.oot_30fps.GetValue()) {
            swap_interval = (std::max)(swap_interval, 2U);
        }""", """        if (process != nullptr && process->GetProgramId() == OcarinaOfTimeId &&
            Settings::values.oot_30fps.GetValue() && !recent_video) {
            swap_interval = (std::max)(swap_interval, 2U);
        }
        // A/B only: when OoT is playing a recently decoded movie, display
        // each frame at one vblank; automatically revert to 30 FPS afterward.
        // This is presentation pacing, not a change to game simulation speed.
        if (recent_video && process != nullptr &&
            process->GetProgramId() == OcarinaOfTimeId) {
            swap_interval = 1;
        }""", "Ocarina 30-FPS override during video")

one("""            if (input.end) {
                decoder->Drain(pictures);
            }
            lk.lock();""", """            if (input.end) {
                decoder->Drain(pictures);
            }
            if (!pictures.empty()) {
                g_leoitchii_video_last_frame_ns.store(
                    std::chrono::duration_cast<std::chrono::nanoseconds>(
                        std::chrono::steady_clock::now().time_since_epoch()).count(),
                    std::memory_order_relaxed);
            }
            lk.lock();""", "decoded video activity")

if data == original:
    raise SystemExit("Nenhuma alteracao de video aplicada")
file.write_text(data, encoding="utf-8", newline="\n")
print("A/B video OoT 30->60 FPS during decoded cutscene installed (opt-in); no frame drop pacing.")
