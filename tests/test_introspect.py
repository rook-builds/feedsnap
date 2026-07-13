"""Tests for ACLI introspection (feedsnap introspect / feedsnap skill)."""
from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from feedsnap import __version__
from feedsnap.cli import main
from feedsnap.introspect import ACLI_VERSION, get_introspect_json, get_skill_md


# ---------------------------------------------------------------------------
# get_introspect_json()
# ---------------------------------------------------------------------------


class TestGetIntrospectJson:
    def test_returns_valid_json(self):
        output = get_introspect_json()
        data = json.loads(output)  # must not raise
        assert isinstance(data, dict)

    def test_top_level_fields_present(self):
        data = json.loads(get_introspect_json())
        assert data["name"] == "feedsnap"
        assert data["version"] == __version__
        assert data["acli_version"] == ACLI_VERSION
        assert isinstance(data["commands"], list)
        assert len(data["commands"]) > 0

    def test_snap_command_present(self):
        data = json.loads(get_introspect_json())
        names = [c["name"] for c in data["commands"]]
        assert "snap" in names

    def test_introspect_command_listed(self):
        data = json.loads(get_introspect_json())
        names = [c["name"] for c in data["commands"]]
        assert "introspect" in names

    def test_skill_command_listed(self):
        data = json.loads(get_introspect_json())
        names = [c["name"] for c in data["commands"]]
        assert "skill" in names

    def test_snap_has_options(self):
        data = json.loads(get_introspect_json())
        snap = next(c for c in data["commands"] if c["name"] == "snap")
        option_names = [o["name"] for o in snap["options"]]
        assert "--limit" in option_names
        assert "--format" in option_names
        assert "--since" in option_names
        assert "--dedup" in option_names

    def test_snap_has_examples(self):
        data = json.loads(get_introspect_json())
        snap = next(c for c in data["commands"] if c["name"] == "snap")
        assert len(snap["examples"]) >= 2
        for ex in snap["examples"]:
            assert "intent" in ex
            assert "command" in ex

    def test_indent_parameter(self):
        compact = get_introspect_json(indent=None)
        pretty = get_introspect_json(indent=4)
        # Compact should be shorter
        assert len(compact) < len(pretty)
        # Both must parse to the same structure
        assert json.loads(compact) == json.loads(pretty)


# ---------------------------------------------------------------------------
# get_skill_md()
# ---------------------------------------------------------------------------


class TestGetSkillMd:
    def test_returns_string(self):
        assert isinstance(get_skill_md(), str)

    def test_has_yaml_frontmatter(self):
        md = get_skill_md()
        assert md.startswith("---\n")
        # Second --- closes the frontmatter block
        assert "---" in md.split("\n", 1)[1]

    def test_frontmatter_has_required_fields(self):
        md = get_skill_md()
        assert "name: feedsnap" in md
        assert "description:" in md
        assert "when_to_use:" in md

    def test_contains_available_commands_section(self):
        assert "## Available commands" in get_skill_md()

    def test_contains_exit_codes_section(self):
        assert "## Exit codes" in get_skill_md()

    def test_contains_output_format_section(self):
        assert "## Output format" in get_skill_md()

    def test_contains_feedsnap_introspect_reference(self):
        assert "feedsnap introspect" in get_skill_md()


# ---------------------------------------------------------------------------
# CLI: feedsnap introspect
# ---------------------------------------------------------------------------


class TestCliIntrospect:
    def test_introspect_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["introspect"])
        assert result.exit_code == 0

    def test_introspect_outputs_valid_json(self):
        runner = CliRunner()
        result = runner.invoke(main, ["introspect"])
        data = json.loads(result.output)
        assert data["name"] == "feedsnap"

    def test_introspect_version_matches_package(self):
        runner = CliRunner()
        result = runner.invoke(main, ["introspect"])
        data = json.loads(result.output)
        assert data["version"] == __version__


# ---------------------------------------------------------------------------
# CLI: feedsnap skill
# ---------------------------------------------------------------------------


class TestCliSkill:
    def test_skill_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["skill"])
        assert result.exit_code == 0

    def test_skill_outputs_markdown_with_frontmatter(self):
        runner = CliRunner()
        result = runner.invoke(main, ["skill"])
        assert result.output.startswith("---\n")

    def test_skill_contains_feedsnap_name(self):
        runner = CliRunner()
        result = runner.invoke(main, ["skill"])
        assert "feedsnap" in result.output


# ---------------------------------------------------------------------------
# CLI: feedsnap --version
# ---------------------------------------------------------------------------


class TestCliVersion:
    def test_version_flag_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0

    def test_version_output_contains_version_string(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert __version__ in result.output
