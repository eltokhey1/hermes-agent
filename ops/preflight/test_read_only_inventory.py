"""Hermes P0 inventory tests. Temporary Git repos only; no actual Hermes access."""
import contextlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from read_only_inventory import _counts, collect, main, SCHEMA, InventoryError


def git(repo: Path, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo-private-username"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.invalid")
        git(self.repo, "config", "user.name", "Test Fixture")
        (self.repo / "README.md").write_text("metadata only", encoding="utf-8")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-q", "-m", "fixture")

    def test_clean_repo(self):
        report = collect(self.repo)
        self.assertEqual(report["schema"], SCHEMA)
        self.assertTrue(report["branch_is_main"])
        self.assertFalse(report["working_tree_dirty"])
        self.assertEqual(report["tracked_changes"], 0)
        self.assertFalse(report["configured_remote_present"])
        self.assertEqual(len(report["head_sha"]), 40)

    def test_secret_filename_and_repo_path_never_emitted(self):
        secret_name = "TOP_SECRET_PASSWORD_12345.txt"
        (self.repo / secret_name).write_text("do not read me", encoding="utf-8")
        git(self.repo, "remote", "add", "origin", "https://username:password@example.invalid/org/repo.git")
        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["--repo", str(self.repo)])
        output = buf.getvalue()
        self.assertEqual(code, 0)
        for forbidden in [secret_name, str(self.repo), "TOP_SECRET", "password", "example.invalid", "origin"]:
            self.assertNotIn(forbidden, output)
        obj = json.loads(output)
        self.assertTrue(obj["working_tree_dirty"])
        self.assertEqual(obj["untracked_entries"], 1)
        self.assertTrue(obj["configured_remote_present"])

    def test_modified_tracked_file(self):
        (self.repo / "README.md").write_text("changed", encoding="utf-8")
        r = collect(self.repo)
        self.assertTrue(r["working_tree_dirty"])
        self.assertEqual(r["tracked_changes"], 1)

    def test_child_directory_of_parent_repo_is_rejected(self):
        child = self.repo / "workspace" / "hermes-agent-install"
        child.mkdir(parents=True)
        with self.assertRaises(InventoryError) as caught:
            collect(child)
        self.assertEqual(caught.exception.code, "REPOSITORY_ROOT_MISMATCH")

        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = main(["--repo", str(child)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(json.loads(buf.getvalue())["error_code"], "REPOSITORY_ROOT_MISMATCH")
        self.assertNotIn(str(child), buf.getvalue())

    def test_nested_independent_git_repo_is_accepted(self):
        child = self.repo / "isolated-hermes-checkout"
        child.mkdir()
        git(child, "init", "-q", "-b", "main")
        git(child, "config", "user.email", "test@example.invalid")
        git(child, "config", "user.name", "Test Fixture")
        (child / "README.md").write_text("nested repo fixture", encoding="utf-8")
        git(child, "add", "README.md")
        git(child, "commit", "-q", "-m", "nested fixture")
        report = collect(child)
        self.assertTrue(report["repository_detected"])
        self.assertFalse(report["working_tree_dirty"])

    def test_aggregates_only(self):
        self.assertEqual(_counts(" M private.txt\n?? untracked.txt"),
                         {"tracked_changes": 1, "untracked_entries": 1, "working_tree_dirty": True})
        self.assertEqual(_counts(""),
                         {"tracked_changes": 0, "untracked_entries": 0, "working_tree_dirty": False})

    def test_non_repo_reports_only_safe_error_code(self):
        other = Path(self.tmp.name) / "not-git"
        other.mkdir()
        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["--repo", str(other)])
        self.assertEqual(code, 2)
        result = json.loads(buf.getvalue())
        self.assertEqual(result["error_code"], "NOT_A_GIT_REPOSITORY")
        self.assertNotIn(str(other), buf.getvalue())

    def test_failing_git_does_not_echo_error_details(self):
        with patch("read_only_inventory._git", side_effect=__import__("read_only_inventory").InventoryError("GIT_COMMAND_FAILED")):
            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                code = main(["--repo", str(self.repo)])
            self.assertEqual(code, 2)
            self.assertNotIn(str(self.repo), buf.getvalue())


    def test_windows_localappdata_missing_is_unknown(self):
        with patch("read_only_inventory._is_windows", return_value=True), patch.dict(
            "read_only_inventory.os.environ", {"LOCALAPPDATA": ""}
        ):
            result = collect(self.repo)
        self.assertIsNone(result["hermes_windows_install_directory_present"])

    def test_windows_localappdata_relative_is_unknown(self):
        with patch("read_only_inventory._is_windows", return_value=True), patch.dict(
            "read_only_inventory.os.environ", {"LOCALAPPDATA": "relative-folder"}
        ):
            result = collect(self.repo)
        self.assertIsNone(result["hermes_windows_install_directory_present"])

    def test_windows_localappdata_absolute_detects_directory(self):
        local_app = Path(self.tmp.name) / "LocalAppData"
        (local_app / "hermes").mkdir(parents=True)
        with patch("read_only_inventory._is_windows", return_value=True), patch.dict(
            "read_only_inventory.os.environ", {"LOCALAPPDATA": str(local_app)}
        ):
            result = collect(self.repo)
        self.assertTrue(result["hermes_windows_install_directory_present"])

    def test_git_trace_env_does_not_create_file(self):
        trace = Path(self.tmp.name) / "unexpected-git-trace.log"
        with patch.dict(__import__("os").environ, {"GIT_TRACE": str(trace)}):
            report = collect(self.repo)
        self.assertTrue(report["repository_detected"])
        self.assertFalse(trace.exists(), "inventory must not write Git trace files")

    def test_git_trace2_event_env_does_not_create_file(self):
        trace = Path(self.tmp.name) / "unexpected-git-trace2.json"
        with patch.dict(__import__("os").environ, {"GIT_TRACE2_EVENT": str(trace)}):
            report = collect(self.repo)
        self.assertTrue(report["repository_detected"])
        self.assertFalse(trace.exists(), "inventory must not write Git trace2 files")

    def test_unicode_line_separator_filename_is_one_untracked_entry(self):
        # core.quotePath=false allows U+2028 inside a porcelain-v1 filename.
        # str.splitlines() mistakes that character for an extra status record.
        git(self.repo, "config", "core.quotePath", "false")
        (self.repo / "private\u2028name.txt").write_text("fixture", encoding="utf-8")
        report = collect(self.repo)
        self.assertTrue(report["working_tree_dirty"])
        self.assertEqual(report["untracked_entries"], 1)
        self.assertEqual(report["tracked_changes"], 0)

    def test_dirty_submodule_is_not_reported_clean(self):
        # All fixture repositories are local; no network or production checkout.
        child = Path(self.tmp.name) / "local-submodule"
        child.mkdir()
        git(child, "init", "-q", "-b", "main")
        git(child, "config", "user.email", "test@example.invalid")
        git(child, "config", "user.name", "Test Fixture")
        (child / "tracked.txt").write_text("initial", encoding="utf-8")
        git(child, "add", "tracked.txt")
        git(child, "commit", "-q", "-m", "fixture")

        git(self.repo, "-c", "protocol.file.allow=always", "submodule",
            "add", "-q", str(child), "deps/local")
        git(self.repo, "commit", "-q", "-m", "add local submodule")
        (self.repo / "deps" / "local" / "tracked.txt").write_text(
            "modified", encoding="utf-8"
        )
        report = collect(self.repo)
        self.assertTrue(report["working_tree_dirty"])
        self.assertEqual(1, report["tracked_changes"])

    def test_git_dir_env_does_not_change_repository_identity(self):
        unrelated = Path(self.tmp.name) / "unrelated.git"
        subprocess.run(["git", "init", "-q", "--bare", str(unrelated)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with patch.dict(__import__("os").environ, {"GIT_DIR": str(unrelated)}):
            report = collect(self.repo)
        sha = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()
        self.assertEqual(report["head_sha"], sha)


if __name__ == "__main__":
    unittest.main()
