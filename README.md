# gene-schematic

Create clean, publication-ready gene/protein schematics with domains and allelic variants.

## Why this is useful

- Fast figure drafting for manuscripts and presentations
- Scriptable Python API for reproducible plots
- Interactive Streamlit editor for quick iteration
- Export-ready downloads: **PNG (300 dpi), SVG, PDF**

## Two ways to use it

| Mode | File | Best for |
|---|---|---|
| **Interactive app** | `app.py` | Editing visually and exporting final figures |
| **Python script/API** | `gene_schematic.py` | Reproducible figure generation from code |

## Quick start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Launch the interactive editor

```bash
streamlit run app.py
```

Then open `http://localhost:8501`.

Default starting track:
- Name: `ABC1`
- Length: `1000`
- Domain: `100–300`

From the app, you can add/remove tracks, domains, variants, adjust styling, and download as:
- `gene_schematic.png`
- `gene_schematic.svg`
- `gene_schematic.pdf`

### 3) Or run the static script

Edit the `if __name__ == "__main__":` block in `gene_schematic.py`, then run:

```bash
python gene_schematic.py
```

Outputs:
- `gene_schematic.png` (300 dpi)
- `gene_schematic.svg`

## Python API example

```python
from gene_schematic import Domain, Variant, GeneTrack, draw_gene_schematic

tracks = [
    GeneTrack(
        name="MY-GENE",
        length=500,
        name_color="#d7191c",
        domains=[Domain(50, 200, "Kinase domain", "#4f9e1f", edge_color="#2d6212")],
        variants=[Variant(125, "R125H", color="#d62728", direction="down", y_offset=0.85, sublabel="freq 0.03")],
    )
]

draw_gene_schematic(tracks, out_png="my_gene.png", out_svg="my_gene.svg")
```

## Data model

### `Domain`

| Field | Type | Default | Description |
|---|---|---|---|
| `start` | float | – | Start position (aa) |
| `end` | float | – | End position (aa) |
| `label` | str | – | Text shown below the domain rectangle |
| `color` | str | – | Fill colour (hex or named) |
| `edge_color` | str | `"black"` | Border colour |

### `Variant`

| Field | Type | Default | Description |
|---|---|---|---|
| `pos` | float | – | Position (aa) |
| `label` | str | – | Text label |
| `color` | str | `"#444444"` | Triangle + label colour |
| `direction` | str | `"down"` | `"down"` = triangle above line pointing down; `"up"` = triangle below line pointing up |
| `y_offset` | float | `0.85` | Extra vertical gap for label placement |
| `sublabel` | str | `""` | Optional second line below the label (e.g. allele frequency) |

### `GeneTrack`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | str | – | Gene/protein name shown on the left |
| `length` | float | – | Total length in aa |
| `name_color` | str | `"black"` | Color of the name label |
| `domains` | list[Domain] | `[]` | Domains to draw |
| `variants` | list[Variant] | `[]` | Variants to mark |
| `line_color` | str | `"black"` | Color of the baseline |
