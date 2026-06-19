from __future__ import annotations

import requests
import random
import time
import json
import datetime

from speedbeesynapse.component.base import (
    HiveComponentBase,
    HiveComponentInfo,
    DataType,
)


@HiveComponentInfo(
    uuid='a29e6f91-77a9-4ef7-a2dc-80294c8f1f41',
    name='Random RESTDB Collector (Industrial Safe)',
    tag='collector',
    inports=0,
    outports=1,
)
class HiveComponent(HiveComponentBase):

    def premain(self, param):

        # ----------------------------
        # RESTDB CONFIG
        # ----------------------------
        self.api_key = "7d33ddf81092633399a4ac51c454e08942e7e"
        self.restdb_url = "https://demoapi-291b.restdb.io/rest/lecturasplc"

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-apikey": self.api_key,
            "cache-control": "no-cache"
        }

        # ----------------------------
        # CONTROL
        # ----------------------------
        self.interval = 5
        self.max_retries = 3

        # ----------------------------
        # SYNAPSE OUTPUTS
        # ----------------------------
        self.temperature = self.out_port1.Column('temperature', DataType.FLOAT)
        self.pressure = self.out_port1.Column('pressure', DataType.FLOAT)
        self.id_pieza = self.out_port1.Column('id_pieza', DataType.INT32)

        self.log.info("Industrial RESTDB component initialized")

    # ----------------------------
    # MAIN LOOP
    # ----------------------------
    def main(self, param):

        while self.is_runnable():

            ts = self.get_timestamp()

            # ----------------------------
            # SIMULATED DATA
            # ----------------------------
            temperature = round(random.uniform(20, 50), 2)
            pressure = round(random.uniform(10, 200), 2)
            id_pieza = random.randint(1, 10)

            # ----------------------------
            # SYNAPSE OUTPUT
            # ----------------------------
            self.temperature.insert(temperature, ts)
            self.pressure.insert(pressure, ts)
            self.id_pieza.insert(id_pieza, ts)

            # ----------------------------
            # BUILD SAFE PAYLOAD
            # ----------------------------
            payload = {
                "timestamp": self._to_iso(ts),
                "temperatura": float(temperature),
                "presion": float(pressure),
                "id_pieza": int(id_pieza)
            }

            self.log.info(f"RESTDB payload: {payload}")

            # ----------------------------
            # SEND
            # ----------------------------
            success = self._send_to_restdb(payload)

            if not success:
                self.log.warning("RESTDB insert failed")

            time.sleep(self.interval)

    # ----------------------------
    # STOP
    # ----------------------------
    def postmain(self, param):
        self.log.info("Industrial RESTDB component stopped")

    # ----------------------------
    # TIME CONVERSION SAFE
    # ----------------------------
    def _to_iso(self, ts):
        # Force clean ISO 8601 UTC
        dt = datetime.datetime.utcfromtimestamp(ts / 1_000_000_000)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # ----------------------------
    # SAFE REST CALL (CRITICAL FIX)
    # ----------------------------
    def _send_to_restdb(self, payload: dict) -> bool:

        # Force deterministic JSON serialization
        try:
            body = json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            self.log.error(f"JSON serialization error: {e}")
            return False

        for attempt in range(1, self.max_retries + 1):

            try:
                self.log.info(f"POST attempt {attempt} -> {self.restdb_url}")

                response = requests.post(
                    self.restdb_url,
                    data=body,   # IMPORTANT: not json=
                    headers=self.headers,
                    timeout=10,
                    verify=False

                )

                self.log.info(f"HTTP {response.status_code}")
                self.log.info(f"Response: {response.text}")

                if response.status_code in (200, 201):
                    return True

            except requests.RequestException as e:
                self.log.error(f"Network error attempt {attempt}: {e}")

            time.sleep(2 * attempt)

        self.log.error("RESTDB failed after max retries")
        return False
