/**
 * Caracas - Drone Frame
 * =====================
 * Uses the jl_scad project-box library (built on BOSL2)
 * for cases, bodies and rounded curvature.
 */

include <libs/jl_scad/utils.scad>
include <libs/jl_scad/box.scad>
include <libs/jl_scad/parts.scad>

// battery bay module (modules only — its own top-level render call is not executed)
use <battery_holder.scad>

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

// battery bay (separate printed part) placement for fit-checking in the frame
show_battery_bay = false;
battery_bay_pos  = [0, 0, 0];  // bay center in frame coords (mm)

// slice heights in mm — the three should add up to frame_height (100)
z_top    = 25;  // height of top slice
z_middle = 45;  // height of middle slice (centered on z=0)
z_bottom = 25;  // height of bottom slice


/// the frame size
frame_thickness = 6;
case_rounding = 25;   // corner rounding of the case (plates nest inside it)
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
            cuboid([frame_length, frame_width, frame_height], rounding=case_rounding);
                    // hollow the case
            cuboid([frame_length-frame_thickness*2, frame_width-frame_thickness*2, frame_height-frame_thickness*2], rounding=case_rounding);
        }
    
    
        arm_pair_ad();  // A front, D back — one rod
        arm_pair_bc();  // B front, C back — one rod
    }          

// open the walls where the arms will go
translate([arm_ad_x,0,arm_ad_z]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
translate([arm_bc_x,0,arm_bc_z]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
}
    
}





// calculate the positions of the arm supports
// the arms will be made of carbon fiber tubes their width is variable per model
// the locaiton of the arms will be relative to each otehr and mirrored.
// starting as an H configuration

arms_location_x = frame_length/2 - arms_from_edge;

// ---- arm pair placement ----------------------------------------------
// Each pair is one continuous rod held by two supports (A+D, B+C).
// x and z are set per pair. z is referenced from the "top" or "bottom"
// outer face of the frame; _z_off = distance inward from that face (mm).
// e.g. ref="top", off=5 puts the rod 5mm below the top face.
arm_ad_x     = arms_location_x;
arm_ad_z_ref = "top";
arm_ad_z_off = z_top/2;   // reproduces the old frame_height/4 position

arm_bc_x     = -arms_location_x;
arm_bc_z_ref = "bottom";
arm_bc_z_off = z_bottom/2;

function arm_z(ref, off) = ref == "top" ? frame_height/2 - off
                                        : -frame_height/2 + off;
arm_ad_z = arm_z(arm_ad_z_ref, arm_ad_z_off);
arm_bc_z = arm_z(arm_bc_z_ref, arm_bc_z_off);

// explode offset of the slice a pair belongs to (top slice moves up, bottom down)
function pair_explode(ref) = part == "all" ? (ref == "top" ? explode : -explode) : 0;

module arm_pair_ad() {
    h = arm_ad_z_ref == "top" ? z_top : z_bottom;
    //A (front)
    translate([arm_ad_x,-frame_width/2+frame_thickness,arm_ad_z]) arm_support(height=h);
    //D (back)
    translate([arm_ad_x,frame_width/2-frame_thickness,arm_ad_z]) rotate([180,0,0]) arm_support(height=h);
}

module arm_pair_bc() {
    h = arm_bc_z_ref == "top" ? z_top : z_bottom;
    //B (front)
    translate([arm_bc_x,-frame_width/2+frame_thickness,arm_bc_z]) arm_support(height=h);
    //C (back)
    translate([arm_bc_x,frame_width/2-frame_thickness,arm_bc_z]) rotate([180,0,0]) arm_support(height=h);
}

// ---- support plates (carbon fiber — separate parts, not printed) ------
// Four plates: one inside the top case, one on each side of the middle
// cut, one inside the bottom case. Thickness = plate_thickness (2.5mm).
show_support_plates = true;
plate_clearance = 0.5;  // per-side fit clearance inside the case

plate_x = frame_length - 2*frame_thickness - 2*plate_clearance;
plate_y = frame_width  - 2*frame_thickness - 2*plate_clearance;
plate_rounding = case_rounding - plate_clearance;

module support_plate() {
    cuboid([plate_x, plate_y, plate_thickness], rounding=plate_rounding, edges="Z");
}

module support_plates() {
    z_in  = frame_height/2 - frame_thickness;            // inner top/bottom face
    z_mid = z_middle/2 + plate_thickness/2;              // plates around the middle cut

    translate([0,0,  z_in - plate_thickness/2])   support_plate();  // top, inside top case
    translate([0,0,  z_mid])                      support_plate();  // above middle cut
    translate([0,0, -z_mid])                      support_plate();  // below middle cut
    translate([0,0, -(z_in - plate_thickness/2)]) support_plate();  // bottom, inside bottom case
}



module proppeler() {
    color("violet") cylinder(20,d=prop_size*2,center=true);
}


module d_parts(){
    // visual guides follow the exploded slices so alignment stays true
    ad_z = arm_ad_z + pair_explode(arm_ad_z_ref);
    bc_z = arm_bc_z + pair_explode(arm_bc_z_ref);

    color("pink") translate([arm_ad_x,0,ad_z]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
    color("pink") translate([arm_bc_x,0,bc_z]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
    translate([arm_ad_x,-(frame_width+prop_size),ad_z]) proppeler();
    translate([arm_bc_x,-(frame_width+prop_size),bc_z]) proppeler();
    translate([arm_bc_x,(frame_width+prop_size),bc_z]) proppeler();
    translate([arm_ad_x,(frame_width+prop_size),ad_z]) proppeler();
}

if (show_battery_bay)
    d_parts();

// battery bay fit check (separate part — not printed with the frame slices)
if (show_battery_bay)
    color("orange") translate(battery_bay_pos - [0, explode_y, 0]) fullsend10a_battery_bay();

// support plates fit check (carbon fiber — not printed with the frame slices)
if (show_support_plates)
    color("DimGray") translate([0, explode_y, 0]) support_plates();




module drone(){
    body();
    //arm_supports();
}

// slice the drone into 3 horizontal slices (bottom/middle/top)
// set part = "all" | "bottom" | "middle" | "top"
part = "all";

// exploded view: Z gap in mm between slices when part="all" (0 = assembled)
explode = 20;

// additional Y explode: slides the fit-check parts out of the case sideways
// (support plates +y, battery bay -y). 0 = everything at true position.
explode_y = 0;


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