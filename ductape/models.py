from dataclasses import dataclass


@dataclass
class Compliance:
    """
    Represents the submission's compliance. The instance may be evaluated to `True`
    if every field is deemed compliant.
    """

    """Whether the ZIP file name is compliant. If `None`, the check is not enforced."""
    zip_name_compliant: bool = None
    """Whether the report name is compliant. If `None`, the check is not enforced."""
    report_name_compliant: bool = None
    """Whether the submission contain the required folders. If `None`, the check is not enforced."""
    folders_compliant: bool = None

    """The submission's original file name."""
    zip_name: str = None
    """The name of the report found in the submission."""
    report_name: str = None
    """A tree diagram representing the submission's folder structure."""
    folder_structure: str = None

    def __bool__(self):
        return all(
            c is True or None
            for c in (self.folders_compliant, self.report_name_compliant, self.zip_name_compliant)
        )


@dataclass
class Submission:
    """
    Represents the student's Canvas submission. All properties found are extracted
    from the submission's file name.
    """

    """The student's name. Extracted from the file name, it is in the format last name, followed by the first."""
    student_name: str
    """The student's Canvas ID. This is the ID to be used for all Canvas operations."""
    canvas_id: int
    """The student's Student Information Services (SIS) ID. Not useful for our purpose."""
    sis_id: int
    """Whether this submission is compliant."""
    compliance: Compliance

    def __hash__(self):
        return hash(self.sis_id)