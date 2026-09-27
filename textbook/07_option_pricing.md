---
kernelspec:
  name: python3
  display_name: Python 3
---

# Chapter 7: Option Pricing

> An option is the right to buy or sell a stock later at a price fixed now, a form of insurance against price moves, and its seller can cancel the risk it carries by holding a continually adjusted number of shares; the fair price is then the cost of doing that, which obeys Chapter 5's diffusion equation run backward from the payout, so today's price is the payout smoothed by a Gaussian whose width grows with the volatility and the time remaining.

:::{note} Running the code
The Python cells on this page run **in your browser**. Click the **power icon** at the top of the page to activate the kernel, then run — or edit — any cell. Packages (NumPy, SciPy, …) load automatically the first time you import them (a few seconds).
:::

## Motivation

When you insure a house, you pay a fixed amount today, the **premium**, and the insurer pays you if the house floods. You accept a small certain loss to avoid a large uncertain one. The insurer has to choose the premium well. If it charges too little, then across many policies it pays out more than it collects; if it charges too much, customers go to a competitor.

The same kind of contract exists for prices. Someone who owns a stock at $\$100$ and cannot afford to see it fall below $\$90$ can buy the right to sell it at $\$90$ in a year. Someone who must buy the stock in a year can buy the right to pay no more than $\$110$ for it. These contracts are **options**. What premium should their seller charge?

The insurer's answer is the expected payout plus a margin. For a stock, that needs the probabilities of its future moves, including its expected growth rate $\mu$, and Chapter 6 showed that data barely determine $\mu$: five years of daily US stock prices leave a drift of $0.11$ only 1.4 standard errors from zero.

The option seller has a tool the flood insurer lacks: the stock itself can be bought and sold. A seller who has promised to pay more when the stock rises can hold shares, which also gain when it rises. This offsetting position is a **hedge**. With the right number of shares, adjusted as the price moves, the gains and losses cancel exactly, and the seller carries no risk. The fair premium is then the cost of running the hedge. That cost depends on how much the stock fluctuates, $\sigma$, and not on which way it tends to go, $\mu$.

This chapter turns that idea into a formula. Hedging and Chapter 6's Itô's lemma give an equation for the option's value, and a change of variables turns it into Chapter 5's diffusion equation, the same equation that describes heat spreading along a rod. The payout at expiration is the starting profile. Going back in time from expiration, it spreads out, so today's price is the payout smoothed by a Gaussian. Worked Example 1 **verifies** a Monte Carlo pricer against the resulting Black–Scholes formula. Example 2 reads a volatility off a market price, which is how market quotes test the model (Exercise 5 runs the test). Example 3 measures how well the hedge works when it is adjusted only once a day.

## Setup & notation

An **option** is a contract that gives its holder the right, but not the obligation, to trade one share of a stock at a price fixed today:

- **Call and put.** A **call** is the right to *buy* the share; a **put** is the right to *sell* it.
- **Strike and expiration.** The **strike** $K$ is the fixed price, and the **expiration** $T$ is the date the right can be used. Using it is **exercising** the option. A **European** option can be exercised only at $T$, and it is the only kind treated here; an American option can be exercised at any time before $T$.
- **Premium.** What the holder pays the seller today for the right. The holder can lose at most the premium; the seller takes on the obligation to pay, and with it the risk.

Other market terms, used throughout:

- **Long and short.** Holding a share is a *long* position: it gains when the price rises. **Selling short** means borrowing a share, selling it now at $S_0$, and later buying one back at $S_T$ to return. It gains $S_0 - S_T$, so it profits when the price falls. A short position in $\Delta$ shares is worth $-\Delta S$.
- **Risk-free rate** $r$. The interest rate on a loan that is certain to be repaid, per year and continuously compounded. A dollar deposited today is worth $e^{rT}$ at time $T$, so a dollar paid at $T$ is worth $e^{-rT}$ today. Converting a future amount to today's value this way is **discounting**.
- **Arbitrage.** A trade that costs nothing, can never lose, and sometimes gains. We assume none exists, because traders would make it at once and their trades would move the prices until it disappeared. The consequence used repeatedly: **two holdings with the same payout in every outcome must have the same price today.**

The derivation assumes:

- **The stock follows geometric Brownian motion** (Chapter 6), $dS_t = \mu S_t\,dt + \sigma S_t\,dW_t$, with constant $\sigma$ and no **dividends**, the cash a company pays its shareholders, which lowers the share price when paid. Worked Example 2 and Exercise 5 test the constant $\sigma$.
- **A constant risk-free rate $r$**, at which anyone can borrow or lend.
- **Frictionless, continuous trading.** Shares can be bought or sold short in any amount, at any instant, at no cost. Worked Example 3 trades daily instead; Exercise 6 asks about costs.

New symbols in this chapter:

- $K$, $T$: the strike, and the expiration in years from today.
- $\mu$: the stock's drift, as in Chapter 6.
- $C$, $P$: today's price (premium) of a call and of a put.
- $V(S, t)$: the value of an option when the stock is at $S$ at time $t$.
- $\Delta$: the **hedge ratio**, the number of shares held per option.
- $\tau = T - t$: the time left until expiration. (Chapter 5 used $\tau$ for a step duration; here it means only this.)
- $\Phi(x)$: the standard Gaussian CDF, as in Chapter 6. Option-pricing texts write it $N(x)$.

## Core ideas

### Calls and puts

At expiration, a call is worth exercising only if $S_T > K$: the holder buys at $K$ a share worth $S_T$. A put is worth exercising only if $S_T < K$. Otherwise the holder lets the right lapse. The payouts are
$$
\text{call: } \max(S_T - K,\ 0), \qquad \text{put: } \max(K - S_T,\ 0).
$$
Each is zero on one side of the strike and grows one-for-one with the price on the other: a ramp with a corner at $K$. An option is **in the money** when its payout would be positive now.

The put is the stock owner's insurance from the Motivation: a share plus a put with $K = 90$ is worth $\max(S_T, 90)$ at expiration, never less than $\$90$. The seller of a call has no limit on what they may owe, since $S_T - K$ has no upper bound. **The payout is a known function of $S_T$, so pricing an option means deciding what that uncertain payout is worth today**, and the seller carries the risk.

### Hedging and the Black–Scholes equation

The idea is to build a portfolio containing the option that is risk-free as a whole, so that we know for certain what it is worth. To do that, we offset the option with a short position in the same stock. At expiration, if the stock finishes above the strike, the short position loses as the stock rises while the call pays $S_T-K$; if the stock finishes below the strike, the call expires worthless while the short position gains as the stock falls. Those terminal outcomes do not by themselves make the portfolio risk-free. Before expiration, the call's market value changes with the stock price, and we must choose the short position to cancel that local change at every instant. The seller of the call holds the mirror image, short the call and long the shares, and the same argument applies (Worked Example 3).

So hold one call and $\Delta$ shares short. The portfolio's value, and its change over an instant $dt$ with $\Delta$ held fixed, are
$$
\Pi = V - \Delta S, \qquad d\Pi = dV - \Delta\,dS .
$$
The share's change $dS$ is given by the stock's model; what we still need is the option's change $dV$. Itô's lemma from [Chapter 6](./06_gbm.md) gives it as a Taylor expansion kept to second order in $dS$:
$$
dV = \frac{\partial V}{\partial t}\,dt + \frac{\partial V}{\partial S}\,dS + \frac12\,\frac{\partial^2 V}{\partial S^2}\,(dS)^2 ,
\qquad (dS)^2 = \sigma^2 S^2\,dt ,
$$
where the last equality is Chapter 6's rule $(dW_t)^2 = dt$ applied to $dS = \mu S\,dt + \sigma S\,dW_t$: the $dS$ term is random, but its square is not. Substituting into $d\Pi$,
$$
d\Pi = \left[\frac{\partial V}{\partial t} + \frac12\sigma^2 S^2\,\frac{\partial^2 V}{\partial S^2}\right] dt + \left(\frac{\partial V}{\partial S} - \Delta\right) dS .
$$
All the randomness is in $dS$, and choosing
$$
\Delta = \frac{\partial V}{\partial S}
$$
removes it: the option and the short position now move together exactly. The drift contribution $\mu S\,dt$ is part of $dS$, so eliminating the entire $dS$ term eliminates $\mu$ as well. **Hedging cancels the stock's moves, and the stock's expected return goes with them, so $\mu$ cannot appear in the price.** Because $\partial V/\partial S$ changes with $S$ and $t$, the balance holds only over an instant, and $\Delta$ must be readjusted continually.

The remaining change is known in advance, so the position is riskless, and a riskless position must earn the risk-free rate: if it earned any other rate, combining it with a loan or deposit at $r$ would be an arbitrage. So
$$
d\Pi = r\Pi\,dt = r\left(V - S\,\frac{\partial V}{\partial S}\right) dt ,
$$
and equating this with the hedged $d\Pi$ above and rearranging gives the **Black–Scholes equation**:
$$
\boxed{\ \frac{\partial V}{\partial t} + \frac12\sigma^2 S^2\,\frac{\partial^2 V}{\partial S^2} + rS\,\frac{\partial V}{\partial S} - rV = 0\ }
$$
It holds before $T$, and the payout gives $V$ at $T$. Each term has a physical reading:

- $\tfrac12\sigma^2 S^2\,\partial^2 V/\partial S^2$ is **diffusion**: the stock's fluctuations spread the value out, in proportion to the curvature of $V$. Where $V$ is a straight line, it contributes nothing.
- $rS\,\partial V/\partial S$ is **drift** at the rate $r$, not $\mu$.
- $-rV$ is **decay**: discounting, which lowers the value of money received later.

The equation passes two checks. A share, $V = S$, gives $rS - rS = 0$. A loan repaying $K$ at $T$ (a **bond**), $V = K e^{-r(T-t)}$, gives $rV - rV = 0$.

The derivation needs two idealizations: the hedge is adjusted at every instant, and $(dW_t)^2$ was replaced by $dt$, which Chapter 6 justified as an average over many short intervals. **If the hedge is adjusted only at a finite number of dates, the difference between $(\Delta W)^2$ and $\Delta t$ gives the leading contribution to the hedging error in each short interval**; Worked Example 3 measures the full error.

### The Black–Scholes equation as a diffusion equation

Four changes of variable turn the equation into Chapter 5's diffusion equation:

- **Time to expiration.** $\tau = T - t$, so the payout becomes the *starting* condition at $\tau = 0$ and the equation runs forward in $\tau$.
- **Log price.** $x = \log S$. The chain rule gives $S\,\partial V/\partial S = \partial V/\partial x$ and $S^2\,\partial^2 V/\partial S^2 = \partial^2 V/\partial x^2 - \partial V/\partial x$, so the coefficients become constants:
$$
\frac{\partial V}{\partial \tau} = \frac12\sigma^2\,\frac{\partial^2 V}{\partial x^2} + \left(r - \tfrac12\sigma^2\right)\frac{\partial V}{\partial x} - rV .
$$
The drift $r - \tfrac12\sigma^2$ is Chapter 6's log-price drift with $r$ in place of $\mu$.
- **Discounting.** $V = e^{-r\tau}U$ removes the $-rV$ term.
- **Moving frame.** $y = x + (r - \tfrac12\sigma^2)\tau$ removes the drift term, leaving
$$
\frac{\partial U}{\partial \tau} = \frac12\sigma^2\,\frac{\partial^2 U}{\partial y^2},
$$
the diffusion equation with $D = \sigma^2/2$.

At $\tau = 0$ the starting profile is the payout, $U(y, 0) = \max(e^y - K, 0)$. Chapter 5 solved the diffusion equation for any starting profile by superposition: each point of $U(y, 0)$ spreads into the Gaussian fundamental solution $G_0$, here with variance $2D\tau = \sigma^2\tau$, and the solution sums these Gaussians:
$$
U(y, \tau) = \int_{-\infty}^{\infty} G_0(y - y', \tau)\,\max\!\left(e^{y'} - K,\ 0\right) dy' .
$$
A single Gaussian would not do: it solves the problem whose starting profile is a spike at one point, while this one starts from the whole ramp. As a check, when $\tau \to 0$ the Gaussian narrows to a spike and the integral returns the payout itself, as the starting condition requires. **The option's value is its payout, shifted in log price by $(r - \tfrac12\sigma^2)\tau$, blurred by a Gaussian of width $\sigma\sqrt{\tau}$, and discounted.** More volatility or more time means a wider blur and a higher price.

At $S = K = 100$, $\tau = 1$, $r = 0.05$ and $\sigma = 0.20$, the integral gives $10.4506$ ([companion script](./code/07_option_pricing/mc_vs_bs.py)), the value of the closed-form formula below.

### Expected payout

As a function of $y'$, the kernel $G_0(y - y', \tau)$ is a Gaussian probability density with mean $\log S + (r - \tfrac12\sigma^2)\tau$ and variance $\sigma^2\tau$. By Chapter 6, that is the distribution of $\log S_T$ for a stock that follows geometric Brownian motion with drift $r$ in place of $\mu$. An integral of a function against a probability density is that function's average, so $U$ is the expected payout of this stock, and $V = e^{-r\tau}U$ discounts it. The price we want is the call's value today: $t = 0$, so $\tau = T$ and $S = S_0$, and we write it $C = V(S_0, 0)$:
$$
\boxed{\ C = e^{-rT}\,\mathbb{E}\!\left[\max(S_T - K,\ 0)\right], \qquad S_T = S_0\exp\!\left[\left(r - \tfrac12\sigma^2\right)T + \sigma\sqrt{T}\,Z\right],\ Z \sim \mathcal{N}(0, 1).}
$$
This is what Chapter 3's Monte Carlo estimates: draw many $Z$, average the payouts, discount. Worked Example 1 does it. The drift $r$ is not a forecast of the stock, whose expected growth is still $\mu$; it appears because hedging removed $\mu$ from the equation, leaving $r$ as the only growth rate.

Here is the insurer's answer from the Motivation, corrected: **the fair premium is an expected payout, discounted, but computed as if the stock grew at $r$**, because that is what the hedge costs. Averaging with the real drift $\mu$ is the trap.

### The Black–Scholes–Merton formula

The integral can be done in closed form:
$$
\boxed{\ C = S_0\, \Phi(d_1) \;-\; K e^{-rT}\, \Phi(d_2)\ }, \qquad
d_1 = \frac{\log(S_0/K) + (r + \tfrac12\sigma^2) T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T} .
$$
The inputs are $S_0$, $K$, $T$, $r$ and $\sigma$, and nothing else.

The same calculation with the put's payout gives
$$
P = K e^{-rT}\, \Phi(-d_2) - S_0\, \Phi(-d_1).
$$
The put is the call's mirror image: the discounted strike, weighted by the probability $\Phi(-d_2)$ of finishing below $K$, minus a short position in $\Phi(-d_1)$ shares.

### Reading the formula

Each factor is a probability, for a stock growing at $r$. $\Phi(d_2)$ is the probability that the call ends in the money, $S_T > K$, so the second term is the strike, paid only if the call is exercised, weighted by how likely that is and discounted. $\Phi(d_1)$ is the same probability with each outcome weighted by the share's final price, so outcomes far above the strike count for more, and $\Phi(d_1) > \Phi(d_2)$.

Limiting cases check the formula:

- **Deep "in the money"** ($S_0 \gg K$): $\Phi(d_1), \Phi(d_2) \to 1$, so $C \to S_0 - K e^{-rT}$. The call is certain to be exercised, so it is worth one share minus the strike paid at $T$.
- **Deep "out of the money"** ($S_0 \ll K$): $C \to 0$. The call is almost certain to expire unused.
- **No volatility** ($\sigma \to 0$): $C \to \max(S_0 - K e^{-rT}, 0)$. With no blur, the stock grows at $r$ for certain, and the call is worth that certain payout, discounted.
- **"At the money"** ($S_0 = K$, $r = 0$): $C = S_0\left[2\Phi(\sigma\sqrt{T}/2) - 1\right] \approx S_0\,\sigma\sqrt{T/(2\pi)}$ for small $\sigma\sqrt{T}$. This is the blur at the corner: a Gaussian of standard deviation $s$ lifts a ramp's corner by $s/\sqrt{2\pi}$, and here $s = \sigma\sqrt{T}$ in relative price. A one-year call at 20% volatility costs about $0.20 \times 0.4 = 8\%$ of the stock price.

## Worked example 1: Monte Carlo against the Black–Scholes formula

Does a Monte Carlo pricer with drift $r$ reproduce the formula, and would the comparison catch a pricer that uses $\mu$? Take $S_0 = K = 100$, $T = 1$, $r = 0.05$, $\sigma = 0.20$.

```{code-cell} python
import numpy as np
from scipy.stats import norm

def bsm_call(S0, K, T, r, sigma):
    d1 = (np.log(S0/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S0*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

def mc_call(S0, K, T, r, sigma, n_paths, rng):
    Z = rng.standard_normal(n_paths)
    ST = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    payoffs = np.exp(-r*T) * np.maximum(ST - K, 0)
    return payoffs.mean(), payoffs.std(ddof=1) / np.sqrt(n_paths)

S0, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
mc_mean, mc_se = mc_call(S0, K, T, r, sigma, 500_000, np.random.default_rng(0))
bs = bsm_call(S0, K, T, r, sigma)

print(f"BS : {bs:.4f}")
print(f"MC : {mc_mean:.4f} +/- {mc_se:.4f}   z = {(mc_mean - bs) / mc_se:+.2f}")

# BS : 10.4506
# MC : 10.4851 +/- 0.0209   z = +1.65
```

The two agree within 1.65 standard errors; noise alone lands within two about 95% of the time. This is **verification**: two computations of one model agree. It says nothing about whether markets price options this way.

A check is worth running only if it catches mistakes. Here is the trap on purpose, with $\mu = 0.10$ where $r$ belongs:

```{code-cell} python
mu = 0.10
Z = np.random.default_rng(1).standard_normal(500_000)
ST = S0 * np.exp((mu - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)    # mu where r belongs
payoffs = np.exp(-r*T) * np.maximum(ST - K, 0)
se = payoffs.std(ddof=1) / np.sqrt(payoffs.size)

print(f"MC with mu : {payoffs.mean():.4f} +/- {se:.4f}   z = {(payoffs.mean() - bs) / se:+.0f}")

# MC with mu : 13.8974 +/- 0.0239   z = +144
```

The price is a third too high and 144 standard errors off. That is the insurer's answer, the expected payout under the stock's actual drift. The check catches it because the formula contains no $\mu$, so the two computations cannot share the mistake. The [companion script](./code/07_option_pricing/mc_vs_bs.py) repeats the check at three strikes (Exercise 3).

## Worked example 2: implied volatility

A market quotes an option's price, not $\sigma$. Since $S_0$, $K$, $T$ and $r$ are known, a quoted price fixes $\sigma$: the **implied volatility** is the $\sigma$ at which the formula matches the quote. Can every quote be inverted?

```{code-cell} python
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

def bsm_call(S0, K, T, r, sigma):
    d1 = (np.log(S0/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S0*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

def implied_vol(C_market, S0, K, T, r):
    """Solve bsm_call(sigma) = C_market for sigma."""
    return brentq(lambda s: bsm_call(S0, K, T, r, s) - C_market, 1e-6, 5.0)

C_20 = bsm_call(100, 100, 1.0, 0.05, 0.20)
print(f"round trip  : {implied_vol(C_20, 100, 100, 1.0, 0.05):.6f}")
print(f"quote 12.00 : {implied_vol(12.00, 100, 100, 1.0, 0.05):.4f}")
try:
    implied_vol(4.00, 100, 100, 1.0, 0.05)
except ValueError as err:
    print(f"quote  4.00 : {err}")

# round trip  : 0.200000
# quote 12.00 : 0.2411
# quote  4.00 : f(a) and f(b) must have different signs
```

The round trip recovers $0.20$, which verifies the inversion, and $\$12.00$ implies $0.241$. The $\$4.00$ quote has no solution. A wider blur always raises the price, so as $\sigma$ goes from zero to infinity the price rises from $\max(S_0 - K e^{-rT}, 0) = \$4.88$ toward $S_0 = \$100$, and no $\sigma$ gives $\$4.00$. That quote would be an arbitrage: buy the call, sell a share short for $\$100$, and lend $\$95.12$. You keep $\$0.88$ today, and at expiration the loan repays $\$100$, which buys back the share, with the call covering any price above $\$100$. With real quotes, a price outside the bounds more often means a wrong input, such as a stale $S_0$, an ignored dividend, or an American option priced with the European formula. **Treat a failed inversion as a problem with the inputs before treating it as free money.**

Implied volatility turns each quote into a test of the model. The model has one $\sigma$, so every strike should imply the same one. Comparing them is **validation**, and real quotes fail it: implied volatility plotted against strike is curved, the **volatility smile**. For stock indices it is lopsided, a **skew**, highest for low-strike puts, which insure against large falls. This is consistent with what geometric Brownian motion leaves out: fatter tails than a Gaussian (Chapter 5's Worked Example 3), sudden falls, volatility that changes over time (Chapter 6's Worked Example 3), and buyers paying extra for crash insurance. Exercise 5 measures a smile from today's quotes.

## Worked example 3: hedging once a day

The derivation adjusts the hedge continuously. A real seller adjusts it at a finite number of dates. How much risk is left, and does $\mu$ stay out?

The seller receives $\$10.45$ for the call and buys $\Delta = \partial C/\partial S_0$ shares; differentiating the formula gives $\Delta = \Phi(d_1) = 0.637$. The shares cost $\$63.68$, so the seller borrows the missing $\$53$ at $r$. At each adjustment date they reset $\Delta$ from the formula, borrowing to buy shares or repaying with shares sold. At expiration, the shares plus the cash balance minus the call's payout is the **hedging error**, which continuous hedging would make exactly zero. The stock drifts at $\mu = 0.10$.

```{code-cell} python
import numpy as np
from scipy.stats import norm

def bsm_call(S0, K, T, r, sigma):
    d1 = (np.log(S0/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S0*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

def bsm_delta(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    return norm.cdf(d1)

def hedging_error(n_steps, mu, n_paths, rng, S0=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20):
    dt = T / n_steps
    S = np.full(n_paths, S0)
    delta = bsm_delta(S, K, T, r, sigma)
    cash = bsm_call(S0, K, T, r, sigma) - delta * S       # sell the call, buy delta shares
    for k in range(1, n_steps + 1):
        S = S * np.exp((mu - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*rng.standard_normal(n_paths))
        cash = cash * np.exp(r*dt)
        if k < n_steps:                                  # no rebalance at expiration
            new_delta = bsm_delta(S, K, T - k*dt, r, sigma)
            cash -= (new_delta - delta) * S
            delta = new_delta
    return cash + delta*S - np.maximum(S - K, 0)

rng = np.random.default_rng(0)
for n in (12, 52, 252):
    err = hedging_error(n, mu=0.10, n_paths=20_000, rng=rng)
    se = err.std(ddof=1) / np.sqrt(err.size)
    print(f"{n:>3} rebalances : mean {err.mean():+.3f} +/- {se:.3f}   SD {err.std(ddof=1):.3f}")

#  12 rebalances : mean -0.033 +/- 0.013   SD 1.883
#  52 rebalances : mean -0.008 +/- 0.007   SD 0.933
# 252 rebalances : mean -0.000 +/- 0.003   SD 0.424
```

On average the hedge recovers the payout to within $\$0.03$, under 0.4% of the price, although the stock drifts at 10% and the price used 5%. The monthly mean is 2.5 standard errors below zero. When the stock trends up, the $\Delta$ the call needs rises during the interval while the seller still holds the old, smaller one, so they are short a few shares while the stock earns $\mu - r$ above the borrowing rate; that costs a little each interval. The cost vanishes as adjustments become continuous, and with $\mu = r$ the mean is exactly zero at any frequency. The [companion script](./code/07_option_pricing/discrete_hedging.py) shows it more clearly at $\mu = 0.30$: $-0.38$ monthly, $-0.08$ weekly, $-0.02$ daily.

The spread is what remains: $\$1.88$ monthly, $\$0.93$ weekly, $\$0.42$ daily, about 4% of the price. Each step multiplies the number of adjustments by about four and halves the spread, consistent with a $1/\sqrt{n}$ rate as $n$ becomes large. To leading order over one short interval, the error is $\tfrac12(\partial^2 V/\partial S^2)\,\sigma^2 S^2\left[(\Delta W)^2 - \Delta t\right]$, the term the continuous derivation drops; higher-order terms remain when the interval is finite. The leading-order errors have conditional mean zero and size proportional to $T/n$, and they are uncorrelated, so their variances add, as in Chapter 5, and $n$ of them give a spread proportional to $\sqrt{n}\,(T/n) \propto 1/\sqrt{n}$. This is Chapter 3's $1/\sqrt{N}$ again.

Like Worked Example 1, this is not validation: the simulated stock follows geometric Brownian motion by construction. **For large $n$, adjusting the hedge $n$ times leaves a spread that falls like $1/\sqrt{n}$, so the seller is riskless only in the continuous limit**; hedging daily, the seller of this call still carries about 4% of its price in risk.

## Intuition

> **Why doesn't the stock's expected return affect the price?** Because the seller can cancel the risk with shares, and the cost of doing so depends on how much the stock moves, not on which way it tends to move. Expected returns still enter through $S_0$: investors' views about $\mu$ are part of what sets today's price.

> **Why does more volatility make both calls and puts worth more?** Both payouts are convex ramps. A wider blur averages over more of the ramp's rising side, while the flat side stays at zero, so the average rises. The buyer gains from large moves and loses at most the premium.

> **Why does the $-\sigma^2/2$ reappear?** For the same reason as in Chapter 6: we simulate the log price, whose drift is $r - \sigma^2/2$, and exponentiate. Leave it out and every $S_T$ is multiplied by $e^{\sigma^2 T/2}$. At Worked Example 1's parameters that prices the call as if $S_0$ were $100\,e^{0.02} = 102.02$: 11.77 instead of 10.45, about an eighth too high, and about 60 standard errors off at 500,000 paths.

> **Monte Carlo simulates a stock that grows at $r$. Isn't that a wrong model?** It would be, as a forecast. It is a way to compute the cost of the hedge, which grows at $r$ whatever the stock does. Simulating with $\mu$ gives the stock's actual expected payout, the 13.90 of Worked Example 1, which is neither the price nor the option's expected return.

> **Why does this option have a closed form when others don't?** A European payout depends only on the endpoint $S_T$, which is lognormal, so the expectation reduces to Gaussian integrals. Options that pay on the average price, on whether the price crosses a level, or that can be exercised early depend on the whole path; Monte Carlo handles them by simulating paths.

## Connections

- **Builds on:** Chapter 6 for geometric Brownian motion, the lognormal solution and the two-variable Itô's lemma; Chapter 5 for the diffusion equation, its fundamental solution and superposition; Chapter 3 for Monte Carlo estimates and their standard errors.
- **Used in:** Chapter 8, which studies the fat tails that the volatility smile reflects.
- **Further directions:** the "Greeks", the price's sensitivities to $S$, $t$, $\sigma$ and $r$ ($\Delta$ is the first); American options by least-squares Monte Carlo (Longstaff–Schwartz); stochastic volatility and jump models, which produce a smile.

## Exercises

1. **Conceptual.** A friend says "I expect the stock to go up, so I should be willing to pay more for a call." Explain why the market price of the call does not depend on this expectation, and what the expectation does tell your friend.

2. **Derivation.** A stock at $S_0$ will be worth either $S_0 u$ or $S_0 d$ at time $T$, with $u > d$, and a call on it pays $C_u$ or $C_d$. Find the number of shares $\Delta$ and the amount $B$ deposited at rate $r$ (negative for a loan) that together pay exactly $C_u$ and $C_d$. Show that their cost is $e^{-rT}\left[q C_u + (1 - q) C_d\right]$ with $q = (e^{rT} - d)/(u - d)$, show that $q$ makes the stock's expected value $S_0 e^{rT}$, and explain why no arbitrage requires $d < e^{rT} < u$. Evaluate for $S_0 = 30$, $u = 1.1$, $d = 0.9$, $r = 0$, $K = 30$.

3. **Computational.** Check Monte Carlo against Black–Scholes for $S_0 = 100$, $K \in \{80, 100, 120\}$, $T = 1$, $r = 0.05$, $\sigma = 0.30$, with $200{,}000$ paths. Report the Monte Carlo mean and standard error, the formula's price, and the Z-score $(\text{MC} - \text{BS})/\text{SE}$.

4. **Derivation.** A call minus a put with the same $K$ and $T$ pays $S_T - K$ in every outcome. Explain why this forces $C - P = S_0 - K e^{-rT}$ without any model of the stock (this is **put–call parity**), then show that the Black–Scholes formulas satisfy it and check it numerically.

5. **Computational.** For a heavily traded stock or fund (SPY, AAPL, META), download the options at the first expiration at least two weeks away. Each quote has a **bid**, the most a buyer offers, and an **ask**, the least a seller accepts; the **mid** is halfway between. For each strike, find the implied volatility of the mid price and plot it against strike. Describe the shape, and say which strikes had no implied volatility and why.

6. **Modeling judgment.** A trader's model prices an SPY call $\$0.50$ below the market. They plan to sell the call at the market price and keep the difference. Using the derivation's assumptions, give three reasons this may be a bad trade even if their model is better than the market's.

7. **Computational.** Repeat Worked Example 3, but price and hedge with $\sigma = 0.20$ while the stock actually moves with $\sigma = 0.25$ ($\mu = 0.10$), adjusting weekly and daily. Compare the mean hedging error with the difference between the formula's prices at $0.25$ and $0.20$. Does adjusting more often help?

:::{admonition} Solutions
:class: dropdown

**1.** The call's price is the cost of hedging it, which depends on $S_0$, $K$, $T$, $r$ and $\sigma$ but not on $\mu$; any other price would allow arbitrage. The market's view of the stock's growth is already in $S_0$. Your friend's expectation changes the call's value *to them*: if they believe in a higher drift than the market does, they expect a higher payout, so the call is a way to act on that view. Whether it is a good buy depends on the premium, the risk they accept and the most they can lose, the same questions as for buying the stock.

**2.** Matching payouts, $\Delta S_0 u + B e^{rT} = C_u$ and $\Delta S_0 d + B e^{rT} = C_d$, gives
$$
\Delta = \frac{C_u - C_d}{S_0 (u - d)}, \qquad B = e^{-rT}\,\frac{u C_d - d C_u}{u - d}.
$$
The cost $\Delta S_0 + B$ rearranges to $e^{-rT}[q C_u + (1 - q) C_d]$, and $q S_0 u + (1 - q) S_0 d = S_0 e^{rT}$. The real probability of the up move appears nowhere: this is the chapter's argument in its simplest form. For $q$ to lie strictly between 0 and 1 we need $d < e^{rT} < u$. If $e^{rT} \ge u$, lending beats the stock in both outcomes, so selling the stock short and lending the proceeds cannot lose; if $e^{rT} \le d$, the reverse trade cannot lose. With the numbers given, the call pays $3$ or $0$, and $\Delta = 1/2$, $B = -13.50$ (borrow $\$13.50$), $q = 1/2$, price $\$1.50$.

**3.** The [companion script](./code/07_option_pricing/mc_vs_bs.py) prints (the `2-sigma` column is twice the standard error):

```text
     K         MC    2-sigma         BS        Z
    80    26.4844     0.1240    26.4621     0.36
   100    14.2657     0.1007    14.2313     0.68
   120     6.9734     0.0746     6.9040     1.86
```

All Z-scores are within $\pm 2$. The standard error falls in dollars with the strike, from $0.062$ to $0.037$, but rises relative to the price, from $0.23\%$ to $0.54\%$, because fewer paths end in the money. With three independent checks, the chance that at least one Z-score exceeds $1.86$ in size is about $18\%$, so $1.86$ is not a warning. When you run several checks, judge the largest against how many you ran.

**4.** One share plus a loan of $K e^{-rT}$, repaid as $K$ at $T$, also pays $S_T - K$ in every outcome, and it never needs adjusting, so equal payouts force equal prices whatever the stock does. For the formulas, $C - P = S_0[\Phi(d_1) + \Phi(-d_1)] - K e^{-rT}[\Phi(d_2) + \Phi(-d_2)] = S_0 - K e^{-rT}$, using $\Phi(x) + \Phi(-x) = 1$. The [companion script](./code/07_option_pricing/put_call_parity.py) checks three cases. Parity holds without the formula, so agreement is a check on the formula.

**5.** See [`code/07_option_pricing/implied_vol_smile.py`](./code/07_option_pricing/implied_vol_smile.py). For SPY the curve typically slopes down: implied volatility is higher at low strikes. A strike has no implied volatility when its mid price lies outside Worked Example 2's bounds. Deep in the money that can happen legitimately, because SPY pays dividends, which lower a call's price below the zero-dividend bound, and the script's $r = 0.04$ is approximate. SPY's options can also be exercised early, so the formula is only approximate for them, and a careful answer says so. The downward slope is consistent with large falls being more common than geometric Brownian motion predicts, and with buyers paying extra for protection against them.

**6.** Three of the derivation's idealizations each give a reason. (i) **Frictionless trading:** the seller receives something near the bid, not the mid, and pays fees, which can use up the $\$0.50$. (ii) **Continuous trading:** Worked Example 3 shows daily hedging still leaves a spread of about 4% of the price, and each adjustment costs money, so the $\$0.50$ is not riskless. (iii) **Geometric Brownian motion with constant $\sigma$:** real prices jump and change volatility (Chapter 5's Worked Example 3; Chapter 8), a call seller loses most after a large rise, and Exercise 7 shows that hedging with too low a $\sigma$ loses about the amount undercharged.

**7.** The [companion script](./code/07_option_pricing/discrete_hedging.py) gives a mean of $-1.944 \pm 0.010$ weekly and $-1.950 \pm 0.007$ daily. The price difference is $1.885$ today, or $1.885\,e^{0.05} = 1.982$ at expiration. So the seller loses about what they undercharged. With the stock drifting at $r$, the loss would match it exactly (the script gives $-1.986 \pm 0.007$); at $\mu = 0.10$ the drift carries paths away from the strike, where $\partial^2 V/\partial S^2$ is largest, and the loss is slightly smaller. Adjusting more often does not help: the mean is unchanged, and the spread falls only from $1.44$ to $1.02$, a factor of $1.4$ where $1/\sqrt{n}$ predicts $2.2$. A hedge cancels the *direction* of the stock's moves only if you know their *size*; with the wrong $\sigma$, more frequent hedging does not remove the loss.

:::

## Further reading

- Hull, *Options, Futures, and Other Derivatives*, Chs. 13–17 — the standard textbook, from
  two-outcome trees through the Black–Scholes–Merton formula, with the market terms
  explained. Use the **US 11th edition**, ISBN 9780136939979 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Options%20Futures%20and%20Other%20Derivatives%20Hull&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- Shreve, *Stochastic Calculus for Finance I: The Binomial Asset Pricing Model* (2004),
  Ch. 1 — Exercise 2's two-outcome hedge developed into a full multi-period model.
  ISBN 9780387249681 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Stochastic%20Calculus%20for%20Finance%20I%20Binomial%20Shreve&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
- The two original 1973 papers, which are separate and both worth reading:
  Black & Scholes, "The Pricing of Options and Corporate Liabilities", *J. Polit. Econ.*
  81(3):637–654, [doi:10.1086/260062](https://doi.org/10.1086/260062) ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,10.1086/260062&tab=Everything&search_scope=MyInst_and_CI&vid=01HVD_INST:HVD2&offset=0); and Merton, "Theory of Rational Option Pricing",
  *Bell J. Econ. Manag. Sci.* 4(1):141–183,
  [doi:10.2307/3003143](https://doi.org/10.2307/3003143) ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,10.2307/3003143&tab=Everything&search_scope=MyInst_and_CI&vid=01HVD_INST:HVD2&offset=0). Merton's earlier Sloan working-paper version is
  **free** at [MIT DSpace](https://dspace.mit.edu/handle/1721.1/49331) — note it is the 1971
  preprint, not the published article.
- For the probabilistic theory behind the drift $r$ (risk-neutral measures, martingales and change of measure):
  Shreve, *Stochastic Calculus for Finance II: Continuous-Time Models* (2004), Chs. 4–5.
  ISBN 9780387401010 ·
  [HOLLIS](https://hollis.harvard.edu/discovery/search?query=any,contains,Stochastic%20Calculus%20for%20Finance%20II%20Shreve&tab=LibraryCatalog&search_scope=MyInstitution&vid=01HVD_INST:HVD2&offset=0).
