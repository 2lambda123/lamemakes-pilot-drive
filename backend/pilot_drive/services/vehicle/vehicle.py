"""
The module that manages the connected vehicle
"""
import os
import time
import obd

from pilot_drive.master_logging.master_logger import MasterLogger
from pilot_drive.master_queue.master_event_queue import MasterEventQueue, EventType

from ..abstract_service import AbstractService
from ..settings import Settings
from .constants import MAX_ATTEMPTS
from .exceptions import InvalidQueryException, FailedObdConnectionException


class Vehicle(AbstractService):
    """
    The vehicle service that interfaces with the connected vehicle
    """

    def __init__(
        self,
        master_event_queue: MasterEventQueue,
        service_type: EventType,
        logger: MasterLogger,
        settings: Settings,
    ):
        """
        Initialize the Vehicle service

        :param event: the dict that will be converted to json & passed to the queue, and in turn
            to the UI.
        :param event_type: the event type that will go on the queue. If no argument is specified,
            it defaults to the calling services type
        :param settings: a settings instance to pull the OBD serial port path and intended stats
            from
        """
        super().__init__(master_event_queue, service_type, logger)

        self.__settings = settings
        self.__connected = False
        self.__failed = False
        self.__connection = None
        self.__max_interval = 0

        self.stats = []

    @property
    def is_connected(self):
        """
        Check if the OBD adapter is connected via python-OBD's status() method.

        :returns: a boolean of True if connected, False if not.
        """
        if self.__connection and self.__connection.status() in [
            obd.OBDStatus.ELM_CONNECTED,
            obd.OBDStatus.OBD_CONNECTED,
            obd.OBDStatus.CAR_CONNECTED,
        ]:
            self.__connected = True
            return True

        self.__connected = False
        return False

    @property
    def obd_port(self):
        """
        The serial port of the OBD/ELM327 reader
        """
        return self.__settings.get_setting("vehicle")["port"]

    @property
    def queried_fields(self):
        """
        Get all intended fields to query from settings
        """
        return self.__settings.get_setting("vehicle")["stats"]

    def __handle_connect(self):
        """
        Initialize the connection to the OBD serial port.
        """
        if self.obd_port:
            if os.path.exists(self.obd_port):
                connection = obd.OBD(self.obd_port)
                if not connection.is_connected():
                    self.__handle_failed_connect()
                    raise FailedObdConnectionException(
                        "OBD Connection was unsuccessful!"
                    )
                self.__failed = False
                if connection != self.__connection:
                    self.__push_info()
                self.__connection = connection
                self.logger.info(f"OBD connection made to {self.obd_port}.")
            else:
                self.__handle_failed_connect()

                raise FailedObdConnectionException(
                    f'Specified path: "{self.obd_port}" does not exist!'
                )
        else:
            # obd.OBD has support for automatic port detection but for
            # reliability, this port needs to be explicity stated in config.
            self.__handle_failed_connect()
            raise FailedObdConnectionException("No serial port was provided!")

    def __handle_failed_connect(self):
        """
        Check if a failure exists, then push the status
        """
        if not self.__failed:
            self.__failed = True

        self.__push_info()

    def __push_info(self):
        """
        Push the current vehicle data to the frontend
        """
        vehicle_info = {
            "connected": self.__connected,
            "failures": self.__failed,
            "stats": self.stats,
        }
        self.push_to_queue(vehicle_info)

    def __query_fields(self, queries_made: float):
        """
        Query the fields that are input.
        Expects a list of dicts in the form of:
        {"name": "<name>", "command": "<python OBD command>", "interval": <int query interval>}

        In
        """
        if self.__connection and len(self.queried_fields) > 0:
            field_index = 0
            for field in self.queried_fields:
                field_name = field["name"]
                field_command = field["command"]
                field_interval = field["interval"]
                if not obd.commands.has_name(field_command):
                    raise InvalidQueryException(
                        f'OBD command: "{field_name}" is not valid!'
                    )

                # If the the current field's interval is greater than the global max, up the max
                if not self.__max_interval and field_interval > self.__max_interval:
                    self.__max_interval = field_interval

                if queries_made % field_interval == 0:
                    # Make the query
                    resp = self.__connection.query(obd.commands[field_command])
                    if resp.value is not None:
                        # Convert to a tuple to get units & magnitude
                        resp_tuple = resp.value.to_tuple()
                        # pint converts tuples a little odd,
                        # values come back as"(<quantity>, (('<unit>', <magnitude>),))"
                        value = {
                            "quantity": resp_tuple[0],
                            "unit": resp_tuple[1][0][0],
                            "magnitude": resp_tuple[1][0][1],
                        }
                        if len(self.stats) == field_index:
                            self.stats.append({"name": field_name, "value": value})
                        else:
                            self.stats[field_index] = {
                                "name": field_name,
                                "value": value,
                            }

                        field_index += 1
                    else:
                        self.logger.error(msg=f'Failed to query for "{field_name}"')
                        continue

            if self.stats:
                self.__push_info()

    def main(self):
        # The number of times a connection to the vehicle has been attempted
        connection_attempts = 0

        # The number of queries made within the specified time interval
        queries_made = 0
        while True:
            if not self.is_connected and connection_attempts != MAX_ATTEMPTS:
                try:
                    self.__handle_connect()
                except FailedObdConnectionException as err:
                    self.logger.warning(
                        msg=f'Invalid serial port specified: "{err}", '
                        f"{MAX_ATTEMPTS-connection_attempts} connection attempts remaining."
                    )
                    connection_attempts += 1
                    time.sleep(
                        0.5
                    )  # Busy wait then continue to try and connect in case it happens to show up
            elif not self.is_connected and connection_attempts >= MAX_ATTEMPTS:
                self.logger.error(
                    msg=f"Failed to connect to serial port in {MAX_ATTEMPTS} attempts. "
                    "The vehicle service is exiting."
                )
                # Exit the service if the connection has been tried MAX_ATTEMPTS
                return

            if self.is_connected:
                self.__query_fields(queries_made=queries_made)
                time.sleep(0.5)
                queries_made = (
                    0 if queries_made == self.__max_interval else queries_made + 0.5
                )

    def refresh(self):
        self.__push_info()
