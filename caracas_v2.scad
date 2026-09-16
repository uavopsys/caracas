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
$fa = 5;

// =============================================================================
// PARAMETERS — everything tunable lives in this block
// =============================================================================

// ---- props & frame ----
prop_size       = 110;           // prop radius; 8 inch ≈ 110mm
frame_length    = prop_size*2;   // keeps propellers from colliding
frame_width     = 100;
frame_thickness = 3;             // case wall thickness
case_rounding   = 25;            // case corner rounding

// ---- support plates (carbon fiber) ----
plate_thickness = 2.5;
plate_clearance = 5;             // per-side gap from the case shell

// ---- slice heights ----
z_top    = 30;  // top slice; 28 to make space for folding arms
z_middle = 45;  // middle slice (centered on z=0); 45 to make space for battery
z_bottom = 30;  // bottom slice

// ---- arms (carbon rods) ----
arms_inner_diameter = 16;        // rod diameter
arms_wall_thicklness = 3;        // support wall strength
arms_support_length = 30;
arms_from_edge = prop_size/2-10;      // rod distance from frame end (keeps prop out of sight)

// arm pairs: A+D is one rod (+x), B+C is one rod (-x).
// z is referenced from the "top"/"bottom" outer face; _z_off = mm inward from it.
// e.g. ref="top", off=5 puts the rod 5mm below the top face.
arm_ad_x     = frame_length/2 - arms_from_edge;
arm_ad_z_ref = "top";
arm_ad_z_off = z_top/2+arms_wall_thicklness-plate_thickness;

arm_bc_x     = -(frame_length/2 - arms_from_edge);
arm_bc_z_ref = "bottom";
arm_bc_z_off = z_bottom/2+arms_wall_thicklness-plate_thickness;


// ---- battery bay (separate printed part, fit-check only) ----
show_battery_bay = false;        // also toggles the d_parts() visual guides
show_props = false;        // toggle proppeler view
battery_bay_pos  = [0, 0, 0];    // bay center in frame coords (mm)

// ---- view ----
show_support_plates = true;
part      = "all";               // "all" | "bottom" | "middle" | "top"
explode   = 50;                  // z gap between slices when part="all" (0 = assembled)
explode_y = 200;                   // slides fit-check parts out in y (plates +y, bay -y)

// ---- battery reference dims (unused by the model; bay dims live in battery_holder.scad)
battery_width  = 65;             // iflight fullsend battery
battery_height = 45;
battery_length = 160;

// =============================================================================
// DERIVED VALUES — computed from the parameters above; do not edit directly
// =============================================================================

frame_height = frame_thickness+z_top+plate_thickness+z_middle+plate_thickness+z_bottom+frame_thickness;

arm_ad_z = arm_z(arm_ad_z_ref, arm_ad_z_off);
arm_bc_z = arm_z(arm_bc_z_ref, arm_bc_z_off);

shell_rim_z = frame_height/2 - case_rounding;  // height where the shell starts curving in



// hollow cylinder: inner D 16, wall 5, length 10, rounded rims
// (rounding is capped at wall/2 = 2.5)
module arm_support(height){
    depth= (frame_width-frame_thickness*1.5)/2;
        rotate([-90,90,0]){
            translate([0,0,-arms_support_length/4])tube(id=arms_inner_diameter, wall=arms_wall_thicklness, h=arms_support_length, rounding=2, center=true);
            *translate([0,0,depth/2])cube([arms_inner_diameter*2, (frame_width-frame_thickness*1.5)/2, height],center=true);
        }

}


module body() {
    
difference(){
    union(){
        // 20x20x20 cube with curvature on all sides
        difference(){
            cuboid([frame_length, frame_width, frame_height], rounding=case_rounding);
                    // hollow the case — inner rounding shrinks by the wall thickness
                    // so the shell stays a uniform 6mm, closed at top/bottom
            cuboid([frame_length-frame_thickness*1.5, frame_width-frame_thickness*1.5, frame_height-frame_thickness*2],
                   rounding=case_rounding-frame_thickness);
        }
    
    
        arm_pair_ad();  // A front, D back — one rod
        arm_pair_bc();  // B front, C back — one rod
    }          

// open the walls where the arms will go
translate([arm_ad_x,0,arm_ad_z]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
translate([arm_bc_x,0,arm_bc_z]) rotate([90,0,0]) cylinder(h=500,d=16,center=true);
}
    
}





// ---- arm pairs --------------------------------------------------------
// Arms are carbon fiber rods in an H configuration; each pair (A+D, B+C)
// is one continuous rod held by two supports. Placement params are at the top.
function arm_z(ref, off) = ref == "top" ? frame_height/2 - off
                                        : -frame_height/2 + off;

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
// cut, one inside the bottom case. Each plate follows the case shell
// cross-section at its own height: middle plates sit where the shell is
// full-size; top/bottom plates where it has curved inward — so smaller.
// Params (plate_thickness, plate_clearance, show_support_plates) are at the top.

// shell cross-section at height z: inward offset and corner radius there
function shell_inset(z)  = abs(z) <= shell_rim_z ? 0
    : case_rounding - sqrt(case_rounding*case_rounding - pow(abs(z) - shell_rim_z, 2));
function shell_corner(z) = abs(z) <= shell_rim_z ? case_rounding
    : sqrt(case_rounding*case_rounding - pow(abs(z) - shell_rim_z, 2));

// one plate sized to the shell cross-section at height z (its center)
module support_plate(z) {
    inset = shell_inset(z) + plate_clearance;
    cuboid([frame_length - 2*inset, frame_width - 2*inset, plate_thickness],
           rounding=max(0, shell_corner(z) - plate_clearance), edges="Z");
}


module m3_hole(){
    cylinder(h=10,d=3.2,center=true);
}


module pattern(){
      x_shift=50;
      y_shift=15;
      z_rotate = 10;
    
      translate([x_shift,0,0]){
      rotate([0,0,z_rotate]) translate([0,y_shift,0]) cuboid([50,10,30], rounding=3, edges="Z");
      rotate([0,0,-z_rotate]) translate([0,-y_shift,0]) cuboid([50,10,30], rounding=3, edges="Z");
      }
      translate([-x_shift,0,0]){
      rotate([0,0,z_rotate]) translate([0,y_shift,0]) cuboid([50,10,30], rounding=3, edges="Z");
      rotate([0,0,-z_rotate]) translate([0,-y_shift,0]) cuboid([50,10,30], rounding=3, edges="Z");
      }



}

**translate ([0,explode_y,100]) pattern();



module foldable_axis(){
        hole_distance=22;
        padding = 6;
        m3_hole = 3.1;
        radius=hole_distance*cos(45/2)+padding+m3_hole;
        thickness=plate_thickness*1.5;
        
        difference(){
            cylinder(h=thickness,r=radius,center=true);
            translate([0,hole_distance*cos(45/2),0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
            translate([0,-hole_distance*cos(45/2),0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
            translate([hole_distance*cos(45/2),0,0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
            translate([-hole_distance*cos(45/2),0,0]) cylinder(h=plate_thickness*2,r=m3_hole/2,center=true);
        }

}

translate([100,100, 20]) foldable_axis();

module support_plates() {
    z_in   = frame_height/2 - frame_thickness;   // inner top/bottom face of the case
    zc_tb  = z_in - plate_thickness/2;           // true center of the top/bottom plates
    zc_mid = z_middle/2 + plate_thickness/2;     // true center of the middle plates

    //top
    translate([0,0,  zc_tb + pair_explode("top")])    support_plate(zc_tb);
    *translate([0,frame_width/3,  zc_tb + pair_explode("top")]) m3_hole();
    *translate([0,-frame_width/3,  zc_tb + pair_explode("top")]) m3_hole();

    //mid top
    translate([0,0,  zc_mid])                         support_plate(zc_mid);
    
    // mid bottom
    translate([0,0, -zc_mid])                         support_plate(-zc_mid);
    
    //bottom
    translate([0,0, -zc_tb + pair_explode("bottom")]) support_plate(-zc_tb);
    translate([zc_tb,zc_tb, -zc_tb + pair_explode("bottom")]) foldable_axis();    
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
    if (show_props) {
    translate([arm_ad_x,-(frame_width+prop_size),ad_z]) proppeler();
    translate([arm_bc_x,-(frame_width+prop_size),bc_z]) proppeler();
    translate([arm_bc_x,(frame_width+prop_size),bc_z]) proppeler();
    translate([arm_ad_x,(frame_width+prop_size),ad_z]) proppeler();
    }
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
// view controls (part, explode, explode_y) are in the PARAMETERS block at top
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