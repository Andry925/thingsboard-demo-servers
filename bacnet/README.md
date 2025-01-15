## Emulator device

### Data Schema

| Variable Name | Object Type | Object Id | Property Id  |
| :------------ | :---------- | :-------- | :----------- |
| Temperature   | analogValue | 1         | presentValue |
| Humidity      | analogValue | 2         | presentValue |
| Relay 1       | binaryInput | 1         | presentValue |
| Relay 2       | binaryInput | 2         | presentValue |

## Gateway connector config

```json
{
  "logLevel": "DEBUG",
  "application": {
    "objectName": "TB_gateway",
    "address": "0.0.0.0",
    "objectIdentifier": 599,
    "maxApduLengthAccepted": 1476,
    "segmentationSupported": "segmentedBoth",
    "vendorIdentifier": 15,
    "deviceDiscoveryTimeoutInSec": 5
  },
  "devices": [
    {
      "deviceInfo": {
        "deviceNameExpressionSource": "constant",
        "deviceNameExpression": "Emulator",
        "deviceProfileExpressionSource": "constant",
        "deviceProfileExpression": "default"
      },
      "host": "DEVICE_HOST",
      "port": 47809,
      "pollPeriod": 5000,
      "attributes": [
        {
          "key": "relay_1",
          "objectType": "binaryInput",
          "objectId": "1",
          "propertyId": "presentValue"
        },
        {
          "key": "relay_2",
          "objectType": "binaryInput",
          "objectId": "2",
          "propertyId": "presentValue"
        }
      ],
      "timeseries": [
        {
          "key": "temperature",
          "objectType": "analogValue",
          "objectId": "1",
          "propertyId": "presentValue"
        },
        {
          "key": "humidity",
          "objectType": "analogValue",
          "objectId": "2",
          "propertyId": "presentValue"
        }
      ],
      "attributeUpdates": [],
      "serverSideRpc": [
        {
          "method": "set_relay_1",
          "requestType": "writeProperty",
          "requestTimeout": 10000,
          "objectType": "binaryInput",
          "objectId": "1",
          "propertyId": "presentValue"
        },
        {
          "method": "set_relay_2",
          "requestType": "writeProperty",
          "requestTimeout": 10000,
          "objectType": "binaryInput",
          "objectId": "2",
          "propertyId": "presentValue"
        }
      ]
    }
  ]
}
```
