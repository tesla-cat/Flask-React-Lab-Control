/*
 ***************************************************************************
 * USB functions for SignalCore Inc SC5503B products using "libusb"
 * functions and driver
 *
 * "libusb" license is covered by the LGPL 
 *	
 *	Copyright (c) 2013 SignalCore Inc.
 *	
 *  rev 2.0
 ****************************************************************************
 * SC5503B header file 
*/

#ifndef __SC5503B_H__
#define __SC5503B_H__

#define MAX_TRANSFER_BYTES				6
#define MAX_DEVICES						256
#define MAX_PORT_NAME_LEN				10

#define CALEEPROMSIZE					15168
#define USEREEPROMSIZE					16384  

//ERROR Set
#ifndef SCISTATUS
	typedef long SCISTATUS;
#endif

#define SCI_ERROR_NONE									0
#define SCI_ERROR_INVALID_DEVICE_HANDLE					-1
#define SCI_ERROR_NO_DEVICE								-2
#define SCI_ERROR_INVALID_DEVICE						-3
#define SCI_ERROR_MEM_UNALLOCATE						-4
#define SCI_ERROR_MEM_EXCEEDED							-5
#define SCI_ERROR_INVALID_REG							-6
#define SCI_ERROR_INVALID_ARGUMENT						-7
#define SCI_ERROR_COMM_FAIL								-8
#define SCI_ERROR_OUT_OF_RANGE							-9
#define SCI_ERROR_PLL_LOCK								-10
#define	SCI_ERROR_TIMED_OUT								-11

//  Define USB SignalCore ID

#define SCI_USB_VID					0x277C  // SignalCore Vendor ID 
#define	SCI_USB_PID					0x0023  // Product ID SC5503B
#define SCI_SN_LENGTH				0x08
#define SCI_PRODUCT_NAME			"SC5503B"

//  Define SignalCore USB endpoints
#define	SCI_ENDPOINT_IN_INT			0x81
#define	SCI_ENDPOINT_OUT_INT		0x02
#define	SCI_ENDPOINT_IN_BULK		0x83
#define	SCI_ENDPOINT_OUT_BULK		0x04

// 	Define for control endpoints
#define USB_ENDPOINT_IN				0x80
#define USB_ENDPOINT_OUT			0x00
#define USB_TYPE_VENDOR				(0x02 << 5)
#define USB_RECIP_INTERFACE			0x01

// The Fine tune frequency stepping modes
#define DISABLEDALC						1 // Disable ALC close loop, use open loop level control
#define DISABLEAUTOLEVEL				1 // Level correction is disabled when frequency is tuned, user set the new rf level
#define DDSFINEMODE						2 //1 Hz tuning steps, DDS & PLL implementation


//Define device registers
#define INITIALIZE						0x01    // Initialize the devices
#define SET_SYSTEM_ACTIVE				0x02    // Set the System Active light
#define DEVICE_STANDBY					0x05    // Shut down power to the analog RF module puts device into standby mode

#define RF_FREQUENCY					0x10	// set the frequency
#define RF_POWER						0x11	// Set Power of rf output
#define SYNTH_MODE						0x12	// LO1 control
#define RF_ALC_MODE						0x13	// Disable the close loop ALC and output power is open loop controlled
#define SET_ALC_DAC_VALUE				0x14	// Write to the amplitude control DAC to control output amplitude
#define REFERENCE_MODE					0x15    // Reference clock settings
#define REFERENCE_DAC_SETTING			0x16    // set reference clock DAC 
#define GET_DEVICE_STATUS				0x17    // load the board status into the SPI output buffer
#define GET_TEMPERATURE					0x18    // load sensor temperature into the SPI output buffer
																				
#define CAL_EEPROM_READ					0x20    // transfer user EEPROM data to SPI output buffer
#define CAL_EEPROM_WRITE				0x21    // calibration EEPROM write
#define USER_EEPROM_READ				0x22    // transfer user EEPROM data to SPI output buffer
#define USER_EEPROM_WRITE				0x23    // user EEPROM write
#define RF_OUT_ENABLE					0x26	// Enable the RF power output
#define STORE_STARTUP_STATE				0x28	// Stores the current settings as the default power-up/init state
#define AUTO_POWER_DISABLE				0x29	// Disable auto power adjust on frequency change
#define GET_ALC_DAC_VALUE				0x2A	// Read back the current LAC DAC value
#define GET_RF_PARAMETERS				0x2B	// Read back current RF parameters such as frequency

#ifdef __cplusplus
extern "C"
{
#endif

typedef struct deviceInfo_t
{
	UINT32 productSerialNumber;
	UINT32 rfModuleSerialNumber;
	float firmwareRevision;
	float synthHardwareRevision;
	float signalHardwareRevision;
	UINT32 calDate; // year,month,day,hour 
	UINT32 manDate; // year,month,day,hour
} 	deviceInfo_t;

typedef struct deviceStatus_t
{
	UINT8 tcxoPllLock;	//Master 10 MHz TCXO
	UINT8 vcxoPllLock;	//100 MHz VCXO
	UINT8 finePllLock;	//Fine Tuning PLL 				
	UINT8 coarsePllLock; //Coarse tuning PLL
	UINT8 sumPllLock;    //Main tuning PLL
	UINT8 extRefDetected; //Indicates whether an external source is detected at the ref input port
	UINT8 refClkOutEnable; //Indicates if the reference output port is enabled
	UINT8 extRefLockEnable; //Indicates if the master tcxo is locked to the external source
	UINT8 alcOpen; // Indicates that the ALC is in open loop 
	UINT8 fastTuneEnable; // Indicates if Tuning mode of the YIG oscillator in the main PLL 
	UINT8 standbyEnable; // Power down of analog circuit 
	UINT8 rfEnable; // RF port is enabled
	UINT8 pxiClkEnable; // PXI 10 MHz port is enabled
}	deviceStatus_t;

typedef struct
{
	ULONG64	frequency; //current rf frequency
	float	powerLevel; //current power level
	UINT8	rfEnable;	//RF power Enable switch on
	UINT8	alcOpen;	// Power ALC loop Open (closed normally)
	UINT8	autoLevelEnable;	//Automatically apply calibration to keep level constant when frequency is changed
	UINT8	fastTune;	//fastTune enable
	UINT8	tuneStep; //0 = 1 MHz step, 1 = 25kHz step, 2 = 1 Hz step
	UINT8	referenceSetting; // bit0=Lock ext. reference disable/enable, bit1=refClkOutDisable/Enable, bit2=ref10MHz/ref100MHz output,  bit3=pxi10Clk Enable
}	rfParameters_t;


/* Export Function Prototypes */
/* sc5503b.c */

/*	Function to find the serial numbers of all SignalCore device with the same product ID
	return:		The number of product devices found 
	output:		2-D array (or pointers) to pass out the list serial numbers for devices found
	Example, calling function could declare:
		char **serialNumberList;
		serialNumberList = (char**)malloc(sizeof(char*)*50); // 50 serial numbers
		for (i=0;i<50; i++)
			searchNumberList[i] = (char*)malloc(sizeof(char)*SCI_SN_LENGTH); 
	and pass searchNumberList into the function.
*/
SCISTATUS __stdcall sc5503b_SearchDevices(char **serialNumberList);

/* Function aimed to handle LabVIEW calls. As labView is not able to handle **pointers
*	*pointer to maximum of 20 devices are passed back
*/
SCISTATUS __stdcall sc5503b_SearchDevicesLV(char *serialNumberList);

/*	Function opens the target USB device.
	return:		pointer to usb_dev_handle type
	input: 		devSerialNum is the product serial number. Product number is available on
				the product label.
*/
SCISTATUS __stdcall sc5503b_OpenDevice(char *devSerialNum, HANDLE *devHandle);

/*	Function opens the target USB device aimed to handle LabVIEW calls.
	return:		pointer to usb_dev_handle type
	input: 		devSerialNum is the product serial number. Product number is available on
				the product label.
*/
SCISTATUS __stdcall sc5503b_OpenDeviceLV(char *devSerialNum, HANDLE *devHandle);

/*	Function  closes USB device associated with the handle.
	return:		error code
	input: 		usb device handle
*/
SCISTATUS __stdcall sc5503b_CloseDevice(HANDLE devHandle);
	


/* 	Register level access function prototypes
=========================================================================================
*/
/* 	Writing the register with via the PXI device handle allocated by sc5503b_OpenDevice
return: error code
input: commandByte contains the target register address, eg 0x10 is the frequency register
input: instructWord contains necessary data for the specified register address
*/
SCISTATUS __stdcall sc5503b_RegWrite(HANDLE devHandle,
	UCHAR commandByte,
	ULONG64 instructWord);

/* 	Reading the register with via the PXI device handle allocated by sc5503b_OpenDevice
input: commandByte contains the target register address, eg 0x10 is the frequency register
input: instructWord contains necessary data for the specified register address
output: receivedWord is the return data request through the commandByte and instructWord
*/
SCISTATUS __stdcall sc5503b_RegRead(HANDLE devHandle,
	UCHAR command,
	ULONG64 instructWord,
	ULONG64 *receivedWord);


/* 	Product configuration wrapper function prototypes
=========================================================================================
*/
/*	Initializes the device
return: error code
input: 		Mode	0: 	The device initializes to the power up state
1:	The device reprograms all internal components to the current device
state
*/
SCISTATUS __stdcall sc5503b_InitDevice(HANDLE devHandle, UINT8 mode);

/*	Puts the device in power standby mode.
return: error code
input: standbyStatus	0:	Take device out off power standby. If the device was in standby,
the device will be reprogrammed to the previous state. However,
give the device at least 1 second wait for it settle
1:	The device is taken into standby. All power to the RF module
(Brick) is turned off to conserve power.
*/
SCISTATUS __stdcall sc5503b_SetDeviceStandby(HANDLE devHandle, UINT8 standbyStatus);

/*	Sets the device frequency
return: error code
input:	frequency in Hz
*/
SCISTATUS __stdcall sc5503b_SetFrequency(HANDLE devHandle, ULONG64 frequency);

/*	Sets the rf power level to to some value
return: error code
input:	powerLevel 	is the value in dBm. resolution of 0.01 dB
*/
SCISTATUS __stdcall sc5503b_SetPowerLevel(HANDLE devHandle,
	float powerLevel);
/*	Turns the RF power on/off
return: error code
input:	mode		1 turns the RF On, 0 turns it off.
*/
SCISTATUS __stdcall sc5503b_SetRfOutput(HANDLE devHandle, UINT8 mode);
/*
Set the automatic level control to either open loop or close-loop. In close-loop, power is
monitored, fed back, and adjusted dynamically. In open loop, power is adjusted without feed-
back.
return: error code
input: 	mode	0  close loop, 1 open loop
*/
SCISTATUS __stdcall sc5503b_SetAlcMode(HANDLE devHandle, UINT8 mode);

/*  Adjust the Automatic level control DAC. User may use this to make corrections if needed
return: error code
input: 	DAC value, 14bit dac
*/
SCISTATUS __stdcall sc5503b_SetAlcDac(HANDLE devHandle, UINT32 dacValue);

/*	Set the synthesizer mode to determine the tuning behavior of the device
return:	error code
input:	fastTuneEnable	0: 	disable fast tuning of LO1
1:	enables the fast tuning of LO1
input:	fineTuneMode	0:	device tunes at 1 MHz step using PLL methods only
1:	device tunes at 25 kHz step using PLL methods only
2:	device tunes at 1 Hz step using DDS and PLL methods
*/
SCISTATUS __stdcall sc5503b_SetSynthesizerMode(HANDLE devHandle,
	UINT8 fastTuneEnable,
	UINT32 fineTuneMode);

/*	Set the reference clock configurations
return:	error code
input:	lockExtEnable	enables the device to lock to an external source. If the source
not available error code returns. The device will not attempt
to lock and waits for source.
input:	RefOutEnable	enable the device to send out its reference clock
input:	Clk100Enable	if RefOutEnable = 1, this changes the clock frequency from
10 MHz to 100 MHz.
*/
SCISTATUS __stdcall sc5503b_SetClockReference(HANDLE devHandle,
	UINT8 lockExtEnable,
	UINT8 refOutEnable,
	UINT8 clk100Enable,
	UINT8 pxiClk);

/*	Sets the value of the Clock reference DAC and hence adjusts reference clock frequency
return: error code
input: 	dacValue	a 14 bit word
*/
SCISTATUS __stdcall sc5503b_SetReferenceDac(HANDLE devHandle, UINT32 dacValue);

/*	Write single byte to the user EEPROM address
return: error code
input: 	memAdd		the address of the EEPROM memory to write to
input:	byteData	the byte data to write to the specified memory address
*/
SCISTATUS __stdcall sc5503b_WriteUserEeprom(HANDLE devHandle,
	UINT32 memAdd,
	UINT8 byteData);

/*	Store the current state of the signal source into EEPROM as the default startup state
return: error code
input:
*/
SCISTATUS __stdcall sc5503b_StoreCurrentState(HANDLE devHandle);

/*	Disables the device from auto adjusting to the power level to the current state when
frequency is changed. Disabling the auto adjust feature allows to device to return faster
for user power level adjust be calling ...SetPowerLevel(). Ff the power remains the same
for the next frequency(ies), this should not be disabled.
return: error code
input:
*/
SCISTATUS __stdcall sc5503b_DisableAutoLevel(HANDLE devHandle, UINT8 mode);


/* Product Export Query (Read) function prototypes */
/*----------------------------------------------------------------------------------------------- */

/*	Function retrives the device attributes such as product serial, calibration dates, firmware revisions
return: error code
output:	deviceInfo		device information structure
*/
SCISTATUS __stdcall sc5503b_GetDeviceInfo(HANDLE devHandle, deviceInfo_t *deviceInfo);
/*	Function retrives the device status - PLL locks status, ref clk config, etc see deviceStatus_t type
return:	error code
output:	device status
*/
SCISTATUS __stdcall sc5503b_GetDeviceStatus(HANDLE devHandle, deviceStatus_t *deviceStatus);

/*	Function retrives the device temperature in degrees Celsius
return:	error code
output:	device temperature
*/
SCISTATUS __stdcall sc5503b_GetTemperature(HANDLE devHandle, float *temperature);

/*	Function retrives the RF ALC DAC value
return:	error code
output:	dac value
*/
SCISTATUS __stdcall sc5503b_GetAlcDacValue(HANDLE devHandle, UINT32 *dacValue);

/*	Function retrives a single byte from cal EEPROM address
return:	error code
input:	input memAdd	memory address
output:	byteData		1 byte data
*/
SCISTATUS __stdcall sc5503b_ReadCalEeprom(HANDLE devHandle,
	UINT32 memAdd,
	UINT8 *byteData);

/*	Function retrives a single byte from user EEPROM address
return:	error code
input:	input memAdd	memory address
output:	byteData		1 byte data
*/
SCISTATUS __stdcall sc5503b_ReadUserEeprom(HANDLE devHandle,
	UINT32 memAdd,
	UINT8 *byteData);

/* Function retrives the rfParameters
return: error code
output: rfParameters
*/
SCISTATUS __stdcall sc5503b_GetRfParameters(HANDLE devHandle,
	rfParameters_t *rfParameters);

/* USB specific related functions */	

/*	Raw transferFunction not made public in documentation but useful to 
*	access factory only registers
*/
SCISTATUS __stdcall sc5503b_UsbTransfer(HANDLE devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn);

# 	ifdef __cplusplus
}
#	endif

#	endif  /* __SC5503B__H__ */	