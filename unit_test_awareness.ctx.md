# Unit tests awareness context
Unit tests are not just for validation—they provide developer insights, protocol interactions, and functional flows. When analyzing code, treat unit tests as a source of knowledge to:
* Understand the developer’s thought process – Tests reveal assumptions, edge cases, and expected behavior.
Analyze functional flows – Following test executions can clarify how different components interact.
* Identify security risks or logical bugs – If a function is called within a test, we should investigate whether it highlights overlooked vulnerabilities or unexpected behavior.

# How to Use Unit Tests in Analysis
Extract insights from the way functions are tested—what is the developer assuming or missing?
Use tests as a guide to explore potential security gaps the developer might not have considered.
Follow the flow of how the function is executed in tests to better understand its role within the protocol.

# Key Focus Areas
* Look for overlooked edge cases in the tests.
* Check if tests unintentionally expose security risks.
* Use tests to map out system behavior and dependencies.

# What to Avoid
* Do not analyze tests for their correctness—assume they are written with intent.
* Do not just summarize tests—use them to inspire deeper analysis of the main code.
* Do not rely solely on tests—cross-check with the actual implementation for hidden risks.