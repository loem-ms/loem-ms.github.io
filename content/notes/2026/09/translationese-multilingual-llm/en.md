## The question

Multilingual LLMs can generate fluent text in many languages, but their training data and post-training are often heavily influenced by English and translated text. This paper asks whether that influence is visible in the final output: **when a model generates directly in another language, does the text still look statistically like a translation?**

The authors study two multilingual LLMs across five languages. They train translationese classifiers only on **human original writing vs. human translations**, then use those classifiers to probe direct LLM generations.

## What they find

A few results stood out to me:

- Direct LLM generation can indeed show **translationese-like statistical patterns**, even without an explicit translation step.
- The effect is particularly strong for German and Spanish, while Greek and Pashto show weaker signals. So it is not simply a matter of lower-resource languages being more translation-like.
- Automatic translationese scores and human perception do not always agree: text can be statistically translation-like while still sounding natural to native speakers.

## Our take

The part I found most interesting is what this result **does not** establish. A translation-like output distribution is not direct evidence that the model internally translates through English.

Human translation and human original writing do not necessarily come from the same distribution in the first place. Translation is conditioned on an already realized source text: information order, explicitness, sentence boundaries, and other choices have partly been fixed before the target-language text is produced. Original writing has more freedom to realize the same content according to the target language itself.

There is also another possible confound: translation and instruction-tuned LLM generation may share generic properties such as standardization, explicitness, or reduced variation. What looks like “translationese” may therefore partly be a broader signature of **constrained generation**, rather than evidence of an internal English pivot.

This led us to a question that feels more directly measurable:

> Instead of asking **“Does the LLM think in English?”**, ask **“Which generation-process distribution is its target-language output closest to?”**

For example, is direct generation closer to native human composition, English-to-target translation, translation from another source language, target-language paraphrasing, or non-translation but constrained human writing?

That shift—from guessing an internal language of thought to comparing observable generation distributions—is the main idea I want to keep thinking about from this paper.
