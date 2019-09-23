import json

from flask import Flask, url_for, request, jsonify
from flask_restful import Resource, reqparse


from models.sensor import SensorModel

from simulation.thingworxSim import simulationThingworx
from simulation.awsSim import simulationAWS
from simulation.azureSim import simulationAZURE


class Sensor(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="Please add the name of the Sensor !"
    )
    parser.add_argument("cloud", type=str, required=True,
                        help="Please add the cloud on which you want to work !")
    parser.add_argument(
        "connection", type=str, required=True, help="Please add the connection Parameters !"
    )
    parser.add_argument(
        "format", type=str, required=True, help="Please add in which format do you want to send Data !"
    )
    parser.add_argument(
        "timeInterval", type=int, required=True, help="Please add the Time Interval between data simulations !"
    )
    parser.add_argument(
        "frequency", type=int, required=True, help="Please add how many times you want to simulate the sensor Behaviour !"
    )
    parser.add_argument(
        "minRange", type=int, required=True, help="Please add the minimum range !"
    )
    parser.add_argument(
        "maxRange", type=int, required=True, help="Please add the maximum range !"
    )

    def get(self):
        # Try except block and Authentication to be added
        return {"sensors": list(map(lambda x: x.json(), SensorModel.query.all()))}

    def post(self):
        # user = current_identity
        # print(user.access)

        # if user.access == "admin":
        data = Sensor.parser.parse_args()
        if SensorModel.find_by_name(data["name"]):
            return {
                "message": "A sensor with name '{}' already exists.".format(
                    data["name"]
                )
            }

        sensor = SensorModel(data["name"], data["cloud"], data["connection"], data["format"],
                             data["timeInterval"], data["frequency"], data["minRange"], data["maxRange"])

        try:
            sensor.save_to_db()
        except:
            return {"message": "An error occurred while adding the sensor, please try again with correct parameters."}

        return sensor.json(), 201
        # else:
        #     return {"message": "You do not have ADMIN Rights"}, 405


class SensorByName(Resource):
    def post(self, name):
        sensor = SensorModel.find_by_name(name)
        if sensor:
            sensor = sensor.json()
            connection = sensor['connection']
            connectionDict = json.loads(connection)
            # print(connectionDict)
            try:
                if sensor['cloud'] == "thingworx":
                    simulationThingworx(
                        connectionDict, sensor['frequency'], sensor['timeInterval'], sensor['minRange'], sensor['maxRange'])
                elif sensor['cloud'] == "aws":
                    simulationAWS(connectionDict)
                elif sensor['cloud'] == "azure":
                    simulationAZURE(connectionDict)
                else:
                    return {"message": "We don't support simulation for this cloud."}

                return {"message": "Simulation Completed"}
            except Exception:
                return {"message": "Something went wrong, Please check the cloud server and try again."}
        else:
            return {"message": "Sensor Not Found"}, 404

    def get(self, name):
        sensor = SensorModel.find_by_name(name)
        if sensor:
            return sensor.json()
        return {"message": "Sensor not found"}, 404

    def delete(self, name):
        #         user = current_identity
        #         print(user.access)

        #         if user.access == "admin":
        sensor = SensorModel.find_by_name(name)
        if sensor:
            sensor.delete_from_db()
            return {"message": "Sensor deleted"}
        else:
            return {"message": "Sensor not found"}


class UpdateSensorRange(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        "minRange", type=int, required=True, help="This field cannot be left blank!"
    )
    parser.add_argument(
        "maxRange", type=int, required=True, help="This field cannot be left blank!"
    )

    def put(self, name):
        data = UpdateSensorRange.parser.parse_args()
        sensor = SensorModel.find_by_name(name)

        try:
            if sensor is None:
                return {"message": "Sensor not Found !"}
            else:
                sensor.minRange = data["minRange"]
                sensor.maxRange = data["maxRange"]
                sensor.save_to_db()
                return sensor.json()
        except Exception as error:
            return {"message": error}


class UpdateSensorFrequencyInterval(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
        "frequency", type=int, required=True, help="This field cannot be left blank!"
    )
    parser.add_argument(
        "timeInterval", type=int, required=True, help="This field cannot be left blank!"
    )

    def put(self, name):
        data = UpdateSensorFrequencyInterval.parser.parse_args()
        sensor = SensorModel.find_by_name(name)
        try:
            if sensor is None:
                return {"message": "Sensor not Found !"}
            else:
                sensor.frequency = data["frequency"]
                sensor.timeInterval = data["timeInterval"]
                sensor.save_to_db()
                return sensor.json()
        except Exception as error:
            return {"message": error}
