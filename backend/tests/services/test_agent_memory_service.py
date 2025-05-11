import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import shutil # For cleaning up test directories
import os

# Adjust the Python path to import the service
# This might be handled by a test runner or conftest.py in a larger project
import sys
# Assuming the test is run from the project root or a similar context
# where 'backend' is a subdirectory.
# If this script is in backend/tests/services, and agent_memory_service is in backend/src/services
# we need to go up two levels to reach the project root, then into backend/src/services
# Or, more simply, if 'backend' is in PYTHONPATH or tests are run with 'python -m unittest discover' from root.
# For robustness in varying execution contexts, let's try to add backend/src to path.
# This is a common pattern for tests.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent 
# backend/tests/services/test_agent_memory_service.py -> backend/tests/services -> backend/tests -> backend -> project_root
# This assumes a structure like:
# project_root/
#   backend/
#     src/
#       services/
#         agent_memory_service.py
#     tests/
#       services/
#         test_agent_memory_service.py

# A more direct relative path if tests are always run from a context where 'backend' is accessible
# or if backend itself is a package.
# Let's assume this test file is at vibetrade/backend/tests/services/test_agent_memory_service.py
# and the service is at vibetrade/backend/src/services/agent_memory_service.py
# We need to add vibetrade/backend/src to sys.path
# Path(__file__).resolve() gives path to this test file.
# .parent gives services dir. .parent.parent gives tests dir. .parent.parent.parent gives backend dir.
# So, backend_src_path = Path(__file__).resolve().parent.parent.parent / "src"
backend_src_path = Path(__file__).resolve().parent.parent.parent / "src"
sys.path.insert(0, str(backend_src_path))


from services.agent_memory_service import (
    AgentMemoryService,
    AgentMemoryError,
    AgentNotFoundError,
    AgentMemoryFileNotFoundError,
    InvalidPathError,
    FileOperationError
)

class TestAgentMemoryService(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for testing that can be cleaned up
        self.test_cache_root = Path("./test_app_cache_dir_temp")
        self.test_cache_root.mkdir(parents=True, exist_ok=True)
        self.service = AgentMemoryService(app_cache_dir=str(self.test_cache_root))
        self.agent_id = "test_agent_123"
        self.agent_memory_base = self.test_cache_root / "agent_memory"

    def tearDown(self):
        # Clean up the temporary directory
        if self.test_cache_root.exists():
            shutil.rmtree(self.test_cache_root)

    def test_initialization_creates_base_directory(self):
        self.assertTrue((self.test_cache_root / "agent_memory").exists())

    def test_get_agent_memory_path_creates_agent_directory(self):
        agent_path = self.service._get_agent_memory_path(self.agent_id)
        expected_path = self.agent_memory_base / self.agent_id
        self.assertEqual(agent_path, expected_path)
        self.assertTrue(expected_path.exists())
        self.assertTrue(expected_path.is_dir())

    def test_get_agent_memory_path_invalid_agent_id(self):
        with self.assertRaisesRegex(InvalidPathError, "Invalid agent_instance_id"):
            self.service._get_agent_memory_path("invalid/agent")
        with self.assertRaisesRegex(InvalidPathError, "Invalid agent_instance_id"):
            self.service._get_agent_memory_path("../another_agent")
        with self.assertRaisesRegex(InvalidPathError, "Invalid agent_instance_id"):
            self.service._get_agent_memory_path("")

    @patch('pathlib.Path.mkdir')
    def test_get_agent_memory_path_os_error_on_mkdir(self, mock_mkdir):
        mock_mkdir.side_effect = OSError("Test OS Error")
        with self.assertRaisesRegex(AgentNotFoundError, "Could not create or access agent memory directory"):
            self.service._get_agent_memory_path("agent_mkdir_fail")

    def test_resolve_safe_path_valid(self):
        relative_path = "notes/file.txt"
        # Ensure agent dir exists first
        self.service._get_agent_memory_path(self.agent_id)
        
        safe_path = self.service._resolve_safe_path(self.agent_id, relative_path)
        expected_path = (self.agent_memory_base / self.agent_id / relative_path).resolve()
        self.assertEqual(safe_path, expected_path)

    def test_resolve_safe_path_empty_relative_path(self):
        with self.assertRaisesRegex(InvalidPathError, "Relative file path cannot be empty"):
            self.service._resolve_safe_path(self.agent_id, "")

    def test_resolve_safe_path_absolute_path_disallowed(self):
        # Path.is_absolute() behavior varies by OS. On Unix, "/abs/path" is absolute.
        # On Windows, "C:\\abs\\path" is.
        # The service's lstrip('/') should handle Unix-like absolute paths.
        with self.assertRaisesRegex(InvalidPathError, "Absolute paths are not allowed: /etc/passwd"):
            self.service._resolve_safe_path(self.agent_id, "/etc/passwd")

        if os.name == 'nt': # pragma: no cover
            with self.assertRaisesRegex(InvalidPathError, r"Absolute paths are not allowed: C:\\windows\\system32"):
                self.service._resolve_safe_path(self.agent_id, "C:\\windows\\system32")
        # No else needed, the first case covers Unix-like absolute paths well.


    def test_resolve_safe_path_traversal_attempt_dot_dot(self):
        with self.assertRaisesRegex(InvalidPathError, "Path traversal attempt detected"):
            self.service._resolve_safe_path(self.agent_id, "../file.txt")
        with self.assertRaisesRegex(InvalidPathError, "Path traversal attempt detected"):
            self.service._resolve_safe_path(self.agent_id, "some_dir/../../elsewhere.txt")

    @patch.object(AgentMemoryService, '_get_agent_memory_path')
    def test_resolve_safe_path_traversal_after_resolve(self, mock_get_agent_memory_path):
        # This tests the final check: if resolved_path.startswith(agent_root_path)
        agent_root = (self.agent_memory_base / self.agent_id).resolve()
        mock_get_agent_memory_path.return_value = agent_root

        # Craft a scenario where (agent_root / relative_file).resolve() might escape
        # This is hard to do reliably cross-platform if Path.resolve() is robust.
        # The primary defense is `if ".." in Path(normalized_relative_path_str).parts:`
        # And the final `startswith` check.
        # For this test, we assume _get_agent_memory_path works, and focus on _resolve_safe_path's logic.
        
        # Simulate a relative path that, when appended to agent_root and resolved,
        # somehow points outside. This is tricky because resolve() usually cleans ".."
        # So, let's assume a hypothetical symlink or a very specific ".." structure.
        # More practically, we can mock `resolve()` itself on the constructed path.
        
        constructed_path_mock = MagicMock(spec=Path)
        # Make it so (agent_root / relative_file_path) returns this mock
        with patch('pathlib.Path.__truediv__', return_value=constructed_path_mock) as mock_truediv:
            constructed_path_mock.resolve.return_value = Path("/some/other/place/outside.txt") # Resolved outside
            mock_truediv.return_value = constructed_path_mock # ensure truediv returns our mock

            with self.assertRaisesRegex(InvalidPathError, "is outside agent directory"):
                 self.service._resolve_safe_path(self.agent_id, "tricky_path.txt")


    def test_read_memory_file_success(self):
        file_path = "read_test.txt"
        content = "Hello, Agent Memory!"
        agent_dir = self.service._get_agent_memory_path(self.agent_id)
        (agent_dir / file_path).write_text(content, encoding="utf-8")

        read_content = self.service.read_memory_file(self.agent_id, file_path)
        self.assertEqual(read_content, content)

    def test_read_memory_file_not_found(self):
        with self.assertRaises(AgentMemoryFileNotFoundError):
            self.service.read_memory_file(self.agent_id, "non_existent_file.txt")

    def test_read_memory_file_is_directory(self):
        dir_path_relative = "a_directory"
        agent_dir = self.service._get_agent_memory_path(self.agent_id)
        (agent_dir / dir_path_relative).mkdir()
        with self.assertRaisesRegex(InvalidPathError, "Path is a directory, not a file"):
            self.service.read_memory_file(self.agent_id, dir_path_relative)

    @patch.object(Path, 'read_text')
    def test_read_memory_file_os_error(self, mock_read_text):
        mock_read_text.side_effect = OSError("Test OS Read Error")
        # Need to create a dummy file for _resolve_safe_path to find
        file_path = "os_error_read.txt"
        agent_dir = self.service._get_agent_memory_path(self.agent_id)
        (agent_dir / file_path).write_text("dummy", encoding="utf-8")

        with self.assertRaisesRegex(FileOperationError, "Error reading file"):
            self.service.read_memory_file(self.agent_id, file_path)

    def test_write_memory_file_success_new_file(self):
        file_path = "write_test.txt"
        content = "Writing new data."
        # Directory for file should be created by write_memory_file
        nested_file_path = "subdir/write_test.txt"

        self.service.write_memory_file(self.agent_id, nested_file_path, content)
        
        expected_full_path = self.agent_memory_base / self.agent_id / nested_file_path
        self.assertTrue(expected_full_path.exists())
        self.assertEqual(expected_full_path.read_text(encoding="utf-8"), content)
        self.assertTrue(expected_full_path.parent.exists()) # Check parent dir creation

    def test_write_memory_file_success_overwrite_file(self):
        file_path = "overwrite_test.txt"
        initial_content = "Initial."
        new_content = "Overwritten."
        
        agent_dir = self.service._get_agent_memory_path(self.agent_id)
        full_path = agent_dir / file_path
        full_path.write_text(initial_content, encoding="utf-8")

        self.service.write_memory_file(self.agent_id, file_path, new_content)
        self.assertEqual(full_path.read_text(encoding="utf-8"), new_content)

    def test_write_memory_file_is_directory(self):
        dir_path_relative = "another_dir"
        agent_dir = self.service._get_agent_memory_path(self.agent_id)
        (agent_dir / dir_path_relative).mkdir(parents=True, exist_ok=True)
        with self.assertRaisesRegex(InvalidPathError, "Path is a directory, cannot write"):
            self.service.write_memory_file(self.agent_id, dir_path_relative, "content")

    @patch.object(Path, 'write_text')
    def test_write_memory_file_os_error(self, mock_write_text):
        mock_write_text.side_effect = OSError("Test OS Write Error")
        file_path = "os_error_write.txt"
        # _resolve_safe_path will run, _get_agent_memory_path ensures agent dir
        self.service._get_agent_memory_path(self.agent_id) 
        
        with self.assertRaisesRegex(FileOperationError, "Error writing file"):
            self.service.write_memory_file(self.agent_id, file_path, "content")
            
    @patch.object(Path, 'mkdir', autospec=True) # Added autospec=True
    def test_write_memory_file_parent_dir_creation_fails(self, mock_mkdir):
        # mock_mkdir is now an autospec'd mock of Path.mkdir
        # Its side_effect function will receive the Path instance as the first argument.

        # Target mkdir for parent directory of the file
        # The first mkdir for agent_path itself in _get_agent_memory_path should succeed.
        # The second mkdir for safe_path.parent in write_memory_file should fail.
        
        # Let _get_agent_memory_path succeed normally
        agent_dir_path_obj = self.agent_memory_base / self.agent_id
        
        # Configure mock_mkdir: first call (for agent dir) passes, subsequent (for parent) fails
        # mock_mkdir is patching Path.mkdir.
        # The first argument to the side_effect function will be the Path instance (self for mkdir).
        original_mkdir = Path.mkdir # Save original for passthrough if needed, though not used here.

        def selective_fail_mkdir(path_instance, mode=0o777, parents=False, exist_ok=False):
            # Define the specific path whose creation should fail
            # This is safe_path.parent in write_memory_file, where safe_path is for "new_subdir/file.txt"
            # So, the parent is "new_subdir" relative to agent's root.
            # Resolve it to match how safe_path.parent would be (already resolved).
            parent_dir_to_fail = (self.agent_memory_base / self.agent_id / "new_subdir").resolve()

            # path_instance is the 'self' of the Path.mkdir call, so it's already a Path object.
            # We should resolve it too for a canonical comparison.
            if path_instance.resolve() == parent_dir_to_fail:
                raise OSError("Simulated OSError for parent directory creation")
            else:
                # For any other path (e.g., self.base_memory_path or agent_id path),
                # let the actual mkdir proceed or simulate success.
                # To avoid complex passthrough, we'll just return None (like successful mock).
                # This assumes that other necessary directories (like agent root) are either
                # already created by setUp or their creation isn't the focus of this specific mock.
                # In our case, self.service._get_agent_memory_path() would have been called
                # implicitly by _resolve_safe_path, which calls Path.mkdir for agent root.
                # We need that call to succeed.
                # The mock applies to ALL Path.mkdir calls.
                # So, base_memory_path.mkdir() in __init__ and agent_path.mkdir() in _get_agent_memory_path also use this mock.
                if path_instance == self.service.base_memory_path or \
                   path_instance == (self.service.base_memory_path / self.agent_id):
                    # Simulate success for these essential setup mkdir calls
                    return None
                # If it's not the one we are targeting to fail, and not the essential setup ones,
                # it's an unexpected mkdir call in this test's context.
                # However, for simplicity, we'll assume any other call should also succeed.
                return None


        mock_mkdir.side_effect = selective_fail_mkdir
        
        with self.assertRaisesRegex(FileOperationError, "Could not create parent directory for new_subdir/file.txt"):
            self.service.write_memory_file(self.agent_id, "new_subdir/file.txt", "content")


    def test_append_to_memory_file_success_existing_file(self):
        file_path = "append_test_existing.txt"
        initial_content = "Line 1\n"
        append_content = "Line 2\n"
        expected_content = initial_content + append_content

        agent_dir = self.service._get_agent_memory_path(self.agent_id)
        full_path = agent_dir / file_path
        full_path.write_text(initial_content, encoding="utf-8")

        self.service.append_to_memory_file(self.agent_id, file_path, append_content)
        self.assertEqual(full_path.read_text(encoding="utf-8"), expected_content)

    def test_append_to_memory_file_success_new_file(self):
        file_path = "append_test_new.txt"
        content = "First line for new append file."
        nested_file_path = "append_subdir/new_file.txt"

        self.service.append_to_memory_file(self.agent_id, nested_file_path, content)
        
        expected_full_path = self.agent_memory_base / self.agent_id / nested_file_path
        self.assertTrue(expected_full_path.exists())
        self.assertEqual(expected_full_path.read_text(encoding="utf-8"), content)
        self.assertTrue(expected_full_path.parent.exists())

    def test_append_to_memory_file_is_directory(self):
        dir_path_relative = "append_dir_test"
        agent_dir = self.service._get_agent_memory_path(self.agent_id)
        (agent_dir / dir_path_relative).mkdir(parents=True, exist_ok=True)
        with self.assertRaisesRegex(InvalidPathError, "Path is a directory, cannot append"):
            self.service.append_to_memory_file(self.agent_id, dir_path_relative, "content")

    @patch.object(Path, 'open', new_callable=mock_open)
    def test_append_to_memory_file_os_error_on_open(self, mock_path_open):
        mock_path_open.side_effect = OSError("Test OS Append Error on open")
        file_path = "os_error_append_open.txt"
        # _resolve_safe_path needs to work, so agent dir needs to exist.
        self.service._get_agent_memory_path(self.agent_id)
        # Parent dir for file also needs to exist for the open call to be reached
        (self.agent_memory_base / self.agent_id / Path(file_path).parent).mkdir(parents=True, exist_ok=True)


        with self.assertRaisesRegex(FileOperationError, "Error appending to file"):
            self.service.append_to_memory_file(self.agent_id, file_path, "content")

    @patch.object(Path, 'open', new_callable=mock_open)
    def test_append_to_memory_file_os_error_on_write(self, mock_path_open):
        # Mock open to succeed, but the write call on the file handle to fail
        mock_file_handle = MagicMock()
        mock_file_handle.write.side_effect = OSError("Test OS Append Error on write")
        mock_path_open.return_value.__enter__.return_value = mock_file_handle # for 'with open(...) as f:'

        file_path = "os_error_append_write.txt"
        self.service._get_agent_memory_path(self.agent_id)
        (self.agent_memory_base / self.agent_id / Path(file_path).parent).mkdir(parents=True, exist_ok=True)

        with self.assertRaisesRegex(FileOperationError, "Error appending to file"):
            self.service.append_to_memory_file(self.agent_id, file_path, "content")


if __name__ == '__main__': # pragma: no cover
    unittest.main(argv=['first-arg-is-ignored'], exit=False)