/*
*	The example program shows how the user may want to program the device. This 
*	serves as only as an example. This examples show how to open the device,
*	set it up for sweep mode, apply software trigger, and end closes the device.
*	The sweep starts at 2.0045 GHz to 2.0055 GHz, over 1 MHz span and step at 10 kHz
*	The dwell time between steps are 10 ms and performs a triangular waveform sweep
*	for 5 cycles, a total of 10s. The sweep should continue after the devices closes
*	or even if the USB cable disconnected after the trigger.
*   
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
void display_rf_parameters(device_rf_params_t *device_rf_params)
{
	printf("\n**********RF PARAMETERS************* \n");
	printf(" The current rf frequency is %f \n",(double)device_rf_params->rf1_freq);
	printf(" The sweep start frequency is %f \n",(double)device_rf_params->start_freq);
	printf(" The sweep stop frequency is %f \n",(double)device_rf_params->stop_freq);
	printf(" The sweep step frequency is %f \n",(double)device_rf_params->step_freq);
	printf(" The sweep dwell is %f ms\n",((float)device_rf_params->sweep_dwell_time)/2);
	printf(" The sweep cycles count is %d \n",device_rf_params->sweep_cycles);
}

/// The main entry-point function.
int main (int argc, char *argv[])
{
	
	//define the device data parameters
	device_rf_params_t device_rf_params;
	list_mode_t list_mode;

	//init some device input values
	unsigned long long int start_freq = (unsigned long long int)(12000000000); // start freq = 12.000 GHz
	unsigned long long int stop_freq = (unsigned long long int)(12050000000); // stop freq = 12.050 GHz
	unsigned long long int step_freq = (unsigned long long int)(1000000); // step at 1 MHz
	unsigned int dwell_time = 200; // delay = dwell_time/2 = 100 ms
	unsigned int sweep_cycles = 10;

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
	free(device_list); // Done with the device_list

	/* Setup List Mode
	*/
	list_mode.sss_mode = 1;	// Use the start-stop-step frequency to generate the sweep
	list_mode.sweep_dir = 0;		// start to stop
	list_mode.tri_waveform = 1;	// triangular waveform
	list_mode.hw_trigger = 0;		// use software trigger
	list_mode.step_on_hw_trig = 0;	// is not use when software trigger is used
	list_mode.return_to_start = 1; // returns the freq to stop at end of sweep cycle
	list_mode.trig_out_enable = 1; // trigger out is enabled
	list_mode.trig_out_on_cycle = 1;// trigger out on every cycle

	/*	Begin communication to the device	
	*/
	printf("\n Enable Sweep/List Mode..........\n\n");	
	status = sc5511a_set_rf_mode(dev_handle, 1); // Set to sweep/list mode
	if (status != SUCCESS) return 1;

	printf(" The start frequency is set to %f Hz \n\n", (double)start_freq);
	status = sc5511a_list_start_freq(dev_handle, start_freq); // Set start Rf freq
	if (status != SUCCESS) return 1;

	printf(" The stop frequency is set to %f Hz \n\n", (double)stop_freq);
	status = sc5511a_list_stop_freq(dev_handle, stop_freq); // Set start Rf freq
	if (status != SUCCESS) return 1;

	printf(" The step frequency is set to %f Hz \n\n", (double)step_freq);
	status = sc5511a_list_step_freq(dev_handle, step_freq); // Set start Rf freq
	if (status != SUCCESS) return 1;

	printf(" The dwell time is set to 10 ms \n\n");
	status = sc5511a_list_dwell_time(dev_handle, dwell_time); // Set to 10 ms dwell
	if (status != SUCCESS) return 1;

	printf(" Set cycle counts to 10 (10s total) \n\n");
	status = sc5511a_list_cycle_count(dev_handle, sweep_cycles); // continuous cycle repeat
	if (status != SUCCESS) return 1;

	printf(" Setup the list mode \n\n");
	status = sc5511a_list_mode_config(dev_handle, &list_mode); // continuous cycle repeat
	if (status != SUCCESS) return 1;

	printf("\n Getting RF parameters ..........\n");
	status = sc5511a_get_rf_parameters(dev_handle, &device_rf_params);  // obtain calData
	if (status != SUCCESS) return 1;
	display_rf_parameters(&device_rf_params);

	printf(" Apply Software Trigger \n\n");
	status = sc5511a_list_soft_trigger(dev_handle); // continuous cycle repeat
	if (status != SUCCESS) return 1;

	printf(" Frequency should now be sweeping \n\n");
	printf("\n Close Device ..........\n");
	sc5511a_close_device(dev_handle); //function closes the device and frees the device Handle

	printf("\n\n********** EXAMPLE DONE **********\n");

	printf("\n\n Press ENTER to exit\n");
	getchar();

	return 1;
}




