"""


"""

# ----

import os
from abc import ABC, abstractmethod
from utils.logger_interface import Logger
from tools.system_interface import get_app_path
from typing import Dict, Tuple, Generic
from confs.yaml_interface import YAML
from confs.jinja2_interface import write_from_template
from tools import parser_interface
from types import SimpleNamespace
from utils.decorator_interface import privatemethod
from exceptions import WorkloadManagerError
from io import StringIO
from execute.executable_interface import app_exec

# ----

# Define all available module properties.
__all__ = ["WorkfloadManager"]

# ----


class WorkloadManager:
    """

    """

    def __init__(self: Generic, wrkldmngr: str, shell: str, *args: Tuple, **kwargs: Dict):
        """
        Description
        -----------

        Creates a new WorkflowManager object.

        """

        # Define the base-class attributes.
        self.logger = Logger(
            caller_name=f"{__name__}.{self.__class__.__name__}")
        self.wrkldmngr = wrkldmngr
        self.schema_file = os.path.join(parser_interface.enviro_get(envvar="WRKLDMNGR_ROOT"),
                                        "schema", "wrkldmngr.yaml")

        self.wrkldmngr_dict = self.config()
        if shell.lower() == "bash":
            self.header = "#!/usr/bin/env bash"

    @privatemethod
    def config(self: Generic) -> Dict:
        """
        Description
        -----------

        This method collects the attributes for the respective workload manager.

        Returns
        -------

        wrkldmngr_dict: ``Dict``

            A Python dictionary containg the respective, supported,
            workload manager attributes.

        Raises
        ------

        WorkloadManager

            - raised if the specified workload manager is not
              supported within the respective schema file.

        """

        # Collect the respective workload manager attributes.
        wrkldmngr_dict = parser_interface.object_getattr(
            object_in=YAML().read_yaml(yaml_file=self.schema_file, return_obj=True),
            key=self.wrkldmngr, force=True)
        if wrkldmngr_dict is None:
            msg = (f"The attributes for workfload manager {self.wrkldmngr} could not "
                   f"be determined from the schema file path {self.schema_file}. Aborting!!!"
                   )
            raise WorkloadManagerError(msg=msg)

        return wrkldmngr_dict

    @app_exec
    async def submit(self: Generic, output_file: str) -> None:
        """

        """

        launcher = parser_interface.dict_key_value(
            dict_in=self.wrkldmngr_dict, key="launcher", force=True, no_split=True)
        if launcher is None:
            raise AttributeError  # TODO

        app_path = get_app_path(app=launcher)
        if app_path is None:
            raise AttributeError  # TODO

        exec_obj = parser_interface.object_define()
        exec_obj.exec_path = f"{app_path} {output_file}"
        exec_obj.run_path = "./"
        exec_obj.scheduler = self.wrkldmngr

        return exec_obj

    @privatemethod
    def write(self: Generic, wlm_dict: Dict, output_file: str) -> None:  # TODO
        """


        """

        wlm_dict["header"] = self.header
        wlm_dict = parser_interface.dict_key_case(
            dict_in=wlm_dict, lowercase=True, uppercase=True)
        tmpl_path = parser_interface.dict_key_value(
            dict_in=self.wrkldmngr_dict, key="template", force=True, no_split=True)
        write_from_template(tmpl_path=tmpl_path, output_file=output_file, in_dict=wlm_dict,
                            skip_missing=True)

    async def run(self: Generic, wlm_dict: Dict, output_file: str, annotate: str) -> None:
        """

        """

        self.write(wlm_dict=wlm_dict, output_file=output_file)
        await self.submit(output_file=output_file)
