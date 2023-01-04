import numpy as np
from csdl import Model

class ReducedShapeParameterUpdateModel(Model):
    def initialize(self):
        self.parameters.declare('unique_shape_parameter_list')

    def define(self):
        unique_shape_parameter_list = self.parameters['unique_shape_parameter_list']
        '''
        COMPUTATION OF MAP BETWEEN DESIGN VARIABLES AND SHAPE PARAMETERS

        REDUCED LIST OF SHAPE PARAMETERS:
            - magnet_width_sp
            - shaft_radius_sp
        '''

        # THE IDEA HERE IS TO REGISTER ALL OF THE SHAPE PARAMETERS WITHIN 
        # unique_shape_parameter_list AS OUTPUTS TO FEED INTO THE FFD MODELS
        # OR WE USE THE SHAPE PARAMETER AS DESIGN VARIABLES 

        ''' 
        ORDER OF OPERATIONS:
        - deform the major radii radially outward
            - shaft, rotor, inner stator, outer stator
            - the movement of subsequent radii also get shifted by preceding shape parameters
            - ex: shaft affects rotor, inner stator, outer stator; rotor affects inner stator, outer stator
        
        - deform internal geometry
            - magnet thickness and position (bounded by the changes in rotor radii limits)
            - stator slots and shoe/teeth (bounded by changes in inner and outer stator)

        - azimuthal deformations can occur whenever (symmetric about their respective centers)
        '''
        # SHAFT RADIUS
        shaft_radius_dv = self.declare_variable('shaft_radius_dv', val=0.)
        shaft_radius_sp = self.register_output(
            'shaft_radius_sp',
            1*shaft_radius_dv
        )
        # MAGNET WIDTH
        magnet_width_dv = self.declare_variable('magnet_width_dv', val=0.)
        magnet_width_sp = self.register_output(
            'magnet_width_sp',
            1*magnet_width_dv
        )

class ShapeParameterUpdateModel(Model):
    def initialize(self):
        self.parameters.declare('unique_shape_parameter_list')
        self.parameters.declare('original_motor_dim')

    def define(self):
        unique_shape_parameter_list = self.parameters['unique_shape_parameter_list']
        orig_motor_dim = self.parameters['original_motor_dim']
        '''
        COMPUTATION OF MAP BETWEEN DESIGN VARIABLES AND SHAPE PARAMETERS

        LIST OF SHAPE PARAMETERS:
            - inner_stator_radius_sp
            - magnet_thickness_sp
            - magnet_width_sp
            - outer_stator_radius_sp
            - rotor_radius_sp
            - shaft_radius_sp
            - stator_tooth_shoe_thickness_sp
            - winding_top_radius_sp
            - winding_width_sp
        '''

        # THE IDEA HERE IS TO REGISTER ALL OF THE SHAPE PARAMETERS WITHIN 
        # unique_shape_parameter_list AS OUTPUTS TO FEED INTO THE FFD MODELS
        # OR WE USE THE SHAPE PARAMETER AS DESIGN VARIABLES 

        ''' 
        ORDER OF OPERATIONS: (OLD)
        - deform the major radii radially outward
            - shaft, rotor, inner stator, outer stator
            - the movement of subsequent radii also get shifted by preceding shape parameters
            - ex: shaft affects rotor, inner stator, outer stator; rotor affects inner stator, outer stator
        
        - deform internal geometry
            - magnet thickness and position (bounded by the changes in rotor radii limits)
            - stator slots and shoe/teeth (bounded by changes in inner and outer stator)

        - azimuthal deformations can occur whenever (symmetric about their respective centers)

        ORDER OF OPERATIONS: (NEW)
        - Deformations will occur radially-out and propagate to next level
            - shaft, then magnet position, then rotor, stator, etc.
            - each deformation will affect the preceding deformations:
                -
        '''
        
        ''' ROTOR DEFORMATIONS '''
        ''' RADIAL '''
        # SHAFT RADIUS
        shaft_radius_dv = self.declare_variable('shaft_radius_dv', val=0.)
        shaft_radius_sp = self.register_output(
            'shaft_radius_sp',
            1*shaft_radius_dv
        )
        shaft_radius = self.register_output('shaft_radius', orig_motor_dim['shaft_radius']+shaft_radius_sp)

        # MAGNET THICKNESS
        magnet_thickness_dv = self.declare_variable('magnet_thickness_dv', val=0.0)
        magnet_thickness_sp = self.register_output(
            'magnet_thickness_sp',
            1*magnet_thickness_dv
        )

        magnet_thickness = self.register_output('magnet_thickness', orig_motor_dim['magnet_thickness']+magnet_thickness_dv)

        # MAGNET POSITION
        rotor_yoke_thickness_dv = self.declare_variable('rotor_yoke_thickness_dv', val=0.0)
        rotor_yoke_thickness = self.register_output(
            'rotor_yoke_thickness',
            rotor_yoke_thickness_dv + orig_motor_dim['rotor_yoke_thickness']
        )
        magnet_position_sp = self.register_output(
            'magnet_position_sp',
            shaft_radius_sp + rotor_yoke_thickness_dv + magnet_thickness_sp/2
        )
        magnet_position = self.register_output('magnet_position', orig_motor_dim['magnet_position']+magnet_position_sp)

        # ROTOR RADIUS
        rotor_magnet_gap_dv = self.declare_variable('rotor_magnet_gap_dv', val=0.0)
        rotor_radius_sp = self.register_output(
            'rotor_radius_sp',
            magnet_position_sp + magnet_thickness_sp/2 + rotor_magnet_gap_dv
        )
        rotor_radius = self.register_output('rotor_radius', orig_motor_dim['rotor_radius']+rotor_radius_sp)

        ''' AZIMUTHAL '''
        magnet_width_dv = self.declare_variable('magnet_width_dv', val=0.)
        magnet_width_sp = self.register_output(
            'magnet_width_sp',
            1*magnet_width_dv
        )
        magnet_width = self.register_output('magnet_width',orig_motor_dim['magnet_width']+magnet_width_dv*6./7.)

        ''' ======================== STATOR DEFORMATIONS ======================== '''
        ''' RADIAL '''
        # INNER STATOR RADIUS
        air_gap_dv = self.declare_variable('air_gap_dv', val=0.)
        air_gap_depth = self.register_output('air_gap_depth', orig_motor_dim['air_gap_depth']+air_gap_dv) # NEEDED FOR WINDAGE LOSS CALCULATIONS
        
        inner_stator_radius_sp = self.register_output(
            'inner_stator_radius_sp',
            rotor_radius_sp + air_gap_dv
        )
        inner_stator_radius = self.register_output('inner_stator_radius', orig_motor_dim['inner_stator_radius']+inner_stator_radius_sp) # NEEDED FOR WINDAGE LOSS CALCULATIONS

        # SLOT BOTTOM RADIUS
        stator_shoe_thickness_dv = self.declare_variable('stator_shoe_thickness_dv', val=0.)
        slot_bottom_sp = self.register_output(
            'slot_bottom_sp',
            inner_stator_radius_sp + stator_shoe_thickness_dv
        )
        stator_shoe_thickness = self.register_output('stator_shoe_thickness',orig_motor_dim['stator_shoe_thickness']+stator_shoe_thickness_dv)

        # SLOT TOP RADIUS
        winding_height_dv = self.declare_variable('winding_height_dv', val=0.0)
        slot_top_sp = self.register_output(
            'slot_top_sp',
            slot_bottom_sp + winding_height_dv
        )
        slot_height = self.register_output('slot_height', orig_motor_dim['slot_height']+winding_height_dv)

        # SLOT TOP RADIUS
        stator_yoke_thickness_dv = self.declare_variable('stator_yoke_thickness_dv', val=0.0)
        stator_yoke_thickness = self.register_output(
            'stator_yoke_thickness',
            stator_yoke_thickness_dv + orig_motor_dim['stator_yoke_thickness']
        )
        outer_stator_radius_sp = self.register_output(
            'outer_stator_radius_sp',
            slot_top_sp + stator_yoke_thickness_dv
        )
        outer_stator_radius = self.register_output('outer_stator_radius', orig_motor_dim['outer_stator_radius']+outer_stator_radius_sp)

        ''' AZIMUTHAL '''

        ''' STATOR-INTERNAL SHIFTS '''
        slot_width_dv = self.declare_variable('slot_width_dv', val=0.)
        slot_width_sp = self.register_output(
            'slot_width_sp',
            1.*slot_width_dv
        )
        slot_width = self.register_output('slot_width', orig_motor_dim['slot_width']+slot_width_dv)

        '''
        THE FINAL OUTPUTS HERE ARE THE SHAPE PARAMETERS THAT FEED INTO THE 
        INDIVIDUAL MESH MODELS WITHIN INSTANCE MODELS
        LIST OF SHAPE PARAMETERS:
            - inner_stator_radius_sp
            - magnet_thickness_sp
            - magnet_width_sp
            - outer_stator_radius_sp
            - rotor_radius_sp
            - shaft_radius_sp
            - stator_tooth_shoe_thickness_sp
            - winding_top_radius_sp
            - winding_width_sp
        '''