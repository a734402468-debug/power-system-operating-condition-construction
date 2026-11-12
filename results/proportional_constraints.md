# Proportional-group constraints

For a load group \(G\), the permitted factor spread is

$$
\max_{i\in G}\alpha_i-\min_{i\in G}\alpha_i\leq\epsilon_G.
$$

With \(x_i=(\alpha_i-1)/s_{\alpha,i}\), Eq. (16) gives the equivalent linear constraints

$$
-\epsilon_G\leq s_{\alpha,i}x_i-s_{\alpha,j}x_j\leq\epsilon_G,
\qquad i<j,\quad i,j\in G.
$$

The scales convert the normalized variables back to factor differences, so the tolerance remains in multiplier units. The exact-relation priority uses independent equations linking each member to one designated member. If the preferred exact relations cannot be satisfied jointly, the pairwise bounds remain applicable under Eq. (12).

The thirteen [constraint-assembly checks](proportional_constraint_checks.csv) cover full-group spread, admissible factors, two-member equivalence, unequal scales, and preservation of the acceptance rule and other constraints. A synthetic quadratic program gives a common factor of 1.02 on the exact-relation branch. These numerical checks use \(\epsilon_G=0.001\); case-study tolerances are given in the [experimental setup](../experimental_setup.md).
