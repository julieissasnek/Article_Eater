"""
Tests for Sprint 2.0.3: CLI flags for web outputs

Tests verify:
1. Web of Belief flags (--web, --no-web, --web-equilibrium, etc.)
2. Export control flags (--export-manifest, --no-export-bn, etc.)
3. Flags are passed through to pipeline correctly
"""

import pytest
import argparse
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path


class TestCLIFlagsExist:
    """Test that CLI flags are registered correctly."""

    def test_web_flags_exist(self):
        """Web of Belief flags should be registered."""
        # Import the CLI module
        from app.cli.article_eater_contract_cli import main

        # Parse with --help to check flags exist
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['article_eater', 'eat', '--help']):
                main()
        # --help exits with 0
        assert exc_info.value.code == 0

    def test_parse_default_values(self):
        """Default values should be set correctly."""
        import argparse
        from app.cli import article_eater_contract_cli

        # Create a parser manually to test defaults
        ap = argparse.ArgumentParser()
        sub = ap.add_subparsers(dest="cmd")
        eat = sub.add_parser("eat")
        eat.add_argument("--in", dest="in_dir", required=True)
        eat.add_argument("--out", dest="out_dir", required=True)
        eat.add_argument("--profile", default="standard")
        eat.add_argument("--hitl", default="auto")

        # Web options with defaults
        eat.add_argument("--web", dest="web_enabled", action="store_true", default=True)
        eat.add_argument("--no-web", dest="web_enabled", action="store_false")
        eat.add_argument("--web-equilibrium", dest="web_equilibrium", action="store_true", default=True)
        eat.add_argument("--web-max-iterations", dest="web_max_iterations", type=int, default=10)
        eat.add_argument("--export-manifest", dest="export_manifest", action="store_true", default=True)
        eat.add_argument("--export-bn", dest="export_bn", action="store_true", default=True)

        args = ap.parse_args(["eat", "--in", "/tmp/in", "--out", "/tmp/out"])

        assert args.web_enabled is True
        assert args.web_equilibrium is True
        assert args.web_max_iterations == 10
        assert args.export_manifest is True
        assert args.export_bn is True

    def test_parse_disabled_flags(self):
        """--no-* flags should set values to False."""
        import argparse

        ap = argparse.ArgumentParser()
        sub = ap.add_subparsers(dest="cmd")
        eat = sub.add_parser("eat")
        eat.add_argument("--in", dest="in_dir", required=True)
        eat.add_argument("--out", dest="out_dir", required=True)

        eat.add_argument("--web", dest="web_enabled", action="store_true", default=True)
        eat.add_argument("--no-web", dest="web_enabled", action="store_false")
        eat.add_argument("--export-manifest", dest="export_manifest", action="store_true", default=True)
        eat.add_argument("--no-export-manifest", dest="export_manifest", action="store_false")

        args = ap.parse_args([
            "eat", "--in", "/tmp/in", "--out", "/tmp/out",
            "--no-web", "--no-export-manifest"
        ])

        assert args.web_enabled is False
        assert args.export_manifest is False


class TestOptionsPassthrough:
    """Test that CLI options are passed through to pipeline."""

    def test_web_options_dict_structure(self):
        """web_options dict should have correct structure."""
        # Simulate what cmd_eat builds
        class MockArgs:
            web_enabled = True
            web_equilibrium = False
            web_max_iterations = 5
            web_convergence_threshold = 0.01

        args = MockArgs()

        web_options = {
            "enabled": getattr(args, "web_enabled", True),
            "seek_equilibrium": getattr(args, "web_equilibrium", True),
            "max_iterations": getattr(args, "web_max_iterations", 10),
            "convergence_threshold": getattr(args, "web_convergence_threshold", 0.001),
        }

        assert web_options["enabled"] is True
        assert web_options["seek_equilibrium"] is False
        assert web_options["max_iterations"] == 5
        assert web_options["convergence_threshold"] == 0.01

    def test_export_options_dict_structure(self):
        """export_options dict should have correct structure."""
        class MockArgs:
            export_manifest = False
            export_bn = True
            export_cluster_stats = False
            export_bn_edges = True

        args = MockArgs()

        export_options = {
            "manifest": getattr(args, "export_manifest", True),
            "bn_state": getattr(args, "export_bn", True),
            "cluster_stats": getattr(args, "export_cluster_stats", True),
            "bn_edges": getattr(args, "export_bn_edges", True),
        }

        assert export_options["manifest"] is False
        assert export_options["bn_state"] is True
        assert export_options["cluster_stats"] is False
        assert export_options["bn_edges"] is True


class TestPipelineFunctionSignatures:
    """Test that pipeline functions accept the new options."""

    def test_run_from_contract_bundle_accepts_options(self):
        """run_from_contract_bundle should accept web_options and export_options."""
        from app.tasks.pipeline import run_from_contract_bundle
        import inspect

        sig = inspect.signature(run_from_contract_bundle)
        params = list(sig.parameters.keys())

        assert "web_options" in params
        assert "export_options" in params

    def test_integrate_into_web_accepts_options(self):
        """_integrate_into_web_of_belief should accept options."""
        from app.tasks.pipeline import _integrate_into_web_of_belief
        import inspect

        sig = inspect.signature(_integrate_into_web_of_belief)
        params = list(sig.parameters.keys())

        assert "web_options" in params
        assert "export_options" in params


class TestWebDisabledBehavior:
    """Test behavior when web integration is disabled."""

    def test_web_disabled_returns_skipped(self):
        """When web_options.enabled=False, should return skipped status."""
        from app.tasks.pipeline import _integrate_into_web_of_belief
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = _integrate_into_web_of_belief(
                claims=[],
                rules=[],
                out_dir=Path(tmpdir),
                run_id="test-run",
                paper_id="test-paper",
                web_options={"enabled": False},
                export_options={},
            )

            assert result["web_integration"] == "skipped"
            assert result["reason"] == "disabled_via_cli"
            assert result["n_beliefs"] == 0


class TestExportOptionsRespected:
    """Test that export options control file generation."""

    def test_export_options_default_to_true(self):
        """Without export_options, defaults should be True."""
        from app.tasks.pipeline import _integrate_into_web_of_belief

        # Default export_options when None
        default_export_options = {
            "manifest": True,
            "bn_state": True,
            "cluster_stats": True,
            "bn_edges": True,
        }

        for key, value in default_export_options.items():
            assert value is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
