# Reflection

## What Changed From The Earlier Prototype

The first version of this project was a transparent content-based recommender. It worked, but it still felt like a ranking script. The final version is more like a real AI system because it now performs a sequence of reasoning steps:

1. interpret a natural-language request
2. retrieve supporting context
3. rank candidates
4. explain the recommendation
5. check whether the result is reliable
6. save a trace log for review

That change matters because the system behavior is no longer only about the scoring formula. Retrieval and self-checking now shape the output directly.

## What I Learned

The biggest lesson was that "more intelligent behavior" is not just adding more features to a score. The project improved the most when I added structure around the score:

- a parser that turns messy user language into explicit preferences
- a retrieval layer that brings in richer evidence
- a warning system that says when the catalog is weak
- tests that verify the system keeps behaving the way I claim it does

That made the project feel more trustworthy than simply making the ranking formula bigger.

## What Surprised Me

The most interesting case was the contradictory request for classical music during an intense workout. A normal scorer would mostly return high-energy non-classical songs and silently ignore the genre request. Adding the genre-coverage safeguard made the system more honest. It still recommends the strongest workout tracks, but it also keeps a classical item in the final list and labels why that happened.

That felt closer to responsible AI behavior because the system exposes the tradeoff instead of hiding it.

## How The Reliability Layer Helped

The reliability work was useful in two ways:

- it gave me automated checks instead of relying only on intuition
- it made the system explain its own uncertainty

The benchmark suite helped confirm that focus, workout, and nostalgic queries were grounded and consistent. The warning system helped separate "the model is wrong" from "the catalog is too limited for this request."

## Limits I Still See

- The catalog is still tiny.
- Retrieval is still lexical rather than semantic.
- The evidence text is hand-authored, which means the system inherits my labeling choices.
- The system is explainable, but it is not deeply personalized because it does not learn from user history.

## What I Would Do Next

If I kept going, I would:

- expand the catalog
- add embedding-based retrieval
- add a simple visual interface for manual review
- store benchmark metrics over time
- let users state negative preferences more directly, such as "no lyrics" or "less aggressive"

The final version feels much closer to a professional applied AI artifact because it does not just produce answers. It shows how it got them, checks itself, and leaves evidence behind for a human reviewer.
