# us-routing: cheap routes

If you can afford a couple of miles of error, you can benefit greatly from a pre-cached and optimized graph of all the United States major routes.

[US Routing](https://github.com/ivanbelenky/us-routing) is a Python library for fast local routing in the United States. It's useful when approximations are acceptable. It bootstraps from the [North American Roads dataset](https://geodata.bts.gov/datasets/usdot::north-american-roads).

install it with your favorite package manager

<pre><code>pip install us-routing</code></pre>

and then just

<pre><code>from us_routing import get_route
r = get_route('New York', 'Los Angeles', edge_distance="DURATION")
</code></pre>

enjoy rich route infromation, lane, max speed, and more attributes
<pre><code>POINT (-73.998 40.751) -> POINT (-74.001 40.746) (0.570 km) 9TH AV, SP_TH_MA, 72 km/h
POINT (-74.001 40.7465) -> POINT (-74.005 40.741) (0.7 km) 9TH AV, SP_TH_MA, 72 km/h
POINT (-74.005 40.741) -> POINT (-74.008 40.742) (0.27 km) W 14TH ST, SP_TH_MA, 72 km/h
POINT (-74.008 40.742) -> POINT (-74.009 40.741) (0.16 km) 10TH AV, SP_TH_MA, 72 km/h
</code></pre>
