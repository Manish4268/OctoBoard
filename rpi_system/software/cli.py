import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Run MPP Tracking on Octoboards",
        epilog="Example: python -m software.cli 1 local  (for simulation mode without hardware)"
    )
    parser.add_argument("i2c_nums", type=str, nargs='+', 
                       help="List of I2C bus numbers (e.g., 1 2 3) or '1 local' for simulation")
    args = parser.parse_args()
    
    # Check if 'local' is in the arguments
    i2c_nums = []
    simulation_mode = False
    
    for arg in args.i2c_nums:
        if arg.lower() == 'local':
            simulation_mode = True
        else:
            try:
                i2c_nums.append(int(arg))
            except ValueError:
                print(f"Error: '{arg}' is not a valid I2C bus number")
                sys.exit(1)
    
    if not i2c_nums:
        print("Error: At least one I2C bus number is required")
        sys.exit(1)
    
    # Set simulation mode based on 'local' argument
    if simulation_mode:
        os.environ['OCTOBOARD_SIMULATION'] = 'True'
        print("=" * 60)
        print("RUNNING IN SIMULATION MODE (No hardware required)")
        print("=" * 60)
        print()
    else:
        os.environ['OCTOBOARD_SIMULATION'] = 'False'
        print("=" * 60)
        print("RUNNING IN HARDWARE MODE (Raspberry Pi)")
        print("=" * 60)
        print()
    
    # Import after setting environment variable
    import time
    from . import get_hardware_classes
    OBoardManager, _, _, _ = get_hardware_classes()
    
    board_managers = []
    
    # Initialize all board managers
    for i2c_num in i2c_nums:
        print(f"Initializing MPP tracking on I2C bus {i2c_num}")
        board_managers.append(OBoardManager(i2c_num=i2c_num))
        time.sleep(.1)

    # time.sleep(10)
    ######################################### ADC CURRENT TEST #########################################
    # board_managers[0].oboards[0].channel[1].set_voltage(0)
    # while True:
    #     v = board_managers[0].oboards[0].channel[0].read_voltage()
    #     c = board_managers[0].oboards[0].channel[0].read_current()
    #     print(f'Measured Voltage={v:.5f}, C={c:.5f}') 
    ################################################# END ##############################################

    ############################################ MUX TEST ###########################################
    # print("MUX test")    
    # for board_manager in board_managers:
    #     time.sleep(.1)
    #     for oboard in board_manager.oboards:
    #         for ch in range(8):
    #             # print(f"CH{ch}")
    #             oboard.channel[ch].set_voltage((ch+2)*0.1)
    #             v = oboard.channel[ch].read_voltage()
    #             c = oboard.channel[ch].read_current()
    #             print(f'CH{ch}: Set voltage {((ch+2)*0.1):.5f} - Measured Voltage={v:.5f}, C={c:.5f},')
                
    # print("Done")   #DEBUG
    ################################################# END ##############################################

    ######################################### SINGLE CHANNEL IV SWEEP ########################################
    # Run operations on each board manager
    # print("Starting IV Sweep")    #DEBUG
    # time.sleep(.1)
    # board_managers[0].oboards[0].channel[7].perform_iv_sweep() 
    # print("Done")   #DEBUG
    ################################################# END ##############################################

    # ######################################### ALL CHANNEL IV SWEEP ########################################
    # Run operations on each board manager
    print("Starting IV Sweep")    #DEBUG
    for board_manager in board_managers:
        time.sleep(.1)
        for oboard in board_manager.oboards:
            for ch in range(8):
                print(f"CH{ch}")
                oboard.channel[ch].perform_iv_sweep() #ch2 current reading not working (maybe an issue with the MUX? Maybe a snap in the wires?)
    print("Done")   #DEBUG
    ################################################# END ##############################################

    # ######################################### Single CHANNEL IV SWEEP ########################################
    # Run operations on each board manager
    # print("Starting IV Sweep")    #DEBUG
    # print(board_managers)
    # for ch in range(8):
    #     print(f"CH{ch}")
    #     board_managers[0].oboards[3].channel[ch].perform_iv_sweep() 
    # print("Done")   #DEBUG

    # ################################################# END ##############################################

    ######################################### ALL CHANNEL MPPT ########################################
    # print("Starting MPPT for all channels")        #DEBUG   
    # iterations = 2
    # while True:
    #     for board_manager in board_managers:
    #         time.sleep(.1)
    #         for oboard in board_manager.oboards:
    #             for ch in range(8):
    #                 try:
    #                     oboard.channel[ch].mpp_track(iterations=iterations, interval=1e-4)
    #                 except Exception as e:
    #                     print(f"Error during MPP tracking on channel {ch} of board {oboard.ID}: {e}")
    #     iterations = 4
    ################################################# END ##############################################

    ######################################### SINGLE CHANNEL MPPT ########################################
    # while True:
    #     try:
    #         board_managers[0].oboards[0].channel[0].mpp_track(iterations=4, interval=1e-4)
    #     except Exception as e:
    #         print(f"Error during MPP tracking on channel {1} of board {board_managers[0].oboards[0].ID}: {e}")
    ################################################# END ##############################################

if __name__ == "__main__":
    main()
    