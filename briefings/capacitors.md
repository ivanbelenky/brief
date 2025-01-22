# capacitor meets square wave meets geometric series

## Problem Statement

We'll analyze the charge present in a capacitor under the influence of a square wave with symmetric semi-period and positive average value. The step function takes the values:

- $E$ when $kT \leq t \leq (2k+1)\frac{T}{2}$
- $0$ when $(2k+1)\frac{T}{2} \leq t \leq kT$

## Charge Equations

The charge function $q(t)$ during charging (when voltage = $E$) is:

$$q(t) = \text{E}\text{C} + (q_{in} - \text{E}\text{C}) \ e^{\frac{-t}{\tau}}$$

During discharge (when voltage = 0):

$$q(t) = q_{in} \ e^{\frac{-t}{\tau}}$$

where:
- $\text{E}$ is the voltage source value
- $\text{C}$ is capacitance
- $\tau$ is the time constant
- $q_{in}$ is initial charge

## Recursive Solution

From $q_{2n}$ to $q_{2n+1}$, we can express:

$$q_{2n+1} = E C + (q_{2n} - E C) e^{\frac{-T}{2 \tau}} = E C (1 - e^{\frac{-T}{2 \tau}})+ q_{2n} e^{\frac{-T}{2 \tau}}$$

where:
- $\text{Q} = \text{EC}$
- $\alpha = e^{\frac{-T}{2 \tau}}$

For $q_{2n+2}$:

$$q_{2n+2} = q_{2n+1} e^{\frac{-T}{2\tau}} = \alpha q_{2n+1}$$

## Convergence

The geometric series converges to:

For odd-numbered steps:

$$\lim_{n\rightarrow \infty}q_{2n+1}=\frac{EC}{1+\alpha}$$

For even-numbered steps:

$$\lim_{n\rightarrow \infty}q_{2n}=\frac{EC\alpha}{1+\alpha}$$

## Special Cases

1. When $\tau \ll T$ ($\alpha \approx 0$):
   - $\lim_{n\rightarrow \infty}q_{2n+1} \approx EC$
   - $\lim_{n\rightarrow \infty}q_{2n} \approx 0$

   The capacitor has sufficient time to fully charge and discharge.

2. When $T \ll \tau$ ($\alpha \approx 1$):
   - $\lim_{n\rightarrow \infty}q_{2n+1} \approx \frac{EC}{2}$
   - $\lim_{n\rightarrow \infty}q_{2n} \approx \frac{EC}{2}$

   The circuit acts as a low-pass filter, averaging the input voltage.
