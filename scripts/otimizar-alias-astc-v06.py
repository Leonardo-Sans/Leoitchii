#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Port restrito de Lichii #858 (alias tick) e #296 (ASTC).

O shader ASTC de Lichii@d590d51820f9 foi verificado byte-a-byte:
Fritchii v4.1 + diff do commit #296 == shader otimizado.
SHA1 git blob da base é validado antes de sobrescrevê-lo.

Alias fast-path pode ser revertido por LEOITCHII_ALIAS_FAST=0.
Não habilita NoSharpening, não altera frame pacing e não remove fog/vegetação.
"""
from pathlib import Path
import hashlib
import sys

source = Path(sys.argv[1]).resolve()
paths = {
    "base": source / "src/video_core/texture_cache/texture_cache_base.h",
    "header": source / "src/video_core/texture_cache/image_base.h",
    "alias": source / "src/video_core/texture_cache/image_base.cpp",
    "cache": source / "src/video_core/texture_cache/texture_cache.h",
    "shader": source / "src/video_core/host_shaders/astc_decoder.comp",
}
original = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
data = dict(original)

def replace_exact(key, before, after, label):
    count = data[key].count(before)
    if count != 1:
        raise SystemExit(
            f"Alias/ASTC {label}: esperado 1 trecho; encontrado {count}. Nenhum arquivo salvo."
        )
    data[key] = data[key].replace(before, after, 1)

replace_exact(
    "header",
    "    u64 modification_tick = 0;\n    size_t lru_index = SIZE_MAX;",
    """    u64 modification_tick = 0;
    /// Última modificação entre as imagens que compartilham este armazenamento.
    u64 newest_alias_tick = 0;
    size_t lru_index = SIZE_MAX;""",
    "campo newest_alias_tick",
)
replace_exact(
    "alias",
    """    lhs.aliased_images.push_back(std::move(lhs_alias));
    rhs.aliased_images.push_back(std::move(rhs_alias));""",
    """    lhs.aliased_images.push_back(std::move(lhs_alias));
    rhs.aliased_images.push_back(std::move(rhs_alias));
    lhs.newest_alias_tick = (std::max)(lhs.newest_alias_tick, rhs.modification_tick);
    rhs.newest_alias_tick = (std::max)(rhs.newest_alias_tick, lhs.modification_tick);""",
    "atualização quando alias adicionado",
)
replace_exact(
    "cache",
    "namespace VideoCommon {\n",
    """namespace VideoCommon {

// Lichii #858: pode desabilitar só a otimização de aliases em uma execução,
// sem modificar opções persistentes do emulador.
[[nodiscard]] inline bool LeoitchiiAliasFastEnabled() {
    static const bool enabled = [] {
        const char* const value = std::getenv("LEOITCHII_ALIAS_FAST");
        return value == nullptr || value[0] != '0';
    }();
    return enabled;
}
""",
    "flag runtime rollback alias",
)
replace_exact(
    "cache",
    """void TextureCache<P>::MarkModification(ImageBase& image) noexcept {
    image.flags |= ImageFlagBits::GpuModified;
    image.modification_tick = ++modification_tick;
}""",
    """void TextureCache<P>::MarkModification(ImageBase& image) noexcept {
    image.flags |= ImageFlagBits::GpuModified;
    image.modification_tick = ++modification_tick;
    if (LeoitchiiAliasFastEnabled()) {
        for (const AliasedImage& alias : image.aliased_images) {
            slot_images[alias.id].newest_alias_tick = image.modification_tick;
        }
    }
}""",
    "propagação de ticks",
)
replace_exact(
    "cache",
    """void TextureCache<P>::SynchronizeAliases(ImageId image_id) {
    boost::container::small_vector<const AliasedImage*, 8> aliased_images;
    Image& image = slot_images[image_id];
    bool any_rescaled = True(image.flags & ImageFlagBits::Rescaled);""",
    """void TextureCache<P>::SynchronizeAliases(ImageId image_id) {
    boost::container::small_vector<const AliasedImage*, 8> aliased_images;
    Image& image = slot_images[image_id];
    if (LeoitchiiAliasFastEnabled() &&
        image.newest_alias_tick <= image.modification_tick) {
        return;
    }
    bool any_rescaled = True(image.flags & ImageFlagBits::Rescaled);""",
    "skip alias inalterado",
)
replace_exact(
    "cache",
    """    image.modification_tick = most_recent_tick;
    if (any_modified) {""",
    """    image.modification_tick = most_recent_tick;
    if (LeoitchiiAliasFastEnabled()) {
        for (const AliasedImage& alias : image.aliased_images) {
            ImageBase& other = slot_images[alias.id];
            other.newest_alias_tick = (std::max)(other.newest_alias_tick, most_recent_tick);
        }
    }
    if (any_modified) {""",
    "propagação em sincronização",
)
replace_exact(
    "base",
    "    std::vector<u8> astc_scan_buffer;",
    "    Common::ScratchBuffer<u8> astc_scan_buffer;",
    "buffer scratch ASTC",
)
replace_exact(
    "cache",
    """                astc_scan_buffer.resize(scan_bytes);
                gpu_memory->ReadBlockUnsafe(gpu_addr, astc_scan_buffer.data(), scan_bytes);
                new_info.astc_opaque = AstcDataLooksOpaque(astc_scan_buffer);""",
    """                // Lichii #296: varrer memória guest in-place sempre que contígua.
                Tegra::Memory::GpuGuestMemory<u8, Tegra::Memory::GuestMemoryFlags::UnsafeRead>
                    scan_data(*gpu_memory, gpu_addr, scan_bytes, &astc_scan_buffer);
                new_info.astc_opaque =
                    AstcDataLooksOpaque(std::span<const u8>{scan_data.data(), scan_data.size()});""",
    "scan ASTC sem cópia",
)

shader_bytes = original["shader"].encode("utf-8")
base_blob = (
    b"blob " + str(len(shader_bytes)).encode("ascii") + b"\0" + shader_bytes
)
git_hash = hashlib.sha1(base_blob).hexdigest()
expected_hash = "01bec11f17ebdaa659e1f2552146197d2404b6b6"
if git_hash != expected_hash:
    raise SystemExit(
        f"Shader ASTC base inesperada: {git_hash}; esperado {expected_hash}. "
        "Não aplicar shader modificado."
    )
patched_shader = Path(__file__).resolve().parents[1] / "patches/astc_decoder_lichii_296.comp"
if not patched_shader.is_file():
    raise SystemExit(f"Shader ASTC validado ausente: {patched_shader}")
# Windows Git checkout pode converter arquivos de texto para CRLF. O shader
# validado foi publicado com LF; normalizamos ANTES de conferir o hash Git.
optimized_bytes = patched_shader.read_bytes().replace(b"\r\n", b"\n")
patched_blob = (
    b"blob " + str(len(optimized_bytes)).encode("ascii") + b"\0" + optimized_bytes
)
if hashlib.sha1(patched_blob).hexdigest() != "c6d5a96d14b382b7eecb63c546c59ea64675ddb5":
    raise SystemExit("Shader otimizado não corresponde ao commit validado Lichii #296")
data["shader"] = optimized_bytes.decode("utf-8")

# Todos os alvos foram validados sem gravação; só agora escreve os cinco.
for name, target in paths.items():
    target.write_text(data[name], encoding="utf-8", newline="\n")
print("Lichii #858 (alias ticks) e #296 (ASTC scan/shader) aplicados; rollback alias via LEOITCHII_ALIAS_FAST=0.")
