# gene_schematic.py
# Usage:
#   python gene_schematic.py
# Output:
#   gene_schematic.png and gene_schematic.svg

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Domain:
    start: float
    end: float
    label: str
    color: str
    edge_color: str = "black"


@dataclass
class Variant:
    pos: float
    label: str
    color: str = "#444444"
    direction: str = "down"   # "down" (above line, tip pointing down) or "up" (below line, tip pointing up)
    y_offset: float = 0.85    # label offset multiplier to avoid overlap
    sublabel: str = ""        # optional second line (e.g. frequency)


@dataclass
class GeneTrack:
    name: str
    length: float
    name_color: str = "black"
    domains: List[Domain] = field(default_factory=list)
    variants: List[Variant] = field(default_factory=list)
    line_color: str = "black"


def build_figure(
    tracks: List[GeneTrack],
    figsize=(13, 7),
    title: Optional[str] = None,
) -> plt.Figure:
    """Build and return a matplotlib Figure without saving or closing it.

    Parameters
    ----------
    tracks:
        List of GeneTrack objects to draw, one per row.
    figsize:
        Matplotlib figure size as (width, height) in inches.
    title:
        Optional title displayed above the figure.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The open figure object; caller is responsible for saving/closing it.
    """
    max_len = max(t.length for t in tracks)
    n = len(tracks)

    fig, ax = plt.subplots(figsize=figsize)
    y_gap = 2.2
    ys = list(reversed([i * y_gap for i in range(n)]))

    domain_h = 0.36
    tri_h = 0.30
    tri_w_frac = 0.012  # width of triangle relative to longest protein

    for y, track in zip(ys, tracks):
        # Baseline
        ax.plot([0, track.length], [y, y], color=track.line_color, lw=6,
                solid_capstyle="butt", zorder=1)

        # Gene name + length
        ax.text(-max_len * 0.10, y, track.name, color=track.name_color,
                fontsize=20, fontweight="bold", va="center", ha="left")
        ax.text(track.length + max_len * 0.015, y, f"{int(track.length)} aa",
                color="black", fontsize=14, va="center", ha="left")

        # Domains
        for d in track.domains:
            rect = FancyBboxPatch(
                (d.start, y - domain_h / 2), d.end - d.start, domain_h,
                boxstyle="round,pad=0,rounding_size=0.06",
                facecolor=d.color, edgecolor=d.edge_color,
                linewidth=2.0, zorder=3,
            )
            ax.add_patch(rect)
            ax.text((d.start + d.end) / 2, y - 0.52, d.label,
                    fontsize=12, fontweight="semibold", ha="center", va="top")

        # Variants
        tri_w = max_len * tri_w_frac
        for v in track.variants:
            if v.direction == "down":
                # triangle above line, tip pointing down onto line
                tri = Polygon(
                    [[v.pos - tri_w / 2, y + tri_h],
                     [v.pos + tri_w / 2, y + tri_h],
                     [v.pos, y + 0.02]],
                    closed=True, facecolor=v.color, edgecolor=v.color, zorder=4
                )
                label_y = y + tri_h + 0.08 + v.y_offset * 0.3
                va = "bottom"
            else:
                # triangle below line, tip pointing up onto line
                tri = Polygon(
                    [[v.pos - tri_w / 2, y - tri_h],
                     [v.pos + tri_w / 2, y - tri_h],
                     [v.pos, y - 0.02]],
                    closed=True, facecolor=v.color, edgecolor=v.color, zorder=4
                )
                label_y = y - tri_h - 0.08 - v.y_offset * 0.3
                va = "top"

            ax.add_patch(tri)

            # Build combined label: main text + optional sublabel on next line
            display_label = v.label
            if v.sublabel:
                display_label = f"{v.label}\n{v.sublabel}"

            ax.text(v.pos, label_y, display_label, fontsize=12, color=v.color,
                    ha="center", va=va, linespacing=1.4)

    if title:
        ax.set_title(title, fontsize=16, pad=12)

    ax.set_xlim(-max_len * 0.12, max_len * 1.12)
    ax.set_ylim(min(ys) - 1.3, max(ys) + 1.8)
    ax.axis("off")
    plt.tight_layout()

    return fig


def draw_gene_schematic(
    tracks: List[GeneTrack],
    figsize=(13, 7),
    out_png="gene_schematic.png",
    out_svg="gene_schematic.svg",
    title: Optional[str] = None,
) -> plt.Figure:
    """Draw a publication-quality gene schematic and save it to disk.

    Builds the figure via :func:`build_figure`, saves PNG (300 dpi) and SVG,
    then closes the figure.

    Parameters
    ----------
    tracks:
        List of GeneTrack objects to draw, one per row.
    figsize:
        Matplotlib figure size as (width, height) in inches.
    out_png:
        Output filename for the PNG image (300 dpi).
    out_svg:
        Output filename for the SVG image.
    title:
        Optional title displayed above the figure.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object (already closed; access saved files for use).
    """
    fig = build_figure(tracks, figsize=figsize, title=title)
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_svg, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_png}, {out_svg}")
    return fig


if __name__ == "__main__":
    # ===== EDIT THIS BLOCK WITH YOUR OWN GENES =====
    tracks = [
        GeneTrack(
            name="EGL-9",
            length=723,
            name_color="#d7191c",
            domains=[
                Domain(20, 80, "Zinc-finger", "#e78be7"),
                Domain(460, 560, "Fe2OG dioxygenase domain", "#7b1fa2"),
            ],
            variants=[
                Variant(540, "et60 & et61 (R557H)", color="#333333", y_offset=1.00),
                Variant(550, "et62 (R557C)", color="#333333", y_offset=1.45),
            ]
        ),
        GeneTrack(
            name="FAT-2",
            length=376,
            name_color="#1a9641",
            domains=[
                Domain(70, 320, "Fatty acid desaturase domain", "#1f4aff"),
            ],
            variants=[
                Variant(20, "et63\n(V25M)", color="#333333", y_offset=0.75),
                Variant(90, "et64-et66\n(S99L)", color="#333333", y_offset=0.75),
                Variant(101, "wa17\n(S101F)", color="#d62728", y_offset=0.75),
            ]
        ),
        GeneTrack(
            name="FTN-2",
            length=170,
            name_color="#d7191c",
            domains=[
                Domain(5, 165, "Ferritin-like diiron domain", "#ff1f1f"),
            ],
            variants=[
                Variant(89, "et67\n(W89*)", color="#333333", y_offset=0.75),
                Variant(137, "et68\n(Q137*)", color="#333333", y_offset=0.75),
            ]
        ),
        GeneTrack(
            name="HIF-1",
            length=719,
            name_color="#1a9641",
            domains=[
                Domain(8, 50, "bHLH\ndomain", "#64dbe0"),
                Domain(85, 150, "PAS\ndomain", "#4f9e1f"),
                Domain(230, 300, "PAS\ndomain", "#38ff38"),
                Domain(305, 350, "PAC", "#58b9b3"),
            ],
            variants=[
                Variant(365, "P400", color="#d62728", direction="up", y_offset=0.75),
                Variant(500, "P621", color="#d62728", direction="up", y_offset=0.75),
                Variant(390, "et69\n(1241-1G>A\nsplice acceptor variant)",
                        color="#333333", y_offset=1.0),
            ]
        ),
    ]

    draw_gene_schematic(
        tracks,
        figsize=(14, 8),
        out_png="gene_schematic.png",
        out_svg="gene_schematic.svg",
        title="Gene/Protein Schematics with Domains and Allelic Variants"
    )
