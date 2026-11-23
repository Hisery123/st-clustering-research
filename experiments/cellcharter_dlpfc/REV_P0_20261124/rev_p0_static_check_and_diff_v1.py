"""REV_P0 static TeX check + unified diff against V1 (read-only on V1).
Usage: python rev_p0_static_check_and_diff_v1.py <rev_dir> <v1_dir> <out_dir>
"""
import re, sys, os, difflib
REV, V1, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PAIRS = [
 ("cellcharter_study_introduction_module_v1_20261122.tex", "cellcharter_study_introduction_module_rev_p0_20261124.tex"),
 ("chapter_02_background_rewrite_v1_20261122.tex", "chapter_02_background_rev_p0_20261124.tex"),
 ("chapter_03_methods_rewrite_v1_20261122.tex", "chapter_03_methods_rev_p0_20261124.tex"),
 ("chapter_04_results_rewrite_v1_20261122.tex", "chapter_04_results_rev_p0_20261124.tex"),
 ("cellcharter_study_conclusion_module_v1_20261122.tex", "cellcharter_study_conclusion_module_rev_p0_20261124.tex"),
 ("thesis_cellcharter_verified_references_20261122.bib", "thesis_cellcharter_references_rev_p0_20261124.bib"),
 ("cellcharter_study_full_preview_layout_v2_20261123.tex", "cellcharter_study_full_preview_rev_p0_20261124.tex"),
]
def strip_comments(t): return re.sub(r'(?<!\\)%.*', '', t)
texts = {n: open(os.path.join(REV, n), encoding='utf-8').read() for _, n in PAIRS}
appendix = open(os.path.join(V1, "appendix_e4_all12_figures_layout_v2_20261123.tex"), encoding='utf-8').read()
body = {n: strip_comments(t) for n, t in texts.items() if n.endswith('.tex')}
body['appendix_layout_v2(unchanged)'] = strip_comments(appendix)
report = []
ok = True
for n, t in body.items():
    b = t.count('{') - t.count('\\{') - (t.count('}') - t.count('\\}'))
    envs_b = re.findall(r'\\begin\{(\w+\*?)\}', t); envs_e = re.findall(r'\\end\{(\w+\*?)\}', t)
    stack, bad = [], []
    for m in re.finditer(r'\\(begin|end)\{(\w+\*?)\}', t):
        if m.group(1) == 'begin': stack.append(m.group(2))
        elif not stack or stack.pop() != m.group(2): bad.append(m.group(2))
    good = (b == 0 and not bad and not stack)
    ok &= good
    report.append(f"{'PASS' if good else 'FAIL'} {n}: brace_balance={b} begin={len(envs_b)} end={len(envs_e)} mismatched={bad} unclosed={stack}")
alltxt = ''.join(body.values())
labels = set(re.findall(r'\\label\{([^}]+)\}', alltxt))
refs = set(re.findall(r'\\ref\{([^}]+)\}', alltxt))
missing_refs = sorted(refs - labels)
dup = sorted({l for l in re.findall(r'\\label\{([^}]+)\}', alltxt) if re.findall(r'\\label\{([^}]+)\}', alltxt).count(l) > 1})
bib = texts["thesis_cellcharter_references_rev_p0_20261124.bib"]
keys = set(re.findall(r'@\w+\{([^,]+),', bib))
cites = set(k.strip() for c in re.findall(r'\\cite\{([^}]+)\}', alltxt) for k in c.split(','))
missing_cites = sorted(cites - keys); uncited = sorted(keys - cites)
ok &= not missing_refs and not missing_cites and not dup
report.append(f"labels={len(labels)} refs={len(refs)} missing_refs={missing_refs} duplicate_labels={dup}")
report.append(f"bib_keys={len(keys)} cited={len(cites)} missing_cites={missing_cites} uncited_bib_entries={uncited}")
stale = [(n, m.group(0)) for n, t in body.items() if not n.startswith('appendix') for m in re.finditer(r'待插入|尚未验收|尚未上传|逐张上传GitHub并核对之前', t)]
app_fallback = len(re.findall(r'待插入', body['appendix_layout_v2(unchanged)']))
report.append(f"stale_placeholder_strings_in_rev_body={stale}")
report.append(f"appendix_layout_v2_fallback_branches={app_fallback} (unchanged V2 file; only rendered if a figure PDF is missing; V2 39-page PDF rendered all 36 figures; logged as open item)")
ok &= not stale
inputs = re.findall(r'\\input\{([^}]+)\}', body["cellcharter_study_full_preview_rev_p0_20261124.tex"])
report.append(f"preview_inputs={inputs}")
report.append("OVERALL " + ("PASS (static only; NOT compiled)" if ok else "FAIL"))
open(os.path.join(OUT, "REV_P0_STATIC_CHECK_20261124.txt"), 'w', encoding='utf-8').write('\n'.join(report) + '\n')
print('\n'.join(report))
with open(os.path.join(OUT, "REV_P0_DIFF_vs_V1_20261124.diff"), 'w', encoding='utf-8') as f:
    for a, b in PAIRS:
        A = open(os.path.join(V1, a), encoding='utf-8').read().splitlines(keepends=True)
        B = open(os.path.join(REV, b), encoding='utf-8').read().splitlines(keepends=True)
        f.writelines(difflib.unified_diff(A, B, fromfile='a/experiments/cellcharter_dlpfc/' + a, tofile='b/experiments/cellcharter_dlpfc/' + b, n=1))
        sm = difflib.SequenceMatcher(None, A, B)
        print(f"DIFF {a} -> {b}: v1_lines={len(A)} rev_lines={len(B)} changed_blocks={sum(1 for o in sm.get_opcodes() if o[0] != 'equal')}")
