# QA Test Plan: Agent Memory Service (agent_memory_service)

**Task ID:** agent_memory_service-qa-plan-001
**Feature ID:** agent_memory_service
**Date Created:** 2025-05-12

## 1. Introduction

This document outlines the test plan for the AgentMemoryService. The service is responsible for managing read/write access to agent-specific runtime memory files. This plan covers functional testing, including positive and negative test cases, error handling, path validation, and adherence to acceptance criteria defined in `context.md`.

**Reference Documents:**
*   Feature Context: `features/agent_memory_service/context.md`
*   Design Notes: `features/agent_memory_service/design_notes.md`

## 2. Test Scope

*   **In Scope:**
    *   `AgentMemoryService` class initialization.
    *   `read_memory_file` method.
    *   `write_memory_file` method.
    *   `append_to_memory_file` method.
    *   Internal helper methods: `_get_agent_memory_path`, `_resolve_safe_path`.
    *   Path validation and security (preventing directory traversal).
    *   Directory creation logic for agent-specific memory paths.
    *   Error handling mechanisms and custom exceptions (`AgentMemoryError`, `AgentNotFoundError`, `AgentMemoryFileNotFoundError`, `InvalidPathError`, `FileOperationError`).
    *   File encoding (UTF-8).
*   **Out of Scope:**
    *   Performance testing.
    *   Concurrency testing (explicitly out of scope in `context.md`).
    *   The `ToolExecutor` or specific tools that use this service.
    *   Management of the global `{app_cache_dir}`.

## 3. Test Approach

*   **Methodology:** Black-box testing based on specifications in `context.md` and `design_notes.md`.
*   **Test Levels:** Unit/Component testing (conceptually, as we are testing the service's API).
*   **Priorities:**
    *   **High:** Core functionality (read, write, append successful paths), security (path traversal prevention), critical error handling.
    *   **Medium:** Other error handling, edge cases for path validation.
    *   **Low:** Minor variations in valid inputs that should behave identically.

## 4. Test Environment & Setup (Conceptual)

*   Python environment with `pathlib` and `logging`.
*   An `app_cache_dir` will be designated for testing (e.g., `/tmp/test_app_cache`).
*   `AgentMemoryService` instance initialized with this `app_cache_dir`.
*   Pre-created files and directory structures for certain test scenarios.
*   Permissions manipulation for specific negative test cases (e.g., read-only files/directories, if feasible in a controlled test setup).

## 5. Test Cases

### 5.1. Service Initialization (`__init__`)

| Test Case ID      | Description                                                                 | Steps                                                                                                | Expected Result                                                                                                                               | Priority |
|-------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_INIT_001      | Initialize service with a valid, non-existent `app_cache_dir`.                | 1. Define a path for `app_cache_dir` that does not exist. <br> 2. Instantiate `AgentMemoryService(app_cache_dir)`. | The `app_cache_dir` and `app_cache_dir/agent_memory` directories are created. <br> No exceptions raised. <br> Logger info message recorded. | High     |
| AMS_INIT_002      | Initialize service with a valid, existing `app_cache_dir`.                  | 1. Create `app_cache_dir/agent_memory`. <br> 2. Instantiate `AgentMemoryService(app_cache_dir)`.         | Service initializes successfully. <br> No exceptions raised. <br> Logger info message recorded.                                               | High     |
| AMS_INIT_003      | Initialize service with an `app_cache_dir` where creation might fail (e.g., permissions). | 1. Define `app_cache_dir` to a path where the process lacks write permission for the parent. <br> 2. Instantiate. | `OSError` is caught during `self.base_memory_path.mkdir`, logged. Service might initialize but subsequent operations requiring the dir will fail predictably. (Behavior per `design_notes.md` line 52) | Medium   |

### 5.2. Agent Directory Management (`_get_agent_memory_path`)

| Test Case ID      | Description                                                                    | Steps                                                                                                                                | Expected Result                                                                                                                                                             | Priority |
|-------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_GAMP_001      | Get path for a new, valid `agent_instance_id`.                                   | 1. Initialize service. <br> 2. Call `_get_agent_memory_path("agent_123")`.                                                           | Directory `{app_cache_dir}/agent_memory/agent_123/` is created. <br> Returns correct `Path` object. <br> No exceptions.                                                        | High     |
| AMS_GAMP_002      | Get path for an existing, valid `agent_instance_id`.                               | 1. Initialize service. <br> 2. Call `_get_agent_memory_path("agent_123")` (creates dir). <br> 3. Call `_get_agent_memory_path("agent_123")` again. | Returns correct `Path` object to the existing directory. <br> No exceptions.                                                                                                   | High     |
| AMS_GAMP_003      | Attempt to get path with an empty `agent_instance_id`.                             | 1. Initialize service. <br> 2. Call `_get_agent_memory_path("")`.                                                                    | `InvalidPathError` raised: "Invalid characters in agent_instance_id: ". <br> Logger warning recorded.                                                                       | High     |
| AMS_GAMP_004      | Attempt to get path with `agent_instance_id` containing '..'.                      | 1. Initialize service. <br> 2. Call `_get_agent_memory_path("../another_agent")`.                                                    | `InvalidPathError` raised: "Invalid characters in agent_instance_id: ../another_agent". <br> Logger warning recorded.                                                        | High     |
| AMS_GAMP_005      | Attempt to get path with `agent_instance_id` containing '/'.                       | 1. Initialize service. <br> 2. Call `_get_agent_memory_path("group/agent_123")`.                                                     | `InvalidPathError` raised: "Invalid characters in agent_instance_id: group/agent_123". <br> Logger warning recorded.                                                         | High     |
| AMS_GAMP_006      | Attempt to get path with `agent_instance_id` containing '\'.                      | 1. Initialize service. <br> 2. Call `_get_agent_memory_path("group\\agent_123")`.                                                    | `InvalidPathError` raised: "Invalid characters in agent_instance_id: group\\agent_123". <br> Logger warning recorded.                                                        | High     |
| AMS_GAMP_007      | Agent directory creation fails due to OS error (e.g. permissions on `agent_memory` parent). | 1. Set up `agent_memory` dir with restrictive permissions. <br> 2. Call `_get_agent_memory_path("new_agent")`.                 | `AgentNotFoundError` raised, wrapping the `OSError`. <br> Logger error message recorded.                                                                                    | Medium   |

### 5.3. Safe Path Resolution (`_resolve_safe_path`)

| Test Case ID      | Description                                                                   | Steps                                                                                                                                                             | Expected Result                                                                                                                                                              | Priority |
|-------------------|-------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_RSP_001       | Resolve a valid, simple `relative_file_path`.                                   | 1. Initialize service. <br> 2. Call `_resolve_safe_path("agent_123", "notes.txt")`.                                                                               | Returns `{app_cache_dir}/agent_memory/agent_123/notes.txt`. <br> No exceptions. Agent directory `agent_123` is created if not existing.                                         | High     |
| AMS_RSP_002       | Resolve a valid `relative_file_path` with subdirectories.                       | 1. Initialize service. <br> 2. Call `_resolve_safe_path("agent_123", "subdir/notes.md")`.                                                                        | Returns `{app_cache_dir}/agent_memory/agent_123/subdir/notes.md`. <br> Agent directory `agent_123` is created. (Parent for file itself is handled by write/append methods). | High     |
| AMS_RSP_003       | Attempt to resolve an empty `relative_file_path`.                               | 1. Initialize service. <br> 2. Call `_resolve_safe_path("agent_123", "")`.                                                                                        | `InvalidPathError` raised: "Relative file path cannot be empty."                                                                                                             | High     |
| AMS_RSP_004       | Attempt to resolve an absolute `relative_file_path`.                              | 1. Initialize service. <br> 2. Call `_resolve_safe_path("agent_123", "/etc/passwd")`.                                                                             | `InvalidPathError` raised: "Absolute paths are not allowed: /etc/passwd". <br> Logger warning recorded.                                                                      | High     |
| AMS_RSP_005       | Attempt to resolve `relative_file_path` containing '..'.                        | 1. Initialize service. <br> 2. Call `_resolve_safe_path("agent_123", "../file.txt")`.                                                                             | `InvalidPathError` raised: "Path traversal attempt ('..') detected in: ../file.txt". <br> Logger warning recorded.                                                          | High     |
| AMS_RSP_006       | Attempt to resolve `relative_file_path` that resolves outside agent directory.  | 1. Initialize service. <br> 2. (Requires careful construction, e.g. if `resolve()` behavior was different) Call `_resolve_safe_path("agent_123", "notes/../../../../etc/hosts")`. | `InvalidPathError` raised, indicating path is outside agent directory. <br> Logger warning recorded. (This is the core path traversal protection)                          | High     |
| AMS_RSP_007       | Resolve path for an agent with invalid `agent_instance_id` (delegated to `_get_agent_memory_path`). | 1. Initialize service. <br> 2. Call `_resolve_safe_path("../invalid_agent", "notes.txt")`.                                                            | `InvalidPathError` (from `_get_agent_memory_path` due to `agent_instance_id`).                                                                                                 | High     |
| AMS_RSP_008       | Resolve path where `_get_agent_memory_path` fails to create agent dir.        | 1. Setup permissions so `_get_agent_memory_path` fails for "agent_x". <br> 2. Call `_resolve_safe_path("agent_x", "notes.txt")`.                                  | `AgentNotFoundError` (from `_get_agent_memory_path`).                                                                                                                        | Medium   |
| AMS_RSP_009       | Resolve a path like `.` (current directory within agent's dir).                 | 1. Initialize service. <br> 2. Call `_resolve_safe_path("agent_123", ".")`.                                                                                       | Returns `{app_cache_dir}/agent_memory/agent_123`. (Note: `is_dir()` checks in read/write/append handle this for file operations).                                        | Medium   |
| AMS_RSP_010       | Resolve a path like `subdir/../file.txt` (normalizes to `file.txt`).            | 1. Initialize service. <br> 2. Call `_resolve_safe_path("agent_123", "subdir/../notes.txt")`.                                                                    | `InvalidPathError` raised: "Path traversal attempt ('..') detected in: subdir/../notes.txt" (due to explicit ".." check before resolve).                               | High     |

### 5.4. Read Memory File (`read_memory_file`)

#### 5.4.1. Positive Cases

| Test Case ID      | Description                                                              | Steps                                                                                                                                                             | Expected Result                                                                                             | Priority |
|-------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|----------|
| AMS_READ_P_001    | Read an existing file with simple path.                                  | 1. Initialize service. <br> 2. Create `agent_memory/agent_abc/file1.txt` with "Hello World". <br> 3. Call `read_memory_file("agent_abc", "file1.txt")`.       | Returns "Hello World". <br> No exceptions. <br> Logger info message.                                         | High     |
| AMS_READ_P_002    | Read an existing file with path containing subdirectories.               | 1. Initialize service. <br> 2. Create `agent_memory/agent_abc/subdir/file2.md` with "## Markdown". <br> 3. Call `read_memory_file("agent_abc", "subdir/file2.md")`. | Returns "## Markdown". <br> No exceptions. <br> Logger info message.                                        | High     |
| AMS_READ_P_003    | Read a file with UTF-8 characters.                                       | 1. Initialize service. <br> 2. Create `agent_memory/agent_utf/text_utf8.txt` with "你好世界". <br> 3. Call `read_memory_file("agent_utf", "text_utf8.txt")`.   | Returns "你好世界". <br> No exceptions.                                                                      | High     |

#### 5.4.2. Negative Cases & Error Handling

| Test Case ID      | Description                                                                     | Steps                                                                                                                                        | Expected Result                                                                                                                            | Priority |
|-------------------|---------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_READ_N_001    | Attempt to read a non-existent file.                                            | 1. Initialize service. <br> 2. Call `read_memory_file("agent_xyz", "nonexistent.txt")`.                                                       | `AgentMemoryFileNotFoundError` raised: "File not found: nonexistent.txt for agent agent_xyz". <br> Logger info message.                    | High     |
| AMS_READ_N_002    | Attempt to read a file with an invalid `agent_instance_id` (e.g., contains '..'). | 1. Initialize service. <br> 2. Call `read_memory_file("../agent_sec", "file.txt")`.                                                           | `InvalidPathError` (from `_resolve_safe_path` via `_get_agent_memory_path`).                                                                 | High     |
| AMS_READ_N_003    | Attempt to read using a path traversal string for `relative_file_path`.         | 1. Initialize service. <br> 2. Call `read_memory_file("agent_sec", "../../../etc/hosts")`.                                                    | `InvalidPathError` (from `_resolve_safe_path`).                                                                                              | High     |
| AMS_READ_N_004    | Attempt to read a directory as a file.                                          | 1. Initialize service. <br> 2. Create directory `agent_memory/agent_dir/data_dir/`. <br> 3. Call `read_memory_file("agent_dir", "data_dir")`.    | `InvalidPathError` raised: "Path is a directory, not a file: data_dir". <br> Logger warning.                                                | High     |
| AMS_READ_N_005    | Attempt to read a file when `_get_agent_memory_path` fails for the agent.       | 1. Setup permissions so `_get_agent_memory_path` fails for "agent_no_access". <br> 2. Call `read_memory_file("agent_no_access", "file.txt")`. | `AgentNotFoundError` (from `_resolve_safe_path` via `_get_agent_memory_path`).                                                               | Medium   |
| AMS_READ_N_006    | Attempt to read a file with OS-level permission issues (e.g. unreadable file).  | 1. Create `agent_memory/agent_perm/locked.txt`. <br> 2. Set file permissions to unreadable. <br> 3. Call `read_memory_file("agent_perm", "locked.txt")`. | `FileOperationError` raised, wrapping the `OSError`. <br> Logger error message.                                                             | Medium   |
| AMS_READ_N_007    | Attempt to read using an empty `relative_file_path`.                            | 1. Initialize service. <br> 2. Call `read_memory_file("agent_abc", "")`.                                                                      | `InvalidPathError` (from `_resolve_safe_path`).                                                                                              | High     |
| AMS_READ_N_008    | Attempt to read using an absolute `relative_file_path`.                         | 1. Initialize service. <br> 2. Call `read_memory_file("agent_abc", "/tmp/somefile.txt")`.                                                    | `InvalidPathError` (from `_resolve_safe_path`).                                                                                              | High     |

### 5.5. Write Memory File (`write_memory_file`)

#### 5.5.1. Positive Cases

| Test Case ID      | Description                                                                 | Steps                                                                                                                                                                | Expected Result                                                                                                                                    | Priority |
|-------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_WRITE_P_001   | Write to a new file with simple path.                                       | 1. Initialize service. <br> 2. Call `write_memory_file("agent_w1", "output.txt", "Data to write")`.                                                                 | File `{app_cache_dir}/agent_memory/agent_w1/output.txt` created with "Data to write". <br> No exceptions. <br> Logger info. Agent dir created.       | High     |
| AMS_WRITE_P_002   | Write to a new file in a new subdirectory.                                  | 1. Initialize service. <br> 2. Call `write_memory_file("agent_w1", "logs/today.log", "Log entry")`.                                                                  | File `{app_cache_dir}/agent_memory/agent_w1/logs/today.log` created with "Log entry". Parent dir `logs` created. <br> No exceptions. <br> Logger info. | High     |
| AMS_WRITE_P_003   | Overwrite an existing file.                                                 | 1. Initialize service. <br> 2. Create `agent_memory/agent_w2/config.yaml` with "old_data". <br> 3. Call `write_memory_file("agent_w2", "config.yaml", "new_data")`. | File `config.yaml` now contains "new_data". <br> No exceptions. <br> Logger info.                                                                    | High     |
| AMS_WRITE_P_004   | Write file with UTF-8 characters.                                           | 1. Initialize service. <br> 2. Call `write_memory_file("agent_w_utf", "notes_utf8.txt", "写入测试")`.                                                              | File created with "写入测试". <br> No exceptions. <br> Logger info.                                                                                   | High     |
| AMS_WRITE_P_005   | Write an empty string as content.                                           | 1. Initialize service. <br> 2. Call `write_memory_file("agent_w_empty", "empty.txt", "")`.                                                                         | File `empty.txt` created and is empty. <br> No exceptions. <br> Logger info.                                                                        | Medium   |

#### 5.5.2. Negative Cases & Error Handling

| Test Case ID      | Description                                                                        | Steps                                                                                                                                                           | Expected Result                                                                                                                            | Priority |
|-------------------|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_WRITE_N_001   | Attempt to write with an invalid `agent_instance_id`.                                | 1. Initialize service. <br> 2. Call `write_memory_file("../agent_sec_w", "file.txt", "content")`.                                                              | `InvalidPathError` (from `_resolve_safe_path` via `_get_agent_memory_path`). No file written.                                                 | High     |
| AMS_WRITE_N_002   | Attempt to write using a path traversal string for `relative_file_path`.             | 1. Initialize service. <br> 2. Call `write_memory_file("agent_sec_w", "../../../etc/config_file", "content")`.                                                 | `InvalidPathError` (from `_resolve_safe_path`). No file written.                                                                             | High     |
| AMS_WRITE_N_003   | Attempt to write to a path that is an existing directory.                            | 1. Initialize service. <br> 2. Create directory `agent_memory/agent_w_dir/my_data/`. <br> 3. Call `write_memory_file("agent_w_dir", "my_data", "content")`.       | `InvalidPathError` raised: "Path is a directory, cannot write: my_data". No file written. <br> Logger warning.                            | High     |
| AMS_WRITE_N_004   | Attempt to write when `_get_agent_memory_path` fails for the agent.                  | 1. Setup permissions so `_get_agent_memory_path` fails for "agent_no_write_access". <br> 2. Call `write_memory_file("agent_no_write_access", "file.txt", "data")`. | `AgentNotFoundError` (from `_resolve_safe_path` via `_get_agent_memory_path`). No file written.                                              | Medium   |
| AMS_WRITE_N_005   | Attempt to write with OS-level permission issues (e.g. read-only file system/dir). | 1. Mount a read-only filesystem for `agent_memory/agent_ro/` or set restrictive permissions. <br> 2. Call `write_memory_file("agent_ro", "file.txt", "data")`.      | `FileOperationError` raised, wrapping `OSError`. No file written. <br> Logger error.                                                        | Medium   |
| AMS_WRITE_N_006   | Attempt to write using an empty `relative_file_path`.                                | 1. Initialize service. <br> 2. Call `write_memory_file("agent_w_inv", "", "content")`.                                                                          | `InvalidPathError` (from `_resolve_safe_path`). No file written.                                                                             | High     |
| AMS_WRITE_N_007   | Attempt to write using an absolute `relative_file_path`.                             | 1. Initialize service. <br> 2. Call `write_memory_file("agent_w_inv", "/tmp/myoutput.txt", "content")`.                                                       | `InvalidPathError` (from `_resolve_safe_path`). No file written.                                                                             | High     |
| AMS_WRITE_N_008   | Parent directory creation for file fails (e.g. permissions).                       | 1. Create `agent_memory/agent_w_p_fail/` with restrictive permissions. <br> 2. Call `write_memory_file("agent_w_p_fail", "subdir/file.txt", "data")`.       | `FileOperationError` raised (from `safe_path.parent.mkdir`). No file written. <br> Logger error.                                            | Medium   |

### 5.6. Append To Memory File (`append_to_memory_file`)

#### 5.6.1. Positive Cases

| Test Case ID      | Description                                                                   | Steps                                                                                                                                                                                          | Expected Result                                                                                                                                                            | Priority |
|-------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_APPEND_P_001  | Append to an existing file.                                                   | 1. Initialize service. <br> 2. Create `agent_memory/agent_a1/log.txt` with "Initial log\n". <br> 3. Call `append_to_memory_file("agent_a1", "log.txt", "Appended log\n")`.                 | File `log.txt` now contains "Initial log\nAppended log\n". <br> No exceptions. <br> Logger info.                                                                            | High     |
| AMS_APPEND_P_002  | Append to a non-existent file (creates the file).                             | 1. Initialize service. <br> 2. Call `append_to_memory_file("agent_a2", "new_log.txt", "First entry\n")`.                                                                                     | File `{app_cache_dir}/agent_memory/agent_a2/new_log.txt` created with "First entry\n". <br> No exceptions. <br> Logger info. Agent dir and parent dirs for file created. | High     |
| AMS_APPEND_P_003  | Append to a file in a new subdirectory (creates dirs and file).               | 1. Initialize service. <br> 2. Call `append_to_memory_file("agent_a2", "data/points.csv", "point1,data\n")`.                                                                                | File `{app_cache_dir}/agent_memory/agent_a2/data/points.csv` created with "point1,data\n". <br> No exceptions. <br> Logger info.                                        | High     |
| AMS_APPEND_P_004  | Append UTF-8 characters.                                                      | 1. Initialize service. <br> 2. Create `agent_memory/agent_a_utf/journal.txt` with "记录1\n". <br> 3. Call `append_to_memory_file("agent_a_utf", "journal.txt", "记录2\n")`.                  | File contains "记录1\n记录2\n". <br> No exceptions. <br> Logger info.                                                                                                       | High     |
| AMS_APPEND_P_005  | Append an empty string to an existing file.                                   | 1. Initialize service. <br> 2. Create `agent_memory/agent_a_empty/data.txt` with "Existing". <br> 3. Call `append_to_memory_file("agent_a_empty", "data.txt", "")`.                       | File content remains "Existing". <br> No exceptions. <br> Logger info.                                                                                                   | Medium   |
| AMS_APPEND_P_006  | Append an empty string to a non-existent file.                                | 1. Initialize service. <br> 2. Call `append_to_memory_file("agent_a_empty_new", "new_empty.txt", "")`.                                                                                        | File `new_empty.txt` created and is empty. <br> No exceptions. <br> Logger info.                                                                                              | Medium   |

#### 5.6.2. Negative Cases & Error Handling

| Test Case ID       | Description                                                                        | Steps                                                                                                                                                              | Expected Result                                                                                                                            | Priority |
|--------------------|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|----------|
| AMS_APPEND_N_001   | Attempt to append with an invalid `agent_instance_id`.                               | 1. Initialize service. <br> 2. Call `append_to_memory_file("../agent_sec_a", "file.txt", "content")`.                                                               | `InvalidPathError` (from `_resolve_safe_path` via `_get_agent_memory_path`). No file modified/created.                                       | High     |
| AMS_APPEND_N_002   | Attempt to append using a path traversal string for `relative_file_path`.            | 1. Initialize service. <br> 2. Call `append_to_memory_file("agent_sec_a", "../../../etc/log_file", "content")`.                                                    | `InvalidPathError` (from `_resolve_safe_path`). No file modified/created.                                                                    | High     |
| AMS_APPEND_N_003   | Attempt to append to a path that is an existing directory.                           | 1. Initialize service. <br> 2. Create directory `agent_memory/agent_a_dir/my_journal/`. <br> 3. Call `append_to_memory_file("agent_a_dir", "my_journal", "content")`. | `InvalidPathError` raised: "Path is a directory, cannot append: my_journal". No file modified/created. <br> Logger warning.                | High     |
| AMS_APPEND_N_004   | Attempt to append when `_get_agent_memory_path` fails for the agent.                 | 1. Setup permissions so `_get_agent_memory_path` fails for "agent_no_append_access". <br> 2. Call `append_to_memory_file("agent_no_append_access", "file.txt", "data")`. | `AgentNotFoundError` (from `_resolve_safe_path` via `_get_agent_memory_path`). No file modified/created.                                     | Medium   |
| AMS_APPEND_N_005   | Attempt to append with OS-level permission issues (e.g. read-only file system/dir).| 1. Mount a read-only filesystem for `agent_memory/agent_ro_a/` or set restrictive permissions. <br> 2. Call `append_to_memory_file("agent_ro_a", "file.txt", "data")`.   | `FileOperationError` raised, wrapping `OSError`. No file modified/created. <br> Logger error.                                               | Medium   |
| AMS_APPEND_N_006   | Attempt to append using an empty `relative_file_path`.                               | 1. Initialize service. <br> 2. Call `append_to_memory_file("agent_a_inv", "", "content")`.                                                                         | `InvalidPathError` (from `_resolve_safe_path`). No file modified/created.                                                                    | High     |
| AMS_APPEND_N_007   | Attempt to append using an absolute `relative_file_path`.                            | 1. Initialize service. <br> 2. Call `append_to_memory_file("agent_a_inv", "/tmp/mylog.txt", "content")`.                                                          | `InvalidPathError` (from `_resolve_safe_path`). No file modified/created.                                                                    | High     |
| AMS_APPEND_N_008   | Parent directory creation for file fails (e.g. permissions).                         | 1. Create `agent_memory/agent_a_p_fail/` with restrictive permissions. <br> 2. Call `append_to_memory_file("agent_a_p_fail", "subdir/file.txt", "data")`.       | `FileOperationError` raised (from `safe_path.parent.mkdir`). No file modified/created. <br> Logger error.                                    | Medium   |

## 6. Acceptance Criteria Mapping

This section maps the Acceptance Criteria from `context.md#3-acceptance-criteria` to the test cases defined above.

*   **AC for User Story 1 (Read Memory):**
    *   Valid read: AMS_READ_P_001, AMS_READ_P_002, AMS_READ_P_003
    *   Non-existent file: AMS_READ_N_001
    *   Invalid agent ID: AMS_READ_N_002 (covers general invalid agent ID concept through path error)
    *   Path traversal: AMS_READ_N_003
*   **AC for User Story 2 (Write/Overwrite Memory):**
    *   Valid write/overwrite: AMS_WRITE_P_001, AMS_WRITE_P_002, AMS_WRITE_P_003, AMS_WRITE_P_004, AMS_WRITE_P_005
    *   Path traversal: AMS_WRITE_N_002
    *   (Invalid agent ID for write is covered by AMS_WRITE_N_001)
*   **AC for User Story 3 (Append to Memory):**
    *   Append to existing: AMS_APPEND_P_001, AMS_APPEND_P_004, AMS_APPEND_P_005
    *   Append to non-existent (creates file): AMS_APPEND_P_002, AMS_APPEND_P_003, AMS_APPEND_P_006
    *   Path traversal: AMS_APPEND_N_002
    *   (Invalid agent ID for append is covered by AMS_APPEND_N_001)

**General ACs covered by various negative/error handling test cases:**
*   Invalid path errors: AMS_GAMP_003-006, AMS_RSP_003-006, AMS_RSP_010, AMS_READ_N_004, AMS_READ_N_007, AMS_READ_N_008, AMS_WRITE_N_003, AMS_WRITE_N_006, AMS_WRITE_N_007, AMS_APPEND_N_003, AMS_APPEND_N_006, AMS_APPEND_N_007.
*   Agent not found / access errors: AMS_GAMP_007, AMS_RSP_007, AMS_RSP_008, AMS_READ_N_005, AMS_WRITE_N_004, AMS_APPEND_N_004.
*   File operation errors (permissions): AMS_INIT_003, AMS_READ_N_006, AMS_WRITE_N_005, AMS_WRITE_N_008, AMS_APPEND_N_005, AMS_APPEND_N_008.

## 7. Test Data Requirements
*   Various text strings for file content, including empty strings, single lines, multiple lines, and strings with UTF-8 characters.
*   Valid and invalid `agent_instance_id` strings.
*   Valid and invalid `relative_file_path` strings, including paths with subdirectories, '..', and absolute paths.

## 8. Reporting
*   Test execution results will be documented separately.
*   Bugs will be logged in the feature's `active_log.md` as per project guidelines.