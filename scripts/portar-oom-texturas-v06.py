#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Leoitchii v0.6 — port restrito Lichii #880.

Imagens comuns da texture cache que não cabem na VRAM NÃO devem receber
uma falsa imagem Vulkan sparse sem memória (preta/inválida). TryCreateImage
pode retornar vazio e o cache reavaliará quando o coletor liberar espaço.
O fallback sparse permanece permitido para imagens virtuais GIGANTES
ou para chamadores que não podem aceitar um retorno vazio.

Também permite descartar imagens GPU-modified já remapeadas na junção.

Port original: zortos293/Lichii@25a28bb4ecbaf8e6110507b701ce89b35ef4ac32
Não garante resolver todos os objetos pretos — depende de ser esse caminho.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
cpp = root / "src/video_core/vulkan_common/vulkan_memory_allocator.cpp"
header = root / "src/video_core/vulkan_common/vulkan_memory_allocator.h"
texture = root / "src/video_core/texture_cache/texture_cache.h"
data = {p: p.read_text(encoding="utf-8") for p in (cpp, header, texture)}

def exactly(path, old, new, description):
    count = data[path].count(old)
    if count != 1:
        raise SystemExit(
            f"OOM {description}: esperado 1 trecho exato, observado {count}; nada gravado"
        )
    data[path] = data[path].replace(old, new, 1)

exactly(
    cpp,
    "vk::Check(AllocateImage(ci, dedicated, image));",
    "vk::Check(AllocateImage(ci, dedicated, false, image));",
    "CreateImage deve ter fallback",
)
exactly(
    cpp,
    "const VkResult result = AllocateImage(ci, dedicated, image);",
    "const VkResult result = AllocateImage(ci, dedicated, true, image);",
    "TryCreateImage deve poder falhar",
)
exactly(
    cpp,
    '''VkResult MemoryAllocator::AllocateImage(const VkImageCreateInfo &ci, bool dedicated,
                                        vk::Image &image) const {''',
    '''VkResult MemoryAllocator::AllocateImage(const VkImageCreateInfo &ci, bool dedicated,
                                        bool may_fail, vk::Image &image) const {''',
    "assinatura cpp",
)
exactly(
    header,
    "VkResult AllocateImage(const VkImageCreateInfo &ci, bool dedicated, vk::Image &image) const;",
    '''VkResult AllocateImage(const VkImageCreateInfo &ci, bool dedicated,
                               bool may_fail, vk::Image &image) const;''',
    "assinatura header",
)
exactly(
    cpp,
    '''    if (result == VK_ERROR_OUT_OF_DEVICE_MEMORY && ci.imageType != VK_IMAGE_TYPE_1D) {
        if (!huge) {
            pressure_events.fetch_add(1, std::memory_order_relaxed);
        }
''',
    '''    if (result == VK_ERROR_OUT_OF_DEVICE_MEMORY && !huge) {
        pressure_events.fetch_add(1, std::memory_order_relaxed);
    }
    if (result == VK_ERROR_OUT_OF_DEVICE_MEMORY && ci.imageType != VK_IMAGE_TYPE_1D &&
        (huge || !may_fail)) {
''',
    "retorno OOM para imagens menores",
)
exactly(
    texture,
    '''        if (True(overlap.flags & ImageFlagBits::GpuModified)) {
            UNIMPLEMENTED();
        }''',
    '''        // Lichii #880: imagem remapeada não descreve a posição atual do guest.
        if (True(overlap.flags & ImageFlagBits::GpuModified) &&
            False(overlap.flags & ImageFlagBits::Remapped)) {
            UNIMPLEMENTED();
        }''',
    "junção de imagens remapeadas",
)
for path, content in data.items():
    path.write_text(content, encoding="utf-8", newline="\n")
print("VRAM Lichii #880: imagens pequenas sem backing retornam falha em TryCreateImage.")
