from qrlib.QRProcess import QRProcess
from qrlib.QRDecorators import run_item
from qrlib.QRRunItem import QRRunItem
from components.DefaultComponent import DefaultComponent

class DefaultProcess(QRProcess):
    """Main process orchestration."""

    def __init__(self) -> None:
        super().__init__()
        self.default_component = DefaultComponent()
        self.register(self.default_component)
        self.data = []

    @run_item(is_ticket=False, post_success=False)
    def before_run(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)

        self.default_component.login()
        self.data = ["a", "b"]
        run_item.set_success()

    @run_item(is_ticket=False)
    def before_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)
        run_item.set_success()

    @run_item(is_ticket=True, post_success=True, post_error=True)
    def execute_run_item(self, *args: Any, **kwargs: Any) -> None:
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)
        self.logger = run_item.logger
        try:
            self.default_component.test()
        except Exception as exc:
            run_item.notification.data = {
                "reason": str(exc),
                "step": "step",
            }
            self.logger.exception(
                "step=execute_run_item status=failed customer_account=%s", account
            )
            run_item.set_error()
            return

        run_item.report_data["test"] = args[0]
        run_item.set_success()

    @run_item(is_ticket=False)
    def after_run_item(self, *args: Any, **kwargs: Any) -> None:
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)
        run_item.set_success()

    @run_item(is_ticket=False, post_success=False)
    def after_run(self, *args: Any, **kwargs: Any) -> None:
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)

        self.default_component.logout()
        run_item.set_success()

    def execute_run(self, **kwargs: Any) -> None:
        for data in self.data:
            self.before_run_item()
            self.execute_run_item()
            self.after_run_item()
