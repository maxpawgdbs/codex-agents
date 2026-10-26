---
name: debug-issue
description: "Diagnose a reported failure, regression, or flaky test by testing the cause before changing code."
---

# Debug an issue

- Establish the failing input, expected result, actual result, and smallest available reproduction.
- Inspect the relevant stack frames and nearby code. Keep the first meaningful error and causal context when shortening logs.
- Form a falsifiable hypothesis and choose a check that distinguishes it from alternatives. Avoid accumulating speculative fixes.
- Fix the established cause within the requested scope. Preserve the failing example as a regression check when it protects meaningful behavior.
- Re-run the reproduction and affected checks. Broaden verification for shared contracts, persistence, authentication, or concurrency when relevant.

If reproduction is unavailable, distinguish what is established from what remains unverified. On failure, report the new evidence before trying another approach. Finish with the cause, fix, observed checks, and remaining uncertainty.
