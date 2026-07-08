# JPEG Encoder Benchmark

Benchmarking `cjpeg` from **libjpeg-turbo**, **IJG libjpeg**, and **mozjpeg** on Apple Silicon (M4).

## Setup

```bash
brew install jpeg-turbo mozjpeg jpeg
```

Test image: 6000×4000 (24MP), generated with gradients, geometric shapes, and noise — designed to resemble a complex natural photo.

All encoders use PPM input, default settings (baseline, no optimize), **q75–100**.

## Results

| Encoder | q75 enc | q85 enc | q95 enc | q100 enc | q85 dec | q85 size |
|---------|---------|---------|---------|----------|---------|----------|
| **libjpeg-turbo** 3.2.0 | 39 ms | 40 ms | 45 ms | 59 ms | 78 ms | 1,819 KB |
| **IJG libjpeg** 10 | 177 ms | 184 ms | 213 ms | 257 ms | 130 ms | 1,841 KB |
| **mozjpeg** 4.1.5 | 656 ms | 955 ms | 1,774 ms | 3,009 ms | 105 ms | 1,720 KB |

### Speedup vs IJG libjpeg (q85)

| Encoder | Encode speedup | Decode speedup |
|---------|----------------|----------------|
| libjpeg-turbo | **4.6× faster** | **1.7× faster** |
| mozjpeg | 0.2× (slower) | 1.2× faster |

### File size vs libjpeg-turbo (q85)

| Encoder | Size ratio |
|---------|-----------|
| IJG libjpeg | 1.01× (1% larger) |
| mozjpeg | **0.95× (5.4% smaller)** |

## Key Takeaways

1. **libjpeg-turbo dominates for encode speed** — 4.6× faster than reference IJG, 24× faster than mozjpeg at q85. This is the SIMD advantage (NEON on Apple Silicon).
2. **libjpeg-turbo also wins decode** — 1.7× faster than IJG, 1.3× faster than mozjpeg.
3. **mozjpeg produces smaller files** — 5.4% smaller at q85, 25% smaller at q75. Useful for bandwidth-constrained delivery, but the encode cost is steep (24× slower than turbo).
4. **IJG libjpeg 10 is essentially a baseline** — 1% larger files and 4.6× slower encode than turbo. No reason to use it over turbo.

## Recommendation

| Use case | Pick |
|----------|------|
| Real-time encode (cameras, scanners) | **libjpeg-turbo** |
| Batch compression where size matters | **mozjpeg** (accept the encode time) |
| Decode/deploy | **libjpeg-turbo** (fastest, most compatible) |
| Legacy compatibility | IJG libjpeg (no real advantage) |

## Run Yourself

```bash
pip install Pillow
brew install jpeg-turbo mozjpeg jpeg
python3 benchmark.py
```
