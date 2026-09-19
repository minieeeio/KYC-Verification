import shutil
import os
import json
from datetime import datetime

from typing import Any

from qrlib.QRProcess import QRProcess
from qrlib.QRDecorators import run_item
from qrlib.QRRunItem import QRRunItem

from components.DefaultComponent import DefaultComponent
from components.GoogleDrive import DriveAPI
from components.Database import SQLdb
from components.OCR import GeminiOCR

from components.OutputWriter import  write_output_row, cleanup_temp_file


class DefaultProcess(QRProcess):
    """Main process orchestration."""

    def __init__(self) -> None:
        super().__init__()
        self.default_component = DefaultComponent()
        self.register(self.default_component)
        self.data = []
        self.driveAPI=DriveAPI()
        self.database=SQLdb()
        self.ocr=GeminiOCR()
        self.files=None
        self.run_stats = {"processed": 0, "flagged": 0, "failed": 0}   
        self.run_start_time = None 
        

    @run_item(is_ticket=False, post_success=False)
    def before_run(self, *args, **kwargs):
        
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)

        self.default_component.login()
        self.data = ["a", "b"]
        self.run_start_time = datetime.now()  
        run_item.set_success()
        
        #KYC Execution
        self.driveAPI.authenticate_credentials()
        self.database.connect_db()
        self.database.setup_deduplication()
        self.ocr.create_client()
        # self.driveAPI.list_files()
        
        
        

    @run_item(is_ticket=False)
    def before_run_item(self, *args, **kwargs):
        # Get run item created by decorator. Then notify to all components about new run item.
        run_item: QRRunItem = kwargs["run_item"]
        self.notify(run_item)
        run_item.set_success()

    @run_item(is_ticket=True, post_success=True, post_error=True)
    def execute_run_item(self, data: Any, **kwargs: Any) -> None:
       
        # Get run item created by decorator. Then notify to all components about new run item.
        return_path=None
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
                "step=execute_run_item status=failed data=%s", data
            )
            raise

        #KYC Execution    
        self.files=self.driveAPI.list_files()
          
        for file_item in self.files:
            id = file_item.get("id")
            name = file_item.get("name")
            status = self.database.check_deduplication(id)
            print(status)

            if status in ("not_found", "failed"):
                return_path = self.driveAPI.download_files(id, name)
                print("Path is printed in", return_path)

            if return_path:
                try:
                    ocr_result = self.ocr.ocr_process(return_path)
                    validated = self.database.KYC_Validation(ocr_result)
                    final_status = self.database.get_final_status(validated)

                    self.logger.info(
                        "step=execute_run_item file=%s status=%s validation_errors=%s is_expired=%s",
                        name, final_status, validated["validation_errors"], validated.get("is_expired")
                    )

                    self.database.record(
                        id, name, status=final_status,
                        error_message="; ".join(validated["validation_errors"]) or None
                    )

                    write_output_row(id, name, final_status, validated)
                    self.driveAPI.move_file(id, final_status)
                    cleanup_temp_file(return_path)
                    self.run_stats[final_status] += 1   

                   

                except Exception as exc:
                    self.database.record(id, name, status="failed", error_message=str(exc))
                    self.logger.exception("step=execute_run_item status=failed file=%s", name)
                    write_output_row(id, name, "failed", {"validation_errors": [str(exc)], "is_expired": False})
                    cleanup_temp_file(return_path)
                    self.run_stats["failed"] += 1
                    continue
                

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
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        os.makedirs("summary", exist_ok=True)
        summary_path = os.path.join("summary", f"summary_{timestamp}.json")
        summary_data = {
            "run_started_at": self.run_start_time.isoformat() if self.run_start_time else None,
            "run_completed_at": datetime.now().isoformat(),
            "total_files": sum(self.run_stats.values()),
            "processed": self.run_stats["processed"],
            "flagged": self.run_stats["flagged"],
            "failed": self.run_stats["failed"],
        }
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)


        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", f"run_{timestamp}.log")
        
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"KYC run finished at {summary_data['run_completed_at']}\n")
            f.write(json.dumps(summary_data, indent=2))


        print("=" * 50)
        print("KYC Document Processor — Run Summary")
        print("=" * 50)
        print(f"Total files:  {summary_data['total_files']}")
        print(f"Processed:    {summary_data['processed']}")
        print(f"Flagged:      {summary_data['flagged']}")
        print(f"Failed:       {summary_data['failed']}")
        print("=" * 50)

        self.default_component.logout()
        run_item.set_success()

    def execute_run(self, **kwargs: Any) -> None:
        for data in self.data:
            self.before_run_item()
            self.execute_run_item(data)
            self.after_run_item()
