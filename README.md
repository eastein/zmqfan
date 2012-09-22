<A name="toc1-0" title="Pipes Rock" />
# Pipes Rock

We all like pipes, but sometimes your pipes need fittings.

* Have limited bandwidth and 20 consumers at the other end of the narrow pipe?  Use zmqfan to republish at the other end.
* Have 2 services, both using bind? Can't configure them differently?  Connect to both and ferry messages from one to the other.

<A name="toc1-8" title="Implementation" />
# Implementation

I'm working on making this work in Python.  If I need to I'll reimplement it in c to get a bit more performance.
