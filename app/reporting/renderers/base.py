import abc
from app.reporting.models import ClinicalReport

class ReportRenderer(abc.ABC):
    """
    Common interface for all clinical report renderers.
    """

    @abc.abstractmethod
    def render(self, report: ClinicalReport) -> str:
        """
        Renders the given ClinicalReport into a specific string format.
        """
        pass
