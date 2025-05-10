# Toolset & System Prompt Design Part C: Memory & Orchestration Tools

This document continues the detailed specification of the Core Toolset. Refer to `03a_toolset_overview_and_market_data.md` for the general toolset overview and response format.

---

### 4. Agent Memory Tools (Interacting with Agent's own cache directory)

These tools allow agents to persist and retrieve their operational data, logs, learned experiences, and configurations from their dedicated memory space in the backend cache directory.

*   **4.1 `read_agent_memory_file`**
    *   **Description:** Reads the content of a specified file (typically YAML or Markdown) from the calling agent's dedicated memory cache directory.
    *   **Invocation Format:**
        ```xml
        <read_agent_memory_file>
            <file_path>string</file_path> <!-- Relative path within the agent's memory dir, e.g., "analyst_logs/daily_analysis_2023-10-26.md" or "trader_config/BTCUSDT_strategy_params.yaml" -->
        </read_agent_memory_file>
        ```
    *   **Parameters:**
        *   `file_path` (string, required): The relative path to the memory file within the agent's own isolated memory space. Agents cannot access other agents' memory directly using this tool.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <memory_file_content file_path_read="string">
            <content_base64>string_base64_encoded</content_base64> <!-- Base64 encoded content of the file. Empty if file not found or empty. -->
            <file_exists>boolean</file_exists>
            <file_type_hint>YAML|MARKDOWN|TEXT|UNKNOWN</file_type_hint> <!-- Based on extension or content sniffing if possible -->
        </memory_file_content>
        ```
        *Error if file_path is invalid or access is denied.*

*   **4.2 `write_agent_memory_file`**
    *   **Description:** Writes (or overwrites if it exists) content to a specified file in the agent's memory cache directory. The `MemoryBankManager` will handle creation of subdirectories if needed.
    *   **Invocation Format:**
        ```xml
        <write_agent_memory_file>
            <file_path>string</file_path> <!-- Relative path, e.g., "market_beliefs/BTCUSDT_context.yaml" -->
            <content_base64>string_base64_encoded</content_base64> <!-- Base64 encoded content to write -->
            <file_type_hint>YAML|MARKDOWN|TEXT</file_type_hint> <!-- Optional: Hint for storage or future retrieval -->
        </write_agent_memory_file>
        ```
    *   **Parameters:**
        *   `file_path` (string, required): Relative path within the agent's memory space.
        *   `content_base64` (string, required): The content to be written, base64 encoded.
        *   `file_type_hint` (string, optional): A hint about the file type.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <memory_file_written file_path_written="string" status_message="File saved successfully." />
        ```

*   **4.3 `append_to_agent_memory_file`**
    *   **Description:** Appends new content to an existing file (typically Markdown logs or text files) in the agent's memory cache directory. If the file does not exist, it will be created.
    *   **Invocation Format:**
        ```xml
        <append_to_agent_memory_file>
            <file_path>string</file_path> <!-- e.g., "daily_activity_log.md" -->
            <content_to_append_base64>string_base64_encoded</content_to_append_base64> <!-- Base64 encoded content to append -->
            <ensure_newline_before_append>boolean</ensure_newline_before_append> <!-- Optional, default true. Adds a newline before appending if file not empty. -->
        </append_to_agent_memory_file>
        ```
    *   **Parameters:**
        *   `file_path` (string, required).
        *   `content_to_append_base64` (string, required).
        *   `ensure_newline_before_append` (boolean, optional).
    *   **Expected Output (Success Data Payload):**
        ```xml
        <memory_file_appended file_path_appended="string" status_message="Content appended successfully." />
        ```

---

### 5. System Orchestration & Agent Management Tools (Primarily for System Orchestrator Agent)

These tools enable the System Orchestrator Agent (SOA) to manage other specialized agents and system-level tasks based on user interactions.

*   **5.1 `create_new_agent_instance`**
    *   **Description:** Instructs the `AgentManager` module to create, initialize, and (optionally) start a new specialized agent instance (e.g., an Analyst Agent for a specific strategy, or a Trader Agent).
    *   **Invocation Format:**
        ```xml
        <create_new_agent_instance>
            <agent_type_template>string</agent_type_template> <!-- e.g., "AnalystAgent_LTECS_v1", "TraderAgent_Default_v1", "AnalystAgent_LARIMERS_v1" -->
            <agent_name_label>string</agent_name_label> <!-- User-friendly label for this instance, e.g., "My BTC Trend Analyst" -->
            <initial_config_json>string_json_object</initial_config_json> <!-- JSON string for agent-specific initial configuration (e.g., strategy parameters, target symbols, risk settings, links to other agents). This config is typically stored in the new agent's memory. -->
            <start_immediately>boolean</start_immediately> <!-- Optional, default "true". Whether to start the agent after creation. -->
        </create_new_agent_instance>
        ```
    *   **Parameters:**
        *   `agent_type_template` (string, required): Identifier for the type or template of agent to create.
        *   `agent_name_label` (string, required): A human-readable name for this instance.
        *   `initial_config_json` (string, required): JSON string containing initial parameters and settings for the new agent.
        *   `start_immediately` (boolean, optional).
    *   **Expected Output (Success Data Payload):**
        ```xml
        <agent_instance_created agent_id="string_uuid" agent_type_template="string" agent_name_label="string" status="INITIALIZED|RUNNING" />
        ```

*   **5.2 `dispatch_task_to_agent`**
    *   **Description:** Sends a specific task, message, or data payload to a designated running agent instance. Used for inter-agent communication or SOA-to-agent delegation.
    *   **Invocation Format:**
        ```xml
        <dispatch_task_to_agent>
            <target_agent_id>string_uuid</target_agent_id> <!-- The unique ID of the recipient agent instance -->
            <task_type>string</task_type> <!-- A string identifying the nature of the task, e.g., "NEW_MARKET_ANALYSIS_SIGNAL", "EXECUTE_TRADE_REQUEST", "CONFIGURATION_UPDATE_REQUIRED" -->
            <task_payload_json>string_json_object</task_payload_json> <!-- JSON string containing the actual data/parameters for the task -->
            <reply_expected>boolean</reply_expected> <!-- Optional, default "false". If true, SOA might expect a response from the target agent via another dispatch. -->
        </dispatch_task_to_agent>
        ```
    *   **Parameters:** As listed.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <task_dispatched_to_agent target_agent_id="string_uuid" dispatched_task_id="string_uuid_internal_task_ref" status="QUEUED_FOR_DELIVERY|DELIVERY_ACKNOWLEDGED" />
        ```

*   **5.3 `schedule_background_job`**
    *   **Description:** Instructs the system's `TaskScheduler` module to set up a recurring or one-time background job. This job, when triggered, will typically result in a task being dispatched to a specified agent.
    *   **Invocation Format:**
        ```xml
        <schedule_background_job>
            <job_name>string</job_name> <!-- A unique, human-readable name for the job, e.g., "BTC_1h_TrendAnalysis_LTECS" -->
            <job_type_identifier>string</job_type_identifier> <!-- An identifier for the type of job, e.g., "PERIODIC_AGENT_TRIGGER", "ONE_TIME_NOTIFICATION" -->
            <cron_expression>string</cron_expression> <!-- Optional: For cron-style scheduling (e.g., "*/15 * * * *" for every 15 minutes). If not provided, interval_seconds must be. -->
            <interval_seconds>integer</interval_seconds> <!-- Optional: For simple interval-based scheduling (e.g., 300 for every 5 minutes). If not provided, cron_expression must be. -->
            <target_agent_id_on_trigger>string_uuid</target_agent_id_on_trigger> <!-- The agent instance ID to be notified or triggered when the job runs. -->
            <task_type_on_trigger>string</task_type_on_trigger> <!-- The task_type to be used when dispatching to the target agent. -->
            <task_payload_on_trigger_json>string_json_object</task_payload_on_trigger_json> <!-- The payload to send to the agent when the job triggers. -->
            <enabled_on_create>boolean</enabled_on_create> <!-- Optional, default "true". -->
        </schedule_background_job>
        ```
    *   **Parameters:** As listed.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <background_job_scheduled internal_job_id="string_uuid_system_job_id" job_name="string" status="SCHEDULED_AND_ACTIVE|SCHEDULED_BUT_DISABLED" next_run_time_utc_iso="string_datetime_iso" />
        ```

*   **5.4 `send_notification`**
    *   **Description:** Sends a notification message to the user via one or more configured channels (e.g., Telegram, UI alert within the web application).
    *   **Invocation Format:**
        ```xml
        <send_notification>
            <channels> <!-- At least one channel required -->
                <channel>string</channel> <!-- "TELEGRAM", "UI_ALERT", "EMAIL" (MVP focuses on TELEGRAM and UI_ALERT) -->
            </channels>
            <message_text>string</message_text> <!-- The core message content. -->
            <subject_text>string</subject_text> <!-- Optional, for channels like EMAIL. -->
            <urgency_level>string</urgency_level> <!-- Optional: "LOW", "MEDIUM", "HIGH", "CRITICAL". Default: "MEDIUM". Affects presentation. -->
        </send_notification>
        ```
    *   **Parameters:** As listed.
    *   **Expected Output (Success Data Payload):**
        ```xml
        <notification_sent_status>
            <channel_status channel="TELEGRAM" delivery_status="SUCCESS|PENDING|FAILED" message_id_or_error="string" />
            <channel_status channel="UI_ALERT" delivery_status="SUCCESS|PENDING|FAILED" message_id_or_error="string" />
            <!-- ... status for each requested channel ... -->
        </notification_sent_status>