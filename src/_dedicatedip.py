class PIADedicatedIP():
    def __init__(self, pia):
        self._pia = pia

    def add(
        self,
        token_file: str,
        timeout_in_s: None | int = None, 
        debug_option: bool = False
    ) -> str:
        """
        To add, put the dedicated IP token in a text file (by
        itself), and specify that file:\n
        DIP20000000000000000000000000000\n
        (This ensures the token is not visible in the process
        command line or environment.)
        """
        return self._pia._exec_one_shot_cmd(
            self._pia._constants.dedicatedip_add_cmd + [token_file],
            timeout_in_s,
            debug_option
        )
    
    def remove(
        self,
        region_id: str,
        timeout_in_s: None | int = None, 
        debug_option: bool = False
    ) -> str:
        """
        To remove, specify the dedicated IP region ID, such as 
        `dedicated-sweden-000.000.000.000`.
        """
        return self._pia._exec_one_shot_cmd(
            self._pia._constants.dedicatedip_remove_cmd + [region_id],
            timeout_in_s,
            debug_option
        )
