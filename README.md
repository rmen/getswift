# getswift
GetSwift Code Test

Developed on python3

Setup:
Install and activate a python3 virtualenv, then pip install the `requests` package, or:

```bash
pip install -r requirements.txt
```

Run:

```bash
cd dronedelivery/
python dispatch.py -d https://codetest.kube.getswift.co/drones -p https://codetest.kube.getswift.co/packages
```

## Analysis
After you've implemented your solution, try answering the following questions. We're not really looking for a particular answer; we're more interested in how well you understand your choices, and how well you can justify them.

- How did you implement your solution?
- Why did you implement it this way?

R: A straightforward implementation that "seems" to work (I have limited time available to work on this sort of exercise so no tests), and no premature optimization. Pseudocode:
   for package in packages_by_delivery_deadline:
       if first_drone_at_depo can deliver package:
       	  assign(package, drone)
       else:
	  add_unassigned(package)

- Let's assume we need to handle dispatching thousands of jobs per second to thousands of drivers. Would the solution you've implemented still work? Why or why not? What would you modify? Feel free to describe a completely different solution than the one you've developed.

R: There are 3 main methods here - enqueing drones and packages, then assigning them to each other. The enque methods are bounded by the sort operation (I believe python uses an adaptive sort called timsort, but still should be nlogn), and the assignment operation is a linear scan through the sequences. Not getting into any detailed analysis, this whole application should be order (2 nlogn + n) ~ nlogn.
Getting back to the question - I'd be more concerned at this stage in implementation with the correctness, so writing tests. And if the implementation is correct, we can take a look at further optimization.

### Assessment
As a rough guide, we look at the following points to assess an analysis:

1. Are there any logical errors?
2. Are there any outright factual errors?
3. Are important tradeoffs identified and analysed? Is the effort put into each tradeoff proportionate to its severity, or is a lot of time spent on analysing a trivial problem, while more pressing concerns are left untouched?
4. What doesn't the analysis cover? How is the scope of the solution framed? Do we get a sense of where the solution is situated in the solution space, and where we can we move to?
