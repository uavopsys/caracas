/**
 * SpeedyBee Fold 8 - Common Modules
 * ==================================
 * Reusable modules and utility functions used across multiple parts
 */

include <config.scad>

// Import eazl library for standoff_base, holder, and mtf02p modules
include <libs/eazl.scad>

// =============================================================================
// GPS PROTECTIVE CASE
// =============================================================================

/**
 * GPS Case - Tapered protective enclosure
 * Creates a truncated cone shape for GPS protection
 */
module gps_case() {
    d1 = GPS_CASE_DIAMETER_TOP;
    d2 = GPS_CASE_DIAMETER_BOTTOM;
    h = GPS_CASE_HEIGHT;

    difference() {
        // Outer shell
        translate([0, 0, -h/2])
            rotate([180, 0, 0])
                cylinder(h, d1, d2, center=true);

        // Inner cavity (95% scale with slight height extension)
        translate([0, 0, -h/2 + WALL_THICKNESS])
            rotate([180, 0, 0])
                scale([0.95, 0.95, 1.1])
                    cylinder(h, d1, d2, center=true);
    }
}

/**
 * GPS Cover - Top cover with air equalization holes
 * Provides weather protection while allowing pressure equalization
 */
module gps_cover() {
    inside = 50;

    difference() {
        union() {
            // Main case
            gps_case();

            // Retention lip
            translate([0, 0, -1])
                difference() {
                    cylinder(5, r=GPS_CASE_DIAMETER_TOP - WALL_THICKNESS, center=true);
                    cylinder(7, r=GPS_CASE_DIAMETER_TOP - WALL_THICKNESS*2, center=true);
                }
        }

        // Air equalization holes pattern (vertical)
        for (x = [0, inside/4, -inside/4]) {
            for (y = [0, inside/4, -inside/4]) {
                if (!(x == 0 && y == 0) || (x == 0 && y == 0)) {
                    translate([x, y, 0])
                        cylinder(inside*2, WALL_THICKNESS/2, WALL_THICKNESS/2, center=true);
                }
            }
        }

        // Air equalization holes pattern (horizontal Y-axis)
        for (x = [-inside/4, inside/4]) {
            translate([x, inside/4, 0])
                rotate([90, 0, 0])
                    cylinder(inside*2, WALL_THICKNESS/2, WALL_THICKNESS/2, center=true);
        }

        // Air equalization holes pattern (horizontal X-axis)
        for (y = [-inside/4, inside/4]) {
            translate([inside/4, y, 0])
                rotate([90, 0, 90])
                    cylinder(inside*2, WALL_THICKNESS/2, WALL_THICKNESS/2, center=true);
        }
    }
}

// =============================================================================
// ANTENNA MOUNTING
// =============================================================================

/**
 * SMA Antenna Holes - Creates dual antenna mounting holes
 *
 * Parameters:
 *   sma_x - Spacing between antenna centers
 *   standoff_height - Height of the mounting plate
 *   sma_radius - Radius of antenna holes
 */
module sma_antennas_hole(sma_x=0, standoff_height=20, sma_radius=SMA_ANTENNA_RADIUS) {
    // Left antenna hole
    translate([sma_x/2, 0, standoff_height/2])
        rotate([0, 0, 0])
            cylinder(standoff_height, sma_radius, sma_radius, center=true);

    // Right antenna hole
    translate([-sma_x/2, 0, standoff_height/2])
        rotate([0, 0, 0])
            cylinder(standoff_height, sma_radius, sma_radius, center=true);
}

// =============================================================================
// STRAP HANDLES (for battery retention)
// =============================================================================

/**
 * Strap Handle - Creates a zip-tie or velcro strap loop
 * Used for securing batteries and components
 */
module strap_handle() {
    thickness = STRAP_HANDLE_THICKNESS;
    width = STRAP_HANDLE_WIDTH;
    height = STRAP_HANDLE_HEIGHT;

    difference() {
        // Outer block
        cube([22 + 2*thickness, width, height + thickness], center=true);

        // Inner cutout for strap
        translate([0, 0, 0])
            cube([22, width + 1, height], center=true);
    }
}

// =============================================================================
// MTF-02P CAMERA INSERT
// =============================================================================

/**
 * MTF-02P Insert - Creates a holder insert for the FPV camera
 * Designed to fit snugly into mounting brackets
 */
module mtf02p_insert() {
    // Offset camera position
    translate([0, 5, 0])
        mtf02p();

    // Create insert shell around camera
    scale([1, 1.4, 1])
        difference() {
            // Outer shell (hull of camera form)
            hull() {
                mtf02p();
            }

            // Inner cavity (95% scale, extended in Y)
            scale([0.95, 1.99, 0.95])
                hull() {
                    mtf02p();
                }

            // Cable routing space
            translate([10, 1, 0])
                cube([6, 6, 6], center=true);
        }
}

/**
 * GPS Protective Cover (for M1025-MI)
 * Angled protective cover for GPS module
 */
module gps_protective_cover() {
    difference() {
        // Main protective shell
        rotate([-10, 0, 0])
            translate([-17.5, -70, 0])
                cube([35, 35, 35]);

        // Cutout for GPS holder
        gep_m1025_mi_mtf02p();

        // Trim excess material
        rotate([-10, 0, 0]) translate([-18.5, -71, 8]) cube(60);
        rotate([-10, 0, 0]) translate([-18.5, -37, -1]) cube(60);
        rotate([-10, 0, 0]) translate([-14, -66, 3]) cube(28);
    }
}

// =============================================================================
// REFERENCE: External modules from eazl.scad
// =============================================================================
// The following modules are imported from eazl.scad:
//
// - standoff_base(inner_spacing, diameter, height, extension, support_pct)
//   Creates dual standoff mounting points with connecting base
//
// - holder(dim_length, dim_width, dim_height, open_pct, thickness, spacing, lips)
//   Creates rectangular component holder with optional opening
//
// - mtf02p()
//   Imports the MTF-02P 3D model
//
// =============================================================================
