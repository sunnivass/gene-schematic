# gene-schematic

A simple, publication-ready tool for drawing gene/protein schematics with
labelled domains and allelic variants.  
Comes in two flavours:

| Mode | File | What it does |
|---|---|---|
| **Script** | `gene_schematic.py` | Edit the `__main__` block and run once to get a PNG + SVG |
| **Interactive app** | `app.py` | Streamlit UI – tweak everything in the browser and download the figure |

---

## Quick start

### 1 – Install dependencies

```bash
pip install -r requirements.txt
```

### 2 – Static script

Edit the `if __name__ == "__main__":` block in `gene_schematic.py` with your
own genes, then run:

```bash
python gene_schematic.py
# → gene_schematic.png  (300 dpi)
# → gene_schematic.svg
```

### 3 – Interactive app

```bash
streamlit run app.py
```

A browser tab opens at `http://localhost:8501`.  
You can:
- Add / remove gene tracks
- Edit gene name, length, and line colour
- Add / remove domains with custom start, end, label, and colour
- Add / remove allelic variants with position, label, colour, direction, and
  label-offset to avoid overlaps
- Download the finished figure as **PNG (300 dpi)** or **SVG**

---

## Data model

```python
from gene_schematic import Domain, Variant, GeneTrack, draw_gene_schematic

tracks = [
    GeneTrack(
        name="MY-GENE",
        length=500,           # protein length in amino acids
        name_color="#d7191c",
        domains=[
            Domain(50, 200, "Kinase domain", "#4f9e1f"),
        ],
        variants=[
            Variant(125, "R125H", color="#d62728", direction="down", y_offset=0.85),
        ],
    ),
]

draw_gene_schematic(tracks, out_png="my_gene.png", out_svg="my_gene.svg")
```

### `Domain`

| Field | Type | Description |
|---|---|---|
| `start` | float | Start position (aa) |
| `end` | float | End position (aa) |
| `label` | str | Text shown below the domain rectangle |
| `color` | str | Fill/edge colour (hex or named) |

### `Variant`

| Field | Type | Default | Description |
|---|---|---|---|
| `pos` | float | – | Position (aa) |
| `label` | str | – | Text label |
| `color` | str | `"#444444"` | Triangle + label colour |
| `direction` | str | `"down"` | `"down"` = triangle above line pointing down; `"up"` = triangle below line pointing up |
| `y_offset` | float | `0.85` | Extra vertical gap for the label – increase to avoid overlapping labels |

### `GeneTrack`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | str | – | Gene/protein name shown on the left |
| `length` | float | – | Total length in aa |
| `name_color` | str | `"black"` | Colour of the name label |
| `domains` | list[Domain] | `[]` | Domains to draw |
| `variants` | list[Variant] | `[]` | Variants to mark |
| `line_color` | str | `"black"` | Colour of the baseline |
