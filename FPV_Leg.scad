/**
V0 - base drone platform

Motor Layout
3 - 1
2 - 4


**/
include <eazl.scad>;
include <C:\\Users\\adoni\\SynologyDrive\\UAV\\3D Print\\CustomBuilt\\Mark4BazStandoffs.scad>;




$fn=60;

module leg(side="R") {
 
   
    difference(){
        //leg size it up
        union(){
        translate([0,-23,-10]) rotate([0,0,0]) scale([.9,2.5,4]) { 
            import ("C:\\Users\\adoni\\SynologyDrive\\UAV\\3D Print\\FPV_leg.stl", 
            convexity=3);
            }
   //opening for charging open into body  
         translate([5,-25,-5]) cube([10,10,10],center=true);
         translate([5,18,-5]) cube([10,10,10],center=true);
         
       }
        translate([0,-26,-5]) cube([50,6,3],center=true);
        translate([0,19,-5]) cube([50,6,3],center=true);
        if ( side == "L" ) translate([11.9,-8,-5]) cube([5,100,400],center=true);

}
  
     // beacon holder aligned with leg
    if ( side == "R" ) translate([8,-4,0.5]) rotate([0,90,0]) holder(17,31,15,70,2,.1);
    if ( side == "L" ) translate([1,-4,0.5]) rotate([0,-90,0]) holder(17,31,15,70,2,.1);

}


 /**       // slice off the top 
        translate([-10,-29,-6]) cube([100,16,20]);
        // thin out the legs
        translate([-25,-60,-87]) cube([50,80,70]);
        translate([35,-60,-87]) cube([50,80,70]);
        // ties
        translate([10,-25,-4]) cube([6,100,3],center=true);
        translate([55,-25,-4]) cube([6,100,3],center=true);
        translate([5,-25,-0]) cube([10,10,20],center=true);
        translate([5,18,-0]) cube([10,10,20],center=true);

**/

//leg("L");