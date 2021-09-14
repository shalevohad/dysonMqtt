import credentialsDyson as connectionDyson
import credentialsBridge as connectionBridge
import dysonConnect as dyc
import time
import json

# General Data
fetch_data_duration_Min = {
    "REQUEST-CURRENT-FAULTS": 60,
    "REQUEST-PRODUCT-ENVIRONMENT-CURRENT-SENSOR-DATA": 10,
    "REQUEST-CURRENT-STATE": 10
}

# Topic and qos
subscribe_topics = [
    ['/status/current', 0],
    ['/status/software', 0],
    ['/status/connection', 0]
]

# declaring what to do when reciving message


def on_message(client, userdata, msg, action="file"):
    print(msg.topic)
    retJson = json.loads(msg.payload.decode("utf-8"))
    returnMethod = retJson["msg"]
    if (returnMethod == "ENVIRONMENTAL-CURRENT-SENSOR-DATA"):
        deviceData = retJson["data"]
    elif(returnMethod == "CURRENT-STATE" or returnMethod == "STATE-CHANGE"):
        deviceData = retJson["product-state"]

    device = {connectionDyson.host: {"time": "", "data": {}}}
    device[connectionDyson.host]["time"] = dysonServer.get_Time_now()
    for attribute, value in deviceData.items():
        device[connectionDyson.host]["data"].update({attribute: value})

    # Bridging
    bridgedServer = dyc.OhMQTTbridge(connectionBridge)
    bridgedServer.connect()
    bridgedServer.Publish(msg.topic, msg.payload)
    # print(bridgedServer)

    # Save to file
    fileName = connectionDyson.host + '_' + returnMethod + '.json'
    with open(fileName, 'w') as json_file:
        json.dump(device[connectionDyson.host], json_file)

    # Pretty Printing JSON string back
    print(json.dumps(device[connectionDyson.host],
                     indent=4, sort_keys=True))


# Declearing variables
dysonServer = dyc.DysonConnect(
    connectionDyson, subscribeTopics=subscribe_topics)

# the main software
dysonServer.PublishSet(fetch_data_duration_Min.keys())
dysonServer.client.on_message = on_message

# continues fetch data according to 'fetch_data_duration_Min' dict command and timing
i = 0
while True:
    time.sleep(1)
    for command, min in fetch_data_duration_Min.items():
        if (i % (min * 60) == 0):
            dysonServer.Publish(command=command)

    i = i+1
