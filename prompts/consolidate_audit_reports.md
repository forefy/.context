-----
- expected_inputs:
    Multiple audit report files from .context/outputs directory
    Audit findings from various runs and tools
    Existing audit report format examples
    Security assessment data with severity classifications

- expected_actions:
    - analyze:
        All audit reports in .context/outputs
        Cross-reference findings across multiple runs
        Validate finding consensus and accuracy
    
    - consolidate:
        Findings that appear consistently across runs
        Only confirmed valid vulnerabilities
        Maintain original audit report format structure
-----

Use all audit reports from .context/outputs directory and generate them into a single consolidated report containing only findings that were agreed upon across all runs and are valid.

Analyze each finding for:
- Consistency across multiple audit runs
- Validation status and accuracy
- Consensus agreement between different tools/runs

Only include findings that meet ALL criteria:
1. Appear in multiple audit runs
2. Have been validated as legitimate vulnerabilities
3. Show consensus agreement across different assessments

Maintain the same audit report format that has been used in previous reports.

Do not include:
- Findings that appear in only one run
- Disputed or uncertain vulnerabilities
- False positives or unvalidated issues

The consolidated report should represent the highest confidence findings with cross-validation support.
