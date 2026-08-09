/**
 * Caracas - Drone Frame
 * =====================
 * Uses the jl_scad project-box library (built on BOSL2)
 * for cases, bodies and rounded curvature.
 */

include <libs/jl_scad/utils.scad>
include <libs/jl_scad/box.scad>
include <libs/jl_scad/parts.scad>

$fs = $preview ? 0.5 : 0.125;
$fa = 1;

// define the props used, that sets the dimension so they do not collide
prop_size=110; //8 inch is about 11cm each prop

// define the carbon fiber thickness
arms_inner_diameter=16; // D -= 16mm
arms_wall_thicklness = 6; // strrength
arms_support_length = 60; // <<- this may be a varuiavble
arms_from_edge = prop_size; // this ensures that the prop is our of sight
plate_thickness = 2.5;


//define battery dimensions
// iflight fullsend battery
battery_width=65;
battery_height=45;
battery_length=160;

// slice heights in mm — the three should add up to frame_height (100)
z_top    = 45;  // height of top slice
z_middle = 20;  // height of middle slice (centered on z=0)
z_bottom = 45;  // height of bottom slice


/// the frame size
frame_thickness = 6;
frame_length = prop_size*4; // ensures there is a little space between the propplers so they do not collide
frame_width  = 100;
frame_height = frame_thickness+z_top+plate_thickness+z_middle+plate_thickness+z_bottom+frame_thickness;



// hollow cylinder: inner D 16, wall 5, length 10, rounded rims
// (rounding is capped at wall/2 = 2.5)
module arm_support(height){
    depth= (frame_width-frame_thickness*2)/2;
        rotate([-90,90,0]){
            translate([0,0,0])tube(id=arms_inner_diameter, wall=arms_wall_thicklness, h=arms_support_length, rounding=2, center=true);
            translate([0,0,depth/2])cube([arms_inner_diameter*2, (frame_width-frame_thickness*2)/2, height],center=true);
        }

}


module body() {
    
difference(){
    union(){
        // 20x20x20 cube with curvature on all sides
        difference(){
            cuboid([frame_length, frame_width, frame_height], rounding=25);
                    // hollow the case
            cuboid([frame_length-frame_thickness*2, frame_width-frame_thickness*2, frame_height-frame_thickness*2], rounding=25);
        }
    
    
         //A
        translate([arms_location_x,-frame_width/2+frame_thickness,frame_height/4]) arm_support(height=z_top);
        //B
        translate([-arms_location_x,-frame_width/2+frame_thickness,-frame_height/4]) arm_support(height=z_top);
        //C
        translate([-arms_location_x,frame_width/2-frame_thickness,-frame_height/4]) rotate([180,0,0]) arm_support(height=z_bottom);
        //D
        translate([arms_location_x,frame_width/2-frame_thickness,frame_height/4]) rotate([180,0,0]) arm_support(height=z_bottom);
    }          

// open the walls where the arms will go
translate([arms_location_x,0,frame_height/4]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
translate([-arms_location_x,0,-frame_height/4]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
}
    
}





// calculate the positions of the arm supports
// the arms will be made of carbon fiber tubes their width is variable per model
// the locaiton of the arms will be relative to each otehr and mirrored.
// starting as an H configuration

arms_location_x = frame_length/2 - arms_from_edge;



module proppeler() {
    color("violet") cylinder(20,d=prop_size*2,center=true);
}

module fullsend_battery() {
    color("blue") cuboid([battery_length, battery_width, battery_height], rounding=2);

}


module d_parts(){
    color("pink") translate([arms_location_x,0,frame_height/4]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
    color("pink") translate([-arms_location_x,0,-frame_height/4]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
    translate([arms_location_x,-(frame_width+prop_size),frame_height/4]) proppeler();
    translate([-arms_location_x,-(frame_width+prop_size),-frame_height/4]) proppeler();
    translate([-arms_location_x,(frame_width+prop_size),-frame_height/4]) proppeler();
    translate([arms_location_x,(frame_width+prop_size),frame_height/4]) proppeler();
    
    translate([-arms_location_x,-(frame_width+prop_size),-frame_height/4]) fullsend_battery();
}


d_parts();




module drone(){
    body();
    //arm_supports();
}

// slice the drone into 3 horizontal slices (bottom/middle/top)
// set part = "all" | "bottom" | "middle" | "top"
part = "all";

// exploded view: Z gap in mm between slices when part="all" (0 = assembled)
explode = 0;


slice_count = 3;

// z range [z0, z1] covered by slice i (0=bottom, 1=middle, 2=top)
function slice_z0(i) = i == 0 ? -frame_height/2
                    : i == 1 ? -z_middle/2
                    :           frame_height/2 - z_top;
function slice_z1(i) = i == 0 ? -frame_height/2 + z_bottom
                    : i == 1 ?  z_middle/2
                    :           frame_height/2;

module drone_slice_at(i) {
    z0 = slice_z0(i);
    z1 = slice_z1(i);
    intersection() {
        drone();
        translate([0, 0, (z0 + z1) / 2])
            cube([frame_length * 2, frame_width * 6, z1 - z0], center=true);
    }
}

module drone_slice(part="all") {
    if (part == "all") {
        if (explode == 0) {
            drone();
        } else {
            for (i = [0:slice_count-1])
                translate([0, 0, (i - (slice_count-1)/2) * explode])
                    drone_slice_at(i);
        }
    } else {
        i = part == "bottom" ? 0 : part == "middle" ? 1 : 2;
        drone_slice_at(i);
    }
}

drone_slice(part);