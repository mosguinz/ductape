from dataclasses import dataclass


@dataclass
class Compliance:
    zip_name_compliant: bool = None
    report_name_compliant: bool = None
    folders_compliant: bool = None

    zip_name: str = None
    report_name: str = None
    folder_structure: str = None

    def __bool__(self):
        return all((self.folders_compliant, self.report_name_compliant, self.zip_name_compliant))


@dataclass
class Submission:
    student_name: str
    canvas_id: int
    sis_id: int
    compliance: Compliance

    def __hash__(self):
        return hash(self.sis_id)
