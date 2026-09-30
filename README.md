# supertonic-onnx-bundles

A normalized, reproducible Supertonic TTS ONNX bundle catalog for consumers such as OnnxVoice.

## What this repository is

- Canonical generated Supertonic ONNX bundle catalog data.
- Source/provenance metadata.
- A public JSON catalog schema.
- Integrity checks and CI.
- No Python package and no model mirror.

OnnxVoice owns catalog parsing, downloads, checksum verification, installation manifests, provider/session creation, and the four-session Supertonic runtime adapter. `supertonicsynth` owns text preprocessing, language policy, voice-style loading, chunking, and high-level synthesis.

## Initial snapshot

The initial catalog is pinned to the archived model location:

```text
supertone-oss-archive/supertonic-3
aafc6e32416a594460b32413efc49d7fe4ce6d46
```

It contains four ONNX graph components, `tts.json`, `unicode_indexer.json`, and ten built-in voice styles (`F1`-`F5`, `M1`-`M5`).

## Canonical files

```text
catalog/bundles.json
catalog/source.json
schemas/bundle-catalog.schema.json
```

## Consumer example

```python
from onnxvoice import OnnxVoice

ov = OnnxVoice()
installation = ov.install("supertonic:supertonic-3")
with ov.open(installation) as runtime:
    ...
```

## Verify locally

```bash
python scripts/check_catalog_integrity.py
onnxvoice catalog supertonic verify \
  --catalog catalog/bundles.json \
  --source catalog/source.json
```

The second command requires the stage-3 OnnxVoice catalog implementation.

## Refresh

```bash
onnxvoice catalog supertonic build \
  --output catalog/bundles.json \
  --source-output catalog/source.json
onnxvoice catalog supertonic verify \
  --catalog catalog/bundles.json \
  --source catalog/source.json
```

Rebuilds at a fixed upstream revision must be byte-for-byte deterministic.

## Licensing

Repository-authored metadata, schema, scripts, and documentation are MIT licensed. Referenced Supertonic-3 model artifacts remain under the upstream OpenRAIL-M model license and are not redistributed by this repository.
