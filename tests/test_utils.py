"""Tests for utility functions in md2pdf.utils."""

from pathlib import Path

import pytest

from md2pdf.utils import ensure_directory, find_markdown_files, get_output_path


class TestFindMarkdownFiles:
    """Tests for find_markdown_files function."""

    def test_find_markdown_files_single(self, temp_workspace):
        """Test finding markdown files in a flat directory."""
        input_dir = temp_workspace / "input"

        # Create test files
        (input_dir / "test1.md").write_text("# Test 1")
        (input_dir / "test2.md").write_text("# Test 2")
        (input_dir / "readme.txt").write_text("Not markdown")

        # Find markdown files
        files = find_markdown_files(input_dir)

        # Verify results
        assert len(files) == 2
        assert all(f.suffix == ".md" for f in files)
        assert all(f.parent == input_dir for f in files)
        # Results should be sorted
        assert files[0].name == "test1.md"
        assert files[1].name == "test2.md"

    def test_find_markdown_files_recursive(self, temp_workspace):
        """Test finding markdown files in nested directories."""
        input_dir = temp_workspace / "input"

        # Create nested structure
        (input_dir / "root.md").write_text("# Root")
        subdir1 = input_dir / "subdir1"
        subdir1.mkdir()
        (subdir1 / "sub1.md").write_text("# Sub 1")
        subdir2 = input_dir / "subdir2"
        subdir2.mkdir()
        (subdir2 / "sub2.md").write_text("# Sub 2")
        nested = subdir1 / "nested"
        nested.mkdir()
        (nested / "deep.md").write_text("# Deep")

        # Find all markdown files recursively
        files = find_markdown_files(input_dir)

        # Verify results
        assert len(files) == 4
        assert all(f.suffix == ".md" for f in files)
        # Check that all expected files are found
        file_names = {f.name for f in files}
        assert file_names == {"root.md", "sub1.md", "sub2.md", "deep.md"}

    def test_find_markdown_files_empty_directory(self, temp_workspace):
        """Test finding markdown files in an empty directory."""
        input_dir = temp_workspace / "input"

        # Find files in empty directory
        files = find_markdown_files(input_dir)

        # Verify no files found
        assert files == []

    def test_find_markdown_files_mixed_extensions(self, temp_workspace):
        """Test that only .md files are returned, not other extensions."""
        input_dir = temp_workspace / "input"

        # Create files with various extensions
        (input_dir / "test.md").write_text("# Markdown")
        (input_dir / "test.markdown").write_text("# Also Markdown")
        (input_dir / "test.txt").write_text("Text file")
        (input_dir / "test.pdf").write_text("PDF file")
        (input_dir / "README").write_text("No extension")

        # Find markdown files
        files = find_markdown_files(input_dir)

        # Verify only .md files are found
        assert len(files) == 1
        assert files[0].name == "test.md"


class TestGetOutputPath:
    """Tests for get_output_path function."""

    def test_get_output_path_preserve_structure(self, temp_workspace):
        """Test output path calculation with structure preservation."""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        # Create nested input file
        subdir = input_dir / "docs" / "section1"
        subdir.mkdir(parents=True)
        input_file = subdir / "test.md"
        input_file.write_text("# Test")

        # Calculate output path with structure preservation
        output_path = get_output_path(
            input_path=input_file,
            input_dir=input_dir,
            output_dir=output_dir,
            preserve_structure=True,
        )

        # Verify structure is preserved
        expected = output_dir / "docs" / "section1" / "test.pdf"
        assert output_path == expected
        assert output_path.name == "test.pdf"
        assert output_path.parent == output_dir / "docs" / "section1"

    def test_get_output_path_flatten(self, temp_workspace):
        """Test output path calculation without structure preservation."""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        # Create nested input file
        subdir = input_dir / "docs" / "section1"
        subdir.mkdir(parents=True)
        input_file = subdir / "test.md"
        input_file.write_text("# Test")

        # Calculate output path without structure preservation
        output_path = get_output_path(
            input_path=input_file,
            input_dir=input_dir,
            output_dir=output_dir,
            preserve_structure=False,
        )

        # Verify structure is flattened
        expected = output_dir / "test.pdf"
        assert output_path == expected
        assert output_path.parent == output_dir

    def test_get_output_path_edge_cases(self, temp_workspace):
        """Test output path calculation with edge cases."""
        input_dir = temp_workspace / "input"
        output_dir = temp_workspace / "output"

        # Test case 1: File with multiple dots in name
        file1 = input_dir / "test.backup.md"
        file1.write_text("# Test")
        path1 = get_output_path(file1, input_dir, output_dir, preserve_structure=False)
        assert path1.name == "test.backup.pdf"
        assert path1.suffix == ".pdf"

        # Test case 2: Deep nesting
        deep_dir = input_dir / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)
        file2 = deep_dir / "deep.md"
        file2.write_text("# Deep")
        path2 = get_output_path(file2, input_dir, output_dir, preserve_structure=True)
        assert path2 == output_dir / "a" / "b" / "c" / "d" / "e" / "deep.pdf"

        # Test case 3: Special characters in filename
        file3 = input_dir / "test-file_v2.md"
        file3.write_text("# Test")
        path3 = get_output_path(file3, input_dir, output_dir, preserve_structure=False)
        assert path3.name == "test-file_v2.pdf"


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_ensure_directory_creates_new(self, temp_workspace):
        """Test that ensure_directory creates a new directory."""
        new_dir = temp_workspace / "new" / "nested" / "path"

        # Verify directory doesn't exist
        assert not new_dir.exists()

        # Create directory
        ensure_directory(new_dir)

        # Verify directory was created
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_directory_already_exists(self, temp_workspace):
        """Test that ensure_directory is idempotent (safe to call multiple times)."""
        existing_dir = temp_workspace / "existing"
        existing_dir.mkdir()

        # Create a file in the directory to verify it's not affected
        test_file = existing_dir / "test.txt"
        test_file.write_text("test content")

        # Call ensure_directory on existing directory
        ensure_directory(existing_dir)

        # Verify directory still exists and file is intact
        assert existing_dir.exists()
        assert existing_dir.is_dir()
        assert test_file.exists()
        assert test_file.read_text() == "test content"
