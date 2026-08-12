/**
 * SpeedyBee Fold 8 - Battery Holder
 * ==================================
 * Secure mounting system for FullSend 10A batteries
 */

include <config.scad>
include <common_modules.scad>

// =============================================================================
// FULLSEND 10A BATTERY BAY
// =============================================================================

/**
 * FullSend 10A Battery Holder
 *
 * Features:
 *   - Protective enclosure with one open side for easy insertion
 *   - Multiple strap handle positions for secure retention
 *   - Handles on rear, middle-front, and middle-back
 *   - Optimized for 160x65x45mm battery pack
 *
 * Battery Specifications:
 *   - Length: 160mm
 *   - Width: 65mm
 *   - Depth: 45mm
 */
module fullsend10a_battery_bay() {
    inner_space = BATTERY_CLEARANCE;
    batt_length = BATTERY_LENGTH;
    batt_width = BATTERY_WIDTH;
    batt_depth = BATTERY_DEPTH;

    // =========================================================================
    // Main Battery Enclosure
    // =========================================================================

    difference() {
        // Outer shell
        cube([
            batt_length + 2*inner_space,
            batt_width + 2*inner_space,
            batt_depth + 2*inner_space
        ], center=true);

        // Inner cavity (offset for single open side)
        translate([inner_space, 0, 0])
            cube([
                batt_length + inner_space,
                batt_width,
                batt_depth
            ], center=true);
    }

    // =========================================================================
    // Strap Handles - Rear Position
    // =========================================================================

    // Rear left handle
    rotate([0, -90, 0])
        translate([10, batt_width/2 + 5, -batt_length/2 - 5])
            strap_handle();

    // Rear right handle
    rotate([0, -90, 0])
        translate([10, -batt_width/2 - 5, -batt_length/2 - 5])
            strap_handle();

    // =========================================================================
    // Strap Handles - Middle-Front Position (Bottom)
    // =========================================================================

    // Front-left position 1
    translate([batt_length/12, -batt_width/2 - 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();

    // Front-left position 2
    translate([-batt_length/12, -batt_width/2 - 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();

    // Front-left position 3
    translate([batt_length/4, -batt_width/2 - 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();

    // Front-left position 4
    translate([-batt_length/4, -batt_width/2 - 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();

    // =========================================================================
    // Strap Handles - Middle-Back Position (Top)
    // =========================================================================

    // Back-right position 1
    translate([batt_length/12, batt_width/2 + 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();

    // Back-right position 2
    translate([-batt_length/12, batt_width/2 + 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();

    // Back-right position 3
    translate([batt_length/4, batt_width/2 + 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();

    // Back-right position 4
    translate([-batt_length/4, batt_width/2 + 5, -batt_depth/2 + 1.75])
        rotate([90, 0, 0])
            strap_handle();
            
    // ======================================================================
    // wire passage
    // ======================================================================
    translate([0, batt_width/2-3 , -batt_depth/2 - 7])
        cube ([batt_length,10,12],center=true);
    translate([0, -batt_width/2+3, -batt_depth/2 -7])
        cube ([batt_length,10,12],center=true);


}

// =============================================================================
// USAGE EXAMPLES (uncomment to render)
// =============================================================================

// Render battery bay
fullsend10a_battery_bay();

// =============================================================================
// PRINTING NOTES
// =============================================================================

/*
 * Recommended Print Settings:
 *   - Layer Height: 0.2mm - 0.3mm
 *   - Wall Count: 3-4 perimeters
 *   - Infill: 20-30% gyroid or honeycomb
 *   - Support: May need support for strap handles depending on orientation
 *
 * Recommended Orientation:
 *   - Print with battery opening facing up for minimal supports
 *   - Strap handles may need light support material
 *
 * Post-Processing:
 *   - Test fit battery before installing
 *   - Use 20-25mm wide velcro/battery straps
 *   - Ensure clearance is adequate (adjust BATTERY_CLEARANCE in config.scad if needed)
 */

