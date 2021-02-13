
# Information on the namings in the log files

Here is a list with more understandable names

## Control Unit

- ctrl_pres         Control Unit pneumatics pressure status

## Scroll pump

- nxdsbs            Scroll bearing service timer
- nxdstrs           Scroll tip reseal service timer
- nxdsf             Scroll frequency
- nxdsct            Scroll controller temperature
- nxdst             Scroll pump temperature

## Turbo pump

- tc400remoteprio   Turbo remote status
- tc400setspdatt    Turbo set speed attained
- tc400spdswptatt   Turbo set speed attained
- tc400ovtemppump   Turbo high pump temperature
- tc400pumpaccel    Turbo pump accelerates
- tc400commerr      Turbo communication error
- tc400pumpstatn    Turbo pump stationary
- tc400errorcode    Turbo error code
- tc400standby      Turbo standby status
- tc400heating      Turbo heating status
- tc400overtempelec Turbo high electronics temperature

## PT compressor

- cpavgl            PT compressor average Low pressure
- cpavgh            PT compressor average High pressure
- cperrcode         PT compressor error code
- cptempwi          PT compressor cooling water in temperature
- cptempwo          PT compressor cooling water out temperature
- cpttime           PT compressor operating hours
- cptempo           PT compressor oil temperature
- cptemph           PT compressor helium temperature
- cparun
  - 0: compressor off
  - 1: compressor on
- cpastate          PT compressor operating state
  - 0: Idling - ready to start
  - 2: Starting
  - 3: Running
  - 4: Running with a warning
  - 5: Stopping
  - 6: Error Lockout
  - 7: Error
  - 8: Helium Cool Down
- cpawarn
  - 0: No warnings
  - 1: Coolant IN running High
  - 2: Coolant IN running Low
  - 4: Coolant OUT running High
  - 8: Coolant OUT running Low
  - 16: Oil running High
  - 32: Oil running Low
  - 64: Helium running High
  - 128: Helium running Low
  - 256: Low Pressure running High
  - 512: Low Pressure running Low
  - 1024: High Pressure running High
  - 2048: High Pressure running Low
  - 4096: Delta Pressure running High
  - 8192: Delta Pressure running Low
  - 131072: Static Pressure running High
  - 262144: Static Pressure running Low
  - 524288: Cold head motor Stall
- cpaerr 
  - 0: No Errors
  - 1: Coolant IN High
  - 2: Coolant IN Low
  - 4: Coolant OUT High
  - 8: Coolant OUT Low
  - 16: Oil High
  - 32: Oil Low
  - 64: Helium High
  - 128: Helium Low
  - 256: Low Pressure High
  - 512: Low Pressure Low
  - 1024: High Pressure High
  - 2048: High Pressure Low
  - 4096: Delta Pressure High
  - 8192: Delta Pressure Low
  - 16384: Motor Current Low
  - 32768: Three Phase Error
  - 65536: Power Supply Error
  - 131072: Static Pressure High
  - 262144: Static Pressure Low
