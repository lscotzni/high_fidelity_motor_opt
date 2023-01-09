from fe_csdl_opt.fea.fea_dolfinx import *
import numpy as np
import os
from python_csdl_backend import Simulator as py_simulator
from matplotlib import pyplot as plt

from electric_motor_mdo.high_fidelity.geometry.motor_mesh_class import MotorMesh
from electric_motor_mdo.high_fidelity.motor_model_class_hf import HFMotorClass
from input_parameters import *

pi = np.pi

def GridIndependenceFunction(file_name, angles, shift, l1, l2, l3, l4):
    mm = MotorMesh(
        file_name=file_name,
        popup=False,
        rotation_angles=angles*pi/180,
        base_angle=shift*pi/180
    )
    mm.l1 = l1
    mm.l2 = l2
    mm.l3 = l3
    mm.l4 = l4

    mm.baseline_geometry=True
    mm.create_motor_mesh()

    m = mm.motor_mesh_object
    A_z_eval_points = mm.A_z_eval_points # COORDINATES FOR FLUX LINKAGE EVALUATION
    parametrization_dict = mm.ffd_param_dict
    original_motor_dim = mm.original_motor_dim

    motor = HFMotorClass(poles=p, slots=p*3, parametrization_dict=parametrization_dict,
                    mechanical_angles=mech_angles, electrical_angles=elec_angles,
                    A_z_eval_points=A_z_eval_points, mesh_file_path=file_name, 
                    original_motor_dim=original_motor_dim
    )

    motor_model = motor.create_motor_model()
    sim = py_simulator(motor_model, display_scripts=False)
    current_amp = 30.
    sim['current_amplitude'] = current_amp
    sim['motor_length'] = 0.07
    # sim['rpm'] = 882.449599 * 4.
    # sim['output_torque_from_rotor'] = 1792.64 / 4
    sim.run()
    #region # collect torque and other values to compare for convergence study
    em_torque = sim['avg_electromagnetic_torque']
    #endregion

    return em_torque

'''
====================================================================================
'''
# OTHER INPUTS COME FROM input_parameters.py

torque_array = np.zeros((len(l1_list), len(l2_list), len(l3_list), len(l4_list)))

for a, l1 in enumerate(l1_list):
    for b, l2 in enumerate(l2_list):
        for c, l3 in enumerate(l3_list):
            for d, l4 in enumerate(l4_list):
                file_name = mesh_file_base_dir + '_{}'.format(a) + \
                '_{}'.format(b) + '_{}'.format(c) + '_{}'.format(d)

                em_torque = GridIndependenceFunction(
                    file_name=file_name,
                    angles=rotor_rotations,
                    shift=shift,
                    l1=l1, l2=l2, l3=l3, l4=l4,
                )

                torque_array[a,b,c,d] = em_torque





