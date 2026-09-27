---
kernelspec:
  name: python3
  display_name: Python 3
---

# Chapter 2: Maximum Likelihood Estimation

> Given data assumed to come from a parametric family, MLE picks the parameter values that make the data we actually saw the most probable thing to have observed (for continuous data, the most *dense* — any exact value has probability zero).

:::{note} Running the code
The Python cells on this page run **in your browser**. Click the **power icon** at the top of the page to activate the kernel, then run — or edit — any cell. Packages (NumPy, SciPy, …) load automatically the first time you import them (a few seconds).
:::

## Motivation

You have data — a sequence of coin flips, a list of game outcomes, a daily stock return — and a candidate probabilistic model for how it was produced. The model has unknown parameters $\theta$ (a probability, a mean and variance, a rate). What value of $\theta$ should you commit to?

MLE answers: pick the $\theta$ that maximizes the probability of the data you actually observed. It is the simplest principled way to fit a probabilistic model, and almost everything later in the book — Monte Carlo error analysis, fitting random-walk drifts, calibrating a GBM, identifying the tail class in extreme value statistics — invokes it.

## Setup & notation

Assume $n$ independent and identically distributed (IID) observations
$$
X_1, X_2, \dots, X_n \overset{\text{iid}}{\sim} f(\cdot \mid \theta),
$$
where $f(x \mid \theta)$ is a probability density (continuous data) or mass function (discrete data) and $\theta$ is the unknown parameter (or vector of parameters) we want to estimate.

Symbols come from [`A_notation.md`](./A_notation.md). New here:

- $L(\theta)$ — **likelihood**: the joint mass (discrete data) or density (continuous data) of the observed sample, read as a function of $\theta$.
- $\ell(\theta) = \log L(\theta)$ — **log-likelihood**.
- $\mathrm{NLL}(\theta) = -\ell(\theta)$ — what numerical solvers minimize.
- $\hat{\theta}_{\mathrm{MLE}}$ — the MLE, the argmax of $L$ (equivalently of $\ell$).

## Core ideas

### The likelihood

By independence, the joint density factorizes:
$$
L(\theta) = \prod_{i=1}^{n} f(X_i \mid \theta).
$$

The crucial conceptual move: $L(\theta)$ is read as a function of *the parameter*, with the data $X_i$ held fixed. Pre-experiment, $f(X \mid \theta)$ is "the probability of $X$ given $\theta$." Post-experiment, $L(\theta)$ ranks candidate $\theta$'s by how well each accounts for what I saw. Same expression, different perspective. Resist upgrading that ranking into "how probable is each $\theta$" — $L$ is not a distribution over $\theta$ and does not integrate to 1. Exercise 1 is about exactly this.

### Why log-likelihood

Two excellent reasons to maximize $\ell = \log L$ instead of $L$ directly:

1. **Algebra.** Products of $n$ terms become sums:
   $$
   \ell(\theta) = \sum_{i=1}^{n} \log f(X_i \mid \theta).
   $$
   Derivatives of sums are easy; derivatives of products are a chain-rule nightmare.
2. **Numerics.** $L$ multiplies $n$ small factors together, so it shrinks geometrically in $n$. For a fair coin, any *specific* sequence of $n$ flips has likelihood exactly $2^{-n}$: at $n = 100$ that is $\approx 10^{-30}$, and by $n = 1075$ it has rounded to zero in double precision and the estimate is destroyed. $\ell = \log L$ turns that product into a sum and stays in a sane numerical range — at $n = 1075$ it is a perfectly ordinary $-745$.

   Two things this argument does *not* say. The bound is not $2^{-n}$ in general — for a biased coin the largest a likelihood can get is $\max(p, 1-p)^n$, so all-heads data under $p = 0.9$ gives $0.9^{100} \approx 3 \times 10^{-5}$, twenty-five orders of magnitude above $2^{-100}$. And the factors are not always $\le 1$: for continuous data they are *densities*, which can exceed 1 wherever the distribution is concentrated ($\mathcal{N}(0, 0.01)$ has density $3.99$ at the origin). Underflow is still the rule in practice, because $n$ factors that are *typically* small still collapse; but "each term is a probability below one" is the wrong reason.

Since $\log$ is strictly increasing, the argmax is the same: $\arg\max_\theta L(\theta) = \arg\max_\theta \ell(\theta)$.

### Two ways to find the maximum

**Analytic.** When $\ell$ is smooth and unimodal in $\theta$, set $\nabla_\theta \ell = 0$ and solve. For many "textbook" distributions (Bernoulli, Gaussian, exponential, Poisson) this gives a closed form — usually a function of the sample mean or sample variance.

**Numeric.** When the model is more complicated — $\theta$ enters through a neural network, a system of ODEs, a tournament simulation — there is no closed form. We hand the negative log-likelihood to an optimizer (`scipy.optimize.minimize`, etc.) and minimize it. **Always pass NLL, not $-L$:** optimizers minimize, and the log keeps the surface numerically tame.

> **Aside: concavity is a separate question.** Maximising wants $\ell$ **concave** in $\theta$ — equivalently, the NLL $-\ell$ **convex**. Get the direction right: a *convex* $\ell$ would push its maximum out to the boundary, which is the opposite of what you want. When $\ell$ is concave, any local maximum is the global one and gradient methods cannot get stuck in a spurious peak. It holds for many simple distributions (Bernoulli in $p$, Gaussian in $\mu$ at fixed $\sigma$) — for Bernoulli, $\ell''(p) = -S/p^2 - (n-S)/(1-p)^2 < 0$ on $(0,1)$, which is exactly the concavity check. It usually fails as soon as $\theta$ enters $f$ nonlinearly (e.g. $\ell$ is not jointly concave in $(\mu, \sigma^2)$, and any neural-net likelihood is wildly non-concave). When in doubt, run the optimizer from multiple random starts.

## Worked example 1: Bernoulli $p$

You flip a possibly-biased coin $n$ times and record $X_i \in \{0, 1\}$ with $X_i \sim \mathrm{Bernoulli}(p)$. Estimate $p$.

### Analytic derivation

The Bernoulli pmf can be written compactly as $f(x \mid p) = p^x (1-p)^{1-x}$ (check: $f(1) = p$, $f(0) = 1-p$). So
$$
\ell(p) = \sum_{i=1}^n \big[X_i \log p + (1 - X_i) \log(1-p)\big] = S \log p + (n - S) \log(1 - p),
$$
where $S = \sum_i X_i$ is the number of successes. Differentiate, set to zero:
$$
\frac{d\ell}{dp} = \frac{S}{p} - \frac{n - S}{1 - p} = 0
\quad\Longrightarrow\quad
\boxed{\hat{p}_{\mathrm{MLE}} = \frac{S}{n} = \bar{X}}.
$$

The MLE is the **sample mean**. This is so familiar that it can feel circular, but the value of the derivation is in the *justification*: out of every possible estimator (median? mode? median-of-medians? something exotic?), MLE picks the sample mean for a principled reason.

### Numeric verification

Even though we have a closed form, it is worth seeing the numerical path because the same code structure works for models without one.

```{code-cell} python
import numpy as np
from scipy.optimize import minimize

rng = np.random.default_rng(seed=0)
p_true, n = 0.3, 500
data = rng.binomial(1, p_true, size=n)

def nll_bernoulli(p, x):
    p = np.clip(p, 1e-9, 1 - 1e-9)   # avoid log(0)
    return -np.sum(x * np.log(p) + (1 - x) * np.log(1 - p))

p_analytic = data.mean()
p_numeric = minimize(nll_bernoulli, x0=0.5, args=(data,),
                     bounds=[(1e-9, 1 - 1e-9)]).x.item()

print(p_true, p_analytic, p_numeric)
# 0.3   0.338   0.338
```

The two estimates agree to within optimizer tolerance, as they must — there is only one minimum of a convex function. Both differ from $p_{\text{true}} = 0.3$ by about $0.04$, which is right in line with the standard error $\sqrt{p(1-p)/n} \approx 0.020$ (we are $\sim 2\sigma$ off, well within the noise of a single sample).

The full version (parameter sweep + plot of the NLL curve with both estimates marked) is in [`code/02_mle/bernoulli_mle.py`](./code/02_mle/bernoulli_mle.py).

## Worked example 2: sum of two Bernoulli flips

Now each observation $X_i$ is the sum of two independent Bernoulli$(p)$ trials, so $X_i \in \{0, 1, 2\}$ with
$$
\mathbb{P}(X = 0) = (1-p)^2, \qquad \mathbb{P}(X = 1) = 2p(1-p), \qquad \mathbb{P}(X = 2) = p^2.
$$
(In other words, $X_i \sim \mathrm{Binomial}(2, p)$.)

This is the simplest example where the *observation* is no longer a single Bernoulli but a derived random variable — the kind of structure that shows up everywhere in modeling (a tournament outcome is a sum of match outcomes; a stock price is a product of returns).

### Analytic derivation

Let $n_0, n_1, n_2$ be the counts of each outcome in $N$ trials ($n_0 + n_1 + n_2 = N$). Then
$$
\ell(p) = n_0 \log[(1-p)^2] + n_1 \log[2p(1-p)] + n_2 \log[p^2].
$$
Differentiating, setting to zero, and solving (a few lines of algebra):
$$
\hat{p}_{\mathrm{MLE}} = \frac{2 n_2 + n_1}{2 N}.
$$

This is again a sample mean — but now of *individual coin outcomes*, not of $X_i$. Out of $2N$ underlying coin flips, $2 n_2 + n_1$ came up heads.

### Numeric estimate

```{code-cell} python
import numpy as np
from scipy.optimize import minimize

rng = np.random.default_rng(seed=1)
p_true, N = 0.7, 50
data = rng.binomial(2, p_true, size=N)
n0, n1, n2 = np.bincount(data.astype(np.intp), minlength=3)   # intp: portable to in-browser wasm32

def nll(p, n0, n1, n2):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return -(2*n0*np.log(1-p) + n1*(np.log(2) + np.log(p) + np.log(1-p)) + 2*n2*np.log(p))

p_analytic = (2*n2 + n1) / (2*N)
p_numeric = minimize(nll, x0=0.5, args=(n0, n1, n2),
                     bounds=[(1e-9, 1 - 1e-9)]).x.item()

print(p_true, p_analytic, p_numeric)
# 0.7   0.66   0.66
```

The two agree to the printed precision, and both sit a little below the true $0.7$ — with
$N = 50$ that gap is ordinary sampling noise, not a bug. Full version with NLL curve in
[`code/02_mle/binomial_mle.py`](./code/02_mle/binomial_mle.py).

### The wrinkle: where "set the derivative to zero" stops working

Everything above found the maximum by solving $\ell'(p) = 0$. That recipe quietly assumes the
maximum is in the *interior* of $[0, 1]$, and it need not be.

Suppose every one of the $N$ observations comes back a $2$ — every pair of flips was two heads.
Then $n_0 = n_1 = 0$, and the log-likelihood collapses to $\ell(p) = 2N \log p$, which is
strictly increasing: it has **no stationary point anywhere in $(0,1)$**. Its derivative
$2N/p$ is never zero. The maximum sits at the boundary, $\hat p = 1$, and the formula
$\hat p = (2n_2 + n_1)/2N$ still returns it — but by arithmetic accident, not because the
derivation applies.

The estimate is also plainly overconfident. Ten such observations are twenty flips, and twenty
flips of a fair coin come up all heads about once in a million times — the MLE responds by
declaring the coin two-headed. **MLE returns the parameter value best supported by the data
it was given, which at a boundary can be a value you have no reason to believe** — and there
it also has no curvature left to warn you, because the Fisher information the Intuition
section uses for error bars is undefined at $p = 1$.

Exercise 5 is the computational face of the same thing — an optimizer at a boundary, and a
defensive `np.clip` that hides the divergence rather than resolving it. **Setting a derivative
to zero finds stationary points; only looking at $L$ itself finds maxima.**

## Intuition

> **Why is the MLE always the sample mean for these examples?** Because both Bernoulli and Binomial are members of the *exponential family*, where the log-likelihood is linear in a sufficient statistic (here, the count of successes). Setting its gradient to zero forces the sample average of that statistic to equal its expectation under $p$ — and for Bernoulli, the expectation is $p$ itself. (This generalizes: MLE for the Gaussian gives the sample mean *and* sample variance for the same reason.)

> **Why minimize NLL instead of maximize $L$?** Three reasons stacked on top of each other: (1) optimizers minimize by convention; (2) $\log$ turns products into sums, simplifying derivatives; (3) $\log$ rescales tiny probabilities into a representable numeric range. Any one alone is reason enough.

> **What does MLE *not* tell you?** It gives a single point estimate, not a distribution over plausible $\theta$ values. The curvature of the log-likelihood at its peak — the **observed Fisher information** $J(\hat\theta) = -\nabla^2 \ell(\hat\theta)$, the *negative Hessian* — measures how sharply the data pin $\theta$ down. Its inverse $J(\hat\theta)^{-1}$ estimates the covariance of $\hat\theta$; the square roots of that matrix's diagonal are the standard errors, from which *asymptotic* confidence intervals follow under the usual regularity conditions. (Sharp peak, large $J$, small variance — the inverse relationship is the whole content.) But MLE itself is silent about uncertainty until you ask. Bayesian inference (not in this book) carries a full posterior distribution as a first-class object.

> **MLE is a function — and a random one.** $\hat{p}$ depends on the random sample $\{X_i\}$, so $\hat{p}$ is itself a random variable. Its mean across resamples is the *true* $p$ (MLE is unbiased here). Its standard deviation across resamples is the **standard error**, and for a Bernoulli sample mean it scales like $\sqrt{p(1-p)/n} \propto 1/\sqrt{n}$. This $1/\sqrt{n}$ shrinkage is the recurring signature of statistical estimation, and you will see it again in Chapter 3.

## Connections

- **Builds on:** independence and the LLN/CLT (Appendix A).
- **Used in:** Ch. 3 (Monte Carlo as an MLE-flavored estimator of an expectation), Ch. 5 (fitting drift/diffusion of random walks), Ch. 6 (fitting GBM drift $\mu$ and volatility $\sigma$), Ch. 8 (fitting Gumbel/Weibull/Fréchet to tail data).
- **Related but not required:** the method of moments (an alternative estimator), Bayesian inference (replaces a point estimate with a posterior).

## Exercises

1. **Conceptual.** A friend says "the likelihood is the probability that the parameter equals $\theta$ given the data." What is wrong with this statement? (Hint: which is random, $X$ or $\theta$, in the frequentist setup?)

2. **Derivation.** Suppose $X_1, \dots, X_n \overset{\text{iid}}{\sim} \mathcal{N}(\mu, \sigma^2)$. Derive the MLEs $\hat\mu$ and $\hat{\sigma}^2$ by setting partial derivatives of $\ell(\mu, \sigma^2)$ to zero. (You should recover the sample mean and the *uncorrected* sample variance with denominator $n$, not $n-1$.)

3. **Computational.** Repeat the Bernoulli example for $n \in \{10, 30, 100, 300, 1000, 3000\}$, drawing 500 datasets at each $n$ and recording $\hat{p}$ for each. Plot the empirical standard deviation of $\hat{p}$ against $n$ on log-log axes. What slope do you read off, and does it match the theoretical $1/\sqrt{n}$?

4. **Modeling judgment.** A pollster surveys 1000 voters and finds 540 prefer candidate A. Report $\hat{p}$ and a back-of-envelope two-sigma uncertainty band using the Bernoulli standard error formula. Now suppose she actually surveyed 200 voters and found 108 prefer A. Same $\hat{p}$ — is your conclusion the same?

5. **Checking the optimizer.** Take the Bernoulli NLL above and pass `scipy.optimize.minimize` an initial guess of $p_0 = 0.999$ *without* the bounds argument. Inspect the **full result object**, not just `result.x`: check `result.success` and `result.message`. Then add `bounds=[(1e-9, 1 - 1e-9)]` and compare. What changed, and what role is the `np.clip` inside `nll_bernoulli` playing? (A recurring practical issue: log-likelihoods diverge at parameter boundaries, and a defensive clip can hide that rather than solve it.)

:::{admonition} Solutions
:class: dropdown

**1.** Frequentist statistics treats $\theta$ as a fixed unknown constant and the data $X$ as random. So "the probability that $\theta$ equals some value" is not even defined in this framework — $\theta$ has no probability distribution. The likelihood $L(\theta)$ is a function of $\theta$ that *evaluates* at each candidate value to "the probability (or, for continuous data, the density) of seeing the data we saw if $\theta$ were that value." It is not itself a probability distribution over $\theta$ (it generally doesn't even integrate to 1 over $\theta$). Bayesian statistics *does* give $\theta$ a distribution (the posterior), but only by also specifying a prior.

**2.** Log-likelihood for IID Gaussian:
$$
\ell(\mu, \sigma^2) = -\tfrac{n}{2}\log(2\pi\sigma^2) - \frac{1}{2\sigma^2}\sum_i (X_i - \mu)^2.
$$
$\partial_\mu\ell = \frac{1}{\sigma^2} \sum_i (X_i - \mu) = 0 \Rightarrow \hat\mu = \bar X$.
Substituting $\hat\mu$ and solving the second equation, $\partial_{\sigma^2}\ell = -\frac{n}{2\sigma^2} + \frac{1}{2\sigma^4}\sum_i(X_i - \hat\mu)^2 = 0 \Rightarrow \hat{\sigma}^2 = \frac{1}{n}\sum_i (X_i - \bar X)^2$. The denominator is $n$ (not $n-1$); MLE for variance is biased, and the unbiased "Bessel-corrected" estimator with $n-1$ comes from a different criterion.

One caveat the stationary-point calculation hides, and it is the same trap as the boundary case above: this derivation assumes $\hat\sigma^2 > 0$. If every observation happens to be identical, then $\sum_i (X_i - \bar X)^2 = 0$ and $\ell \to +\infty$ as $\sigma^2 \to 0^+$ — the likelihood is *unbounded* and no maximiser exists. Setting a derivative to zero cannot tell you that; only looking at $L$ itself can.

**3.** See [`code/02_mle/standard_error_scaling.py`](./code/02_mle/standard_error_scaling.py). The slope on log-log axes should be very close to $-0.5$, matching $\mathrm{SE}(\hat p) = \sqrt{p(1-p)/n}$.

**4.** $\hat p = 0.540$ in both cases. Standard error $\approx \sqrt{0.540 \cdot 0.460 / n}$: $\approx 0.0158$ for $n = 1000$, giving a two-sigma band of $\pm 0.032$, i.e. $[0.508, 0.572]$ — clear of $0.5$, so this is evidence of a real lead. For $n = 200$, $\approx 0.0352$, giving $\pm 0.071$, i.e. $[0.470, 0.610]$ — which comfortably contains $0.5$, so the same point estimate now supports no conclusion about who is ahead. Sample size is not a footnote. Note also how little the band shrinks for the effort: five times the respondents buys only a $\sqrt5 \approx 2.2$-fold narrowing, which is the $1/\sqrt{n}$ tax again.

**5.** Both runs land on the right answer, $\hat p = 0.338$ — but only one of them *knows* it did. Without bounds you get `success=False` and a message about precision loss (on SciPy 1.18 it reads `'Desired error not necessarily achieved due to precision loss.'`, but the exact wording is a SciPy internal and has changed between versions — read the `success` flag, not the string); with bounds, `success=True` and a clean convergence message.

The reason is the `np.clip` inside `nll_bernoulli`. Unbounded, the optimizer steps into $p > 1$, where $\log p$ and $\log(1-p)$ would be undefined — but the clip silently pins $p$ to $1 - 10^{-9}$ instead. So the NLL stays *finite* (no NaN), and the surface out there is perfectly **flat**: every $p > 1$ returns the same value, the gradient is zero, and the line search cannot make progress. Hence the precision-loss warning.

The lesson is the useful part. The clip is defensive coding that prevented a crash and, in exchange, converted a loud failure into a quiet one — a flat region the optimizer had to blunder out of. `bounds` fixes the actual problem, by keeping the search inside the domain where the model is defined. The tiny $\epsilon$ then avoids the boundary itself, where the log-likelihood genuinely diverges. **Always read `result.success`**: an optimizer that returns a number has not necessarily converged.

:::

## Further reading

- Wasserman, *All of Statistics*, Ch. 9 (Maximum Likelihood) for a tight, mathematically
  careful treatment with asymptotic theory. ISBN 9780387402727 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,9780387402727&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- Stigler, *The History of Statistics* (1986), Ch. 9 for the historical context — MLE was
  popularized by Fisher in the 1920s and was controversial for decades.
  ISBN 9780674403413 (paperback) · [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,History%20of%20Statistics%20Stigler&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- For the connection to information theory (MLE = minimizing KL divergence between the
  empirical and model distributions): MacKay, *Information Theory, Inference and Learning
  Algorithms*, §22. **Free in full** from the author, with Cambridge's permission:
  [inference.org.uk](https://www.inference.org.uk/itila/book.html) ·
  [PDF](https://www.inference.org.uk/itprnn/book.pdf) · [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Information%20Theory%20Inference%20Learning%20Algorithms%20MacKay&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
