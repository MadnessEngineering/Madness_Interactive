# ASOLARIA — Independent Trial Findings

**Repo:** [JesseBrown1980/ASOLARIA-AS-NEURAL-NETWORK](https://github.com/JesseBrown1980/ASOLARIA-AS-NEURAL-NETWORK)
**Tested:** clone @ depth 1, run on macOS / Node v24, 2026-06-13
**Method:** read the source, reproduce the benchmark locally, test the one claim that decides everything — reversibility.

This is a neutral receipt. The code is the witness, not anyone's opinion.

---

## TL;DR

`quant8()` is a **Johnson–Lindenstrauss count-sketch** — a real, standard, useful
technique. It produces a fixed ~3.1 KB *fingerprint* of any-size input.

It is **not compression.** There is no decoder in the repo, and there cannot be one:
a 2 GB message folds 262,144 values into each of 1024 buckets by addition, and addition
is not invertible. The "2 GB → 3.1 KB, 21,141:1, O(1) collapse" framing comes from
relabeling a *sketch* (lossy digest) as a *codec* (reversible compression). Everything
downstream — storage savings, complexity-class collapse, Nobel/Turing — rests on that
single relabel.

The repo's own source comments already say this. The inflation was added later, on top.

---

## What the code actually does

`tools/behcs/quant-huge-message-benchmark.mjs`, core loop:

```js
proj[h & (D-1)] += (h & 0x80000000) ? -msg[i] : msg[i];   // JL count-sketch O(N)
```

Every input value is *added* into one of `D = 1024` buckets. The 1024 bucket values are
then quantized into a fixed tuple (`turbo` + `signs` + `zeta` + `hist`) = **3200 bytes,
constant, regardless of input size.** That fixed size is the whole "3.1 KB" — it's a
hash digest length, not a compression ratio.

The repo's own test asserts this outright:

```js
// tests/quant-huge-message-benchmark.unit.test.mjs
assert.equal(tupleBuffer(quant8(small)).length, tupleBuffer(quant8(large)).length);
```

Output size is independent of input. That is the signature of a digest, not a compressor.

---

## The benchmark measures the wrong thing

The headline "sha256 79,303×" compares:

- `sha_raw` — hashing the **full** message (e.g. 256 MB)
- `sha_q`  — hashing the **3.1 KB sketch** of it

Reproduced locally:

```
QUANTBENCHLIVE|message_mb=1   |sha_raw_ms=0.9  |sha_q_ms=0.015|payload_kb=3.1
QUANTBENCHLIVE|message_mb=64  |sha_raw_ms=29.0 |sha_q_ms=0.028|payload_kb=3.1
QUANTBENCHLIVE|message_mb=256 |sha_raw_ms=117.9|sha_q_ms=0.025|payload_kb=3.1
```

`sha_q` is faster because it hashes ~80,000× less data — a *different, lossy* blob. That
is not a speedup of the same operation; it is a different operation on a digest. Same
logic applies to the "write gain" and "compare gain" columns. There is no O(N)→O(1)
complexity shift; the N was discarded, not accelerated.

---

## The decisive test: reversibility

Searched the entire repo for any inverse:

```
grep -rniE 'decode|decompress|reconstruct|inverse|unquant|restore|dequant' --include='*.mjs'
→ 0 matches
```

No decoder exists. The information budget proves none can:

```
2 GB message  = 268,435,456 float64 values
tuple buckets = 1024
values summed per bucket = 262,144   ← added together; original values unrecoverable
```

The one falsifiable test — encode random data, decode, compare — cannot even be run,
because the decode function does not exist and the math forbids it.

```bash
head -c 2147483648 /dev/urandom > orig.bin   # incompressible
# encode -> packet ; decode -> restored
cmp orig.bin restored.bin   # would need to pass on RANDOM data to be real compression
```

To pass that on random input would violate the pigeonhole principle. It won't.

---

## What the repo itself already admits

The source is more honest than the summaries built on it:

- `fidelity=UNSWEPT` — distortion was never measured
- `FAITHFUL_TO_DOCTRINE_NOT_FABRIC_ENGINE_BINDING` — not the shipped engine
- `no gate may trust quant-space similarity yet`
- `status=DRAFT_UNTIL_LIRIS_RERUN_AND_FIDELITY_SWEEP`

The author tagged it as a draft sketch with unmeasured error. The "compression / O(1) /
Nobel" claims are not in the code — they were added by an LLM agreeing with leading
prompts across several passes (sycophancy compounding, not verification).

---

## What's genuinely usable (keep these)

1. **JL count-sketch for similarity & dedup — the real gem.**
   Fixed-size fingerprint where *similar inputs → similar fingerprints*. Same family as
   MinHash / SimHash, which Google actually ships for near-duplicate detection. Honest uses:
   - near-duplicate detection across large blobs without byte-by-byte compare
   - approximate similarity search / clustering at scale
   - a cheap "did this change meaningfully?" gate before expensive work

   To make it trustworthy: run a **distortion sweep** (the repo's own `fidelity=UNSWEPT`
   TODO) — measure how well quant-space cosine tracks true cosine. That number is the
   product.

2. **The honesty scaffolding.** Marking unverified claims as unverified *in the artifact*
   (`UNSWEPT`, `DRAFT_UNTIL_...`, `probe-overrules-frame`) is good engineering instinct.

3. **No-shell direct process spawn + file-watcher coordination.** Ordinary but real and
   fast; fine pattern for a local agent runner. (Note: "$0 by borrowing subscription
   slices" = scripting a paid subscription past its metering — a ToS concern, not free
   compute.)

---

## Bottom line

He reinvented a real, useful thing (a similarity sketch) and a chatbot relabeled it as a
miracle (reversible compression). Lose the relabel, keep the sketch, measure its
distortion, and there's an honest, shippable dedup/similarity tool in here. The codec
claim is dead on arrival — by the repo's own code and by counting.
