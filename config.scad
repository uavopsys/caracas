/**
 * SpeedyBee Fold 8 - Configuration File
 * =====================================
 * All parameters and constants for the SpeedyBee Fold 8 drone parts
 *
 * This file centralizes all measurements, tolerances, and design parameters
 * to make adjustments easier and maintain consistency across all parts.
 */

// =============================================================================
// GLOBAL SETTINGS
// =============================================================================

// Resolution for curved surfaces (higher = smoother but slower to render)
$fn = 60;

// =============================================================================
// FRAME SPECIFICATIONS (SpeedyBee Fold 8 specific)
// =============================================================================

// Standoff dimensions
STANDOFF_BASE_INNER_SPACING = 20.5;  // Spacing between standoffs (tested: 22, 21.8, 21.4)
STANDOFF_BASE_DIAMETER = 5.25;       // Standoff hole diameter (was 5.10, too tight)
STANDOFF_BASE_HEIGHT = 10;           // Default standoff height
STANDOFF_HEIGHT_25MM = 25;           // Standard 25mm standoff height

// Base opening dimensions
BASE_OPENING_HEIGHT = STANDOFF_BASE_HEIGHT - 5;
BASE_OPENING_WIDTH = STANDOFF_BASE_INNER_SPACING - 2;

// =============================================================================
// MATERIAL & PRINTING PARAMETERS
// =============================================================================

// Wall thickness for all parts
WALL_THICKNESS = 2;

// 3D printer tolerance/spacing
PRINT_SPACING = 0.1;
PRINT_TOLERANCE = 0.2;  // Extra clearance for tight fits

// =============================================================================
// ANTENNA SPECIFICATIONS
// =============================================================================

// SMA antenna parameters
SMA_ANTENNA_RADIUS = 4.5;            // SMA connector hole radius
SMA_ANTENNA_SUPPORT_WIDTH = 6;       // Width of antenna support structure
SMA_X_SPACING = STANDOFF_BASE_INNER_SPACING * 2 + SMA_ANTENNA_SUPPORT_WIDTH + 2;

// DJI 04 Pro native antenna
DJI04_ANTENNA_RADIUS = 3.5 / 2;      // Native DJI antenna width

// =============================================================================
// GPS MODULE SPECIFICATIONS
// =============================================================================

// GEP-M10-DQ GPS
GPS_M10_ARM_LENGTH = 70;
GPS_M10_ARM_ANGLE = 35;

// GEP-M1025-MI GPS
GPS_M1025_ARM_LENGTH = 30;
GPS_M1025_ARM_ANGLE = 80;
GPS_M1025_STANDOFF_HEIGHT = 6;
GPS_M1025_ARM_WIDTH = 30;
GPS_M1025_ARM_DEPTH = GPS_M1025_STANDOFF_HEIGHT * 2;
GPS_M1025_THICKNESS = 6;

// Micoair MG-A01 (Ublox M10050)
GPS_MICOAIR_ARM_LENGTH = 70;
GPS_MICOAIR_ARM_ANGLE = 70;
GPS_MICOAIR_STANDOFF_HEIGHT = 22 / 2;

// GPS case dimensions
GPS_CASE_DIAMETER_TOP = 30;
GPS_CASE_DIAMETER_BOTTOM = 26;
GPS_CASE_HEIGHT = 15;

// =============================================================================
// BATTERY SPECIFICATIONS
// =============================================================================

// FullSend 10A Battery
BATTERY_LENGTH = 160;
BATTERY_WIDTH = 67;
BATTERY_DEPTH = 47;
BATTERY_CLEARANCE = 2.3;  // Inner spacing around battery

// Strap handle dimensions
STRAP_HANDLE_THICKNESS = 4;
STRAP_HANDLE_WIDTH = 8;
STRAP_HANDLE_HEIGHT = 5;

// =============================================================================
// CAMERA/VTX SPECIFICATIONS
// =============================================================================

// MTF-02P FPV Camera position adjustments
MTF_X_OFFSET = 0;
MTF_Y_OFFSET = -14;
MTF_Z_OFFSET = -2.5;

// =============================================================================
// MOUNTING & POSITIONING
// =============================================================================

// Extension dimensions
EXTENSION_LENGTH = 40;               // GPS arm extension (was 60)
EXTENSION_WIDTH = 34;

// Position adjustments
GPS_POSITION_OFFSET = 2.5;           // Bring GPS closer
ELRS_POSITION_OFFSET = 0;            // Shift ELRS receiver

// Zip tie slot dimensions
ZIP_TIE_WIDTH = 4;
ZIP_TIE_CLEARANCE = 15;
ZIP_TIE_THICKNESS = 2;

// =============================================================================
// EXTERNAL FILE PATHS
// =============================================================================

// Path to eazl library (common modules)
EAZL_LIBRARY_PATH = "C:/Users/adoni/OneDrive/Documents/OpenSCAD/libraries/eazl.scad";

// Path to 3MF imports
SPEEDYBEE_GPS_MOUNT_PATH = "C:/Users/adoni/SynologyDrive/UAV/3D Print/CustomBuilt/speedybee-mario-8-extended-and-lifted-gps-mount.3mf";
MTF_02P_PATH = "C:/Users/adoni/SynologyDrive/UAV/3D Print/CustomBuilt/MTF/MTF-02P.3mf";

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Calculate outer dimension from inner dimension and wall thickness
 */
function outer_dim(inner, thickness) = inner + (2 * thickness);

/**
 * Calculate inner dimension with printer tolerance
 */
function inner_dim_with_tolerance(nominal, tolerance=PRINT_TOLERANCE) = nominal + tolerance;

/**
 * Calculate hole diameter with clearance
 */
function hole_diameter(nominal_diameter, clearance=PRINT_SPACING) = nominal_diameter + (2 * clearance);
