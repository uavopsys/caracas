
include <libs/jl_scad/utils.scad>
include <libs/jl_scad/box.scad>
include <libs/jl_scad/parts.scad>

// caracas plate
frame_width=90;
frame_length=200;
plate_thickness=2.5;
case_rounding=25;



module m3_hole(){
    cylinder(h=10,d=3.2,center=true);
}


module foldable_axis(){
        hole_distance=22;
        m3_hole = 3.1;
        
        rotate([0,0,90]) 
        {
            translate([0,hole_distance,0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
            translate([0,-hole_distance,0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
        }
        translate([0, -hole_distance,0]) rotate([0,0,90]) 
        {
            translate([0,hole_distance,0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
            translate([0,-hole_distance,0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
        }
 
}


 // one plate sized to the shell cross-section at height z (its center)
module support_plate() {
    cuboid([frame_length, frame_width , plate_thickness],
           rounding=case_rounding, edges="Z");
}

module support_holes(){
    
}
support_plate();
translate ([10,0,10]) foldable_axis();