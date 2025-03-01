# willing to build a house --> real estate skiddie --> finding out that humans like multiples of 5

What is this?

<img style="width:50%;height:50%;justify-content:center"  src="https://github.com/ivanbelenky/brief/blob/master/assets/frontiers.png?raw=true"/>

<br>

It was early January 2024, and I was trying to understand how to decide on a piece of land purchase. I have plans in the near future to build a house for my family and me.

At that point, I had only one yearly report that mentioned the market was at its lowest point. This source did not provide a dataset; it only contained references to non-disclosed privately gathered data and some Excel charts. However, it was respectable enough to trust. Additionally, news articles suggested that this was the best moment to buy.

There is a fairly good (in my Grug eyes) rule of thumb that asserts that large public mentions of a market event signal the beginning of the next typical cyclical phase. In other words, popular opinions tend to lag behind true phenomena, such as:

- lowest low --> about to rise
- highest high --> about to drop
- growing fast --> just reached its highest high
- ...

### Bias

My professional bias led me to build a sensor, a thermometer to validate public opinion and confirm my rule of thumb, so I could time my purchase correctly. I started thinking about setting up a couple of scrapers on some popular and high-traffic real estate websites to monitor trends.

- I focused on one site in particular, let's call it `real-state-company-webapp.com`
- `stack`: PHP + Angular
- I began exploring how to batch scrape properties
- The query `?items_per_page=1000` worked --> my Grug monkey brain was happy
- I discovered a "hidden" API, which I'll refer to as `real-state-company.com/api/`: the server state was dumped in the response and contained references to this unused API, at least not used by the browser.
- Hitting it returned all the results! My Grug monkey brain was even happier than before.
- Accessing the domain directly, i.e. `real-state-company.com`, led me to a `CRM` in construction website.
- I attempted to log in with default credentials, but nothing happened.
- Checking the raw response revealed drumrolls `debug=True`; they were developing in production --> I had complete access to most of their infrastructure resources.

<img style="width:50%;height:50%;justify-content:center"  src="https://github.com/ivanbelenky/brief/blob/master/assets/env_dump.png?raw=true"/>

### Reaching Out and Dumping Their Database

After discovering the environment dump, I reached out to them:

- It took them two weeks to respond.
- I contacted the real estate company numerous times.
- There was no response to my emails.
- I sent a direct message to the VP of Engineering on LinkedIn.
- He did not reply but propagated the message down the chain of corporate bureaucracy.

Talking to them and using their data freely:

- I was contacted by the tech team.
- They were indifferent about me using and disclosing the most valuable data (listings that were sold and their final selling values after negotiation!). After all, they were not even using this data and had no plans for it.
- I proceeded to dump the entire database locally.

### Learning How to Negotiate

Having access to both listing and final selling prices was a gold mine. I began analyzing the distributions of the ratio between them, regardless of the absolute values. I wanted to gauge what were the negotiations margins allowed in my price range.

<img style="width:50%;height:50%;justify-content:center"  src="https://github.com/ivanbelenky/brief/blob/master/assets/sell_to_list_hist.png?raw=true"/>

As you can see, the data was quite noisy—after all, it was entered by humans who either made mistakes when updating listing prices or purposefully misrepresented the values. Why lie? Well, in my country, lying is a common practice in real estate to enable tax evasion and facilitate under-the-table transactions. For example, a house listed at 100 ends up "officially" selling at 50, but in reality, the buyer pays 50 in white money and 25 under the table in cash. This way, both parties benefit—the seller receives more money, and the buyer pays fewer taxes. My Grug brain started seeing patterns in the noise.

To perform some qualitative analysis, I removed samples with a ratio greater than 1.

This led me to our first image. What are those frontiers? They are subsets of our domain highly populated by real samples—actual sales that occurred. After visually inspecting a few examples, I noticed that:

- Sell price to list price ratios occupied random real values, like `0.8534`. Therefore, it was evident that there was no phenomenon of a high population of, lets say, 10% discount properties, but rather a continuum depending on price.
- Thus, what needs to guide this behavior is the absolute amount of discount, not the relative amount.

To informally test this hypothesis, I created an artificial property valued at 91.3K. I then scatter-plotted the discount ratios for selling values with discounts that are multiples of 5, such as:

- 71,300$
- 76,300$
- 81,300$
- 86,300$

<img style="width:50%;height:50%;justify-content:center"  src="https://github.com/ivanbelenky/brief/blob/master/assets/frontiers_with_test.png?raw=true"/>


monkey brain likes `5*N`
