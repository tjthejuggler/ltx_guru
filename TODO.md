# LTX Balls Documentation TODO

## Outstanding Questions
1. Battery Specifications
   - What type of battery is used?
   - What is the expected runtime?
   - How is it charged?

2. Physical Specifications
   - How many LEDs per ball?
   - What is the LED arrangement?
   - What are the physical dimensions?
   - What is the ball's weight?
   - What type of charging port is used?

3. Performance Specifications
   - What is the reliable WiFi range?
   - What is the maximum number of balls that can be synchronized?
   - What is the refresh rate/FPS of the LED display?

4. Technical Limitations
   - Are there known issues or limitations?
   - What are the memory constraints for programs?
   - Are there temperature limitations?

## Successfully Read Documents

1. `README.TXT.txt`
   - Basic introduction to the software package
   - Mentions LighTriX Editor for PC/MAC
   - Mentions LTX Remote app for Android/Windows/OSX
   - Installation instructions for different platforms

2. `manual/LTX_BALL_Changing the default network credentials.pdf`
   - Detailed button timing controls
   - Network configuration process
   - Default network credentials
   - Process for changing WiFi settings

3. `manual/LTX_editor_tutorial.txt`
   - Contains link to video tutorial: https://vimeo.com/190998885

4. `manual/Sequence_upload.pdf`
   - Process for uploading sequences to WiFi props
   - PRG file export instructions
   - Upload procedure using LTX Remote
   - Status indicators during upload

5. `manual/LighTriX_Editor_buttons.pdf`
   - Comprehensive editor interface documentation
   - Timeline controls
   - Image manipulation features
   - Color and fade controls
   - Project management functions

## Unreadable/Pending Documents

1. `PLAYLTX_ball_manual.doc`
   - Main manual (DOC format not readable)
   - Need alternative format or manual extraction

2. `manual/PLAYLTX_ball_manual.doc`
   - Duplicate of main manual in manual directory

3. `manual/LTX_Remote_App_3_ball.pdf` (Partial)
   - Installation requirements for different platforms
   - Network configuration details (SSID: PLAYLTX, password: pixelprops256)
   - LED status indicators (blue = power on, green = connected)
   - Auto-connection behavior with hotspot device
   - Still need: Complete app overview and functionality documentation

4. Image Files (Need Visual Analysis)
   - `manual/LTX_Editor_add_color.jpg`
   - `manual/LTX_Editor_scale.jpg`

5. Program Files (Binary/Unreadable)
   - `4px_ball_prg_to_upload/4px_colors.prg`
   - `4px_ball_prg_to_upload/4px_color_fast.prg`
   - `4px_ball_prg_to_upload/4px_effects.prg`
   - `4px_ball_prg_to_upload/4px_strobes.prg`
   - `4px_ball_prg_to_upload/4pxball.prg`

## Network Communication
1. Command Protocol
   - [x] Identified working command format (66/'B' as first byte)
   - [x] Verified command structure (12 bytes with opcode at byte 8)
   - [x] Successfully implemented color commands
   - [x] Successfully implemented brightness commands
   - [x] Documented packet formats in README
   - [ ] Test all possible color combinations
   - [ ] Test brightness range limits
   - [ ] Investigate if any other command opcodes exist

2. Packet Analysis
   - [x] Successfully captured and analyzed packets using Wireshark
   - [x] Understood difference between broadcast and direct communication
   - [x] Documented Wireshark filter setup (udp.port == 41412)
   - [x] Analyzed packet headers and payload structure
   - [ ] Create comprehensive packet capture examples
   - [ ] Document typical packet timing/intervals
   - [ ] Analyze packet behavior in poor network conditions

3. Professional Software Analysis
   - [x] Captured and analyzed professional software packets
   - [x] Documented multi-packet approach
   - [ ] Investigate why sequences aren't visible in captures
   - [ ] Study timing between multiple packets
   - [ ] Test different network conditions
   - [ ] Compare reliability with single-packet approach

4. Sequence Communication
   - [ ] Investigate why sequence uploads are not visible in Wireshark
   - [ ] Determine if sequences use a different port or protocol
   - [ ] Compare packet patterns between basic commands and sequences
   - [ ] Document the sequence upload protocol
   - [ ] Analyze how sequences are stored/processed by the ball

## Additional Questions
1. PRG File Format
   - What is the structure of .prg files?
   - How are colors and effects encoded?
   - Are there any tools to view/edit .prg files directly?
   - What are the differences between the sample programs provided?

2. Mosaic Software
   - What is the Mosaic software mentioned in the documentation?
   - How is it used to set start times for backup mode?
   - Is this a separate application from LighTriX Editor and LTX Remote?
   - Where can it be obtained?

## Next Steps
1. Request readable version of PLAYLTX_ball_manual
2. Request working copy of LTX_Remote_App_3_ball.pdf
3. Analyze image files for additional interface documentation
4. Document the contents of sample PRG files in 4px_ball_prg_to_upload/
5. Get answers to outstanding questions
