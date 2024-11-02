# US Routing: cheap routes

<br/>
If you can afford a couple of miles of error, you can benefit greatly from a pre-cached and optimized graph of all the United States major routes.

[US Routing](https://github.com/ivanbelenky/us-routing) is a Python library for fast local routing in the United States. It's useful when approximations are acceptable. It bootstraps from the [North American Roads dataset](https://geodata.bts.gov/datasets/usdot::north-american-roads).

</br>

install it with your favorite package manager

<pre><code>pip install us-routing</code></pre>

and then just

<pre><code>from us_routing import get_route
r = get_route('New York', 'Los Angeles', edge_distance="DURATION")
</code></pre>


<center><img style="width:75%;height:750%;justify-content:center"  src="https://github.com/ivanbelenky/us-routing/raw/master/assets/usroutegraph.png?raw=true"/></center>
