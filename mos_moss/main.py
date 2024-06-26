from pathlib import Path

import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.callback(no_args_is_help=True)
def callback():
    """Mos' MOSS utility... and other things."""
    pass


@app.command()
def format_check(
    zip_file: Annotated[
        Path,
        typer.Argument(
            help="The batch submission ZIP file generated from Canvas.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    asmt: Annotated[
        str,
        typer.Argument(help="Assignment name, like Canvas or 03."),
    ],
    parts: Annotated[
        list[str],
        typer.Argument(
            help="Parts that requires folder to be present, such as A and B.",
        ),
    ] = None,
    report: Annotated[bool, typer.Option(help="Whether a report is required.")] = True,
    file_name_check: Annotated[
        bool, typer.Option(help="Whether to enforce the check for the ZIP file name.")
    ] = True,
    report_name_check: Annotated[
        bool, typer.Option(help="Whether to enforce the check for the report name.")
    ] = True,
    folder_check: Annotated[
        bool, typer.Option(help="Whether to enforce the check for the folders.")
    ] = True,
    evil: Annotated[bool, typer.Option(help="Exactly adhere to the Grading Policy.")] = False,
    send_message: Annotated[
        bool,
        typer.Option(help="Whether to send a message to student with non-compliant submissions."),
    ] = False,
    verbose: Annotated[
        bool, typer.Option(help="Verbose mode. Show directory structure for each submission.")
    ] = False,
):
    """
    Check the student's submission format.

    By default, it will enforce the ZIP file and report naming format, and the required folders.
    """
    typer.echo("Check format")


@app.command()
def moss(
    zip_file: Annotated[Path, typer.Option(exists=True, dir_okay=False, resolve_path=True)],
    language: Annotated[str, typer.Option()],
):
    """Run MOSS."""
    typer.echo("Run MOSS")


@app.command()
def unzip(
    zip_file: Annotated[
        Path,
        typer.Argument(
            help="The batch submission ZIP file generated from Canvas.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    original_name: Annotated[
        bool, typer.Option(help="Whether to keep the submission's original name.")
    ] = False,
):
    """Unzip Canvas submission files."""
    typer.echo("Unzip Canvas submission files.")
