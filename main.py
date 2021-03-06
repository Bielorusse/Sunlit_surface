'''
----------------------------------------------------------------------------------------------------
Python main script for sunlit_surface
----------------------------------------------------------------------------------------------------
'''

import scmod, animod, datetime, os, numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def writing_output_text_file(
    start_date,
    end_date,
    NUMBER_OF_ITERATIONS,
    DELTA_T,
    SPATIAL_RESOLUTION
):
    """
    writing output text file
    input:
     - start_date   datetime.datetime
     - end_date     datetime.datetime
     - NUMBER_OF_ITERATIONS     integer
     - DELTA_T                  float
     - SPATIAL_RESOLUTION       integer
    """

    output_directory = "output_directory"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(
        "{0}/sunlit_surface_output_{1}.txt".format(
            output_directory,
            end_date.strftime("%Y%m%d_%H%M")
        ),
        "w"
    ) as file:

        file.write(
            "----------------------------------------------\n"
            + "Results of sunlit_surface \n"
            + "Date {}\n".format(end_date.strftime("%Y%m%d_%H%M"))
            + "----------------------------------------------\n\n"
            + "Input parameters:\n"
            + "    - computation time (h:m:s)      {}\n".format(end_date - start_date)
            + "    - simulation time (s)           {}\n".format(NUMBER_OF_ITERATIONS * DELTA_T)
            + "    - spatial resolution (degrees)  {}\n".format(SPATIAL_RESOLUTION)
            + "----------------------------------------------\n\n"
        )

start_date = datetime.datetime.now()

SAVE_VIDEO = False

PLANET_DISPLAY_RADIUS = 15.0e6 # km

# Declaring planet surface spatial resolution in degrees
SPATIAL_RESOLUTION = 10

# Declaring planet's orbital parameters
PLANET_SEMI_MAJOR_AXIS = 57909176 # in km
PLANET_ECCENTRICITY = 0.20563069
PLANET_INCLINATION = 0 # in degrees
PLANET_RAAN = 0 # in degrees
PLANET_ARGUMENT_OF_PERIAPSIS = 0 # in degrees

# Declaring planetary constants
MU_SUN = 1.32712440018E11 # in km3/s2
PLANET_RADIUS = 2440 # in km
PLANET_SIDEREAL_PERIOD = 58.646 * 86400 # in seconds
PLANET_ROTATIONAL_VELOCITY = 360 / PLANET_SIDEREAL_PERIOD # in degrees per second
PLANET_AXIAL_TILT = 2 # in degrees

# Declaring time variables
NUMBER_OF_ITERATIONS = int(round(9 * PLANET_SIDEREAL_PERIOD / 86400))
DELTA_T = 86400 # in seconds

# Declaring time, latitude and longitude arrays
time = list(range(0, NUMBER_OF_ITERATIONS * DELTA_T, DELTA_T))
lat = list(range(-90, 91, SPATIAL_RESOLUTION))
lon = list(range(0, 361, SPATIAL_RESOLUTION))

# Declaring array that contains sunlight time over planet's surface
sunlight = np.zeros((len(time) + 1, len(lat), len(lon)))

# Declaring planet's positions arrays
planet_position_vector = np.zeros((len(time), 3))

# computiong planet positions and sunlight times
for j in range(len(time)):

    planet_position_vector[j, :] = scmod.from_orbital_to_cartesian_coordinates(
        PLANET_SEMI_MAJOR_AXIS,
        PLANET_ECCENTRICITY,
        PLANET_INCLINATION,
        PLANET_RAAN,
        PLANET_ARGUMENT_OF_PERIAPSIS,
        time[j],
        MU_SUN
    )

    for k in range(len(lat)):

        for l in range(len(lon)):

            scmod.prompt_progress(
                j * len(lon) * len(lat) + k * len(lon) + l,
                len(time) * len(lat) * len(lon)
            )

            surface_position_vector = scmod.geographic_to_cartesian_coord(lat[k], lon[l], PLANET_RADIUS)

            # planet rotation
            surface_position_vector = scmod.rotate_frame_around_z(
                surface_position_vector, PLANET_ROTATIONAL_VELOCITY * time[j]
            )

            sunlight_time = scmod.compute_sunlight(
                surface_position_vector, planet_position_vector[j, :], DELTA_T
            )

            sunlight[j + 1, k, l] = sunlight[j, k, l] + sunlight_time

sunlight = scmod.normalize_np_array(sunlight)

end_date = datetime.datetime.now()
writing_output_text_file(
    start_date,
    end_date,
    NUMBER_OF_ITERATIONS,
    DELTA_T,
    SPATIAL_RESOLUTION
)

animod.display_animation(
    time,
    lat,
    lon,
    PLANET_ROTATIONAL_VELOCITY,
    PLANET_DISPLAY_RADIUS,
    planet_position_vector,
    sunlight,
    SAVE_VIDEO
)
