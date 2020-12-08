/*
*	The example program shows how the user may want to program the device. This 
*	serves as only as an example. 
*	User may not want to use the calibration data or the method of application 
*	as outlined here. This device provide an extra user EEPROM for convenience, 
*	and may be used to store user calibration in applications where full system 
*	calibration is performed.
*	
*	This example shows how to initialize the device, read information stored
*	in the calibration EEPROM, reading device temperature, calculate the
* 	attenuator setting based on user inputs, set the attenuators and preamp,
*	calculate the conversion gain, read and write to the user EEPROM, and reading
*	the entire calibration EEPROM.
*/

//#include <unistd.h>
#include <Windows.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sc5503b.h>


 /* Some local functions to display results and perform memory allocation */
void displayDeviceStatus(const deviceStatus_t *status)
{
	//DecodeStatus takes in a DeviceStatus_t and prints out the status.
	
	printf("\n\n Device status as read from device \n");
	printf("extRefDetected: %d \n",status->extRefDetected);
	printf("External reference lock status: %d \n",status->tcxoPllLock);
	printf("VCXO 100MHz PLL lock status: %d \n",status->vcxoPllLock); 
	printf("Summing PLL lock status: %d \n",status->sumPllLock); 
	printf("Coarse PLL lock status: %d \n",status->coarsePllLock); 
	printf("Fine PLL lock status: %d \n",status->finePllLock); 
	printf("External reference lock enabled: %d \n",status->extRefLockEnable); 
	printf("Reference clk out enabled: %d \n",status->refClkOutEnable); 
	printf("RF enabled: %d \n",status->rfEnable);
	printf("Fast tune enabled: %d \n",status->fastTuneEnable);
	printf("ALC open loop: %d \n",status->alcOpen);
	printf("StandBy Enabled: %d \n",status->standbyEnable); 
	printf("PXI 10 MHz clk Out Enabled: %d \n",status->pxiClkEnable); 
	printf("\n \n");
	
	if(status->extRefLockEnable)
	{
		if(status->extRefDetected)
		{
			if(status->tcxoPllLock)
			{
				printf("External Reference Detected. Locked to external reference.\n");
			}
			else
			{
				printf("Error: External Reference Detected. Unable to lock to external reference.\n");
			}
		}
		else
		{
			printf("Error: No external reference detected.\n");
		}
	}

}

void displayDeviceAttributes(deviceInfo_t *devInfo)
{
	printf("\n**********DEVICE ATTRIBUTES************* \n");
	printf(" The product serial number is 0x%08X \n",devInfo->productSerialNumber);
	printf(" The module serial number is 0x%08X \n",devInfo->rfModuleSerialNumber);
	printf(" The product firmware rev. is %f \n",devInfo->firmwareRevision);
	printf(" The product hardware rev. is %f \n",devInfo->signalHardwareRevision);
	printf(" The product cal date is: %08X \n\n",
					devInfo->calDate);	
}



/// The main entry-point function.
int main (int argc, char *argv[])
{
	
	//define the device data parameters
	deviceStatus_t devStatus;
	deviceInfo_t devInfo;
	float deviceTemp;
	
	//init some device input values
	unsigned long long int rfFreq = (unsigned long long int)(2000000000); // chan #1 freq = 2.0 GHz
	float powerLevel = 0.0; // rf level;
	
	// parameter to work with the USB device(s)
	#define MAXDEVICES 50
	HANDLE devHandle; //device handle
	int input; // user input to select the device found
	int numOfDevices; // the number of device types found
	char **deviceList;  // 2D to hold serial numbers of the devices found 
	int status; // status reporting of functions
	
	// test read and write 
	int i;
	unsigned char byte;
	unsigned char userData[8] = {0xA1,0xA2,0xA3,0xA4,0x05,0x06,0x07,0xA8};
	unsigned int userMemAdd; 

	// generic counter
	
	
	/* 	Begin by looking for devices attached to the host 
	*	=============================================================================================
	*/
	
	deviceList = (char**)malloc(sizeof(char*)*MAXDEVICES); // MAXDEVICES serial numbers to search
	for (i=0;i<MAXDEVICES; i++)
		deviceList[i] = (char*)malloc(sizeof(char)*SCI_SN_LENGTH); // SCI SN has 8 char
		
	numOfDevices = sc5503b_SearchDevices(deviceList); //searches for SCI for device type
	
	if (numOfDevices == 0) 
	{
		printf("No signal core devices found or cannot not obtain serial numbers\n");
		for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]);
		free(deviceList);
		return 1;
	}

	printf("\n There are %d SignalCore %s USB devices found. \n \n", numOfDevices, SCI_PRODUCT_NAME);
	i = 0;
	while ( i < numOfDevices)
	{
		printf("	Device %d has Serial Number: %s \n", i+1, deviceList[i]);
		i++;
	}
	/* 	*/
	printf("\n Enter the number of the device you wish to select : ");
	
	scanf(" %d",&input);
	getchar();
	if ((input < 1) || (input > numOfDevices)) 
	{
		printf(" No such device !!! exiting... \n");
		return 1;
	}
	/*	Open the selected device through the use of its serial number
	*/
	sc5503b_OpenDevice(deviceList[input - 1], &devHandle);
	
	if (devHandle == NULL) 
	{
		printf("Device with serial number: %s cannot be opened.\n", deviceList[input - 1]);
		printf("Please ensure your device is powered on and connected\n");
		for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]); 
		free(deviceList);
		free(devHandle); //devHandle is allocated memory on OpenDevice(); 
		return 1;
	}

	for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]); 
	free(deviceList); // Done with the deviceList


	/*	Begin communication to the device	
	*/

	printf("\n Init the device ..........\n");	
	status = sc5503b_InitDevice(devHandle, 0);  // reset the device to power on state
	if (status != EXIT_SUCCESS) return 1;
	Sleep(1000); // Give time for the device to properly reset. Reset is not required for most programming purposes.
	printf("\n Enable Rf Output ..........\n");	
	status = sc5503b_SetRfOutput(devHandle, 0x01);
	if (status != EXIT_SUCCESS) return 1;
	status = sc5503b_SetAlcMode(devHandle, 0x01);
	if (status != EXIT_SUCCESS) return 1;

	printf("\n Getting the device status..........\n");	
	status = sc5503b_GetDeviceStatus(devHandle, &devStatus); // Obtain the current status of the device
	if (status != EXIT_SUCCESS) return 1;
	
	displayDeviceStatus(&devStatus); // display the device status 
	
	printf("\nGetting device Info ..........\n");
	status = sc5503b_GetDeviceInfo(devHandle, &devInfo);  // obtain calData
	printf("\nSet Done ..........\n");	
	if (status != EXIT_SUCCESS) return 1;
	displayDeviceAttributes(&devInfo);

	status = sc5503b_SetFrequency(devHandle, rfFreq); // Set channel #1 freq
	if (status != EXIT_SUCCESS) return 1;
	printf("\n Freq ..........\n");
	status = sc5503b_SetPowerLevel(devHandle, powerLevel); // Set channel #1 rf power level
	if (status != EXIT_SUCCESS) return 1;
	printf("\n Pow ..........\n");

	printf(" The frequency is set to %f Hz \n\n", (double)rfFreq);

	printf("\n********* Reading 16 bytes from Cal EEPROM ***********\n\n");
	for (i=0x04; i < 0x0B; i++)
	{
	status = sc5503b_ReadCalEeprom(devHandle, i, &byte);
	printf("%02X ", byte);
	}
	printf("\n\n");

	status = sc5503b_GetTemperature(devHandle, &deviceTemp); // obtain the temperature
	if (status != EXIT_SUCCESS) return 1;
	printf("\n The temperature of the device is %f degC\n\n", deviceTemp);

	printf("\n********* Writing 8 bytes to User EEPROM ***********\n\n");

	userMemAdd = 0x10;
	for (i=0; i < 8; i++)
	{
	status = sc5503b_WriteUserEeprom(devHandle, userMemAdd + i, userData[i]);
	//Sleep(2); // require a short wait between EEPROM writes, adjust for user system, needs windows.h
	printf("%02X ", userData[i]);
	}	
	printf("\n\n********* Reading 8 bytes from User EEPROM ***********\n\n");	
	for (i=0x0; i < 0x8; i++)
	{
	status = sc5503b_ReadUserEeprom(devHandle,userMemAdd + i, &byte);
	printf("%02X ", byte);
	}	

	printf("\n\n********** EXAMPLE DONE **********\n");
	

	sc5503b_CloseDevice(devHandle); //function closes the device and frees the device Handle
	return 1;
}




