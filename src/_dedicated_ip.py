from ._types import PIACommandResult, PIACommandStatus

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

class PIADedicatedIP():
    def __init__(self, pia):
        self._pia = pia

    def add(
        self,
        token: str | None = None,
        token_file: str | None = None,
        **kwargs
    ) -> PIACommandResult[PIACommandStatus, Optional[Exception]]:
        """
        To add, pass in a dedicated IP token with the `token`
        argument, or place it in a text file, by itself like 
        so:\n
        `DIP20000000000000000000000000000`\n
        and pass in its path with the `token_file` argument.
        (This ensures the token is not visible in the process
        command line or environment.)\n
        Command status may be `INVALID_ARGS`, `TEMP_FILE_ERROR`,
        or `SUCCESS`.
        """
        temp_file = None

        if (token_file):
            try:
                token_file_path = Path(token_file)
            except Exception as e:
                return PIACommandResult[PIACommandStatus, Exception](
                    PIACommandStatus.INVALID_ARGS, e, None
                )
        elif (token):
            try:
                temp_file = NamedTemporaryFile(
                    mode="w",
                    encoding='utf-8',
                    delete=False
                )
                temp_file.write(token)
                token_file_path = Path(temp_file.name)
            except Exception as e:
                if (temp_file): temp_file.close()

                return PIACommandResult[PIACommandStatus, Exception](
                    PIACommandStatus.TEMP_FILE_ERROR, e, None
                )
        else:
            return PIACommandResult[PIACommandStatus, Exception](
                PIACommandStatus.INVALID_ARGS, 
                Exception('No token or token file provided!'), None
            )
        
        code, logs = self._pia._exec_one_shot_cmd(
            self._pia._constants.dedicatedip_add_cmd + [token_file_path.absolute()],
            **kwargs
        )

        if (temp_file):
            temp_file.close()

        return PIACommandResult[PIACommandStatus, None](
            PIACommandStatus.from_cli_exit_code(code), None, logs
        )
    
    def remove(
        self,
        region_id: str,
        **kwargs
    ) -> str:
        """
        To remove, specify the dedicated IP region ID, such as 
        `dedicated-sweden-000.000.000.000`.
        """
        # TODO verify region
        # TODO return PIACommandResult
        return self._pia._exec_one_shot_cmd(
            self._pia._constants.dedicatedip_remove_cmd + [region_id],
            **kwargs
        )[1]
