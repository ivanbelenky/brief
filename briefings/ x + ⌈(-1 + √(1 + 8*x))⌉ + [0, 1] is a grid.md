# x + ⌈(-1 + √(1 + 8*x))⌉ + [0, 1] is a grid

<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>

<br>

From the post $$x + 1 \ \text{is a list}$$ and from the most recent one $$\begin{pmatrix} x \ll 1 + 2 & x \ll 1 + 3 \end{pmatrix} \ \text{is a binary tree}$$ I bring to you the grid. If details are needed please refer to [x+1](https://ivanbelenky.com/articles/x+1%20is%20a%20list) or [[x<<1 + 2, x<<1 +3]](https://ivanbelenky.com/articles/x%3C%3C1%20+%202,%20x%3C%3C2%20+%203).


With the help of my dearest Fama, we saw that a top bottom level ordering from a single node gives rise to

<pre>
  <code>
1
2 3
4 5 6
7 8 9 10
  </code>
</pre>


where each level L items was upper bounded by $$\sum_{i=1}^{L+1} i = \frac{L^2 + L}{2}$$ and lower bounded similarly by $$ \frac{L^2 - 2L}{2}$$. So given that this two bounds imply 1 level of separation, the "level" for all other integers will be non integer. This can be seen by setting the equality for

$$x=\frac{L^2 + L}{2}$$

we got that

$$
L^2+L-2x = 0
$$

giving us a non complex value for all postive natural numbers

$$
\frac{-1 + \sqrt{1 + 8x}}{2}
$$

where the ceil value determines the level. With this setting $$f(x) = \begin{pmatrix} x + \left\lceil\frac{-1 + \sqrt{1 + 8x}}{2}\right\rceil, & x + \left\lceil{\frac{-1 + \sqrt{1 + 8x}}{2}}\right\rceil + 1 \end{pmatrix} $$ gives birth to a grid

<img style="width:50%;height:50%;justify-content:center"  src="https://github.com/ivanbelenky/brief/blob/master/assets/grid.png?raw=true"/>
