import paho.mqtt.client as mqtt
from datetime import datetime
import pytz
import json


class OhMQTTbridge:
    def __init__(self, connection):
        self.username = str(connection.username)
        self.password = str(connection.password)
        self.host = str(connection.host)
        self.port = int(connection.port)
        self.clientid = str(connection.clientid)
        self.protocol = mqtt.MQTTv311
        self.tz_Z = pytz.timezone('Zulu')

    def connect(self):
        self.client = mqtt.Client(
            client_id=self.clientid, protocol=self.protocol)
        self.client.username_pw_set(self.username,
                                    self.password)
        self.client.connect(self.host,
                            port=self.port, keepalive=60)

        # start the loop
        self.client.loop_start()
        return self.client

    def Publish(self, commandTopic, command):
        ret = self.client.publish(
            commandTopic, command)
        return ret

    def get_Time_now(self):
        dateTime_now = datetime.now(self.tz_Z)
        datetime_now_string = dateTime_now.strftime("%Y-%m-%dT%H:%M:%S")+"Z"
        return datetime_now_string

    def disconnect(self):
        self.client.disconnect()

    def topicSubscriber(self, topic):
        self.client.subscribe(topic)
        self.subscribeTopics = True

    def __del__(self):
        self.disconnect()


class DysonConnect(OhMQTTbridge):

    def __init__(self, connection, subscribeTopics=False):
        OhMQTTbridge.__init__(self, connection)
        self.DeviceName = str(connection.type) + \
            '/' + str(connection.serial)
        self.connect(subscribeTopics)

    def connect(self, subscribeTopics=False):
        self.client = OhMQTTbridge.connect(self)

        # subscribe to topics
        if (subscribeTopics != False and isinstance(subscribeTopics, list)):
            for topic in subscribeTopics:
                topic[0] = self.DeviceName + str(topic[0])

            self.topicSubscriber(subscribeTopics)

    def set_command_data(self, command, command_topic, data=""):
        commmon_Command_struct = {
            "f": command_topic,
            "mode-reason": "LAPP",
            "time": self.get_Time_now(),
            "msg": ""
        }

        commmon_Command_struct["msg"] = command
        if (command == "STATE-SET" and data != ""):
            command_keys = list(commmon_Command_struct.keys())
            command_keys.append("data")
            command_values = list(commmon_Command_struct.values())
            command_values.append(data)
            commmon_Command_struct = dict(zip(command_keys, command_values))

        return json.dumps(commmon_Command_struct)

    def Publish(self, command, data=""):
        command_topic = self.DeviceName + '/command'
        ret = OhMQTTbridge.Publish(self,
                                   commandTopic=command_topic, command=self.set_command_data(command, command_topic, data))
        return ret

    def PublishSet(self, commandList):
        if (isinstance(commandList, list)):
            for command in commandList:
                self.Publish(command=command)

    def get_Device_Name(self):
        return self.DeviceName
