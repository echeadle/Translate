"""Command-line interface for md2pdf."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from md2pdf.config import Config
from md2pdf.converter import ConversionError, InvalidMarkdownError, MarkdownConverter
from md2pdf.themes import get_theme_css, load_custom_css
from md2pdf.styles import get_page_css

console = Console()


def main(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        help="Markdown file or directory to convert",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output PDF file (single file mode only)",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-d",
        help="Output directory for PDFs (directory mode)",
    ),
    preserve_structure: bool = typer.Option(
        True,
        "--preserve-structure/--no-preserve-structure",
        help="Preserve directory structure in batch mode",
    ),
    create_output_dir: Optional[str] = typer.Option(
        None,
        "--create-output-dir",
        "-c",
        help="Create a subdirectory for output files (use 'auto' for timestamp or provide a name)",
    ),
    theme: Optional[str] = typer.Option(
        None,
        "--theme",
        help="Built-in theme (github, minimal, academic, dark, modern)",
    ),
    css: Optional[Path] = typer.Option(
        None,
        "--css",
        help="Path to custom CSS file",
    ),
    page_numbers: Optional[bool] = typer.Option(
        None,
        "--page-numbers/--no-page-numbers",
        help="Enable/disable page numbers in PDF footer (overrides .env)",
    ),
):
    """Convert markdown file(s) to PDF format.

    Examples:

        # Convert a single file
        md2pdf document.md

        # Convert with custom output name
        md2pdf document.md --output my_doc.pdf

        # Convert to timestamped subdirectory
        md2pdf document.md --create-output-dir auto

        # Convert to named subdirectory
        md2pdf document.md --create-output-dir my_pdfs

        # Convert entire directory
        md2pdf docs/

        # Convert directory with automatic subdirectory (keeps things organized)
        md2pdf docs/ --create-output-dir auto

        # Convert directory with custom output location
        md2pdf docs/ --output-dir pdfs/

        # Flatten directory structure
        md2pdf docs/ --no-preserve-structure
    """
    try:
        # Load configuration
        config = Config.load()
        config.validate()
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(2)

    # Apply CLI overrides to config
    if page_numbers is not None:
        config.enable_page_numbers = page_numbers

    # Validate theme and css flags (mutually exclusive)
    if theme and css:
        console.print(
            "[red]Error:[/red] Cannot use --theme and --css together.\n"
            "Choose one:\n"
            "  • --theme for built-in themes\n"
            "  • --css for custom CSS files"
        )
        raise typer.Exit(1)

    # Determine style source and generate CSS
    try:
        if css:
            style_css = load_custom_css(css)
        elif theme:
            style_css = get_theme_css(theme)
        else:
            style_css = get_theme_css("github")  # default
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Generate complete CSS (page + styling)
    page_css = get_page_css(config)
    final_css = page_css + style_css

    # Create converter with custom CSS
    converter = MarkdownConverter(config, css=final_css)

    # Handle create-output-dir option
    if create_output_dir is not None:
        if create_output_dir.lower() == "auto":
            # Create timestamped subdirectory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            subdir_name = f"converted_{timestamp}"
        else:
            # Use provided name
            subdir_name = create_output_dir

        # Adjust output paths based on whether it's file or directory mode
        if output_dir is None:
            base_output = Path(config.default_output_dir)
        else:
            base_output = output_dir

        output_dir = base_output / subdir_name

    # Determine if input is file or directory
    if input_path.is_file():
        # Single file mode
        if output_dir is not None and create_output_dir is None:
            console.print(
                "[yellow]Warning:[/yellow] --output-dir is ignored in single file mode (use --create-output-dir instead)"
            )

        # Determine output path
        if output is None:
            if create_output_dir is not None and output_dir is not None:
                # Use the created subdirectory
                output = output_dir / f"{input_path.stem}.pdf"
            else:
                # Default: same directory as input
                output = input_path.parent / f"{input_path.stem}.pdf"

        # Convert with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Converting {input_path.name}...", total=None)

            try:
                converter.convert_file(input_path, output)
                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] Created: {output}")
                sys.exit(0)
            except (InvalidMarkdownError, ConversionError) as e:
                progress.update(task, completed=True)
                console.print(f"[red]✗ Error:[/red] {e}")
                sys.exit(1)

    elif input_path.is_dir():
        # Directory mode
        if output is not None:
            console.print(
                "[yellow]Warning:[/yellow] --output is ignored in directory mode"
            )

        # Determine output directory
        if output_dir is None:
            output_dir = Path(config.default_output_dir)

        console.print(f"Converting markdown files in [cyan]{input_path}[/cyan]...")

        # Convert with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Converting files...", total=None)

            results = converter.convert_directory(
                input_path,
                output_dir,
                preserve_structure,
            )

            progress.update(task, completed=True)

        # Display results
        if not results:
            console.print("[yellow]No markdown files found.[/yellow]")
            sys.exit(0)

        success_count = sum(1 for r in results if r["success"])
        failure_count = len(results) - success_count

        # Create results table
        table = Table(title="Conversion Results")
        table.add_column("Status", style="bold")
        table.add_column("Input File")
        table.add_column("Output File")

        for result in results:
            if result["success"]:
                status = "[green]✓[/green]"
                output_str = str(result["output"])
            else:
                status = "[red]✗[/red]"
                output_str = f"[red]{result['error']}[/red]"

            table.add_row(
                status,
                str(result["input"].relative_to(input_path)),
                output_str,
            )

        console.print()
        console.print(table)
        console.print()

        # Summary
        if failure_count == 0:
            console.print(
                f"[green]✓ Successfully converted {success_count} file(s)[/green]"
            )
            sys.exit(0)
        elif success_count == 0:
            console.print(f"[red]✗ Failed to convert all {failure_count} file(s)[/red]")
            sys.exit(2)
        else:
            console.print(
                f"[yellow]⚠ Converted {success_count} file(s), "
                f"failed {failure_count} file(s)[/yellow]"
            )
            sys.exit(1)
    else:
        console.print(f"[red]Error:[/red] {input_path} is not a file or directory")
        sys.exit(2)


def cli():
    """Entry point for the CLI application."""
    typer.run(main)


if __name__ == "__main__":
    cli()
