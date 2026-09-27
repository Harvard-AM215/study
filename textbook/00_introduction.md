# Introduction

> This book teaches you to build, run, and — above all — *judge* mathematical models of real phenomena, with code you can edit and run right in your browser.

## What this book is

Mathematical modeling is the craft of turning a messy real-world question into something you can compute with, and then knowing how much to trust the answer that comes out. A model is never the phenomenon itself — it is a deliberate simplification that keeps the few features you think matter and throws the rest away. The skill is in choosing well, and in checking honestly.

Each chapter takes one **canonical model class** — random walks and diffusion, geometric Brownian motion, compartmental (SIR) flows, agent models, queues — and walks it end to end: the motivating question, the mathematics (derivations sketched, not belabored), two or three worked examples with runnable Python, intuition callouts for the parts that trip people up, and exercises with worked solutions. The emphasis throughout is less "here is a formula" and more "here is how you would decide whether this model is any good."

## What you'll be able to do

The chapters differ in subject, but they drill the same handful of modeling competencies. By the end you should be able to:

- **Formulate** — turn a vague phenomenon into a precise question, a set of assumptions, and a mathematical structure that could answer it.
- **State assumptions** — name a model's explicit *and* implicit assumptions, and predict where they break.
- **Verify vs. validate** — check that your code correctly computes the model you specified (verification, against known mathematics) *and*, separately, that the model matches reality (validation, against data). Confusing these two is the single most common modeling mistake, and the distinction is returned to in most chapters.
- **Estimate** — fit parameters from data and interpret what the fit does and does not establish.
- **Reason about uncertainty** — attach error bars, think in distributions, and flag when you are extrapolating.
- **Recognize the class** — meet an unfamiliar phenomenon and identify which canonical structure fits (the "same skeleton, new skin" skill).
- **Communicate** — describe a model's assumptions, evidence, and limits honestly.

## How to use this book

- **For mastery** — read in order, and *work the exercises before peeking at the solutions*. Run (and break) the code rather than just reading it.
- **As reference** — after the *Random Walks & the Diffusion Equation* chapter, the chapters are mostly independent, so you can jump to the model class you need.
- **Notation** — the [*Notation & Probability Primer*](A_notation.md) appendix fixes the symbols and the handful of probability facts used throughout. If a symbol is unfamiliar, look there first.
- **Appendices** — Portfolio Optimization and Dimensional Analysis are optional side-trips, not part of the main sequence.

## Running the code in your browser

The Python cells in the chapters run **in your browser** — nothing to install. (The appendices are reference material and carry no runnable cells, so they have no kernel and no Run button; a code block there is there to be read.)

1. On any chapter with code, click the **power icon** near the top of the page to start the in-browser kernel.
2. Once it's live, each code cell gets a **Run** button, and you can **edit** the code and re-run it — change a parameter, break an assumption, and see what happens. That experimentation is the point.
3. The **first** cell you run downloads the scientific packages (NumPy, SciPy, …) — a few seconds, once per page. After that it's instant.

The in-page snippets are kept minimal and self-contained. The **full versions** — with plots, parameter sweeps, and extra examples — live alongside each chapter in its `code/` directory, meant to be downloaded and run locally.

### …and in Colab

Chapters with code also carry an **Open in Colab** badge at the top — a second way to run
the same notebook, with a full Python and an unrestricted network. For everything in the
current published set the two are interchangeable, so use whichever you prefer.

The difference shows up only in chapters that want **live market data**, and it is worth
knowing about in advance. The in-browser kernel has no general internet access: it runs
inside this page, and the browser blocks it from reaching other sites. Those chapters fall
back to a committed public dataset — Federal Reserve exchange rates and Treasury yields —
and say so when they run. The fallback keeps the statistical properties the chapters
actually need (fat tails, volatility clustering), but it is a *different asset class*, and
at least one conclusion genuinely changes character with it, which the chapter flags where
it happens. Open those in Colab if you want them on US equities.[^data]

[^data]: **Why isn't the stock data just committed here, like the exchange rates are?**
    Because we are not allowed to republish it. A stock index is a commercial product
    rather than a public fact — S&P Dow Jones Indices, NASDAQ and CBOE compute, brand and
    license their index data, and that is their business. So "free to download" and "free to
    republish" are different permissions, and essentially every convenient source grants the
    first while withholding the second: FRED carries the S&P 500 but states that reproducing
    it is prohibited without written permission, Yahoo's terms restrict redistribution, and
    the academic library this book downloads from carries a copyright notice with no grant
    attached. Fetching it yourself is fine, which is exactly what the Colab path does. The
    exchange rates and Treasury yields *are* committed here because they come from the
    Federal Reserve, whose data carries the label "Public Domain: Citation Requested"
    (Board of Governors of the Federal Reserve System, retrieved from FRED, Federal Reserve
    Bank of St. Louis). Baseball results are committed for a third reason: game outcomes are
    facts, and facts are not copyrightable by anyone.

## Prerequisites

- **Mathematics:** single-variable calculus, basic linear algebra, and introductory probability (the level of a first probability course). The [*Notation & Probability Primer*](A_notation.md) appendix reviews exactly what's assumed.
- **Programming:** enough Python to read a short script and change a number in it. The in-page cells are meant to be *edited* — that is most of what you need. Chapters that go further use NumPy, but introduce what they use; you do not need prior experience with any specific modeling library. If you have programmed in another language and never in Python, you are in a fine position to start here.

## A note on models

> All models are wrong, but some are useful. — George Box

Every number this book produces comes with an implicit "…assuming the model is right." A good modeler says that clause out loud, and then goes looking for the evidence that would prove it wrong. That habit — build it, check it against known math, check it against reality, and be honest about the gap — is the whole subject.
