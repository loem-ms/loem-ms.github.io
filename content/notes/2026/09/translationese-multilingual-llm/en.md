I recently read **An Investigation of Translationese in the Generations of Multilingual Large Language Models** ([arXiv:2608.17399](https://arxiv.org/abs/2608.17399)).

The paper asks a simple but interesting question: even when a multilingual LLM is asked to generate directly in a target language, does its output still look statistically like translated text?

The answer is often yes. The authors train translationese classifiers on human original vs. human translated text, then apply them to direct LLM generations. For some languages, especially German and Spanish, a substantial portion of direct generations are classified as translation-like.

What I found more interesting, however, is what this result **does not** tell us. A translation-like output distribution is not direct evidence that the model internally translates through English.

Human translation and human original writing do not necessarily come from the same distribution in the first place. Translation is conditioned on an already realized source text: information order, explicitness, sentence boundaries, and other choices have partly been fixed before the target-language text is produced. Original writing has more freedom to realize the same content according to the target language itself.

This led us to a slightly different question:

> Instead of asking **“Does the LLM think in English?”**, ask **“Which generation-process distribution is its target-language output closest to?”**

For example, is direct target-language generation closer to:

- native human composition,
- English-to-target human translation,
- translation from another source language,
- target-language paraphrasing, or
- non-translation but constrained human writing?

The last condition may be especially important. Translation and instruction-tuned LLM generation may share generic properties such as standardization, explicitness, or reduced variation. If so, what looks like “translationese” may partly be a broader signature of constrained generation rather than evidence of an internal English pivot.

So my main takeaway from this paper is not that multilingual LLMs “think in English,” but that **the provenance of their output distribution is itself worth studying**. That feels both more measurable and harder to over-interpret.
