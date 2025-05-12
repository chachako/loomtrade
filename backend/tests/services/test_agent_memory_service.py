import pytest
from pathlib import Path
from backend.src.services.agent_memory_service import (
    AgentMemoryService,
    AgentMemoryError,
    AgentNotFoundError,
    AgentMemoryFileNotFoundError,
    InvalidPathError,
    FileOperationError
)

TEST_APP_CACHE_DIR = "test_cache"
TEST_AGENT_ID = "test_agent_001"
TEST_FILE_NAME = "test_file.txt"
TEST_FILE_CONTENT = "This is a test file content."
MALICIOUS_AGENT_ID = "../test_agent_001"
MALICIOUS_RELATIVE_PATH = "../test_file.txt"

@pytest.fixture
def service(tmp_path: Path) -> AgentMemoryService:
    """Fixture to create an AgentMemoryService instance with a temporary cache directory."""
    cache_dir = tmp_path / TEST_APP_CACHE_DIR
    return AgentMemoryService(str(cache_dir))

@pytest.fixture
def agent_id() -> str:
    return TEST_AGENT_ID

@pytest.fixture
def agent_memory_path(service: AgentMemoryService, agent_id: str) -> Path:
    """Helper fixture to get the agent's memory path and ensure it exists."""
    return service._get_agent_memory_path(agent_id)

class TestAgentMemoryServiceRead:

    def test_read_memory_file_success(self, service: AgentMemoryService, agent_id: str, agent_memory_path: Path):
        """Test successful reading of a file."""
        file_path = agent_memory_path / TEST_FILE_NAME
        file_path.write_text(TEST_FILE_CONTENT, encoding="utf-8")

        content = service.read_memory_file(agent_id, TEST_FILE_NAME)
        assert content == TEST_FILE_CONTENT

    def test_read_memory_file_not_found(self, service: AgentMemoryService, agent_id: str):
        """Test reading a non-existent file."""
        with pytest.raises(AgentMemoryFileNotFoundError):
            service.read_memory_file(agent_id, "non_existent_file.txt")

    def test_read_memory_file_is_directory(self, service: AgentMemoryService, agent_id: str, agent_memory_path: Path):
        """Test attempting to read a directory as a file."""
        dir_name = "test_dir"
        (agent_memory_path / dir_name).mkdir()
        
        with pytest.raises(InvalidPathError) as excinfo:
            service.read_memory_file(agent_id, dir_name)
        assert "Path is a directory" in str(excinfo.value)

    def test_read_memory_file_invalid_agent_id_chars(self, service: AgentMemoryService):
        """Test read_memory_file with an agent_instance_id containing invalid characters."""
        with pytest.raises(InvalidPathError) as excinfo:
            service.read_memory_file(MALICIOUS_AGENT_ID, TEST_FILE_NAME)
        assert "Invalid characters in agent_instance_id" in str(excinfo.value)
        
        with pytest.raises(InvalidPathError) as excinfo:
            service.read_memory_file("agent/with/slash", TEST_FILE_NAME)
        assert "Invalid characters in agent_instance_id" in str(excinfo.value)

    def test_read_memory_file_relative_path_traversal(self, service: AgentMemoryService, agent_id: str):
        """Test read_memory_file with a relative_file_path containing '..'"""
        with pytest.raises(InvalidPathError) as excinfo:
            service.read_memory_file(agent_id, MALICIOUS_RELATIVE_PATH)
        assert "Path traversal attempt ('..') detected" in str(excinfo.value)

    def test_read_memory_file_empty_relative_path(self, service: AgentMemoryService, agent_id: str):
        """Test read_memory_file with an empty relative_file_path."""
        with pytest.raises(InvalidPathError) as excinfo:
            service.read_memory_file(agent_id, "")
        assert "Relative file path cannot be empty" in str(excinfo.value)

    def test_read_memory_file_absolute_relative_path(self, service: AgentMemoryService, agent_id: str, tmp_path: Path):
        """Test read_memory_file with a relative_file_path that is an absolute path."""
        absolute_path = str(tmp_path / "some_other_file.txt")
        with pytest.raises(InvalidPathError) as excinfo:
            service.read_memory_file(agent_id, absolute_path)
        assert "Absolute paths are not allowed" in str(excinfo.value)

    def test_read_memory_file_permission_error_mocked(self, service: AgentMemoryService, agent_id: str, agent_memory_path: Path, mocker):
        """Test read_memory_file when an OSError (e.g. permission denied) occurs during read."""
        file_path_str = TEST_FILE_NAME
        full_file_path = agent_memory_path / file_path_str
        
        # Create the file so _resolve_safe_path and initial checks pass
        full_file_path.write_text("initial content", encoding="utf-8")

        # Mock Path.read_text to raise an OSError
        mocker.patch.object(Path, 'read_text', side_effect=OSError("Permission denied"))
        
        with pytest.raises(FileOperationError) as excinfo:
            # We need to ensure the mocked Path object is the one whose read_text is called.
            # The service resolves the path internally. We rely on the mock patching all Path instances.
            service.read_memory_file(agent_id, file_path_str)
        assert "Error reading file" in str(excinfo.value)
        assert "Permission denied" in str(excinfo.value)

# TODO: Add tests for write_memory_file and append_to_memory_file in subsequent tasks.
# class TestAgentMemoryServiceWrite:
#     pass
# class TestAgentMemoryServiceAppend:
#     pass