# Query-selection timing environment

The confirmation profiles ran in a shared CPU environment.
Concurrent reader inference and unrelated workloads consumed CPU resources.
No process isolation or exclusive CPU allocation was available.
The profiles alternate method order and report within-query median times.
They exclude compilation, ranking, rendering, and reader inference.

Support-check counts are the primary efficiency evidence.
Microseconds describe these recorded runs only.
They do not estimate deployment latency or end-to-end speedup.
