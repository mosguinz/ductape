from pathlib import Path

import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated

from mos_moss import config as Config
from mos_moss import file_handler as FileHandler

app = typer.Typer()
Config.load_keys()


@app.callback(no_args_is_help=True)
def callback():
    """Mos' MOSS utility... and other things."""
    pass


@app.command()
def config(
    key_to_set: Annotated[Config.ConfigKey, typer.Argument()],
    value_to_set: Annotated[str, typer.Argument()] = None,
):
    """
    Query or set configuration values.

    Configuration keys are saved in the home directory in plaintext file.
    """
    value = Config.get_config(key_to_set)
    if not value_to_set:
        typer.echo(value)
        return
    if not value:
        print(
            "[bold red]Warning: [/bold red]"
            f"The keys will be stored in a plaintext file at {Config.CONFIG_PATH}."
        )
        confirm = typer.confirm("Are you sure you want to continue?")
        if confirm:
            Config.set_config(key_to_set, value_to_set)


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
    destination: Annotated[
        Path,
        typer.Argument(
            help="Location to place the extracted ZIP files.",
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = None,
    original_name: Annotated[
        bool, typer.Option(help="Whether to keep the submission's original name.")
    ] = False,
):
    """Unzip Canvas submission files."""
    final_dest = None
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Unzipping...")
        final_dest = FileHandler.unzip_canvas_submission(zip_file, destination, original_name)

    print(f"Items extracted to {final_dest}")
