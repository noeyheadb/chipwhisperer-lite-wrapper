import sys
import os
import chipwhisperer as cw
import numpy as np
from chipwhisperer.capture import scopes
from chipwhisperer.capture.acq_patterns.basic import AcqKeyTextPattern_Basic
from typing import Optional, Tuple, Dict
from datetime import datetime
from .cw_trace import CWTrace
from .utils import visualization_single_trace, check_and_reformat_dir


class CWLiteWrapper:
    def __init__(self):
        self._scope: Optional[cw.capture.scopes.OpenADC] = None
        self._target: Optional[cw.targets.SimpleSerial] = None
        self._ktp: Optional[cw.capture.acq_patterns.basic.AcqKeyTextPattern_Basic] = None
        self._trig_cnt: Optional[int] = None
        self._export_path: Optional[str] = check_and_reformat_dir("./cw-export/")
        pass

    def __repr__(self):
        try:
            status = self.status(verbose=False)
            conn = status.get("connected")
        except RuntimeError:
            return f"<CW Conn: {False}>"

        if conn is True:
            detail = f" ({status.get('name')}) samples: {status.get('samples')} " \
                     f"last_trig_cnt: {status.get('last_trig_cnt')}"
        else:
            detail = f""

        return f"<CW Conn: {conn}{detail}>"

    def reset(self) -> None:
        self.disconnect()
        self._scope = None
        self._target = None
        self._ktp = None
        self._trig_cnt = None
        pass

    def disconnect(self):
        self._scope.dis()
        pass

    def connect(self,
                verbose: bool = True
                ) -> None:
        self._scope = cw.scope(scope_type=scopes.OpenADC)
        self._scope.default_setup()
        self._scope.adc.samples = 24400
        self._target = cw.target(self._scope, target_type=cw.targets.SimpleSerial)
        self._ktp = cw.ktp.Basic()
        self._ktp.setInitialKey("00112233445566778899AABBCCDDEEFF")  # initial key (128bit, 16byte)
        if verbose:
            print(f"{self._scope.get_name()} Connected!")
            print(f"Default mode is '128-bit fixed key and 128-bit random textin'. "
                  f"Please Change key & textin mode appropriately.")
        pass

    def _check_connection(self,
                          raise_exception: bool
                          ) -> bool:
        if self._scope is None:
            if raise_exception:
                raise RuntimeError("Scope object is None. Please connect the cw-lite using 'connect()'.")
            else:
                return False
        if not self._scope.getStatus():
            if raise_exception:
                raise RuntimeError("Connection is invalid. Please connect again using 'connect()'.")
            else:
                return False
        return True

    def status(self,
               verbose: bool = True
               ) -> Dict:
        self._check_connection(raise_exception=True)
        result = {
            "connected": self._scope.getStatus(),
            "name": self._scope.get_name(),
            "samples": self._scope.adc.samples,
            "trig_mode": self._scope.adc.basic_mode,
            "offset": self._scope.adc.offset,
            "pre_samples": self._scope.adc.presamples,
            "scale": self._scope.clock.adc_src,
            "saved_trig_cnt": f"{self._trig_cnt}" if self._trig_cnt is not None else "unknown",
            "last_trig_cnt": f"{self._scope.adc.trig_count}"
            if self._scope.adc.basic_mode == "rising_edge" else "unknown",
            "key_length": self._ktp.keyLen(),
            "fixed_key": self._ktp.get_key_type(),
            "fixed_key_value": None if not self._ktp.get_key_type() else self._ktp.getInitialKey().replace(" ", ''),
            "textin_length": self._ktp.textLen(),
            "fixed_textin": self._ktp.getPlainType(),
            "fixed_textin_value": None if not self._ktp.getPlainType() else self._ktp.getInitialText().replace(" ", '')
        }
        if verbose:
            print(f"-------------------------------- INFO --------------------------------\n",
                  f"Connected    : {result.get('connected')}\n",
                  f"Name         : {result.get('name')}\n",
                  f"samples      : {result.get('samples')}\n",
                  f"trig_mode    : {result.get('trig_mode')}\n",
                  f"offset       : {result.get('offset')}\n",
                  f"PreSamples   : {result.get('pre_samples')}\n",
                  f"Scale        : {result.get('scale')}\n",
                  f"SavedTrigCnt : {result.get('saved_trig_cnt')}\n",
                  f"LastTrigCnt  : {result.get('last_trig_cnt')}\n",
                  f"Key length   : {result.get('key_length')}\n",
                  f"Fixed Key    : {result.get('fixed_key')}",
                  "\n" if not result.get("fixed_key") else f" : {result.get('fixed_key_value')}\n",
                  f"Textin_length: {result.get('textin_length')}\n",
                  f"Fixed text   : {result.get('fixed_textin')}",
                  f"\n" if not result.get("fixed_textin") else f" : {result.get('fixed_textin_value')}\n",
                  f"----------------------------------------------------------------------\n",
                  sep="")
        return result

    def _capture(self) -> cw.Trace:
        key, pt = self._ktp.new_pair()
        trace = cw.capture_trace(self._scope, self._target, pt, key)
        if trace is None or trace.wave.shape[0] != self._scope.adc.samples:
            for _ in range(3):
                trace = cw.capture_trace(self._scope, self._target, pt, key)
                if trace is not None and trace.wave.shape[0] == self._scope.adc.samples:
                    return trace
            else:
                raise RuntimeError("Unable to capture the valid trace from CW device.")
        return trace

    def capture_single_trace(self,
                             visualization: bool = False,
                             update_trig_cnt: bool = False,
                             verbose: bool = True
                             ) -> CWTrace:
        self._check_connection(raise_exception=True)
        trace: cw.Trace = self._capture()
        if visualization:
            visualization_single_trace(trace.wave)
        if verbose:
            print(f"key : {trace.key}\n"
                  f"in  : {trace.textin}\n"
                  f"out : {trace.textout}\n")
        if update_trig_cnt:
            self._trig_cnt = self._scope.adc.trig_count
        return CWTrace(trace)

    def capture_multiple_traces(self,
                                quantity: int,
                                identifier: str,
                                poi: Optional[Tuple[int, int]] = None,
                                verbose: bool = True
                                ) -> dict:
        self._check_connection(raise_exception=True)
        now = datetime.now()
        capture_time = f"{now.year}.{now.month}.{now.day}.{now.hour}.{now.minute}.{now.second}"

        if poi is not None:
            poi_len = poi[1] - poi[0]
            traces = np.empty((quantity, poi_len))
        else:
            poi = (0, self._scope.adc.samples)
            traces = np.empty((quantity, self._scope.adc.samples))

        textins = []
        textouts = []
        keys = []

        for i in range(quantity):
            trace = self._capture()
            traces[i] = trace.wave[poi[0]:poi[1]]
            textouts.append(trace.textout.hex().upper())

            if not self._ktp.getPlainType():  # random textin
                textins.append(trace.textin.hex().upper())
            elif i == 0:                      # fixed  textin
                textins.append(trace.textin.hex().upper())

            if not self._ktp.get_key_type():  # random key
                keys.append(trace.key.hex().upper())
            elif i == 0:                      # fixed  key
                keys.append(trace.key.hex().upper())

            if verbose:
                print(f'\r{" " * 60}', end='', flush=True)
                print(f'\rMeasuring... {((i + 1) / quantity) * 100:.2f}% ({i + 1}/{quantity})', end='', flush=True)

        keys = np.array(keys)
        textins = np.array(textins)
        textouts = np.array(textouts)

        np.save(f"{self._export_path}{identifier}-{capture_time}-trace.npy", traces)
        np.save(f"{self._export_path}{identifier}-{capture_time}-key.npy", keys)
        np.save(f"{self._export_path}{identifier}-{capture_time}-textin.npy", textins)
        np.save(f"{self._export_path}{identifier}-{capture_time}-textout.npy", textouts)

        return {"trace": traces, "key": keys, "textin": textins, "textout": textouts}

    def set_scope_detail(self,
                         samples: Optional[int] = None,
                         trigger_mode: Optional[str] = None,
                         offset: Optional[int] = None,
                         pre_samples: Optional[int] = None,
                         scale: Optional[str] = None
                         ) -> None:
        self._check_connection(raise_exception=True)
        if samples is not None:
            if not 0 <= samples <= 24400:
                raise RuntimeError("Samples must be between 0 and 24400.")
            self._scope.adc.samples = samples

        if trigger_mode is not None:
            if not (trigger_mode == "rising_edge" or trigger_mode == "falling_edge"):
                raise RuntimeError("Not supported trigger mode. (Available: rising_edge, falling_edge)")
            self._scope.adc.basic_mode = trigger_mode

        if offset is not None:
            if offset < 0:
                raise RuntimeError("Offset must be a positive number.")
            print(f"If the offset is not zero, you may not be able to capture it smoothly.", file=sys.stderr)
            self._scope.adc.offset = offset

        if pre_samples is not None:
            if pre_samples < 0:
                raise RuntimeError("pre_samples must be a positive number.")
            self._scope.adc.presamples = pre_samples

        if scale is not None:
            if not (scale == "clkgen_x4" or scale == "clkgen_x1"):
                raise RuntimeError("Not supported scale mode. (Available: clkgen_x1, clkgen_x4)")
            self._scope.clock.adc_src = scale
        pass

    def set_fixed_key(self,
                      hex_str: str
                      ) -> None:
        self._check_connection(raise_exception=True)
        hex_str = hex_str.strip().replace(" ", "")
        if len(hex_str) / 2 != self._ktp.keyLen():
            raise RuntimeError("The length of the key is not correct.")
        self._ktp.set_key_type(True)
        if self._ktp.get_key_type():
            self._ktp.setInitialKey(hex_str)
        else:
            raise RuntimeError("Unexpected exception has occurred.")
        pass

    def set_random_key(self) -> None:
        self._check_connection(raise_exception=True)
        self._ktp.set_key_type(False)
        pass

    def get_key_type_and_value(self) -> dict:
        return {"is_fixed": self._ktp.get_key_type(),
                "value": self._ktp.getInitialKey() if self._ktp.get_key_type() is True else None}

    def set_key_length(self,
                       bit: int = 128
                       ) -> None:
        if bit % 8 != 0:
            raise RuntimeError("Key length must be in 8-bit units.")
        if self._ktp.keyLen() != bit / 8:
            self._ktp.key_len = bit / 8
        pass

    def set_fixed_textin(self,
                         hex_str: str
                         ) -> None:
        self._check_connection(raise_exception=True)
        hex_str = hex_str.strip().replace(" ", "")
        if len(hex_str) / 2 != self._ktp.textLen():
            raise RuntimeError("The length of the textin is not correct.")
        self._ktp.setPlainType(True)
        if self._ktp.getPlainType():
            self._ktp.setInitialText(hex_str)
        else:
            raise RuntimeError("Unexpected exception has occurred.")
        pass

    def set_random_textin(self) -> None:
        self._check_connection(raise_exception=True)
        self._ktp.setPlainType(False)
        pass

    def get_textin_type_and_value(self) -> dict:
        return {"is_fixed": self._ktp.getPlainType(),
                "value": self._ktp.getInitialText() if self._ktp.getPlainType() is True else None}

    def set_textin_length(self,
                          bit: int = 128
                          ) -> None:
        if bit % 8 != 0:
            raise RuntimeError("Textin length must be in 8-bit units.")
        if self._ktp.textLen() != bit / 8:
            self._ktp.text_len = bit / 8
        pass

    def set_trig_cnt_manually(self,
                              trig_cnt: int
                              ) -> None:
        self._trig_cnt = trig_cnt
        pass

    def get_saved_trig_cnt(self):
        return self._trig_cnt

    def xmega_programmer(self,
                         dot_hex_path: str
                         ) -> None:
        self._check_connection(raise_exception=True)
        if not os.path.exists(dot_hex_path):
            raise RuntimeError("The .hex file does not exist.")
        cw.program_target(self._scope, cw.programmers.XMEGAProgrammer, dot_hex_path)
        pass

    def change_export_path(self,
                           export_directory_path: str
                           ) -> None:
        if export_directory_path is None:
            raise RuntimeError("Export_path is invalid.")
        self._export_path = check_and_reformat_dir(export_directory_path)
        pass
    pass
