import credentialsDyson as connectionDyson
import dysonConnect as dyc

# Main Program
dysonServer = dyc.DysonConnect(connectionDyson)
data = {
    # הפעלת מתח
    "fpwr": "OFF",
    # הפעלת סיבוב
    # "oson": "ON",
    # מעלות סיום סיבוב
    # "osau": "0200",
    # מעלות תחילת סיבוב
    # "osal": "0210",
    # מהירות מאורר
    # "fnsp": "0008",
    # "ancp": "CUST"
}
retData = dysonServer.Publish(command="STATE-SET", data=data)
dysonServer.disconnect()
