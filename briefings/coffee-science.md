# coffee and neutron transport

<script>
  MathJax = {tex: {inlineMath: [['$', '$'], ['\\(', '\\)']]}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>
<style>
.math-display { width:100%; overflow-x:auto; padding:.3rem 0; }
.math-display mjx-container[display="true"] { min-width:max-content; margin:.7em 0; }
.coffee-parallel { width:100%; border-collapse:collapse; text-align:left; font-size:.9em; margin:1em 0; }
.coffee-parallel th, .coffee-parallel td { padding:.5em .4em; border-bottom:1px solid #ddd; }
</style>

I was trying to describe how coffee particles get smaller as I grind them.
The equation looked familiar from neutron transport. Both count particles
leaving one state and arriving from other states.

## counting fractures

Lets put mass on a grid $x_i=i\Delta x$, with spacing $\Delta x$ and positive
integers $i$. For each mass we keep track of

- $N_i(t)$, the average number of particles of mass $x_i$ at time $t$
- $a_i$, how often one of those particles breaks, per unit time
- $b_{ij}$, the average number of pieces of mass $x_i$ made when one parent
  of mass $x_j$ breaks

In a short time $\Delta t$, a parent at $x_j$ breaks with probability
approximately $a_j\Delta t$. So the change
$\Delta N_i=N_i(t+\Delta t)-N_i(t)$ is

<div class="math-display">
$$
\frac{\Delta N_i}{\Delta t}\simeq\sum_{j\gt i}a_jb_{ij}N_j-a_iN_i.
$$
</div>

We gain pieces from larger masses, $j\gt i$. We lose pieces at $x_i$ when they
break into smaller ones.

Now make the mass spacing small. Write $N_i\simeq n(x_i,t)\Delta x$ and
$b_{ij}\simeq b(x_i\mid x_j)\Delta x$.
$n(x,t)\,dx$ counts particles in $[x,x+dx]$.
$b(x\mid y)\,dx$ counts the pieces in that interval from a broken parent of
mass $y$.

As the time step and mass spacing go to zero, we get

<div class="math-display">
$$
\partial_t n(x,t)=\int_x^\infty a(y)b(x\mid y)n(y,t)\,dy-a(x)n(x,t).
$$
</div>

The integral starts at $x$ because a parent smaller than $x$ cannot produce
a fragment of mass $x$.

## the neutron version

Neutrons change energy and direction when they collide with nuclei.
For scattering and absorption, without fission, the
[neutron transport equation](https://scale-manual.ornl.gov/6.3.3/NEWT.html#boltzmann-transport-equation)
with [time dependence](https://open-sn.github.io/opensn/theory/time_discretization.html) is

<div class="math-display">
$$
\frac{1}{v(E)}\partial_t\psi+\Omega\cdot\nabla\psi=-\Sigma_t\psi+\int_0^\infty\!\int_{4\pi}\Sigma_s(E',\Omega'\!\to E,\Omega)\psi'\,d\Omega'\,dE'+q.
$$
</div>

Here $\psi=\psi(\mathbf r,E,\Omega,t)$ is angular flux.
It is neutron density per volume, energy and solid angle, multiplied by
the speed $v(E)$. Solid angle measures a patch of directions.
$\mathbf r$ is position, $E$ is energy and $\Omega$ is the unit vector giving
travel direction. Primes mark incoming states, so
$\psi'=\psi(\mathbf r,E',\Omega',t)$.

$\Sigma_t$ is the total collision probability per distance.
$\Sigma_s$ gives the probability of scattering from $(E',\Omega')$ to
$(E,\Omega)$ per distance, outgoing energy and solid angle.
The double integral adds arrivals from all incoming energies and directions.
$4\pi$ covers the full sphere of directions.

$\Omega\cdot\nabla\psi$ accounts for motion through space.
$\nabla$ takes derivatives with respect to position.
$q$ counts neutrons supplied by an external source per volume, time, energy
and solid angle.

To compare rates per unit time, use neutron density $h=\psi/v(E)$.
Then we can line up the terms

<table class="coffee-parallel">
<thead><tr><th></th><th>Fracture</th><th>Neutrons</th></tr></thead>
<tbody>
<tr><td>Change in time</td><td>$\partial_t n$</td><td>$\partial_t h$</td></tr>
<tr><td>Loss rate</td><td>$a(x)$</td><td>$v(E)\Sigma_t(E)$</td></tr>
<tr><td>Gain kernel</td><td>$a(y)b(x\mid y)$</td><td>$v(E')\Sigma_s(E',\Omega'\to E,\Omega)$</td></tr>
</tbody>
</table>

The fracture equation above only tracks changes in mass.
The neutron equation also has motion through space and an external source.
Neutrons can gain or lose energy to nuclei. A fragment has to be smaller
than its parent.
