"""P1 static TeX check (+ style scan) and unified diff against REV_P0 counterparts.
Usage: python p1_static_check_and_diff_v1.py <cellcharter_dlpfc dir> <out_dir>
"""
import re, sys, os, difflib
D, OUT = sys.argv[1], sys.argv[2]
FILES = ["cellcharter_study_full_preview_p1_20261124.tex", "cellcharter_study_abstract_p1_20261124.tex",
         "cellcharter_study_introduction_p1_20261124.tex", "chapter_02_background_p1_20261124.tex",
         "chapter_03_methods_p1_20261124.tex", "chapter_04_results_discussion_p1_20261124.tex",
         "cellcharter_study_conclusion_p1_20261124.tex", "appendix_e4_all12_figures_p1_20261124.tex",
         "appendix_cellcharter_records_p1_20261124.tex"]
BODY = FILES[1:7]  # main text (abstract..conclusion) for style scan
PAIRS = [("cellcharter_study_introduction_module_rev_p0_20261124.tex", "cellcharter_study_introduction_p1_20261124.tex"),
         ("chapter_02_background_rev_p0_20261124.tex", "chapter_02_background_p1_20261124.tex"),
         ("chapter_03_methods_rev_p0_20261124.tex", "chapter_03_methods_p1_20261124.tex"),
         ("chapter_04_results_rev_p0_20261124.tex", "chapter_04_results_discussion_p1_20261124.tex"),
         ("cellcharter_study_conclusion_module_rev_p0_20261124.tex", "cellcharter_study_conclusion_p1_20261124.tex"),
         ("thesis_cellcharter_references_rev_p0_20261124.bib", "thesis_cellcharter_references_p1_20261124.bib"),
         ("cellcharter_study_full_preview_rev_p0_20261124.tex", "cellcharter_study_full_preview_p1_20261124.tex")]
strip = lambda t: re.sub(r'(?<!\\)%.*', '', t)
raw = {f: open(os.path.join(D, f), encoding='utf-8').read() for f in FILES}
txt = {f: strip(t) for f, t in raw.items()}
rep, ok = [], True
for f, t in txt.items():
    b = (t.count('{') - t.count('\\{')) - (t.count('}') - t.count('\\}'))
    st, bad = [], []
    for m in re.finditer(r'\\(begin|end)\{(\w+\*?)\}', t):
        if m.group(1) == 'begin': st.append(m.group(2))
        elif not st or st.pop() != m.group(2): bad.append(m.group(2))
    # bare underscore outside math/texttt/paths: rough heuristic on \emph and caption text
    bare_us = [m.group(0)[:60] for m in re.finditer(r'\\emph\{[^}]*[^\\]_[^}]*\}', t)]
    good = b == 0 and not bad and not st and not bare_us
    ok &= good
    rep.append(f"{'PASS' if good else 'FAIL'} {f}: braces={b} mismatched={bad} unclosed={st} bare_underscore_in_emph={bare_us}")
allt = ''.join(txt.values())
labs = re.findall(r'\\label\{([^}]+)\}', allt)
refs = set(re.findall(r'\\(?:eq)?ref\{([^}]+)\}', allt))
miss = sorted(refs - set(labs)); dup = sorted({l for l in labs if labs.count(l) > 1})
bib = open(os.path.join(D, "thesis_cellcharter_references_p1_20261124.bib"), encoding='utf-8').read()
keys = set(re.findall(r'@\w+\{([^,]+),', bib))
cites = {k.strip() for c in re.findall(r'\\cite\{([^}]+)\}', allt) for k in c.split(',')}
ok &= not miss and not dup and not (cites - keys)
rep.append(f"labels={len(labs)} refs={len(refs)} missing_refs={miss} duplicate_labels={dup}")
rep.append(f"bib_keys={len(keys)} cited={len(cites)} missing_cites={sorted(cites-keys)} uncited={sorted(keys-cites)}")
codes = [(f, m.group(0)) for f in BODY for m in re.finditer(r'(?<![A-Za-z0-9_])E[1-5][a-d]?(?:/E[1-5])?(?![A-Za-z0-9_])', txt[f])]
proc = [(f, m.group(0)) for f in BODY for m in re.finditer(r'GitHub|SHA|Windows|Codex|上传|审计|冻结缓存|commit', txt[f])]
stale = [(f, m.group(0)) for f in FILES for m in re.finditer(r'待插入|尚未验收|尚未上传', txt[f])]
ok &= not codes and not stale
rep.append(f"experiment_codes_in_main_text={codes}")
rep.append(f"process_words_in_main_text={proc}  (informational; allowed only where needed for method disclosure)")
rep.append(f"stale_placeholders={stale}")
inputs = re.findall(r'\\input\{([^}]+)\}', txt[FILES[0]])
n_axis = len(re.findall(r'\\begin\{axis\}', allt))
missing_inputs = [i for i in inputs if not os.path.exists(os.path.join(D, i + '.tex'))]
ok &= not missing_inputs
rep.append("preview_inputs=" + str(inputs) + " missing=" + str(missing_inputs))
rep.append("pgfplots_figures=" + str(n_axis))
rep.append("OVERALL " + ("PASS (static only; NOT compiled)" if ok else "FAIL"))
open(os.path.join(OUT, "P1_STATIC_CHECK_20261124.txt"), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
print('\n'.join(rep))
with open(os.path.join(OUT, "P1_DIFF_vs_REV_P0_20261124.diff"), 'w', encoding='utf-8') as fo:
    for a, b in PAIRS:
        A = open(os.path.join(D, a), encoding='utf-8').read().splitlines(keepends=True)
        B = open(os.path.join(D, b), encoding='utf-8').read().splitlines(keepends=True)
        fo.writelines(difflib.unified_diff(A, B, fromfile='a/' + a, tofile='b/' + b, n=0))
        r = difflib.SequenceMatcher(None, ''.join(A), ''.join(B)).quick_ratio()
        print(f"DIFF {a} -> {b}: rev_p0_lines={len(A)} p1_lines={len(B)} char_similarity_upper_bound={r:.2f}")
