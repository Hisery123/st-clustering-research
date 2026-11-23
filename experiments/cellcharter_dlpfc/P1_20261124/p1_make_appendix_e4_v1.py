"""Create appendix_e4_all12_figures_p1_20261124.tex from the unchanged layout-V2 appendix.
Only (a) the header comment/section title/intro paragraph and (b) the 36 missing-figure fallback
lines are changed. Every \\includegraphics path, caption and label is copied byte-for-byte; the
script asserts this. Usage: python p1_make_appendix_e4_v1.py <v2_appendix.tex> <out.tex>
"""
import re, sys
src = open(sys.argv[1], encoding='utf-8').read()
lines = src.split('\n')
assert lines[5].startswith(r'\section{E4全12切片原始图件}'), lines[5]
header = [
 "% P1 (2026-11-24): derived from appendix_e4_all12_figures_layout_v2_20261123.tex (unchanged).",
 "% Changed: header, section title, intro paragraph, and missing-figure fallback text only.",
 "% All \\includegraphics paths, captions and labels are byte-identical to layout V2.",
 r"\section{全部12张DLPFC切片的空间分布图件}",
 lines[6],  # \label{sec:cc-e4-appendix-v1}
 "本附录列出全部12张DLPFC切片的空间聚类图、标记基因表达图与参考层--聚类交叉计数图，作为第\\ref{subsec:cc-res-maps-p1}节的完整补充。所有图件均使用随机种子22911、参考类别数条件下A、B两种15维组合的原始预测；聚类编号未依据参考标签重排。12张切片来自3名供体，不构成12个独立的生物学重复。图件由原始计数与预测直接绘制，未作任何重绘或生成式处理。",
]
body = lines[8:]
out = '\n'.join(header + body)
pat = re.compile(r'\\emph\{\[待插入原始E4图件：[^\]]*\]\}')
out, n = pat.subn(r'\\emph{[编译提示：未找到该图件的PDF，请检查相对路径。]}', out)
assert n == 36, n
for key in [r'\\includegraphics\[[^\]]*\]\{[^}]+\}', r'\\captionof\{figure\}\{.*?\}\n', r'\\label\{[^}]+\}', r'\\subsection\{[^}]+\}']:
    a = re.findall(key, '\n'.join(lines[8:])); b = re.findall(key, '\n'.join(body))
    assert a == b and a, key
open(sys.argv[2], 'w', encoding='utf-8').write(out)
print("APPENDIX_P1_OK fallbacks_replaced=", n, "figures=", len(re.findall(r'\\includegraphics', out)))
