from google.protobuf.json_format import MessageToDict

from qm.pb.inc_qua_config_pb2 import QuaConfig


def convert_msg_to_config(config):
    msg_dict = MessageToDict(config)

    if 'v1beta' in msg_dict:
        return _convert_v1_beta(msg_dict["v1beta"])
    else:
        raise Exception("Invalid config")


def _convert_mixers(mixers):
    if mixers is None:
        return {}

    ret = {}
    for name, data in mixers.items():
        temp_list = []
        for correction in data["correction"]:
            if "frequency" in correction:
                frequency = float(correction["frequency"])
            else:
                frequency = 0.0

            if "frequencyNegative" in correction:
                if bool(correction["frequencyNegative"]):
                    frequency = -frequency

            if "loFrequency" in correction:
                lo_frequency = float(correction["loFrequency"])
            else:
                lo_frequency = 0.0

            temp_dict = {"intermediate_frequency": frequency, "lo_frequency": lo_frequency,
                         "correction": _convert_matrix(correction["correction"])}
            temp_list.append(temp_dict)

        ret[name] = temp_list
    return ret


def _convert_matrix(matrix):
    if "v00" in matrix:
        v00 = matrix["v00"]
    else:
        v00 = 0.0

    if "v01" in matrix:
        v01 = matrix["v01"]
    else:
        v01 = 0.0

    if "v10" in matrix:
        v10 = matrix["v10"]
    else:
        v10 = 0.0
    if "v11" in matrix:
        v11 = matrix["v11"]
    else:
        v11 = 0.0

    return [v00, v01, v10, v11]


def _convert_integration_weights(integration_weights):
    if integration_weights is None:
        return {}

    ret = {}
    for name, data in integration_weights.items():
        ret[name] = {"cosine": data["cosine"], "sine": data["sine"]}
    return ret


def _convert_digital_wave_forms(digital_wave_forms):
    if digital_wave_forms is None:
        return {}

    ret = {}
    for name, data in digital_wave_forms.items():
        temp_list = []
        for sample in data["samples"]:
            value = 0
            if "value" in sample:
                value = 1

            if "length" in sample:
                temp_list.append((value, sample["length"]))
            else:
                temp_list.append((value, 0))

        ret[name] = {"samples": temp_list}
    return ret


def _convert_wave_forms(wave_forms):
    if wave_forms is None:
        return {}

    ret = {}
    for name, data in wave_forms.items():
        if "arbitrary" in data:
            ret[name] = data["arbitrary"]
            ret[name]["type"] = "arbitrary"
        elif "constant" in data:
            ret[name] = data["constant"]
            if "sample" not in ret[name]:
                ret[name]["sample"] = 0.0
            ret[name]["type"] = "constant"
        elif "compressed" in data:
            ret[name] = {}
            ret[name]["samples"] = data["compressed"]["samples"]
            ret[name]["sample_rate"] = data["compressed"]["sampleRate"]
            ret[name]["type"] = "compressed"

    return ret


def _convert_pulses(pulses):
    if pulses is None:
        return {}

    ret = {}

    for name, data in pulses.items():
        temp_dict = {"length": data.get("length"), "waveforms": data.get("waveforms"),
                     "digital_marker": data.get("digitalMarker"), "integration_weights": data.get("integrationWeights")}

        if "operation" in data:
            for key, value in QuaConfig.PulseDec.Operation.items():
                if value == data["operation"]:
                    temp_dict["operation"] = key.lower()
        else:
            temp_dict["operation"] = "measurement"

        ret[name] = temp_dict
    return ret


def _convert_v1_beta(config):
    results = {}
    results["version"] = 1
    results["controllers"] = _convert_controllers(config.get("controllers"))
    results["elements"] = _convert_elements(config.get("elements"))
    results["pulses"] = _convert_pulses(config.get("pulses"))
    results["waveforms"] = _convert_wave_forms(config.get("waveforms"))
    results["digital_waveforms"] = _convert_digital_wave_forms(config.get("digitalWaveforms"))
    results["integration_weights"] = _convert_integration_weights(config.get("integrationWeights"))
    results["mixers"] = _convert_mixers(config.get("mixers"))
    return results


def _convert_controllers(controllers):
    if controllers is None:
        return {}

    ret = {}
    for name, data in controllers.items():
        ret[name] = {"type": data["type"]}
        if "analogOutputs" in data:
            ret[name]["analog_outputs"] = _convert_controller_analog_outputs(data["analogOutputs"])
        if "analogInputs" in data:
            ret[name]["analog_inputs"] = _convert_controller_analog_inputs(data["analogInputs"])
        if "digitalOutputs" in data:
            ret[name]["digital_outputs"] = _convert_controller_digital_outputs(data["digitalOutputs"])

    return ret


def _convert_inputs(inputs):
    if inputs is None:
        return {}

    ret = {}
    for name, data in inputs.items():
        ret[name] = {"delay": data.get("delay", 0)}
        ret[name]["buffer"] = data.get("buffer", 1)

        if "output" in data:
            # deprecation from 0.0.28
            ret[name]["output"] = _port_reference(data["output"])
        if "port" in data:
            ret[name]["port"] = _port_reference(data["port"])

    return ret


def _convert_elements(elements):
    if elements is None:
        return {}

    ret = {}
    for name, data in elements.items():
        element_config_data = {"outputs": _convert_element_output(data.get("outputs")),
                               "digitalInputs": _convert_inputs(data.get("digitalInputs"))}

        if "timeOfFlight" in data:
            element_config_data["time_of_flight"] = int(data["timeOfFlight"])

        if "smearing" in data:
            element_config_data["smearing"] = int(data["smearing"])

        if "intermediateFrequency" in data:
            freq = int(data["intermediateFrequency"])
            if "intermediateFrequencyNegative" in data and bool(data["intermediateFrequencyNegative"]):
                    freq = -freq
            element_config_data["intermediate_frequency"] = freq

        if "operations" in data:
            element_config_data["operations"] = data["operations"]

        if "measurementQe" in data:
            element_config_data["measurement_qe"] = data["measurementQe"]

        if "singleInput" in data:
            element_config_data["singleInput"] = _convert_single_inputs(data["singleInput"])
        elif "mixInputs" in data:
            element_config_data["mixInputs"] = _convert_mix_inputs(data["mixInputs"])

        if "holdOffset" in data:
            element_config_data["hold_offset"] = _convert_hold_offset(data["holdOffset"])

        ret[name] = element_config_data

    return ret


def _convert_mix_inputs(mix_inputs):
    res = {"I": _port_reference(mix_inputs["I"]), "Q": _port_reference(mix_inputs["Q"]),
           "mixer": mix_inputs.get("mixer")}

    if "loFrequency" in mix_inputs:
        res["lo_frequency"] = int(mix_inputs["loFrequency"])
    else:
        res["lo_frequency"] = 0.0

    return res


def _convert_single_inputs(single):
    res = {"port": _port_reference(single["port"])}
    return res


def _convert_hold_offset(hold_offset):
    res = {"duration": hold_offset["duration"]}
    return res


def _convert_controller_analog_outputs(outputs):
    if outputs is None:
        return {}

    ret = {}
    for name, data in outputs.items():
        if "offset" in data:
            ret[name] = {"offset": data["offset"]}
        else:
            ret[name] = {"offset": 0.0}
    return ret


def _convert_controller_analog_inputs(inputs):
    if inputs is None:
        return {}

    ret = {}
    for name, data in inputs.items():
        offset = 0.0
        if "offset" in data:
            offset = data["offset"]

        gain_db = 0
        if "gainDb" in data:
            gain_db = data["gainDb"]

        ret[name] = {"offset": offset, "gain_db": gain_db}
    return ret


def _convert_controller_digital_outputs(outputs):
    if outputs is None:
        return {}

    ret = {}
    for name, data in outputs.items():
        ret[name] = {}
    return ret


def _convert_element_output(outputs):
    if outputs is None:
        return {}

    ret = {}
    for name, data in outputs.items():
        ret[name] = _port_reference(data)
    return ret


def _port_reference(data):
    return data["controller"], data["number"]
