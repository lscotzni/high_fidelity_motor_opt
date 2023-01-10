import lsdo_dash.api as ld 
import seaborn as sns
import numpy as np 
import pyvista
from dolfinx.plot import create_vtk_mesh
from fe_csdl_opt.fea.fea_dolfinx import *
sns.set()

"""
This script creates the Dash class which defines
- plotting procedure
- which variables to save
- configuration

"""

class MotorDashboard(ld.BaseDash):
    def __init__(self, instances=1, input_load_torque=1.0):
        self.instances = instances
        self.input_load_torque = input_load_torque
        super().__init__()
        
    def setup(self):
        self.set_clientID('simulator')

        key_variables = [
            'efficiency', 'current_amplitude', 'motor_mass', 'motor_length', 'avg_electromagnetic_torque', 'avg_input_power', 
            'avg_voltage_amp', 'hysteresis_loss', 'eddy_current_loss', 'copper_loss', 'output_torque', 'output_power'
        ]
        electrical_variables = []
        electrical_variables.extend(['em_instance_model_{}.flux_linkage_abc'.format(i+1) for i in range(self.instances)])
        electrical_variables.extend(['em_instance_model_{}.flux_linkage_dq'.format(i+1) for i in range(self.instances)])

        mesh_deformation_variables = ['ffd_instance_model_{}.uhat'.format(i+1) for i in range(self.instances)]
        geometric_variables_deltas = [
            'shaft_radius_dv', 'magnet_thickness_dv', 'rotor_yoke_thickness_dv', 'rotor_magnet_gap_dv', 'magnet_width_dv', 'air_gap_dv', 
            'stator_shoe_thickness_dv', 'winding_height_dv', 'stator_yoke_thickness_dv', 'slot_width_dv'
        ]
        geometric_variables_shape_params = [
            'shaft_radius_sp', 'magnet_thickness_sp', 'magnet_position_sp', 'rotor_radius_sp', 'magnet_width_sp', 'inner_stator_radius_sp',
            'slot_bottom_sp', 'slot_top_sp', 'outer_stator_radius_sp', 'slot_width_sp'
        ]
        geometric_variables = [
            'shaft_radius', 'magnet_thickness','magnet_position', 'rotor_radius', 'magnet_width', 'air_gap_depth', 'inner_stator_radius', 
            'stator_shoe_thickness', 'slot_height', 'outer_stator_radius', 'slot_width'
        ]

        variables_dict = {
            'key_variables': key_variables,
            'electrical_variables': electrical_variables,
            'geometric_variables_deltas': geometric_variables_deltas,
            'geometric_variables_shape_params': geometric_variables_shape_params,
            'geometric_variables': geometric_variables,
            'mesh_deformation_variables': mesh_deformation_variables
        }

        for key in variables_dict:
            for variable in variables_dict[key]:
                self.save_variable(variable, history=True)

        self.save_variable('torque_delta_constraint', history=True)

        self.add_frame(1,
                       height_in=8.,
                       width_in=12.,
                       ncols=6,
                       nrows = 3,
                       wspace=0.4,
                       hspace=0.4)

        self.add_frame(2,
                       height_in=8.,
                       width_in=12.,
                       ncols=6,
                       nrows = 4,
                       wspace=0.4,
                       hspace=0.4)

    def plot(self,
             frames,
             data_dict_current,
             data_dict_history,
             limits_dict,
             video=False):
        """
        Gets called to create a frame given optimization output. Defined by user.
        The method has the following high level structure:
        - Read variables from argument
        - call "clear_frame" method for each frame
        - plot variables onto each frame
        - call "save_frame" method for each frame

        Parameters
        ----------
            frames: Frame
                Frame object defined in setup
            data_dict_current: dictionary
                dictionary where keys (names of variable) contain current iteration values of respective variable
            data_dict_all: dictionary
                dictionary where keys (names of variable) contain all iteration values of respective variable
            limits_dict: dictionary
                dictionary where keys (names of variables) contain [min, max] of respective variable.
                *NOT YET WORKING*
            video: bool
                *NOT YET WORKING*
        """
        input_load_torque = self.input_load_torque

        frame = frames[1]
        frame.clear_all_axes()

        # get the matplotlib ax method
        ax_subplot = frame[0, 0]
        x_axis = data_dict_history['simulator']['global_ind']
        efficiency = data_dict_history['simulator']['efficiency']
        sns.lineplot(x=x_axis, y=np.array(efficiency).flatten(), ax=ax_subplot)
        ax_subplot.set_ylabel('Objective: efficiency')
        ax_subplot.set_ylim(-0.5, 1.05)
        print('efficiency:')
        print(efficiency)

        # get the matplotlib ax method
        ax_subplot = frame[0, 1]
        current_amp = data_dict_history['simulator']['current_amplitude']
        sns.lineplot(x=x_axis, y=np.array(current_amp).flatten(), ax=ax_subplot)
        ax_subplot.set_ylabel('Current amplitude (A)')

        ax_subplot = frame[0, 2]
        voltage_amp = data_dict_history['simulator']['avg_voltage_amp']
        sns.lineplot(x=list(range(len(voltage_amp))), y=np.array(voltage_amp).flatten(), ax=ax_subplot)
        ax_subplot.set_ylabel('Voltage (V)')
        # ax_subplot.legend()

        # get the matplotlib ax method
        ax_subplot = frame[1:3, 0:3]
        torque_delta = data_dict_history['simulator']['torque_delta_constraint']
        em_torque = data_dict_history['simulator']['avg_electromagnetic_torque']
        output_torque = data_dict_history['simulator']['output_torque']
        print(output_torque)
        print(torque_delta)
        input_load_torque = self.input_load_torque * np.ones_like(x_axis)
        sns.lineplot(x=x_axis, y=np.array(torque_delta).flatten(), marker='*', ax=ax_subplot, label='Torque Constraint')
        sns.lineplot(x=x_axis, y=np.array(em_torque).flatten(), ax=ax_subplot, label='EM Torque')
        sns.lineplot(x=x_axis, y=np.array(output_torque).flatten(), marker='*', ax=ax_subplot, label='Output Torque')
        sns.lineplot(x=x_axis, y=np.array(input_load_torque).flatten(), ax=ax_subplot, label='Input Load Torque')
        ax_subplot.set_ylabel('Torque outputs (Nm)')
        ax_subplot.legend()
        ax_subplot.set_ylim(-1, 1.1 * self.input_load_torque)

        # get the matplotlib ax method
        ax_subplot = frame[0:2, 3:6]
        input_power = data_dict_history['simulator']['avg_input_power']
        output_power = data_dict_history['simulator']['output_power']
        x_axis = list(range(len(input_power)))
        sns.lineplot(x=x_axis, y=np.array(input_power).flatten(), ax=ax_subplot, label='Input Power')
        sns.lineplot(x=x_axis, y=np.array(output_power).flatten(), ax=ax_subplot, label='Output Power')
        ax_subplot.set_ylabel('Input & Output Power (W)')

        ax_subplot = frame[2, 3:5]
        copper_loss = data_dict_history['simulator']['copper_loss']
        hyst_loss = data_dict_history['simulator']['hysteresis_loss']
        ec_loss = data_dict_history['simulator']['eddy_current_loss']
        x_axis = list(range(len(input_power)))
        sns.lineplot(x=x_axis, y=np.array(copper_loss).flatten(), ax=ax_subplot, label='Copper Loss')
        sns.lineplot(x=x_axis, y=np.array(hyst_loss).flatten(), ax=ax_subplot, label='Hysteresis Loss')
        sns.lineplot(x=x_axis, y=np.array(ec_loss).flatten(), ax=ax_subplot, label='Eddy Current Loss')
        ax_subplot.set_ylabel('Power losses (W)')

        ax_subplot = frame[2, 5]
        motor_mass = data_dict_history['simulator']['motor_mass']
        motor_length = data_dict_history['simulator']['motor_length']
        x_axis = list(range(len(input_power)))
        sns.lineplot(x=x_axis, y=np.array(motor_mass).flatten(), ax=ax_subplot, label='mass')
        sns.lineplot(x=x_axis, y=np.array(motor_length).flatten(), ax=ax_subplot, label='length')
        ax_subplot.set_ylabel('Motor Mass & Length')
        ax_subplot.set_ylim(0,50)

        # Write the frame
        frame.write()

        frame = frames[2]
        frame.clear_all_axes()
        '''
        LAYOUT:
        Top: rotor dimensions, stator dimensions (and air-gap)
        Bottom: rotor DVs, stator DVs (and air-gap)
        '''

        ax_subplot = frame[0:2, 0:2]
        shaft_radius = data_dict_history['simulator']['shaft_radius']
        magnet_position = data_dict_history['simulator']['magnet_position']
        rotor_radius = data_dict_history['simulator']['rotor_radius']
        inner_stator_radius = data_dict_history['simulator']['inner_stator_radius']
        outer_stator_radius = data_dict_history['simulator']['outer_stator_radius']
        sns.lineplot(x=x_axis, y=np.array(shaft_radius).flatten(), ax=ax_subplot, label='Shaft Radius')
        sns.lineplot(x=x_axis, y=np.array(magnet_position).flatten(), ax=ax_subplot, label='Radial Magnet Position')
        sns.lineplot(x=x_axis, y=np.array(rotor_radius).flatten(), ax=ax_subplot, label='Rotor Radius')
        sns.lineplot(x=x_axis, y=np.array(inner_stator_radius).flatten(), ax=ax_subplot, label='Inner Stator Radius')
        sns.lineplot(x=x_axis, y=np.array(outer_stator_radius).flatten(), ax=ax_subplot, label='Outer Stator Radius')
        # sns.lineplot(x=x_axis, y=np.array(rotor_yoke).flatten(), ax=ax_subplot, label='Rotor Yoke Thickness')
        # sns.lineplot(x=x_axis, y=np.array(magnet_rotor_separation).flatten(), ax=ax_subplot, label='Magnet Rotor Separation')

        ax_subplot = frame[0:2, 2:4]
        magnet_thickness = data_dict_history['simulator']['magnet_thickness']
        air_gap_depth = data_dict_history['simulator']['air_gap_depth']
        stator_shoe_thickness = data_dict_history['simulator']['stator_shoe_thickness']
        slot_height = data_dict_history['simulator']['slot_height']
        rotor_yoke = magnet_position - magnet_thickness/2 - shaft_radius # UPDATE LATER WITH VARIABLE FROM SIMULATOR
        magnet_rotor_separation = rotor_radius - magnet_position - magnet_thickness/2 # UPDATE LATER WITH VARIABLE FROM SIMULATOR
        stator_yoke_thickness = outer_stator_radius - slot_height - stator_shoe_thickness - inner_stator_radius
        sns.lineplot(x=x_axis, y=np.array(rotor_yoke).flatten(), ax=ax_subplot, label='Rotor Yoke Thickness')
        sns.lineplot(x=x_axis, y=np.array(magnet_thickness).flatten(), ax=ax_subplot, label='Magnet Thickness')
        sns.lineplot(x=x_axis, y=np.array(magnet_rotor_separation).flatten(), ax=ax_subplot, label='Magnet Rotor Separation')
        sns.lineplot(x=x_axis, y=np.array(air_gap_depth).flatten(), ax=ax_subplot, label='Air Gap Depth')
        sns.lineplot(x=x_axis, y=np.array(stator_shoe_thickness).flatten(), ax=ax_subplot, label='Stator Shoe Thickness')
        sns.lineplot(x=x_axis, y=np.array(slot_height).flatten(), ax=ax_subplot, label='Slot Height')
        sns.lineplot(x=x_axis, y=np.array(stator_yoke_thickness).flatten(), ax=ax_subplot, label='Stator Yoke Thickness')


        ax_subplot = frame[2:4, 0:2]
        shaft_radius_dv = data_dict_history['simulator']['shaft_radius_dv']
        magnet_thickness_dv = data_dict_history['simulator']['magnet_thickness_dv']
        rotor_yoke_thickness_dv = data_dict_history['simulator']['rotor_yoke_thickness_dv']
        rotor_magnet_gap_dv = data_dict_history['simulator']['rotor_magnet_gap_dv']
        sns.lineplot(x=x_axis, y=np.array(shaft_radius_dv).flatten(), ax=ax_subplot, label='Shaft Radius DV')
        sns.lineplot(x=x_axis, y=np.array(magnet_thickness_dv).flatten(), ax=ax_subplot, label='Magnet Thickness DV')
        sns.lineplot(x=x_axis, y=np.array(rotor_yoke_thickness_dv).flatten(), ax=ax_subplot, label='Rotor Yoke Thickness DV')
        sns.lineplot(x=x_axis, y=np.array(rotor_magnet_gap_dv).flatten(), ax=ax_subplot, label='Rotor-Magnet Gap DV')
        ax_subplot.set_title('Radial Rotor Geometric Design Variables')
        ax_subplot.set_ylabel('Deformation (m)')

        ax_subplot = frame[2:4, 2:4]
        air_gap_dv = data_dict_history['simulator']['air_gap_dv']
        stator_shoe_thickness_dv = data_dict_history['simulator']['stator_shoe_thickness_dv']
        winding_height_dv = data_dict_history['simulator']['winding_height_dv']
        stator_yoke_thickness_dv = data_dict_history['simulator']['stator_yoke_thickness_dv']
        sns.lineplot(x=x_axis, y=np.array(air_gap_dv).flatten(), ax=ax_subplot, label='Air Gap DV')
        sns.lineplot(x=x_axis, y=np.array(stator_shoe_thickness_dv).flatten(), ax=ax_subplot, label='Stator Shoe Thickness DV')
        sns.lineplot(x=x_axis, y=np.array(winding_height_dv).flatten(), ax=ax_subplot, label='Slot Height DV')
        sns.lineplot(x=x_axis, y=np.array(stator_yoke_thickness_dv).flatten(), ax=ax_subplot, label='Stator Yoke Thickness DV')
        ax_subplot.set_title('Radial Stator Geometric Design Variables')
        ax_subplot.set_ylabel('Deformation (m)')

        ax_subplot = frame[2:4, 4:6]
        magnet_width_dv = data_dict_history['simulator']['magnet_width_dv']
        slot_width_dv = data_dict_history['simulator']['slot_width_dv']
        sns.lineplot(x=x_axis, y=np.array(magnet_width_dv).flatten(), ax=ax_subplot, label='Magnet-Pole Width DV')
        sns.lineplot(x=x_axis, y=np.array(slot_width_dv).flatten(), ax=ax_subplot, label='Slot Width DV')
        ax_subplot.set_title('Azimuthal Geometric Design Variables')
        ax_subplot.set_ylabel('Deformation (rad)')
        

        # 
        # air_gap_depth = data_dict_history['simulator']['air_gap_depth']
        # inner_stator_radius = data_dict_history['simulator']['inner_stator_radius']
        # air_gap_depth = data_dict_history['simulator']['outer_stator_radius']
        # air_gap_depth = data_dict_history['simulator']['stator_shoe_thickness']
        # air_gap_depth = data_dict_history['simulator']['slot_height']
        # stator_yoke = 

        # ax_subplot = frame[0:2, 4:6]

        frame.write()
        
        mesh, boundaries_mf, subdomains_mf, association_table = import_mesh(
            prefix='mesh_files/motor_mesh_1',
            dim=2,
            subdomains=True
        )
        V = VectorFunctionSpace(mesh, ('CG', 1))
        plotter = pyvista.Plotter()
        mesh_grid = pyvista.UnstructuredGrid(*create_vtk_mesh(V)) # function space from FEA
        # mesh_grid = pyvista.read("mesh_files/motor_mesh_1.msh")
        # mesh_grid.point_data["u_hat"] = data_dict_history['simulator']['ffd_instance_model_1.uhat'][-1].reshape((int(28602/2),2))
        # mesh_grid.points = np.zeros((int(28602/2),3))
        # mesh_grid.points[:,:2] = data_dict_history['simulator']['ffd_instance_model_1.uhat'][-1].reshape((int(28602/2),2))
        displacement = np.zeros((int(28602/2),3))
        displacement[:,:2] = data_dict_history['simulator']['ffd_instance_model_1.uhat'][-1].reshape((int(28602/2),2))
        # mesh_grid.set_active_scalars()
        mesh_grid['displacement'] = displacement
        warped = mesh_grid.warp_by_vector('displacement')
        # plot = plotter.add_mesh(mesh_grid)
        plotter.add_mesh(warped)
        # if not pyvista.OFF_SCREEN:
        #     plotter.show()
        # frame.write()
        not_nan_list = []
        for i in range(len(x_axis)):
            if not np.isnan(efficiency[i]) and efficiency[i] > 0:
                not_nan_list.append(i+1) # paraview indexing starts at 1

        print(not_nan_list)
        # print(output_power)


if __name__ == '__main__':
    dashboard = MotorDashboard(input_load_torque=828.30709113/4.)
    # dashboard.use_timestamp() # to use older timestamps
    dashboard.visualize_most_recent(show=True)