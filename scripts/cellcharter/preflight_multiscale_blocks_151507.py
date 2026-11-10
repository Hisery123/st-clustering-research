"""Read-only preflight: inspect feature scale of five CellCharter blocks.

No clustering, no training, no reference labels, no files written.
Uses the frozen seed22911 L4 aggregated array (4226 spots x 25 dims).
This post-hoc diagnostic is NOT an experimentally validated innovation.
"""
import hashlib
from pathlib import Path
import numpy as np

SOURCE = Path(r"D:\paper\CellCharter_reproduction\results\cellcharter_v032_151507_seed22911_oracleK7\cellcharter_aggregated.npy")

def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Existing aggregation file not found: {SOURCE}")
    x = np.load(SOURCE, allow_pickle=False, mmap_mode="r")
    if x.shape != (4226, 25) or not np.issubdtype(x.dtype, np.number):
        raise ValueError(f"Unexpected shape/type: {x.shape}, {x.dtype}")
    if not np.isfinite(x).all():
        raise ValueError("Non-finite feature values")
    sha = hashlib.sha256()
    with SOURCE.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(part)
    print("INPUT_FILE_SHA256", sha.hexdigest(), flush=True)
    print("INPUT_SHAPE", x.shape, "DTYPE", x.dtype, flush=True)
    print("BLOCK  MEAN_ABS  RMS  AVG_COLUMN_STD  MAX_COLUMN_STD  AVG_ABS_CORR_TO_SELF", flush=True)
    base = np.asarray(x[:, :5], dtype=np.float64)
    for block in range(5):
        z = np.asarray(x[:, block*5:(block+1)*5], dtype=np.float64)
        mu = float(np.mean(np.abs(z)))
        rms = float(np.sqrt(np.mean(z*z)))
        stds = np.std(z, axis=0)
        corrs = []
        for column in range(5):
            a, b = base[:, column], z[:, column]
            if np.std(a) > 0 and np.std(b) > 0:
                corrs.append(abs(float(np.corrcoef(a, b)[0, 1])))
        corr = float(np.mean(corrs)) if corrs else float("nan")
        print(f"L{block} {mu:.8f} {rms:.8f} {np.mean(stds):.8f} {np.max(stds):.8f} {corr:.8f}", flush=True)
    print("MULTISCALE_BLOCK_PREFLIGHT_COMPLETE; NO_LABELS; NO_GMM; NO_FILES_WRITTEN", flush=True)

if __name__ == "__main__":
    main()
