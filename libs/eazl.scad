module slider_track(extension=18){
       //sliders
        slider_width = 8; // standard 1.0
        slider_thickness = 4; // standard 1.0
        channel_width = slider_width/2; // standard 1.0
        channel_height = slider_thickness/2; // standard 1.0
        channel_length = 300; // standard 1.0

        
        translate([0,0,0])
        difference(){
        color("brown") cube([slider_width,extension,slider_thickness],center=true);
        color("red") cube([channel_width,channel_length,channel_height+0.1],center=true);
        }

}



//====================================================================
// MODULE: holder()
//====================================================================
// Creates a rectangular component holder with rounded corners,
// a hollow interior for electronics (e.g., GPS, LiDAR modules),
// and an optional open side to allow wire routing or airflow.
//
// PARAMETERS:
// - dim_length   : Inner cavity length (e.g., GPS module length)
// - dim_width    : Inner cavity width (e.g., GPS module width)
// - dim_height   : Inner cavity height (PCB thickness or sensor height)
// - open_pct     : Percentage of the front face left open (for wiring)
// - thickness    : Wall thickness of the holder
//
// FEATURES:
// - Smooth rounded corners via hull + cylinders
// - Inner cutout using cube to ensure PCB fits flat and square
// - Optional front opening (centered horizontally)
//
// EXAMPLE USE CASES:
// - holder(dim_length=25, dim_width=25, dim_height=6) 
//   for mounting a u-blox GPS unit with an open front for wire access.
//
// - holder(dim_length=22, dim_width=16, dim_height=8, open_pct=50)
//   to house a downward-facing LiDAR sensor with partial exposure.
//
// NOTE:
// All coordinates are centered at origin for easier placement and stacking.
// Combine with standoffs or mounts as needed.
//====================================================================
module holder(
    dim_length=20,
    dim_width=10,
    dim_height=5,
    open_pct=80,
    thickness=1.5,
    spacing=0.1,
    lips=false,
    lip_depth=1.0
    ) {
    
    //quality
    radius=2;
    print_spacing = spacing * 2;

    // define the "inner" dimenstions
    inner_length = dim_length + print_spacing;
    inner_width = dim_width + print_spacing;
    inner_dim_height = dim_height;

    // define the "outer" dimensions
    outer_length = dim_length + 2*thickness;
    outer_width = dim_width + 2*thickness;
    outer_height = dim_height + thickness;

    open_width = inner_length * open_pct / 100;
    
    echo("holder() -> Opening width: ", open_width," (mm)");
    echo("holder() -> 3D prinetr spacing: ", print_spacing, " (mm)");


    // local coordinates 0,0,0
    translate([0,0,0]) {
        difference() {
            // Outer tray shape
            hull() {
                for (x = [-outer_length/2 + radius, outer_length/2 - radius]) {
                    for (y = [-outer_width/2 + radius, outer_width/2 - radius]) {
                        translate([x,y,0])
                            cylinder(r=radius, h=outer_height, $fn=40);
                    }
                }
            }

            // Inner cutout (cube so that pcb fit properlly)
            translate([-inner_length/2,-inner_width/2,thickness])
                color("red") cube([inner_length,inner_width,dim_height+0.1]);
            
            // opening on one side
            translate([0, -outer_width/2+thickness/2 , outer_height/2])
                color("red") cube([open_width, thickness+0.1, dim_height-thickness  ], center=true);
           
           
        }// end difference
        if (lips){
        rotate([0,0,90]) translate([0, (inner_length-lip_depth)/2, dim_height+thickness-0.5]) color("orange") cube([dim_width/2, lip_depth, 1], center=true);
        rotate([0,0,90]) translate([0,-(inner_length-lip_depth)/2, dim_height+thickness-0.5]) color("orange") cube([dim_width/2, lip_depth, 1], center=true);
        }
    }//end translate
}//end module


//====================================================================
// MODULE: standoff()
//====================================================================
// Creates a cylindrical standoff with a defined outer wall thickness.
// The inner cylinder is hollowed out to allow space for a screw, wire,
// or mounting hardware. The outer shell is solid and colored gray,
// while the inner void (for visualization) is colored red.
//
// PARAMETERS:
// - diameter   : Inner hole diameter (e.g., for screw or post)
// - height     : Total height of the standoff
// - thickness  : Wall thickness (inner_spacing between inner and outer walls)
//
// FEATURES:
// - Outer cylinder (gray) with inner hollow core (red)
// - Uses difference() to subtract the inner void from the solid
// - Centered at base (Z=0)
//
// EXAMPLE USE CASES:
// - standoff(diameter=3, height=10) 
//   for M3 screw standoffs used to mount flight controllers.
//
// - standoff(diameter=6, height=12, thickness=2)
//   to route LED wires or support structural posts.
//
// NOTE:
// This is a purely visual standoff. For threaded inserts or screw 
// modeling, additional detail would be required.
//====================================================================
module standoff(
    diameter = 5,
    height=10,
    thickness=1.5,
    spacing=0.1

    ) {
        print_spacing = spacing * 2;
        inner_diam = diameter + print_spacing;
        outer_diam = diameter+2*thickness;
        translate([0,0,height/2])
        difference() {
            cylinder(h=height, d=outer_diam, center=true);
                translate([0,0,-spacing])
                    color("red") cylinder(h=height+spacing*3, d=inner_diam, center=true);
        }
} //end module


module stackable_slider(
    inner_spacing = 5, // inner spacing between spacers
    diameter = 5, // outer diameter of standoff
    height=10,
    extension=20,
    support_pct=100,
    thickness=1.5,
    spacing=0.1
    ) {
 
        //sliders
        slider_width = 8; // standard 1.0
        slider_thickness = 4; // standard 1.0
        channel_width = slider_width/2; // standard 1.0
        channel_height = slider_thickness/2; // standard 1.0
        channel_length = 300; // standard 1.0

        // support
        support_x = inner_spacing ;
        support_y = thickness-spacing;
        support_z = height*support_pct/100; // height of support 

        // translate
        move_x = (inner_spacing)/2+2*thickness-spacing ;
        move_y=(-diameter-thickness-1*spacing)/2;
        move_z=+support_z/2; //flush at 0

        difference(){
        union() {
            hull(){
            translate([move_x,0,0]) 
                standoff(diameter,height,thickness,spacing);
            translate([-move_x,0,0]) 
                standoff(diameter,height,thickness,spacing);
            }
            translate([0,0,move_z]) 
                cube([support_x,support_y,support_z],center=true);

            // slider deck
            translate([0,-extension/2,slider_thickness/2])
                    color("green") cube([slider_width,extension+5,slider_thickness],center=true);

        }//union

             translate([move_x,0,spacing]) 
                    color("red") cylinder(h=height*2, d=diameter+2*spacing, center=true);
            translate([-move_x,0,spacing]) 
                    color("red") cylinder(h=height*2, d=diameter+2*spacing, center=true);
//             translate([0,-channel_length/2+15,2+channel_height-(slider_thickness-channel_height)/2]) 

            translate([0,-channel_length/2+15,channel_height/2+slider_thickness/2]) 
                    color("red") cube([channel_width,channel_length,channel_height+spacing],center=true);
            rotate([0,0,90])        
            translate([-extension,-channel_length/2+15,channel_height/2+slider_thickness/2]) 
                    color("red") cube([5,channel_length,channel_height+spacing],center=true);
        }
        

}


module standoff_base(
    inner_spacing = 5, // inner spacing between spacers
    diameter = 5, // outer diameter of standoff
    height=10,
    extension=20,
    support_pct=100,
    thickness=1.5,
    spacing=0.1
    ) {
 
        //sliders
        slider_width = 8; // standard 1.0
        slider_thickness = 4; // standard 1.0
        channel_width = slider_width/2; // standard 1.0
        channel_height = slider_thickness/2; // standard 1.0
        channel_length = 300; // standard 1.0

        // support
        support_x = inner_spacing ;
        support_y = thickness-spacing;
        support_z = height*support_pct/100; // height of support 

        // translate
        move_x = (inner_spacing)/2+2*thickness-spacing ;
        move_y=(-diameter-thickness-1*spacing)/2;
        move_z=+support_z/2; //flush at 0

        rotate ([0,180,0]) translate ([0,0,-height]) difference(){
        union() {
            hull(){
            translate([move_x,0,0]) 
                standoff(diameter,height,thickness,spacing);
            translate([-move_x,0,0]) 
                standoff(diameter,height,thickness,spacing);
            }
            translate([0,0,move_z]) 
                cube([support_x,support_y,support_z],center=true);
            
            
            

          

        }//union



             translate([move_x,0,spacing]) 
                    color("red") cylinder(h=height*2, d=diameter+2*spacing, center=true);
            translate([-move_x,0,spacing]) 
                    color("red") cylinder(h=height*2, d=diameter+2*spacing, center=true);
            translate([0,0,support_z/2-0.1]) 
                    color("purple") cube([inner_spacing-(thickness*2),10,support_z], center=true);

            
        
        }
        

}




module slider_lock (){

       //sliders
        slider_width = 8; // standard 1.0
        slider_thickness = 4; // standard 1.0
        channel_width = slider_width/2; // standard 1.0
        channel_height = slider_thickness/2; // standard 1.0
        channel_length = 300; // standard 1.0

  
        lock_length = slider_width *2;
        lock_width = slider_width *2 ;
        lock_thickness = slider_thickness * 2;



        color("grey") cube([channel_width,lock_length+4,channel_height],center=true);
        color("orange") cube([slider_width,lock_length,slider_thickness],center=true);


       /* //translate([lock_length,lock_width/4-30,lock_thickness/4]) 
        difference(){
        color("orange") cube([lock_width,lock_length,lock_thickness],center=true);

        translate([0,0,channel_height/2])
            slider_track();
        }
*/
        


}



module gps_slider (gps_width=20,gps_height=8){

    //GPS
    translate([0,-slider_one_length-gps_width/2,0]) 
        rotate([0,0,180]) 
            holder(gps_width,gps_width,gps_height);
 

}


module mtf02p () {
    { import ("C:\\Users\\adoni\\SynologyDrive\\UAV\\3D Print\\CustomBuilt\\MTF\\MTF-02P.3mf", convexity=3);}
}


//holder();