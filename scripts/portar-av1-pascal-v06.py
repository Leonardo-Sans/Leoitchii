#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Leoitchii v0.6 — port parcial Lichii #879 + correção #912.

GTX 1050 Ti Pascal: AV1 não é decodificado por hardware. Solicita libdav1d
antes do fallback de decoder do FFmpeg. Verifica capacidade ANTES de criar
contextos CUDA/D3D/Vulkan, evitando inicializações inúteis. Adiciona logs
para distinguir decodificação CPU versus GPU. NÃO limita a contagem de threads
do dav1d: Lichii #912 comprovou mais frames perdidos ao fazer isso.

Compatibilidade: texto exato do Fritchii v4.1. Falhar antes de gravar
qualquer arquivo se um alvo difere.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
ff = root / "src/video_core/host1x/ffmpeg.cpp"
vid = root / "src/video_core/host1x/nx2_video_decoder.cpp"
ff_before = ff.read_text(encoding="utf-8")
vid_before = vid.read_text(encoding="utf-8")

def replace_exact(data, before, after, label):
    n = data.count(before)
    if n != 1:
        raise SystemExit(f"AV1: {label}: esperado 1 trecho, observado {n}. Nenhum arquivo gravado.")
    return data.replace(before, after, 1)

ff_new = ff_before
ff_new = replace_exact(
    ff_new,
    '''#endif
    if (!m_codec) {
        m_codec = avcodec_find_decoder(av_codec);
    }''',
    '''#endif
    if (!m_codec && av_codec == AV_CODEC_ID_AV1) {
        // Lichii #879: preferir dav1d em software quando não há AV1 de hardware.
        m_codec = avcodec_find_decoder_by_name("libdav1d");
    }
    if (!m_codec) {
        m_codec = avcodec_find_decoder(av_codec);
    }''',
    "decodificador AV1",
)
ff_new = replace_exact(
    ff_new,
    '''            LOG_INFO(HW_GPU, "Using {} GPU decoder", av_hwdevice_get_type_name(type));
''',
    "",
    "log de driver prematuro",
)
ff_new = replace_exact(
    ff_new,
    '''        if (!this->InitializeWithType(type)) {
            continue;
        }

        if (decoder.SupportsDecodingOnDevice(&hw_pix_fmt, type)) {
            decoder_context.InitializeHardwareDecoder(*this, hw_pix_fmt);
            return true;
        }''',
    '''        // Lichii #879: não criar dispositivos que o decoder não suporta.
        if (!decoder.SupportsDecodingOnDevice(&hw_pix_fmt, type)) {
            continue;
        }
        if (this->InitializeWithType(type)) {
            LOG_INFO(HW_GPU, "Using {} GPU decoder", av_hwdevice_get_type_name(type));
            decoder_context.InitializeHardwareDecoder(*this, hw_pix_fmt);
            return true;
        }''',
    "hardware-context",
)
vid_new = vid_before
vid_new = replace_exact(vid_new, "#include <array>\n", "#include <array>\n#include <chrono>\n", "include chrono")
vid_new = replace_exact(vid_new, "#include <libswscale/swscale.h>", "#include <libavutil/hwcontext.h>\n#include <libswscale/swscale.h>", "include hwcontext")
vid_new = replace_exact(
    vid_new, "    impl->name = std::string{mime};",
    '''    impl->name = std::string{mime};
    const auto open_start = std::chrono::steady_clock::now();''',
    "timestamp abertura",
)
vid_new = replace_exact(
    vid_new,
    r'''    impl->context.emplace(*impl->decoder);
    if (Settings::values.nvdec_emulation.GetValue() == Settings::NvdecEmulation::Gpu) {
        impl->hardware.emplace();
        impl->hardware->InitializeForDecoder(*impl->context, *impl->decoder);
    }
    impl->open = impl->context->OpenContext(*impl->decoder);
    LOG_INFO(HW_GPU, "nx2 video: decoder for \"{}\" {}", mime, impl->open ? "open" : "failed to open");''',
    r'''    impl->context.emplace(*impl->decoder);
    AVCodecContext* const codec_ctx = impl->context->GetCodecContext();
    const std::string_view decoder_name{impl->decoder->GetCodec()->name};
    const bool prefer_gpu =
        Settings::values.nvdec_emulation.GetValue() == Settings::NvdecEmulation::Gpu;
    if (prefer_gpu) {
        impl->hardware.emplace();
        impl->hardware->InitializeForDecoder(*impl->context, *impl->decoder);
    }
    impl->open = impl->context->OpenContext(*impl->decoder);
    const auto open_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                             std::chrono::steady_clock::now() - open_start)
                             .count();
    if (!impl->open) {
        LOG_ERROR(HW_GPU, "nx2 video: decoder {} failed for \"{}\"", decoder_name, mime);
    } else if (codec_ctx->hw_device_ctx) {
        const auto* hardware =
            reinterpret_cast<const AVHWDeviceContext*>(codec_ctx->hw_device_ctx->data);
        LOG_INFO(HW_GPU, "nx2 video: \"{}\" GPU ({}) with {} opened in {} ms",
                 mime, av_hwdevice_get_type_name(hardware->type), decoder_name, open_ms);
    } else {
        // Lichii #912: o dav1d escolhe sozinho a quantidade de threads.
        LOG_INFO(HW_GPU, "nx2 video: \"{}\" CPU with {} ({} threads), opened in {} ms",
                 mime, decoder_name,
                 codec_ctx->thread_count ? std::to_string(codec_ctx->thread_count) : "default",
                 open_ms);
    }''',
    "log e modo decodificador",
)
if "Dav1dThreads" in vid_new or "context->thread_count = " in vid_new:
    raise SystemExit("AV1: patch introduziria limitação de threads desatualizada")
ff.write_text(ff_new, encoding="utf-8", newline="\n")
vid.write_text(vid_new, encoding="utf-8", newline="\n")
print("AV1 Lichii #879/#912: dav1d preferido, hw init condicionado, decoder logado, threads default.")
