# Smart Book Validation Report

**Generated**: Violation(severity=<ViolationSeverity.CRITICAL: 'CRITICAL'>, section='PART_VII_T15_REDUCTIONS', concept='T1_5_COUNT', issue_type='COUNT_MISMATCH', message="Section(s) ['PART_VII_T15_REDUCTIONS'] state 'T1_5_COUNT' = 1, but canonical value from §§34 = 13", suggested_fix='Update PART_VII_T15_REDUCTIONS to use value 13', affected_text=None)
**Manifest Version**: 1.0.0
**Last Updated**: 2026-03-03

## Summary
- Total sections scanned: 21
- Total concepts defined: 10
- Total violations found: 4

## Violations by Severity

- **CRITICAL**: 2
- **MEDIUM**: 2

## Detailed Violations

### 1. CRITICAL: COUNT_MISMATCH

- **Section**: PART_VII_T15_REDUCTIONS
- **Concept**: T1_5_COUNT
- **Message**: Section(s) ['PART_VII_T15_REDUCTIONS'] state 'T1_5_COUNT' = 1, but canonical value from §§34 = 13

- **Suggested Fix**: Update PART_VII_T15_REDUCTIONS to use value 13


### 2. CRITICAL: COUNT_MISMATCH

- **Section**: PART_VII_T15_REDUCTIONS, PART_VII_T15_REDUCTIONS
- **Concept**: T1_5_COUNT
- **Message**: Section(s) ['PART_VII_T15_REDUCTIONS', 'PART_VII_T15_REDUCTIONS'] state 'T1_5_COUNT' = 22, but canonical value from §§34 = 13

- **Suggested Fix**: Update PART_VII_T15_REDUCTIONS, PART_VII_T15_REDUCTIONS to use value 13


### 3. MEDIUM: REQUIRES_REVIEW

- **Section**: §35, §40, §54, §78, §100, §115, §142, §147
- **Concept**: T1_5_COUNT
- **Message**: Concept 'T1_5_COUNT' was updated on 2026-02-27. The following sections may need review: ['§35', '§40', '§54', '§78', '§100', '§115', '§142', '§147']

- **Suggested Fix**: Manually review these sections to ensure they remain consistent with the updated definition in §§34


### 4. MEDIUM: REQUIRES_REVIEW

- **Section**: §48A, §49, §50, §51, §52, §53, §54
- **Concept**: CREDENCE_FORMULA_LOGODDS
- **Message**: Concept 'CREDENCE_FORMULA_LOGODDS' was updated on 2026-02-27. The following sections may need review: ['§48A', '§49', '§50', '§51', '§52', '§53', '§54']

- **Suggested Fix**: Manually review these sections to ensure they remain consistent with the updated definition in §§48

