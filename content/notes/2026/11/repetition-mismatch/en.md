## The question

Pre-training data mixtures are usually tuned with small-scale experiments, and the winning mixture is then extrapolated to the target training budget. When high-quality data is scarce, it has to be repeated — and the more the budget grows, the more often those small sources are repeated.

This paper asks whether that change in repetition is itself the reason small mixture experiments fail to scale: **does the optimal mixture shift because the repetition rate of scarce sources changes with the budget, in ways a short proxy run never sees?**

The question matters most exactly where data is scarce — for example when native-language or other high-quality data must be sampled repeatedly in a multilingual mixture.

## What they find

The proposed fix is simple: instead of subsampling naively, downsample the source documents and the training tokens proportionally, so that **the repetitions per source in the small experiment match the target run**. The contribution is isolating repetition mismatch as a confound in mixture experiments, rather than inventing subsampling itself.

A few findings stood out to me:

- At 1.17B parameters, the prediction error for the WikiText/FineWeb mixture falls from 0.85 to 0.10 using a single repetition-controlled experiment at a 1/16-token horizon (Table 1). Without repetition control, comparable accuracy needs multiple training horizons, consuming 19%, 44% and 94% of the target token budget for two, three and four horizons.
- With three sources at 757M parameters, two repetition-controlled horizons recover the optimal mixture at the tested sweep resolution (Table 2). The 30M model is an exception, so proxy-model scale still matters.
- The evidence has clear limits: models are at most 1.17B parameters, training reaches only about 3.8B tokens, most configurations use a single seed, and the comparator relies on linear extrapolation.

## Our take

The useful shift in perspective is to treat **repetition count as a first-class variable of the experiment**, tracked alongside mixture weights and token budgets — not as a side effect of limited data.

For low-resource pretraining this feels directly relevant. When scarce native-language data must be repeated many times, a small pilot that does not reproduce that repetition regime is quietly testing a different mixture than the one that will actually be trained. Matching repetitions is a cheap control to add before trusting a pilot's ranking.

Two reservations keep me from reading the result too broadly:

- The gains are shown on curated-domain validation loss, which does not by itself establish downstream capability gains.
- The 1/16 figure describes one training horizon, not the total experimental cost. Multiple mixture and learning-rate runs remain (Appendix E), so repetition matching reduces the cost of prediction; it does not make mixture search cheap.

## What I want to know next

The experiment I would like to see is a matched-repetition pilot on a multilingual or code-data mixture:

> **Does repetition matching still help when the scarce source is a language, and does it hold up on a downstream evaluation rather than validation loss alone?**

There is also a trade-off to measure: preserving repetitions means reducing the unique data in the pilot. Whether that sacrifice is worth it at very small budgets is exactly the kind of thing Figure 2, Tables 1–2 and the cost accounting in Appendix E can help sketch before running anything.
