# app.py – Interactive gene-schematic editor (Streamlit)
# Usage:
#   streamlit run app.py

import io
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import streamlit as st

from gene_schematic import Domain, GeneTrack, Variant, build_figure

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gene Schematic Editor",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 Gene Schematic Editor")
st.markdown(
    "Build a publication-quality gene/protein schematic interactively. "
    "Add tracks, domains and allelic variants, then download the figure."
)

# ── session-state defaults ──────────────────────────────────────────────────────
DEFAULT_TRACKS = [
    {
        "name": "EGL-9",
        "length": 723,
        "name_color": "#d7191c",
        "line_color": "#000000",
        "domains": [
            {"start": 20, "end": 80, "label": "Zinc-finger", "color": "#e78be7"},
            {"start": 460, "end": 560, "label": "Fe2OG dioxygenase domain", "color": "#7b1fa2"},
        ],
        "variants": [
            {"pos": 540, "label": "et60 & et61 (R557H)", "color": "#333333",
             "direction": "down", "y_offset": 1.00},
            {"pos": 550, "label": "et62 (R557C)", "color": "#333333",
             "direction": "down", "y_offset": 1.45},
        ],
    },
    {
        "name": "FAT-2",
        "length": 376,
        "name_color": "#1a9641",
        "line_color": "#000000",
        "domains": [
            {"start": 70, "end": 320, "label": "Fatty acid desaturase domain", "color": "#1f4aff"},
        ],
        "variants": [
            {"pos": 20,  "label": "et63\n(V25M)",    "color": "#333333",
             "direction": "down", "y_offset": 0.75},
            {"pos": 90,  "label": "et64-et66\n(S99L)", "color": "#333333",
             "direction": "down", "y_offset": 0.75},
            {"pos": 101, "label": "wa17\n(S101F)",   "color": "#d62728",
             "direction": "down", "y_offset": 0.75},
        ],
    },
    {
        "name": "FTN-2",
        "length": 170,
        "name_color": "#d7191c",
        "line_color": "#000000",
        "domains": [
            {"start": 5, "end": 165, "label": "Ferritin-like diiron domain", "color": "#ff1f1f"},
        ],
        "variants": [
            {"pos": 89,  "label": "et67\n(W89*)",  "color": "#333333",
             "direction": "down", "y_offset": 0.75},
            {"pos": 137, "label": "et68\n(Q137*)", "color": "#333333",
             "direction": "down", "y_offset": 0.75},
        ],
    },
    {
        "name": "HIF-1",
        "length": 719,
        "name_color": "#1a9641",
        "line_color": "#000000",
        "domains": [
            {"start": 8,   "end": 50,  "label": "bHLH\ndomain", "color": "#64dbe0"},
            {"start": 85,  "end": 150, "label": "PAS\ndomain",  "color": "#4f9e1f"},
            {"start": 230, "end": 300, "label": "PAS\ndomain",  "color": "#38ff38"},
            {"start": 305, "end": 350, "label": "PAC",          "color": "#58b9b3"},
        ],
        "variants": [
            {"pos": 365, "label": "P400", "color": "#d62728",
             "direction": "up", "y_offset": 0.75},
            {"pos": 500, "label": "P621", "color": "#d62728",
             "direction": "up", "y_offset": 0.75},
            {"pos": 390, "label": "et69\n(1241-1G>A\nsplice acceptor variant)",
             "color": "#333333", "direction": "down", "y_offset": 1.0},
        ],
    },
]

if "tracks" not in st.session_state:
    st.session_state["tracks"] = json.loads(json.dumps(DEFAULT_TRACKS))


# ── helper: colour picker that also accepts free-text hex ──────────────────────
def color_input(label: str, value: str, key: str) -> str:
    """Return a hex colour chosen via st.color_picker."""
    try:
        chosen = st.color_picker(label, value=value, key=key)
    except Exception:
        chosen = value
    return chosen


# ── sidebar: figure-level settings ─────────────────────────────────────────────
with st.sidebar:
    st.header("Figure settings")
    fig_title = st.text_input("Title", value="Gene/Protein Schematics with Domains and Allelic Variants")
    fig_w = st.slider("Figure width (in)", 8, 24, 14)
    fig_h = st.slider("Figure height (in)", 4, 16, 8)

    st.divider()
    st.header("Tracks")
    if st.button("➕ Add track"):
        st.session_state["tracks"].append(
            {
                "name": "New Gene",
                "length": 500,
                "name_color": "#000000",
                "line_color": "#000000",
                "domains": [],
                "variants": [],
            }
        )
        st.rerun()

    if st.button("🔄 Reset to example"):
        st.session_state["tracks"] = json.loads(json.dumps(DEFAULT_TRACKS))
        st.rerun()


# ── per-track editors ──────────────────────────────────────────────────────────
tracks_data = st.session_state["tracks"]
to_delete_track: list[int] = []

for ti, track in enumerate(tracks_data):
    with st.expander(f"**Track {ti + 1}: {track['name']}**", expanded=(ti == 0)):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        track["name"] = col1.text_input("Gene name", value=track["name"], key=f"t{ti}_name")
        track["length"] = col2.number_input(
            "Length (aa)", min_value=1, max_value=100_000,
            value=int(track["length"]), key=f"t{ti}_len"
        )
        track["name_color"] = color_input("Name colour", track["name_color"], key=f"t{ti}_nc")
        track["line_color"] = color_input("Line colour", track["line_color"], key=f"t{ti}_lc")

        # ── Domains ────────────────────────────────────────────────────────────
        st.markdown("**Domains**")
        to_delete_domain: list[int] = []
        for di, dom in enumerate(track["domains"]):
            dc1, dc2, dc3, dc4, dc5 = st.columns([2, 2, 4, 2, 1])
            dom["start"] = dc1.number_input(
                "Start", min_value=0, max_value=int(track["length"]),
                value=int(dom["start"]), key=f"t{ti}_d{di}_start"
            )
            dom["end"] = dc2.number_input(
                "End", min_value=0, max_value=int(track["length"]),
                value=int(dom["end"]), key=f"t{ti}_d{di}_end"
            )
            dom["label"] = dc3.text_input("Label", value=dom["label"], key=f"t{ti}_d{di}_lbl")
            dom["color"] = color_input("Colour", dom["color"], key=f"t{ti}_d{di}_col")
            if dc5.button("🗑", key=f"t{ti}_d{di}_del", help="Remove domain"):
                to_delete_domain.append(di)

        for di in reversed(to_delete_domain):
            track["domains"].pop(di)
        if to_delete_domain:
            st.rerun()

        if st.button("➕ Add domain", key=f"t{ti}_adddom"):
            track["domains"].append(
                {"start": 0, "end": int(track["length"]) // 2,
                 "label": "New domain", "color": "#888888"}
            )
            st.rerun()

        # ── Variants ───────────────────────────────────────────────────────────
        st.markdown("**Variants**")
        to_delete_variant: list[int] = []
        for vi, var in enumerate(track["variants"]):
            vc1, vc2, vc3, vc4, vc5, vc6 = st.columns([2, 4, 2, 2, 2, 1])
            var["pos"] = vc1.number_input(
                "Position", min_value=0, max_value=int(track["length"]),
                value=int(var["pos"]), key=f"t{ti}_v{vi}_pos"
            )
            var["label"] = vc2.text_input("Label", value=var["label"], key=f"t{ti}_v{vi}_lbl")
            var["color"] = color_input("Colour", var["color"], key=f"t{ti}_v{vi}_col")
            var["direction"] = vc4.selectbox(
                "Direction", ["down", "up"],
                index=0 if var["direction"] == "down" else 1,
                key=f"t{ti}_v{vi}_dir"
            )
            var["y_offset"] = float(vc5.number_input(
                "Y-offset", min_value=0.0, max_value=5.0, step=0.05,
                value=float(var["y_offset"]), key=f"t{ti}_v{vi}_yoff"
            ))
            if vc6.button("🗑", key=f"t{ti}_v{vi}_del", help="Remove variant"):
                to_delete_variant.append(vi)

        for vi in reversed(to_delete_variant):
            track["variants"].pop(vi)
        if to_delete_variant:
            st.rerun()

        if st.button("➕ Add variant", key=f"t{ti}_addvar"):
            track["variants"].append(
                {"pos": int(track["length"]) // 2, "label": "New variant",
                 "color": "#444444", "direction": "down", "y_offset": 0.85}
            )
            st.rerun()

        st.divider()
        if st.button(f"🗑 Remove track '{track['name']}'", key=f"t{ti}_del"):
            to_delete_track.append(ti)

for ti in reversed(to_delete_track):
    tracks_data.pop(ti)
if to_delete_track:
    st.rerun()


# ── build GeneTrack objects and render ─────────────────────────────────────────
def build_tracks(data: list) -> list[GeneTrack]:
    result = []
    for t in data:
        domains = [Domain(**d) for d in t["domains"]]
        variants = [Variant(**v) for v in t["variants"]]
        result.append(
            GeneTrack(
                name=t["name"],
                length=t["length"],
                name_color=t["name_color"],
                line_color=t["line_color"],
                domains=domains,
                variants=variants,
            )
        )
    return result


if tracks_data:
    try:
        gene_tracks = build_tracks(tracks_data)

        fig = build_figure(gene_tracks, figsize=(fig_w, fig_h), title=fig_title or None)
        st.pyplot(fig)

        # ── download buttons ───────────────────────────────────────────────────
        dl1, dl2 = st.columns(2)

        png_buf = io.BytesIO()
        fig.savefig(png_buf, format="png", dpi=300, bbox_inches="tight")
        png_buf.seek(0)
        dl1.download_button(
            "⬇ Download PNG (300 dpi)", data=png_buf,
            file_name="gene_schematic.png", mime="image/png"
        )

        svg_buf = io.BytesIO()
        fig.savefig(svg_buf, format="svg", bbox_inches="tight")
        svg_buf.seek(0)
        dl2.download_button(
            "⬇ Download SVG", data=svg_buf,
            file_name="gene_schematic.svg", mime="image/svg+xml"
        )

        plt.close(fig)

    except Exception as exc:
        st.error(f"Could not render figure: {exc}")
else:
    st.info("Add at least one track using the sidebar.")
