/*
*	The example program shows how the user may want to program the device. This 
*	serves as only as an example. This example show how to open the device,
*	sets the RF mode to fixed tone, sets the frequency to 15 GHz, and then
*	closes the device.
*/

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#endif

#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "sc5511a.h"


 /* Some local functions to display results and perform memory allocation */
void display_device_status(device_status_t *device_status)
{
	printf("\n\n*********DEVICE STATUS READ FROM DEVICE***************\n");
	if (device_status->pll_status.ref_100_pll_ld)
		printf(" 100MHz reference is locked\n");
	else 
		printf(" 100MHz reference is unlocked\n");
	if (device_status->pll_status.sum_pll_ld)
		printf(" RF1 main oscillator is locked \n");
	else
		printf(" RF1 main oscillator is unlocked \n");
	if (device_status->operate_status.ref_out_select)
		printf(" 100 MHz Ref Out Selected \n");
	else
		printf(" 10 MHz Ref Out Selected \n");
	if (device_status->operate_status.rf1_out_enable)
		printf(" RF1 output is enabled \n");
	else
		printf(" RF1 output is disabled \n");
	if (device_status->operate_status.alc_mode)
		printf(" The ALC is in open mode \n");
	else
		printf(" The ALC is in close mode \n");
	if (device_status->list_mode.sss_mode)
		printf(" Using Start-Stop-Step frequencies \n");
	else
		printf(" Using frequencies stored in list buffer \n");
	if (device_status->operate_status.rf1_mode)
		printf(" List/Sweep mode is selected, waiting for trigger \n");
	else
		printf(" Fix frequency mode is selected \n");
	if (device_status->operate_status.over_temp)
		printf(" The device temperature has exceeded the threshold \n");
	else
		printf(" The device temperature has not exceeded the threshold \n");
}

void display_device_info(device_info_t *dev_info)
{
	printf("\n**********DEVICE ATTRIBUTES************* \n");
	printf(" The product serial number is 0x%08X \n",dev_info->product_serial_number);
	printf(" The product firmware rev. is %f \n",dev_info->firmware_revision);
	printf(" The product hardware rev. is %f \n",dev_info->hardware_revision);
	printf(" The product manufacture date is: 20%d-%d-%d\n\n",
							dev_info->man_date.year,dev_info->man_date.month,
							dev_info->man_date.day);	
}

void display_rf_parameters(device_rf_params_t *device_rf_params)
{
	printf("\n**********RF PARAMETERS************* \n");
	printf(" The current rf1 frequency is %f Hz\n", (double)device_rf_params->rf1_freq);
	printf(" The sweep start frequency is %f Hz\n",(double)device_rf_params->start_freq);
	printf(" The sweep stop frequency is %f Hz\n",(double)device_rf_params->stop_freq);
	printf(" The sweep dwell time is %f ms\n",((float)device_rf_params->sweep_dwell_time)/2);
	printf(" The rf_level is %f dBm \n", device_rf_params->rf_level);
	printf(" The current rf2 is %d MHz \n",device_rf_params->rf2_freq);
}

/// The main entry-point function.
int main (int argc, char *argv[])
{
	
	//define the device data parameters
	device_status_t dev_status;
	device_info_t dev_info;
	device_rf_params_t device_rf_params;
	
	//init some device input/output values
	unsigned long long int rf_freq = (unsigned long long int)(15000000000); // chan #1 freq = 15.0 GHz
	unsigned long long int tmp_u64;
	unsigned short rf2_freq = 2000;	
	float temperature;
	float rf_level = 4;

	// parameters to work with the USB device(s)
	#define MAXDEVICES 50
	sc5511a_device_handle_t *dev_handle; //device handle
	int input; // user input to select the device found
	int num_of_devices; // the number of device types found
	char **device_list;  // 2D to hold serial numbers of the devices found 
	int i, status; // status reporting of functions

	
	
	/* 	Begin by looking for devices attached to the host 
	*	=============================================================================================
	*/
	
	device_list = (char**)malloc(sizeof(char*)*MAXDEVICES); // MAXDEVICES serial numbers to search
	for (i=0;i<MAXDEVICES; i++)
		device_list[i] = (char*)malloc(sizeof(char)*SCI_SN_LENGTH); // SCI SN has 8 char
		
	num_of_devices = sc5511a_search_devices(device_list); //searches for SCI for device type
	
	if (num_of_devices == 0) 
	{
		printf("No signal core devices found or cannot not obtain serial numbers\n");
		for(i = 0; i<MAXDEVICES;i++) free(device_list[i]);
		free(device_list);
		printf("\n\n Press ENTER to exit\n");
		getchar();
		return 1;
	}

	printf("\n There are %d SignalCore %s USB devices found. \n \n", num_of_devices, SCI_PRODUCT_NAME);
	i = 0;
	while ( i < num_of_devices)
	{
		printf("	Device %d has Serial Number: %s \n", i+1, device_list[i]);
		i++;
	}
	/* 	*/
	printf("\n Enter the number of the device you wish to select : ");
	
	scanf(" %d",&input);
	getchar();
	if ((input < 1) || (input > num_of_devices)) 
	{
		printf(" No such device !!! exiting... \n");
		return 1;
	}

	/*	Open the selected device through the use of its serial number
	*/
	printf("\n Open the device ..........\n");	
	dev_handle = sc5511a_open_device(device_list[input - 1]);
	if (dev_handle == NULL) 
	{
		printf("Device with serial number: %s cannot be opened.\n", device_list[input - 1]);
		printf("Please ensure your device is powered on and connected\n");
		for(i = 0; i<MAXDEVICES;i++) free(device_list[i]); 
		free(device_list);
		free(dev_handle); //dev_handle is allocated memory on OpenDevice(); 
		printf("\n\n Press ENTER to exit\n");
		getchar();
		return 1;
	}

	for(i = 0; i<MAXDEVICES;i++) free(device_list[i]); 
	free(device_list); // Done with the deviceList

	/*	Begin communication to the device	
	*/
	printf("\n Reading the temperature..........\n");	
	status = sc5511a_get_temperature(dev_handle, &temperature); // Set to single tone mode, not sweep/list
	if (status != SUCCESS) return 1;
	printf("\n The device temperature is %f\n", temperature);

	printf("\n Disable Sweep/List Mode..........\n");	
	status = sc5511a_set_rf_mode(dev_handle, 0); // Set to single tone mode, not sweep/list
	if (status != SUCCESS) return 1;

	printf(" The RF1 frequency is set to %f Hz \n\n", (double)rf_freq);
	status = sc5511a_set_freq(dev_handle, rf_freq); // Set Rf freq
	if (status != SUCCESS) return 1;

	printf(" Enable RF1 output \n");
	status = sc5511a_set_output(dev_handle, 1); // enable the RF1 output
	if (status != SUCCESS) return 1;

	printf(" The RF2 frequency is set to %f Hz \n\n", (double)rf2_freq);
	status = sc5511a_set_rf2_freq(dev_handle, rf2_freq); // Set Rf freq
	if (status != SUCCESS) return 1;

	printf(" The RF Level is set to %f dBm \n\n", rf_level);
	status = sc5511a_set_level(dev_handle, rf_level); // Set Rf freq
	if (status != SUCCESS) return 1;

	printf(" The Ref to 100 MHz out, lock enabled \n\n", rf_level);
	status = sc5511a_set_clock_reference(dev_handle, 1, 1); // Set Rf freq
	if (status != SUCCESS) return 1;

	printf("\n Getting the device status..........\n");	
	status = sc5511a_get_device_status(dev_handle, &dev_status); // Obtain the current status of the device
	if (status != SUCCESS) return 1;	
	display_device_status(&dev_status); // display the device status 
	
	printf("\nGetting device Info ..........\n");
	status = sc5511a_get_device_info(dev_handle, &dev_info);  // obtain calData
	if (status != SUCCESS) return 1;
	display_device_info(&dev_info);

	printf("\nGetting RF parameters ..........\n");
	status = sc5511a_get_rf_parameters(dev_handle, &device_rf_params);  // obtain calData
	if (status != SUCCESS) return 1;
	display_rf_parameters(&device_rf_params);

	//Example using reg_read 
	printf("\nUsing RegRead to get RF2 frequency ..........\n");
	status = sc5511a_reg_read(dev_handle, GET_RF_PARAMETERS, 8, &tmp_u64);
	printf("The RF2 Frequency is %d ", (unsigned short)(tmp_u64 >> 24));

	printf("\nClose Device ..........\n");
	sc5511a_close_device(dev_handle); //function closes the device and frees the device Handle


	printf("\n\n********** EXAMPLE DONE **********\n");

	printf("\n\n Press ENTER to exit\n");
	getchar();

	return 1;
}




