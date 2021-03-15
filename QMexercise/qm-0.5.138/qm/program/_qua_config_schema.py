
from qm.pb.inc_qua_config_pb2 import QuaConfig
from marshmallow import Schema, fields, post_load
from marshmallow_polyfield import PolyField
from qm._logger import logger


def validate_config(config):
    pass


def load_config(config):
    return QuaConfigSchema().load(config)


PortReferenceSchema = fields.Tuple(
    (
        fields.String(),
        fields.Int()
    ),
    description="(tuple) of the form ((string) controller name, (int) controller output/input port)"
)


class AnalogOutputPortDefSchema(Schema):
    offset = fields.Number(
        description='DC offset to output, range: (-0.5, 0.5). Will be applied only when program runs.')

    class Meta:
        title = 'OPX analog output port'
        description = 'specification of the properties of a physical analog output port of the OPX. '

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.AnalogOutputPortDec()
        item.offset = data["offset"]
        return item


class AnalogInputPortDefSchema(Schema):
    offset = fields.Number(
        description='DC offset to input, range: (-0.5, 0.5). Will be applied only when program runs.')

    gain_db = fields.Int(
        strict=True,
        description="Gain of the pre-ADC amplifier in dB. In practice only attenuation is allowed and range is -12 to 0",
    )

    class Meta:
        title = 'OPX analog input port'
        description = 'specification of the properties of a physical analog input port of the OPX. '

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.AnalogInputPortDec()
        if "offset" in data:
            item.offset = data["offset"]
        else:
            item.offset = 0.0
        if "gain_db" in data:
            item.gainDb.value = data["gain_db"]

        return item


class DigitalOutputPortDefSchema(Schema):
    offset = fields.Number()

    class Meta:
        title = 'OPX digital port'
        description = 'For future use'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.DigitalOutputPortDec()
        return item


class ControllerSchema(Schema):
    type = fields.Constant("opx1")
    analog = fields.Dict(fields.Int(), fields.Nested(AnalogOutputPortDefSchema),
                         description='a collection of analog output ports and the properties associated with them.')

    analog_outputs = fields.Dict(fields.Int(), fields.Nested(AnalogOutputPortDefSchema),
                                 description='a collection of analog output ports and the properties associated with them.')
    analog_inputs = fields.Dict(fields.Int(), fields.Nested(AnalogInputPortDefSchema),
                                description='a collection of analog input ports and the properties associated with them.')
    digital_outputs = fields.Dict(fields.Int(), fields.Nested(DigitalOutputPortDefSchema),
                                  description='a collection of digital output ports and the properties associated with them.')

    class Meta:
        title = 'controller'
        description = 'specification of a single OPX controller. Here we define its static properties. '

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.ControllerDec()
        item.type = data["type"]

        if "analog" in data:
            # Deprecated in 0.0.41
            logger.warning("'analog' under controllers.<controller> is deprecated. "
                           "use 'analog_outputs' instead")
            if "analog_outputs" in data:
                for k, v in data["analog_outputs"].items():
                    item.analogOutputs.get_or_create(k).CopyFrom(v)
            else:
                for k, v in data["analog"].items():
                    item.analogOutputs.get_or_create(k).CopyFrom(v)
        else:
            for k, v in data["analog_outputs"].items():
                item.analogOutputs.get_or_create(k).CopyFrom(v)

        if "analog_inputs" in data:
            for k, v in data["analog_inputs"].items():
                item.analogInputs.get_or_create(k).CopyFrom(v)

        if "digital_outputs" in data:
            for k, v in data["digital_outputs"].items():
                item.digitalOutputs.get_or_create(k).CopyFrom(v)

        return item


class DigitalInputSchema(Schema):
    delay = fields.Int(description='the digital pulses played to this element will be delayed by this amount [nsec] '
                                   'relative to the analog pulses. <br />'
                                   'An intinsic negative delay of 143+-2nsec exists by default')
    buffer = fields.Int(description='all digital pulses played to this element will be convolved'
                                    'with a digital pulse of value 1 with this length [nsec]')
    output = PortReferenceSchema
    port = PortReferenceSchema

    class Meta:
        title = 'digital input'
        description = 'specification of the digital input of a element'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.DigitalPortReference()
        item.delay = data["delay"]
        item.buffer = data["buffer"]
        item.port.SetInParent()
        if "output" in data:
            # deprecation from 0.0.28
            logger.warning("'output' under elements.<el>.digitalInputs.<name>.output is deprecated. "
                           "use 'port' instead elements.<el>.digitalInputs.<name>.port")
            item.port.controller = data["output"][0]
            item.port.number = data["output"][1]
        if "port" in data:
            item.port.controller = data["port"][0]
            item.port.number = data["port"][1]
        return item


class IntegrationWeightSchema(Schema):
    cosine = fields.List(fields.Float(), description='W_cosine, a fixed-point vector of integration weights, <br />'
                                                     'range: [-2048, 2048] in steps of 2**-15')
    sine = fields.List(fields.Float(), description='W_sine, a fixed-point vector of integration weights, <br />'
                                                   'range: [-2048, 2048] in steps of 2**-15')

    class Meta:
        title = 'integration weights'
        description = '''specification of a set of measurement integration weights. Result of integration will be: <br />
        sum over i of (W_cosine[i]*cos[w*t[i]] + W_sine[i]*sin[w*t[i]])*analog[i]. <br />
        Here: <br />
        w is the angular frequency of the quantum element, and analog[i] is the analog data acquired by the controller. <br />
        W_cosine, W_sine are the vectors associated with the 'cosine' and 'sine' keys, respectively. <br />
        Note: the entries in the vector are specified in 4nsec intervals, and each entry is repeated four times
        during the demodulation.<br /><br />
        Example: <br />
        W_cosine = [2.0], W_sine = [0.0] will lead to the following demodulation operation: <br />
        2.0*(cos[w*t[0]]*analog[0] + cos[w*t[1]]*analog[1] + cos[w*t[2]]*analog[2] + cos[w*t[3]]*analog[3])
        '''

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.IntegrationWeightDec()
        if "cosine" in data:
            item.cosine.extend(data["cosine"])
        if "sine" in data:
            item.sine.extend(data["sine"])
        return item


class WaveFormSchema(Schema):
    pass


class ConstantWaveFormSchema(WaveFormSchema):
    type = fields.String(description="\"constant\"")
    sample = fields.Float(description='value of constant, range: (-0.5, 0.5)')

    class Meta:
        title = 'constant waveform'
        description = 'raw data constant amplitude of a waveform'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.WaveformDec()
        item.constant.SetInParent()
        item.constant.sample = data["sample"]
        return item


class ArbitraryWaveFormSchema(WaveFormSchema):
    type = fields.String(description="\"arbitrary\"")
    samples = fields.List(fields.Float(), description='list of values of arbitrary waveforms, range: (-0.5, 0.5)')

    class Meta:
        title = 'arbitrary waveform'
        description = 'raw data samples of the modulating envelope of an arbitrary waveform'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.WaveformDec()
        item.arbitrary.SetInParent()
        item.arbitrary.samples.extend(data["samples"])
        return item


def _waveform_schema_deserialization_disambiguation(object_dict, data):
    type_to_schema = {
        'constant': ConstantWaveFormSchema,
        'arbitrary': ArbitraryWaveFormSchema,
    }
    try:
        return type_to_schema[object_dict['type']]()
    except KeyError:
        pass

    raise TypeError("Could not detect type. "
                    "Did not have a base or a length. "
                    "Are you sure this is a shape?")


_waveform_poly_field = PolyField(
    deserialization_schema_selector=_waveform_schema_deserialization_disambiguation,
    required=True
)


class DigitalWaveFormSchema(Schema):
    samples = fields.List(fields.Tuple([fields.Int(), fields.Int()]), description=
    '''(list of tuples) specifying the analog data according to following code: <br />
    The first entry of each tuple is 0 or 1 and corresponds to the digital value, <br /> 
    and the second entry is the length in nsec to play the value, in steps of 1. <br />
    If value is 0, the value will be played to end of pulse.
    ''')

    class Meta:
        title = 'digital waveform'
        description = 'raw data samples of a digital waveform'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.DigitalWaveformDec()
        for sample in data["samples"]:
            s = item.samples.add()
            s.value = bool(sample[0])
            s.length = int(sample[1])
        return item


class MixerSchema(Schema):
    freq = fields.Int(description='element resonance frequency associated with correction matrix')
    intermediate_frequency = fields.Int(description='intermediate frequency associated with correction matrix')
    lo_freq = fields.Int(description='LO frequency associated with correction matrix')
    lo_frequency = fields.Int(description='LO frequency associated with correction matrix')
    correction = fields.Tuple((fields.Number(), fields.Number(), fields.Number(), fields.Number()),
                              description='(tuple) a 2x2 matrix entered as a 4 element tuple specifying the correction matrix')

    class Meta:
        title = 'mixer'
        description = '''specification of the correction matrix elements for an IQ mixer that drives an element.
        This is a list of correction matrices for each LO frequency and QE resonance frequency.'''

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.CorrectionEntry()

        lo_frequency = 0
        if "lo_freq" in data:
            # Deprecated in 0.0.45
            logger.warning("'lo_freq' under mixers.<mixer> is deprecated. "
                           "use 'lo_frequency' instead")

            item.loFrequency = data["lo_freq"]
            lo_frequency = data["lo_freq"]

        if "lo_frequency" in data:
            item.loFrequency = data["lo_frequency"]
            lo_frequency = data["lo_frequency"]

        if "freq" in data:
            # Deprecated in 0.0.45
            logger.warning("'freq' under mixers.<mixer> is deprecated. "
                           "use 'intermediate_frequency' instead")
            item.frequency = data["freq"] - lo_frequency

        if "intermediate_frequency" in data:
            item.frequency = abs(data["intermediate_frequency"])
            item.frequencyNegative = data["intermediate_frequency"] < 0

        item.correction.SetInParent()
        item.correction.v00 = data["correction"][0]
        item.correction.v01 = data["correction"][1]
        item.correction.v10 = data["correction"][2]
        item.correction.v11 = data["correction"][3]
        return item


class PulseSchema(Schema):
    operation = fields.String(description='type of operation. Possible values: control, measurement')
    length = fields.Int(description='length of pulse [nsec]. Possible values: 16 to 4194304 in steps of 4')
    waveforms = fields.Dict(fields.String(),
                            fields.String(
                                description='name of waveform to be played at the input port given in associated keys'),
                            description='''a specification of the analog waveform to be played with this pulse. <br />
                            If associated element has singleInput, key is "single". <br />
                            If associated element has "mixInputs", keys are "I" and "Q".''')
    digital_marker = fields.String(description='name of the digital marker to be played with this pulse')
    integration_weights = fields.Dict(fields.String(),
                                      fields.String(description=
                                                    'the name of the integration weights as it appears under the "integration_weigths" entry in the configuration dict'),
                                      description='''if measurement pulse, a collection of integration weights associated with this pulse, <br />
                                       to be applied to the data output from the element and sent to the controller. <br />
    Keys: name of integration weights to be used in the measurement command.''')

    class Meta:
        title = 'pulse'
        description = '''specification of a single pulse.  Here we define its analog
                         and digital components, as well as properties related to measurement associated with it.'''

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.PulseDec()
        item.length = data["length"]
        if data["operation"] == "measurement":
            item.operation = QuaConfig.PulseDec.MEASUREMENT
        elif data["operation"] == "control":
            item.operation = QuaConfig.PulseDec.CONTROL
        if "integration_weights" in data:
            for k, v in data["integration_weights"].items():
                item.integrationWeights[k] = v
        if "waveforms" in data:
            for k, v in data["waveforms"].items():
                item.waveforms[k] = v
        if "digital_marker" in data:
            item.digitalMarker.value = data["digital_marker"]
        return item


class SingleInputSchema(Schema):
    port = PortReferenceSchema

    class Meta:
        title = 'single input'
        description = 'specification of the input of an element which has a single input port'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.SingleInput()
        _port(item.port, data["port"])
        return item


class HoldOffsetSchema(Schema):
    duration = fields.Int(description='''to be implemented''')

    class Meta:
        title = 'Hold Offset'
        description = 'to be implemented'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.HoldOffset()
        item.duration = data["duration"]
        return item


class MixInputSchema(Schema):
    I = PortReferenceSchema
    Q = PortReferenceSchema
    mixer = fields.String(description='''the mixer used to drive the input of the element,
    taken from the names in mixers entry in the main configuration''')
    lo_frequency = fields.Int(
        description='the frequency of the local oscillator which drives the mixer')

    class Meta:
        title = 'mixer input'
        description = 'specification of the input of an element which is driven by an IQ mixer'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.MixInputs()
        _port(item.I, data["I"])
        _port(item.Q, data["Q"])
        item.mixer = data.get("mixer", "")
        item.loFrequency = data.get("lo_frequency", 0)
        return item


class SingleInputCollectionSchema(Schema):
    inputs = fields.Dict(keys=fields.String(), values=PortReferenceSchema,
                         description='''A collection of named input to the port''')

    class Meta:
        title = 'single input collection'
        description = 'define a set of single inputs which can be switched during play statements'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        item = QuaConfig.SingleInputCollection()
        for (name, pair) in data["inputs"].items():
            port = item.inputs.get_or_create(name)
            _port(port, pair)
        return item


class ElementSchema(Schema):
    frequency = fields.Int(description='''resonance frequency [Hz].
    Actual carrier frequency output by the OPX to the input of this element is frequency - lo_frequency.
    ''')

    intermediate_frequency = fields.Int(description='''intermediate frequency [Hz].
    The actual frequency to be output by the OPX to the input of this element
    ''', allow_none=True)

    measurement_qe = fields.String(description='not implemented')
    operations = fields.Dict(keys=fields.String(), values=fields.String(
        description='the name of the pulse as it appears under the "pulses" entry in the configuration dict'),
                             description='''A collection of all pulse names to be used in play and measure commands''')
    singleInput = fields.Nested(SingleInputSchema)
    mixInputs = fields.Nested(MixInputSchema)
    singleInputCollection = fields.Nested(SingleInputCollectionSchema)
    time_of_flight = fields.Int(description='''delay time [nsec] from start of pulse until output of element reaches OPX.
    Minimal value: 180. Used in measure command, to determine the delay between the start of a measurement pulse
    and the beginning of the demodulation and/or raw data streaming window.''')
    smearing = fields.Int(description='''padding time, in nsec, to add to both the start and end of the raw data
    streaming window during a measure command.''')
    outputs = fields.Dict(keys=fields.String(),
                          values=PortReferenceSchema,
                          description='collection of up to two output ports of element. Keys: "out1" and "out2".')
    digitalInputs = fields.Dict(keys=fields.String(),
                                values=fields.Nested(DigitalInputSchema))
    outputPulseParameters = fields.Dict(description='pulse parameters for TimeTagging')

    hold_offset = fields.Nested(HoldOffsetSchema)

    class Meta:
        title = 'quantum element (QE)'
        description = '''specification of a single element. Here we define to which port of the OPX the element is
                        connected, what is the RF frequency
                           of the pulses  sent and/or received from this element, and others,
                           as described in the drop down list.'''

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        el = QuaConfig.ElementDec()
        if "frequency" in data:
            # Deprecated in 0.0.43
            logger.warning("'frequency' under elements.<element> is deprecated. "
                           "use 'intermediate_frequency' instead")
            if "mixInputs" in data:
                el.intermediateFrequency.value = data["frequency"] - data["mixInputs"].loFrequency
            else:
                el.intermediateFrequency.value = data["frequency"]

        if "intermediate_frequency" in data and data["intermediate_frequency"] is not None:
            el.intermediateFrequency.value = abs(data["intermediate_frequency"])
            el.intermediateFrequencyNegative = data["intermediate_frequency"] < 0
        if "singleInput" in data: el.singleInput.CopyFrom(data["singleInput"])
        if "mixInputs" in data: el.mixInputs.CopyFrom(data["mixInputs"])
        if "singleInputCollection" in data: el.singleInputCollection.CopyFrom(data["singleInputCollection"])
        if "measurement_qe" in data:
            el.measurementQe.value = data["measurement_qe"]
        if "time_of_flight" in data:
            el.timeOfFlight.value = data["time_of_flight"]
        if "smearing" in data:
            el.smearing.value = data["smearing"]
        if "operations" in data:
            for k, v in data["operations"].items():
                el.operations[k] = v
        if "inputs" in data: _build_port(el.inputs, data["inputs"])
        if "outputs" in data: _build_port(el.outputs, data["outputs"])
        if "digitalInputs" in data:
            for k, v in data["digitalInputs"].items():
                item = el.digitalInputs.get_or_create(k)
                item.CopyFrom(v)
        if "outputPulseParameters" in data:
            pulseParameters = data["outputPulseParameters"]
            el.outputPulseParameters.signalThreshold = pulseParameters["signalThreshold"]
            el.outputPulseParameters.signalPolarity = \
                el.outputPulseParameters.Polarity.Value(pulseParameters["signalPolarity"].upper())
            el.outputPulseParameters.derivativeThreshold = pulseParameters["derivativeThreshold"]
            el.outputPulseParameters.derivativePolarity = \
                el.outputPulseParameters.Polarity.Value(pulseParameters["derivativePolarity"].upper())
        if "hold_offset" in data:
            el.holdOffset.CopyFrom(data["hold_offset"])
        return el


def _build_port(col, data):
    if data is not None:
        for k, (controller, number) in data.items():
            col[k].controller = controller
            col[k].number = number


def _port(port, data):
    port.controller = data[0]
    port.number = data[1]


class QuaConfigSchema(Schema):
    version = fields.Int(description='config version. Currently: must be 1')
    elements = fields.Dict(keys=fields.String(), values=fields.Nested(ElementSchema),
                           description=
                           '''A collection of quantum elements. Each quantum element represents and describes a controlled entity
                           which is connected to the ports (analog input, analog output and digital outputs) of the OPX.''')

    controllers = fields.Dict(fields.String(), fields.Nested(ControllerSchema),
                              description=
                              '''A collection of controllers. Each controller represents a control and computation resource
                              on the OPX hardware. Note: currently
                              only a single controller is supported.''')

    integration_weights = fields.Dict(keys=fields.String(), values=fields.Nested(IntegrationWeightSchema),
                                      description=
                                      '''A collection of integration weight vectors used in the demodulation of pulses
                                      returned from a quantum element.''')

    waveforms = fields.Dict(keys=fields.String(), values=_waveform_poly_field,
                            description=
                            '''A collection of analog waveforms to be output when a pulse is played. 
                            Here we specify their defining type (constant, arbitrary or compressed) and their
                            actual datapoints.''')
    digital_waveforms = fields.Dict(keys=fields.String(), values=fields.Nested(DigitalWaveFormSchema),
                                    description=
                                    '''A collection of digital waveforms to be output when a pulse is played.
                                    Here we specify their actual datapoints.''')
    pulses = fields.Dict(keys=fields.String(), values=fields.Nested(PulseSchema),
                         description=
                         '''A collection of pulses to be played to the quantum elements. In the case of a measurement pulse,
                         the properties related to the measurement are specified as well.''')
    mixers = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(MixerSchema)),
                         description=
                         '''A collection of IQ mixer calibration properties, used to post-shape the pulse to compensate
                         for imperfections in the mixers used for upconverting the analog waveforms.''')

    class Meta:
        title = 'QUA Config'
        description = 'QUA program config root object'

    @post_load(pass_many=False)
    def build(self, data, **kwargs):
        configWrapper = QuaConfig()
        configWrapper.v1beta.SetInParent()
        config = configWrapper.v1beta
        version = data["version"]
        if str(version) != "1":
            raise RuntimeError("Version must be set to 1 (was set to " + str(version) + ")")
        if "elements" in data:
            for el_name, el in data["elements"].items():
                config.elements.get_or_create(el_name).CopyFrom(el)
        if "controllers" in data:
            for k, v in data["controllers"].items():
                config.controllers.get_or_create(k).CopyFrom(v)
        if "integration_weights" in data:
            for k, v in data["integration_weights"].items():
                iw = config.integrationWeights.get_or_create(k)
                iw.CopyFrom(v)
        if "waveforms" in data:
            for k, v in data["waveforms"].items():
                iw = config.waveforms.get_or_create(k)
                iw.CopyFrom(v)
        if "digital_waveforms" in data:
            for k, v in data["digital_waveforms"].items():
                iw = config.digitalWaveforms.get_or_create(k)
                iw.CopyFrom(v)
        if "mixers" in data:
            for k, v in data["mixers"].items():
                iw = config.mixers.get_or_create(k)
                iw.correction.extend(v)
        if "pulses" in data:
            for k, v in data["pulses"].items():
                iw = config.pulses.get_or_create(k)
                iw.CopyFrom(v)
        return configWrapper
