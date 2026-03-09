from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def savefig_clean(fig: plt.Figure, path: str | Path, *, dpi: int = 600) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def savefig_clean_pair(fig: plt.Figure, path_no_ext: str | Path, *, dpi: int = 600) -> None:
    path_no_ext = Path(path_no_ext)
    path_no_ext.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path_no_ext.with_suffix(".png"), dpi=dpi, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(path_no_ext.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
