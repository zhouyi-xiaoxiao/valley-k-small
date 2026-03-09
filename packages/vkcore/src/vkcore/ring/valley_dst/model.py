from __future__ import annotations

from typing import List

import numpy as np

from vkcore.ring import valley_study as vs

from .common import wrap_paper


def ring_neighbors_paper(src_paper: int, n: int, k_total: int) -> List[int]:
    k = k_total // 2
    out: List[int] = []
    for r in range(1, k + 1):
        out.append(wrap_paper(src_paper + r, n))
        out.append(wrap_paper(src_paper - r, n))
    return out


def build_graph_directed_shortcut(
    *,
    n: int,
    k_total: int,
    n0_paper: int,
    target_paper: int,
    sc_src_paper: int,
    sc_dst_paper: int,
) -> vs.GraphData:
    if k_total % 2 != 0:
        raise ValueError("Model assumes K = 2k is even.")
    if sc_src_paper == sc_dst_paper:
        raise ValueError("Shortcut endpoints must be distinct.")
    if sc_dst_paper in set(ring_neighbors_paper(sc_src_paper, n, k_total)):
        raise ValueError(
            f"Invalid shortcut: dst={sc_dst_paper} is already a ring neighbour of src={sc_src_paper} for K={k_total}."
        )

    n0 = wrap_paper(n0_paper, n) - 1
    target = wrap_paper(target_paper, n) - 1
    sc_src = wrap_paper(sc_src_paper, n) - 1
    sc_dst = wrap_paper(sc_dst_paper, n) - 1

    k = k_total // 2
    neigh: List[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        for r in range(1, k + 1):
            neigh[i].add((i + r) % n)
            neigh[i].add((i - r) % n)
    neigh[sc_src].add(sc_dst)

    deg = np.array([len(neigh[i]) for i in range(n)], dtype=np.int16)
    deg_max = int(deg.max())
    neigh_pad = -np.ones((n, deg_max), dtype=np.int16)
    for i in range(n):
        arr = np.fromiter(neigh[i], dtype=np.int16)
        neigh_pad[i, : arr.size] = arr

    src_list: List[int] = []
    dst_list: List[int] = []
    w_list: List[float] = []
    for i in range(n):
        p = 1.0 / float(deg[i])
        for j in neigh[i]:
            src_list.append(i)
            dst_list.append(j)
            w_list.append(p)

    return vs.GraphData(
        N=n,
        K=k_total,
        n0=n0,
        target=target,
        sc_u=sc_dst,
        sc_v=sc_src,
        neigh_pad=neigh_pad,
        deg=deg,
        src=np.asarray(src_list, dtype=np.int32),
        dst=np.asarray(dst_list, dtype=np.int32),
        w=np.asarray(w_list, dtype=np.float64),
    )
