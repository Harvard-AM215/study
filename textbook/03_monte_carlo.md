---
kernelspec:
  name: python3
  display_name: Python 3
---

# Chapter 3: Monte Carlo Methods

> Any quantity you can write as the expected value of a random variable can be estimated by sampling that variable many times and averaging; the estimation error shrinks predictably as $1/\sqrt{N}$ and can be estimated from the same samples.

:::{note} Running the code
The Python cells on this page run **in your browser**. Click the **power icon** at the top of the page to activate the kernel, then run — or edit — any cell. Packages (NumPy, SciPy, …) load automatically the first time you import them (a few seconds).
:::

## Motivation

Suppose you want the area of an irregular region, the value of a high-dimensional integral, the probability of a complicated event, or the expected payoff of a financial contract. Different as they look, these problems share one mathematical form: each asks for the expected value of some function $g(X)$, where $X$ is drawn from a probability distribution. When the expectation cannot be computed analytically, you can estimate it by simulation. Draw many samples $X_1,\ldots,X_N$ from the distribution, evaluate $g(X_i)$ on each, and average. This is the **Monte Carlo method**: use random samples to approximate a quantity you cannot easily calculate directly.

A practical question follows immediately: **how many samples should you draw?** Intuitively, more is better, since every additional sample adds "resolution" to possible outcomes. But every sample also costs time and computing resources: you want enough samples for a "good enough" estimate and not many more. This requires knowing two things. How far is the current estimate likely to be from the true model expectation? And how much would another batch of samples improve it? This chapter develops the error calculation that answers both questions. It also returns to Chapter 1's distinction between verification and validation. A Monte Carlo error bar measures how uncertain you are about a quantity *within* your model. It says nothing about whether the model itself describes the phenomenon you care about.

## Setup & notation

Start with a distribution you can sample from, and let $X$ denote one draw. The distribution is often defined only implicitly, as the output of a generative procedure such as a simulated queue or a random walk. The function $g$ converts a draw into the number you record: a hit or miss, a waiting time, a payoff. The target of the calculation is the expectation of that number,

$$
\mu = \mathbb{E}[g(X)] =
\begin{cases}
\int g(x)\,f(x)\,dx & \text{for a continuous } X,\\[2pt]
\sum_x g(x)\,f(x) & \text{for a discrete } X,
\end{cases}
$$

where $f$ is the probability density or probability mass function of $X$. In both cases each possible value of $g$ is weighted by how often it occurs. Symbols follow the conventions of [Appendix A](./A_notation.md); the ones used throughout this chapter are:

- $N$: the number of draws, which you choose.
- $X_1,\ldots,X_N$: the draws, and $g(X_1),\ldots,g(X_N)$ the **recorded values**.
- $\mu$: the true expectation, unknown and the object of the calculation.
- $\hat\mu_N$: the **estimate** of $\mu$ computed from $N$ draws. One complete computation of $\hat\mu_N$ is a **run**.
- $\sigma_g^2 = \mathrm{Var}(g(X))$: the true variance of one recorded value, which sets the size of the sampling error.
- $s_g$: the sample standard deviation of the recorded values, used to estimate $\sigma_g$.

## Core ideas

Throughout this section the draws $X_1,\ldots,X_N$ are **independent and identically distributed (IID)** with density $f$, and the recorded values have finite variance, $0<\sigma_g^2<\infty$. We need independence for the error formula below to hold, and finite variance for it to have physical meaning. Sampling schemes that produce correlated draws, previewed in Exercise 6, need a different error analysis. Before applying any error formula, you should always check the assumptions behind the process that generated your samples.

### The Monte Carlo estimator

The Monte Carlo estimate of $\mu$ is the sample mean of the recorded values:

$$
\boxed{\hat\mu_N = \frac{1}{N}\sum_{i=1}^N g(X_i).}
$$

Since each $g(X_i)$ is a random variable, $\hat\mu_N$ is itself a random variable too. Repeat the estimation with a batch of fresh draws and you get a different estimate $\hat\mu_N$. Everything else in this section characterizes how those estimates are distributed around $\mu$. We will proceed in three steps. The law of large numbers says they converge to $\mu$. The central limit theorem says how they scatter around $\mu$ at finite $N$: approximately as a Gaussian. The standard deviation of that Gaussian is the standard error, the quantity you actually need for your simulation budget allocation.

### Convergence and the Law of Large Numbers

As $N$ grows, the sample mean of IID values approaches their expectation. This is the **law of large numbers (LLN)**, reviewed in [Appendix A](./A_notation.md):

$$
\hat\mu_N \to \mu \qquad \text{as} \qquad N\to\infty.
$$

It guarantees that, given enough samples, the estimator computes the right thing. It says nothing about *how many* draws are enough, which is the question of practical importance. Answering it requires knowing how the estimates are distributed at finite $N$.

### The distribution of the estimator $\hat\mu_N$

Imagine repeating the run many times, each repetition giving a new $\hat\mu_N$. For large $N$ the **central limit theorem (CLT)** says these estimates are approximately Gaussian:

$$
\hat\mu_N \;\overset{d}{\approx}\;
\mathcal{N}\!\left(\mu,\frac{\sigma_g^2}{N}\right).
$$

The Gaussian is centered on $\mu$, so the estimator is *unbiased*, and its variance shrinks as $1/N$. The Gaussian shape immediately gives the coverage rules: about 68% of runs land within one standard deviation of $\mu$ and about 95% within two. This is a large-sample approximation, not a statement about any particular run. When $g(X)$ is highly skewed, as it is for a rare event, $N$ may need to be very large before the approximation is trustworthy.

### The standard error

One could be tempted to take the standard deviation $\sigma_g/\sqrt N$ of that Gaussian, the typical distance between one run's estimate and the true $\mu$, and use it as a measure of the estimation error. Not only is this exactly the right thing to do, but the formula holds for *any* $N$, not just in the Gaussian limit of the central limit theorem.

To see why, note that variance arithmetic gives the same result directly. The recorded values are independent, so the variance of their sum is $N\sigma_g^2$. Dividing the sum by $N$ divides the variance by $N^2$, leaving $\sigma_g^2/N$. Therefore, this formula for the standard deviation of $\hat\mu_N$ is exact for IID draws with finite variance at every $N$. Pretty cool.

This quantity is usually called the **standard error** (SE) of $\hat\mu_N$:

$$
\boxed{\mathrm{SE}(\hat\mu_N)=\frac{\sigma_g}{\sqrt N}.}
$$

You can check that the formula makes sense in two limiting cases. At $N=1$ the standard error equals $\sigma_g$, the spread of a single recorded value. If $g$ is constant, then $\sigma_g=0$ and a single draw gives the exact expectation. In practice $\sigma_g$ is unknown, and we need to estimate it from the same recorded values used to compute the mean, as Worked Example 2 shows.

The SE formula also gives the recurring rule: **error $\propto 1/\sqrt N$**. Halving the standard error takes four times as many draws, and reducing it tenfold takes a hundred times as many. The exponent does not depend on the dimension of $X$, though $\sigma_g$ and the cost of one draw may. The $1/\sqrt N$ rate alone does not fix a budget: you also need the numerator, since an $N$ that is generous for one integrand can be hopeless for another.

> **Aside: reducing variance.** More draws are only one way to shrink an error bar. Sometimes you can rewrite the calculation so that you average a different random quantity with the same expectation and a smaller $\sigma_g$. This is called **variance reduction**. Control variates, antithetic variates, and importance sampling are examples of this technique. The references in Further reading develop them.

### Estimating a probability

A very common Monte Carlo calculation is that of estimating a probability. Suppose you want $p=\mathbb{P}(X\in A)$ for some event $A$. Take $g$ to be the **indicator function** $g(X)=\mathbb{1}\{X\in A\}$, which records $1$ if the sampling outcome corresponds to your event of interest and $0$ otherwise. Then $\mathbb{E}[g(X)]=p$, and $\hat\mu_N$ is the fraction of hits, written $\hat p_N$. A $0/1$ variable has variance $\sigma_g^2=p(1-p)$, so the general formula becomes

$$
\mathrm{SE}(\hat p_N)=\sqrt{\frac{p(1-p)}{N}}.
$$

This is the Bernoulli sample mean of Chapter 2. At $p=0$ or $p=1$ every draw agrees and the error vanishes, while the largest absolute standard error occurs at $p=1/2$. Estimating an area is the same calculation: sample uniformly from a region of known area, record whether each point lands in the target, and scale the hit fraction by the known area. Worked Example 1 does this for $\pi$.

The trap with small probabilities is that a small *absolute* error can still be large compared with $p$ itself. In our case and for $p>0$, the **relative standard error** is

$$
\frac{\mathrm{SE}(\hat p_N)}{p}
=\sqrt{\frac{1-p}{pN}}
\approx\frac{1}{\sqrt{pN}}\qquad(p\ll1).
$$

The product $pN$ is the expected number of hits. As $p\to0$ at fixed $N$, the absolute error shrinks while the relative error grows without bound. For $p=10^{-6}$, a relative standard error of $10\%$ needs about $100$ expected hits, or $N\approx10^8$ draws. If you expect your estimated probability to be small (i.e. you are looking at *rare events*), budget the number of simulations by the expected hit count, not just by the total number of draws.

### What the error bar tells you

The standard error measures how much the estimate fluctuates around the expectation *under the distribution you sample from*. That makes it a tool for **verification**: checking that a calculation computes the intended mathematical quantity. Comparing an estimate with a known answer, as Worked Example 1 does with $\pi$, is one such check. The error bar on its own does not check that the code implements the intended model.

No amount of sampling can establish whether a queue really has exponential service times or whether a stock-price model describes observed returns. That is **validation**, and it needs evidence from outside the simulation. This is Chapter 1's distinction again: more draws make a statement about the model more precise, while comparison with observations tests whether the statement is true of the world. A Monte Carlo error bar covers sampling noise. It does not cover bugs, approximations in the equations, uncertainty in fitted parameters, or wrong modeling assumptions.

## Worked example 1: estimating $\pi$ by darts

How can you estimate $\pi$ by Monte Carlo? Inscribe a quarter-circle of radius $1$ inside the unit square $[0,1]^2$. The square has area $1$ and the quarter-circle has area $\pi/4$, so a dart thrown uniformly at the square lands inside the quarter-circle with probability $\pi/4$. Estimate that probability by counting hits, then multiply by $4$.

```{code-cell} python
import numpy as np

def estimate_pi(N, rng):
    pts = rng.uniform(0, 1, size=(N, 2))
    inside = (pts[:, 0]**2 + pts[:, 1]**2) < 1.0
    return 4 * inside.mean()

rng = np.random.default_rng(seed=0)
print(estimate_pi(10_000, rng))    # 3.1484
print(estimate_pi(1_000_000, rng)) # 3.14106
```

The runs give $3.1484$ for $N=10^4$ and $3.14106$ for $N=10^6$. Both are close to $\pi$, but how close should we expect them to be?

### How fast does it converge?

Each dart is a Bernoulli trial with hit probability $p=\pi/4$. Multiplying the hit fraction by four also multiplies its standard error by four:

$$
\mathrm{SE}(\hat\pi_N)
=4\sqrt{\frac{(\pi/4)(1-\pi/4)}{N}}
\approx\frac{1.64}{\sqrt N}.
$$

At $N=10^4$, the standard error is about $0.016$, while the observed error is about $0.007$. At $N=10^6$, they are about $0.0016$ and $0.0005$. Both discrepancies happen, by chance, to be smaller than one standard error.

You can also work backwards from a target error to a sampling budget. Setting $1.64/\sqrt N$ equal to $0.1$, $0.01$, or $0.001$ gives roughly $270$, $27{,}000$, or $2.7$ million darts. These are targets for the standard error, not guarantees of correctly rounded digits. Exercise 2 adds a confidence level to the budget. [The code](./code/03_monte_carlo/estimate_pi.py) for the full dart example also shows the convergence curves visually.

## Worked example 2: estimating the error from the sample

How do you report uncertainty when you don't have a known answer to compare against? Consider the integral $I=\int_0^1 e^{-x^2}\,dx$. We first compute the estimate and its error bar, and only afterward compare with the known value.

Draw $U\sim\mathrm{Uniform}(0,1)$: its density is one on the integration interval, so $\mathbb{E}[e^{-U^2}]=I$. We then calculate $g(U_i)=e^{-U_i^2}$ and average the recorded values. Since we don't have access to the true $\sigma_g$, we estimate it by computing the sample variance $s_g^2$. Dividing its square root by $\sqrt N$ gives the estimated standard error:

$$
s_g^2=\frac{1}{N-1}\sum_{i=1}^N\bigl(g(U_i)-\hat\mu_N\bigr)^2,
\qquad
\widehat{\mathrm{SE}}(\hat\mu_N)=\frac{s_g}{\sqrt N}.
$$

The $N-1$ denominator gives the usual unbiased estimate of the variance of the (unknown) distribution of $g(U_i)$. Remember to keep the two scales apart: $s_g$ describes the spread of the recorded values, while $s_g/\sqrt N$ describes the spread of their average.

The cell prints the estimate as plus or minus two estimated standard errors:

```{code-cell} python
import numpy as np

rng = np.random.default_rng(seed=1)
N = 100_000
U = rng.uniform(0, 1, size=N)
g = np.exp(-U**2)
I_hat = g.mean()
se = g.std(ddof=1) / np.sqrt(N)

print(f"estimate: {I_hat:.4f} +/- {2*se:.4f}  (2 sigma band)")
# estimate: 0.7468 +/- 0.0013  (2 sigma band)
```

The result is $0.7468\pm0.0013$. Under the Gaussian approximation of the central limit theorem, intervals constructed this way contain the true expectation in about 95% of repeated runs.

Now we can check. The integral has no closed-form solution, but it defines the **error function** $\mathrm{erf}(z)=\tfrac{2}{\sqrt\pi}\int_0^z e^{-t^2}\,dt$. This is a standard special function, tabulated to high precision in SciPy and every major numerical library. Rearranging, we get $I=\tfrac{\sqrt\pi}{2}\,\mathrm{erf}(1)=0.74682\ldots$, which lies inside the reported interval. The [numerical checks](./code/03_monte_carlo/chapter_checks.py) reproduce both the cell and this comparison.

**NOTE: The estimate and its error bar come from the same sample.** This works well here because the integrand is bounded and smooth, so a uniform sample sees all of it. If most of an integral comes from a narrow peak, a uniform sample may miss the peak and underestimate both the integral and its uncertainty. That is the rare-event trap in a different form: a small $s_g$ computed from a sample that never saw the peak is not evidence that $\sigma_g$ is small.

**Importance sampling** corrects for this by weighting each recorded value by the reciprocal of its sampling density (see Further readings). The same recipe, uniform draws and a sample-based error bar, extends unchanged to integrals over $[0,1]^d$ in any dimension, a point the Intuition section returns to.

## Intuition

> **Why $1/\sqrt N$ and not $1/N$?** The variance of a sum of $N$ IID values grows like $N$, so the variance of their mean shrinks like $N/N^2=1/N$. The error scale is the standard deviation, the square root of the variance, which gives $1/\sqrt N$. The same arithmetic produced the $1/\sqrt n$ standard errors of Chapter 2 and will produce the $\sqrt t$ spreading of random walks in Chapter 5.

> **Why does Monte Carlo help in high dimensions?** A regular grid of $N$ points in $d$ dimensions has only $N^{1/d}$ points per axis. For a smooth integrand and a second-order quadrature rule, the error scales as the grid spacing squared, or $N^{-2/d}$. At $d=50$ that exponent is $-0.04$, against Monte Carlo's $-1/2$ in every dimension. The comparison is between rates only. The variance $\sigma_g$, the smoothness of the integrand, and the cost of one draw still decide which method is practical for a given problem.

> **What does "many samples" mean in practice?** Nothing on its own. The relative standard error is $\sigma_g/(|\mu|\sqrt N)$ for $\mu\ne0$. If $\sigma_g/|\mu|\approx1$, then $10^4$ draws give about 1% relative error and $10^6$ give about 0.1%. If $\sigma_g/|\mu|$ is $100$, the same draws give 100% and 10%. Near $\mu=0$ relative error is a poor target, and an absolute tolerance is the right one. A sample size is large or small only relative to the variability of $g$ and the accuracy you need.

> **My error bar is tiny, so my answer is right?** The calculated answer is precise under your sampling assumptions. That is all the error bar says. Whether the code computes the intended quantity is a separate question. Whether the quantity says anything true about the world is another, answered by validation against outside data. More draws help with neither.

> **Is a Monte Carlo average an MLE?** Sometimes the two coincide: the hit fraction is the Bernoulli MLE for $p$, and the sample mean is the Gaussian MLE for the mean. In general they need not. The Monte Carlo estimator is justified by the law of large numbers and the central limit theorem for IID values with finite variance, and it needs no likelihood model for those values.

## Connections

- **Builds on:** Chapter 1 for verification versus validation, which this chapter sharpens: comparing a Monte Carlo estimate with a closed form is verification, and no amount of simulation validates the model's own assumptions. Chapter 2 for the Bernoulli sample mean and its standard error, which reappear here as the hit-counting estimator. Appendix A for the law of large numbers, the central limit theorem, and variance arithmetic.
- **Used in:** Chapter 4, where a tournament simulation is Monte Carlo over an enormous discrete sample space. Chapters 6 and 7, where averages over simulated geometric Brownian motion paths estimate expectations and option payoffs. Chapter 9, where outbreak probabilities of stochastic SIR models are estimated by counting hits.
- **Related but not required:** variance reduction (importance sampling, control variates, antithetic variates) averages a different quantity with the same expectation and smaller $\sigma_g$. Quasi-Monte Carlo replaces random draws with deliberately spread-out points. Markov chain Monte Carlo produces dependent draws when independent sampling is impractical; Exercise 6 previews what dependence changes.

Whenever a later chapter averages simulated outcomes, first identify what one draw is and whether the draws are independent. Only then does this chapter's error formula apply.

## Exercises

1. **Conceptual.** A classmate says: "Monte Carlo error scales like $1/\sqrt N$, so I will need a quadrillion samples to reach an accuracy of $10^{-7}$." What is wrong with taking the formula that literally?

2. **Derivation.** You want a Monte Carlo estimate of $\pi$ accurate to $\pm 10^{-3}$ with 95% confidence. Use the standard error from Worked Example 1 to find the required $N$, taking 95% to mean two standard errors. Repeat for $\pm 10^{-6}$, and say in one sentence why nobody computes $\pi$ this way.

3. **Computational.** Estimate $\int_0^\pi \sin(x)\, dx$ by Monte Carlo with $N = 10^6$ (the true value is $2$). Report the estimate with a two-standard-error band computed from the same sample, and check whether the true value falls inside. Which part of your check was possible only because the true value is known, and what would you report without it?

4. **Computational.** Repeat the dart-throwing estimate of $\pi$ $1000$ times with $N = 10{,}000$ darts each, and plot a histogram of the $1000$ values of $\hat\pi$. Compare their mean and standard deviation with the predictions of Worked Example 1. Is the histogram visibly Gaussian?

5. **Modeling judgment.** A colleague simulates their epidemic model $10^6$ times and reports: "the probability of a major outbreak is $3.21\% \pm 0.02\%$, so I have validated it to three digits." In this chapter's vocabulary: what does the $\pm 0.02\%$ cover, what did the million runs verify, and what would it take to *validate* the $3.21\%$?

6. **Computational.** In the 0/1 *knapsack problem* you have $n$ items, item $i$ has a positive integer weight $w_i$ and value $v_i$, and you must choose a subset of maximum total value whose total weight does not exceed a capacity $W$. Generate an instance with $n=50$ items, integer weights drawn uniformly from $1$ to $49$, integer values drawn uniformly from $1$ to $99$, and capacity $W=200$. Represent a subset as a vector $x\in\{0,1\}^n$.

   Run the following random search for $10{,}000$ steps. Start from the empty subset $x=0$. At each step, pick one item at random, flip $x_i$ from $0$ to $1$ or back, and accept the move if the new subset is feasible, meaning its total weight is at most $W$. Keep track of the best feasible value seen so far and report it.

   Then answer: Can every feasible subset be reached from every other by such moves? Does the acceptance rule favor valuable subsets? Now change the acceptance rule to the simplest value-aware one: accept a feasible move that raises the total value, and accept a feasible move that lowers it by $\Delta v$ with probability $e^{-\Delta v/T}$, with $T=20$. Compare the best values found by the two rules on the same instance and explain why neither run proves optimality. Finally, what happens to the IID assumption of this chapter? A seeded implementation is in [the companion script](./code/03_monte_carlo/knapsack_mcmc.py).

:::{admonition} Solutions
:class: dropdown

**1.** The formula is $\sigma_g/\sqrt N$, and a budget needs the numerator $\sigma_g$, an error target, and a confidence level. A nearly constant integrand needs few draws. A heavy-tailed integrand can have a large or even infinite variance, in which case the formula may not apply at all. A rare-event indicator has a *small* variance but a large relative error. Even the arithmetic is off: for $\sigma_g=1$, a standard error of $10^{-7}$ takes $10^{14}$ draws, not $10^{15}$. In practice, estimate $\sigma_g$ from a pilot run, remembering that a pilot can miss rare contributions.

**2.** From Worked Example 1, $\mathrm{SE}(\hat\pi_N) \approx 1.64/\sqrt N$. For $\pm 10^{-3}$ at two standard errors, $2 \times 1.64/\sqrt N \le 10^{-3}$ gives $N \ge 3280^2 \approx 1.1 \times 10^7$. For $\pm 10^{-6}$, $N \ge (3.28 \times 10^6)^2 \approx 1.1 \times 10^{13}$, about ten trillion darts. Deterministic series compute $\pi$ to that precision in microseconds.

**3.** Change variables so the sample is uniform on $[0,1]$: with $x=\pi U$, the recorded value is $g(U) = \pi \sin(\pi U)$, the factor $\pi$ being the length of the original interval. The seeded run of [the companion script](./code/03_monte_carlo/integrate_sin.py) with $N = 10^6$ gives $2.0003 \pm 0.0019$, which contains $2$. The comparison with $2$ is verification and is possible only because the answer is known. One interval containing the truth is weak evidence on its own. Without the known answer you would still report $2.0003 \pm 0.0019$ as an approximate 95% interval: the error estimate survives even when the error check does not.

**4.** The mean of the $1000$ estimates should be close to $\pi$ and their standard deviation close to $1.64/\sqrt{10^4} \approx 0.0164$. The seeded run of [the companion script](./code/03_monte_carlo/pi_clt_demo.py) gives $3.14160$ and $0.0165$. The histogram is roughly bell-shaped, with bin-to-bin fluctuations. The agreement in spread confirms the standard error formula, and the bell shape is the central limit theorem at work, which is what justifies reading two standard errors as a 95% band.

**5.** The quoted $\pm 0.02\%$ matches *one* estimated standard error: $\sqrt{0.0321(1-0.0321)/10^6}\approx0.000176$, or $0.018$ percentage points, which rounds to the quoted $0.02$. The [numerical checks](./code/03_monte_carlo/chapter_checks.py) reproduce this. So the $\pm 0.02\%$ covers Monte Carlo sampling noise under the model, as a one-standard-error band rather than a 95% one, and a report should say which convention it uses.

The million runs establish sampling precision. They do not verify that the code implements the intended model, and they do not validate the outbreak probability. Verification needs known limiting cases or an independent implementation. Validation needs outbreak data that were not used to tune the model, with a matching definition of "major outbreak" under comparable conditions. That comparison carries its own uncertainty, set by the amount and quality of the data, and whether it can resolve three digits is a separate calculation.

**6.** On the seeded instance with $50$ items, the [companion script](./code/03_monte_carlo/knapsack_mcmc.py) finds a best value of $1185$ for the blind walk and $1375$ for the value-aware walk at $T=20$. The exact optimum, computed by dynamic programming, is $1392$.

*Reachability.* Every feasible subset can reach every other: remove items one at a time until the knapsack is empty, then add the items of the destination subset one at a time. Since weights are positive, every intermediate subset is feasible.

*Acceptance.* Reachability does not mean a short walk finds the best subset. The blind rule ignores value entirely: it accepts a feasible move that lowers the value as readily as one that raises it, so it drifts among mediocre subsets and its best value stalls early.

*Comparison.* The value-aware rule is a **Metropolis** acceptance step. It climbs whenever it can and occasionally steps down, which lets it leave a local optimum instead of stopping at the first subset no single flip can improve. On this instance it closes most of the gap to the optimum in the same $10{,}000$ steps. The temperature matters: a very small $T$ reduces the rule to pure hill climbing, which gets trapped, and a very large $T$ recovers the blind walk. Neither run certifies optimality, since the walk reports only the best value it happened to visit. For an instance this small, dynamic programming gives the exact optimum to compare against, and the value-aware walk stops short of it.

*IID.* Successive subsets differ by one item, so the states of the walk are strongly dependent. Averages over such a trace need a correlation-aware error analysis, and the best value seen is not a sample mean at all. An optimization trace does not inherit this chapter's error bar.
:::

## Further reading

- Glasserman, *Monte Carlo Methods in Financial Engineering* (2003), Chs. 1–4 — exhaustive
  on variance reduction with finance applications. ISBN 9780387004518 · [Publisher / DOI](https://doi.org/10.1007/978-0-387-21617-1) ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Monte%20Carlo%20Methods%20in%20Financial%20Engineering%20Glasserman&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- MacKay, *Information Theory, Inference and Learning Algorithms*, Ch. 29 (Monte Carlo methods) — clearer high-level intuition than most textbooks. **Free in full** from the
  author, with Cambridge's permission:
  [inference.org.uk](https://www.inference.org.uk/itila/book.html) ·
  [PDF](https://www.inference.org.uk/itprnn/book.pdf) · ISBN 9780521642989 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,9780521642989&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- For the original story: Metropolis, "The Beginning of the Monte Carlo Method",
  *Los Alamos Science* 15 (1987), pp. 125–130. **Free** from the US Department of Energy:
  [OSTI](https://www.osti.gov/biblio/1054744) ·
  [PDF](https://www.osti.gov/servlets/purl/1054744) (the whole special issue on Ulam;
  the article begins at printed p. 125) · Report LA-UR-88-9067 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,The%20Beginning%20of%20the%20Monte%20Carlo%20Method&tab=Everything&search_scope=Everything&vid=01HVD_INST:HVD2&offset=0).
