import os
import numpy as np

def interpolate_bfield(magnetfield_array, ips_time, adwin_time):
    """Interpolate the magnetfield strength for the ADwin data from ips data
    
    This assumes the magnet field sweep was just in one direction.
    Using the data saved via GPIB directly from the IPS, a channel is
    interpolated (using np.linspace) with the BField that matches the ADWin
    data length.
    
    Parameters
    ----------
    magnetfield_array : numpy.ndarray()
        The magnetfield data recorded from the IPS.
    adwin_time : 
        The data frame containing the data recorded by ADWin.
        
        Returns
    -------
    numpy.ndarrary()
        The interpolated magnet field file.
    
    """

    if not isinstance(magnetfield_array, np.ndarray):
        print('Wrong type:', type(magnetfield_array))
        return
    
    if not isinstance(adwin_time, np.ndarray):
        print('Wrong type:', type(adwin_time))
        return
    
    if not isinstance(ips_time, np.ndarray):
        print('Wrong type:', type(ips_time))
        return

    # Calculate the derivative of the IPS Magnetfield data for the purpose of finding when
    # the sweep started and stopped (i.e. dB > 0).
    Bdiff = np.hstack((np.array([0]), np.diff(magnetfield_array)))

    # Get the indices of the start and end times,
    start_i = np.where(Bdiff != 0)[0][0] - 1
    #print('start_i:', start_i)
    #print('bdiff at that point:', Bdiff[start_i])
    #print('mag array there, too:', magnetfield_array[start_i])
    end_i = np.where(Bdiff != 0)[0][-1] 
    #print('end_i:', end_i)
    #print('bdiff at that point:', Bdiff[end_i])
    #print('mag array there, too:', magnetfield_array[end_i])

    # Get the start and end timestamps and minutes
    start_t = ips_time[start_i]
    #print(start_t)
    end_t = ips_time[end_i]
    #print(end_t)
    #start_min = df_ips.Time_m[start_t]
    #end_min = df_ips.Time_m[end_t]

    # Get the start and end magnet field strengths in mT
    start_b = np.round(magnetfield_array[start_i], 6) * 1000
    end_b = np.round(magnetfield_array[end_i], 6) * 1000

    #print(start_b, end_b)

    # Calculate the rate in mT/min
    rate = np.round((end_b - start_b) /(end_t - start_t), 1)
    #print(rate)

    # Get the indices in the adwin index
    start_i = np.where(adwin_time == start_t)[0][0] #df_adwin.index.get_loc(start_t) - 1
    end_i = np.where(adwin_time == end_t)[0][0] #df_adwin.index.get_loc(end_t)  + 0

    #print(start_i, end_i)

    # Generate the start and end arrays, i.e. the parts of the measurement before
    # and after the magnet field sweep is running
    start_array = np.zeros((start_i,)) + start_b
    end_array = np.zeros((adwin_time.shape[0] - end_i,)) + end_b

    # Generay the sweep array 
    mid_array = np.linspace(start_b, end_b, end_i - start_i, False)

    # Combine the generated arrays to one big array
    B_array = np.hstack((start_array, mid_array, end_array))
    # Create the time series in the adwin data frame
    return B_array #pd.TimeSeries(data=B_array, index=df_adwin.index)
