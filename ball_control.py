import socket
import sys
import time

def verify_ball(ip, sock):
    """
    Verify a discovered ball by sending a test command
    """
    # Send a quick black color to test (no visible change)
    command = bytearray(12)
    command[0] = 66  # 'B'
    command[8] = 0x0A  # Color opcode
    command[9] = 0  # R
    command[10] = 0  # G
    command[11] = 0  # B
    
    try:
        sock.sendto(command, (ip, 41412))
        data, addr = sock.recvfrom(1024)
        return True if data else False
    except:
        return False

def get_my_ip(network):
    """
    Get our IP address on the specified network
    """
    try:
        # Create a temporary socket to determine our IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't actually send anything, just helps determine local IP
        s.connect((f"{network}.1", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def discover_balls(network="192.168.1", timeout=5, continuous=True):
    """
    Discover balls by capturing their broadcast packets using a raw socket
    
    This function uses a raw socket (requires root/sudo) to:
    1. Capture all UDP traffic on the network
    2. Parse IP and UDP headers to find packets to/from port 41412
    3. Look for the ball's identifier (NPLAYLTXBALL) in the payload
    4. Verify discovered balls by sending a test command
    
    Args:
        network: Network prefix (e.g. "192.168.1")
        timeout: How long to search for balls (seconds)
        continuous: Whether to keep searching after finding first ball
        
    Returns:
        set: Set of IP addresses of discovered balls
        
    Note:
        Must be run with sudo due to raw socket usage
    """
    print("Starting ball discovery...")
    print(f"Network: {network}.0/24")
    print("Listening for ball broadcasts...\n")
    
    discovered_balls = set()
    
    # Create raw socket to capture UDP traffic
    # Raw sockets let us see all packets including headers
    # This requires root privileges but lets us properly
    # parse the broadcast packets from the balls
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        sock.settimeout(0.5)
        print("Capturing UDP traffic...")
    except PermissionError:
        print("Error: Raw socket requires root privileges")
        print("Please run with: sudo python3 ball_control.py")
        sys.exit(1)
    
    # Create test command (black color)
    command = bytearray(12)
    command[0] = 66  # 'B'
    command[8] = 0x0A  # Color opcode
    command[9] = 0  # R
    command[10] = 0  # G
    command[11] = 0  # B
    
    start_time = time.time()
    current_ip = 1
    
    try:
        while continuous or time.time() - start_time < timeout:
            if discovered_balls:
                break  # Exit once we find at least one ball
            try:
                # Wait for broadcast packet
                data, (ip, port) = sock.recvfrom(1024)
                
                # Parse packet headers:
                # - IP header is first 20 bytes
                # - UDP header is next 8 bytes (20-28)
                # - Payload starts at byte 28
                ip_header = data[:20]
                ip_src = socket.inet_ntoa(ip_header[12:16])  # Source IP is bytes 12-16
                
                udp_header = data[20:28]
                src_port = int.from_bytes(udp_header[0:2], 'big')  # Source port
                dst_port = int.from_bytes(udp_header[2:4], 'big')  # Dest port
                
                payload = data[28:]  # Rest is payload
                
                # Debug output
                print(f"\nPacket: {ip_src}:{src_port} -> :{dst_port}")
                print(f"Data (hex): {payload.hex()}")
                
                # Look for ball identifier in payload
                if dst_port == 41412 and '4e504c41594c545842414c4c' in payload.hex().lower():
                    if ip_src not in discovered_balls:
                        discovered_balls.add(ip_src)
                        print(f"Found ball at {ip_src} (verified)")
                        # Send color command to newly discovered ball
                        try:
                            # Create UDP socket for sending color
                            color_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            # Send a black color to verify (no visible change)
                            command = bytearray(12)
                            command[0] = 66  # 'B'
                            command[8] = 0x0A  # Color opcode
                            command[9] = 0   # R
                            command[10] = 0  # G 
                            command[11] = 0  # B
                            color_sock.sendto(command, (ip_src, 41412))
                            color_sock.close()
                        except Exception as e:
                            print(f"Error sending color to discovered ball: {e}")
                        
                        if not continuous:  # If not continuous, exit after first ball
                            break
                            
            except socket.timeout:
                sys.stdout.write('.')
                sys.stdout.flush()
                if not continuous and time.time() - start_time >= timeout:
                    break
                continue
                
    finally:
        sock.close()
        print("\nDiscovery complete")
        
    return discovered_balls

def select_ball(balls):
    """
    Let user select a ball from the discovered ones
    """
    if not balls:
        print("No balls found!")
        sys.exit(1)
        
    print(f"\nFound {len(balls)} balls:")
    ball_list = list(balls)
    for i, ip in enumerate(ball_list):
        print(f"{i+1}. {ip}")
        
    while True:
        try:
            choice = input("\nSelect a ball (enter number): ")
            idx = int(choice) - 1
            if 0 <= idx < len(ball_list):
                return ball_list[idx]
            print("Invalid selection, try again")
        except ValueError:
            print("Please enter a number")

def send_brightness_command(ip, brightness):
    """
    Send a brightness command to the juggling ball with redundancy
    brightness: value 0-255
    
    Uses same redundancy pattern as color commands for reliability
    """
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Send multiple packets with decreasing prefix values
        prefix_values = [0x1e, 0x19, 0x14, 0x0f, 0x0a, 0x05]  # 30->5
        for prefix in prefix_values:
            # Format command
            command = bytearray(12)  # Initialize all bytes to 0
            command[0] = 66  # 'B'
            command[8] = 0x10  # Brightness opcode
            command[9] = brightness
            
            # Send command and print hex data
            sock.sendto(command, (ip, 41412))
            print(f"Sent brightness packet: {command.hex()}")
        
        print(f"Set brightness to {brightness} on {ip}")
        
    except Exception as e:
        print(f"Error sending command: {e}")
        sys.exit(1)
    finally:
        sock.close()

def send_color_command(ip, color, brightness=None):
    """
    Send a color command to the juggling ball with redundancy
    color: tuple of (r,g,b) values 0-255
    
    Sends multiple packets with decreasing prefix values for reliability:
    - 6 packets total
    - Prefix values: 0x1e, 0x19, 0x14, 0x0f, 0x0a, 0x05 (30->5)
    - Same color command and RGB values in each packet
    - Packets sent in rapid succession
    """
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Base color values
        r, g, b = color
        
        # Send multiple packets with decreasing prefix values
        prefix_values = [0x1e, 0x19, 0x14, 0x0f, 0x0a, 0x05]  # 30->5
        for prefix in prefix_values:
            # Format command
            command = bytearray(12)  # Initialize all bytes to 0
            command[0] = 66  # 'B'
            command[8] = 0x0A  # Color opcode
            command[9] = r  # RGB values
            command[10] = g
            command[11] = b
            
            # Send command and print hex data
            sock.sendto(command, (ip, 41412))
            print(f"Sent color packet: {command.hex()}")
        
        print(f"Sent color {color} to {ip}:41412")
        
    except Exception as e:
        print(f"Error sending command: {e}")
        sys.exit(1)
    finally:
        sock.close()

def validate_brightness(value):
    """
    Validate and convert brightness value
    """
    try:
        brightness = int(value)
        if not 0 <= brightness <= 255:
            raise ValueError
        return brightness
    except:
        print("Error: Brightness should be 0-255")
        sys.exit(1)

def print_help():
    print("""
Ball Control Script Usage:
    python ball_control.py [options] [command]

Options:
    --network=SUBNET   Network to scan (default: 192.168.1)
    --timeout=SECS    Scan timeout in seconds (default: 5)
    --no-continuous   Exit after timeout even if no balls found
    --rgb=R,G,B      Set custom RGB color (values 0-255)
    --brightness=N   Set brightness level (0-255)
    --help           Show this help message

Commands:
    scan            Just scan for balls and list them
    red             Set found ball(s) to red
    green           Set found ball(s) to green
    blue            Set found ball(s) to blue
    off             Turn found ball(s) off (black)
    color           Set custom RGB color (requires --rgb)
    
Example:
    python ball_control.py --network=192.168.0 scan
    python ball_control.py --timeout=10 red
    python ball_control.py --rgb=255,128,0 color
    python ball_control.py --brightness=128 red
    """)

if __name__ == "__main__":
    # Parse command line arguments
    network = "192.168.1"
    timeout = 5
    continuous = True
    command = "scan"
    custom_rgb = None
    brightness = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--network="):
            network = arg.split("=")[1]
        elif arg.startswith("--timeout="):
            timeout = int(arg.split("=")[1])
        elif arg == "--no-continuous":
            continuous = False
        elif arg == "--help":
            print_help()
            sys.exit(0)
        elif arg.startswith("--brightness="):
            brightness = validate_brightness(arg.split("=")[1])
        elif arg.startswith("--rgb="):
            try:
                r, g, b = map(int, arg.split("=")[1].split(","))
                if not all(0 <= x <= 255 for x in (r, g, b)):
                    raise ValueError
                custom_rgb = (r, g, b)
            except:
                print("Error: RGB values should be 0-255 (e.g. --rgb=255,128,0)")
                sys.exit(1)
        elif not arg.startswith("--"):
            command = arg
        i += 1
    
    # Validate network format
    if not network.count(".") == 2:
        print("Error: Network should be in format: 192.168.1")
        sys.exit(1)
    
    print(f"Searching for balls on network {network}.0/24 (press Ctrl+C to stop)...")
    try:
        # Discover available balls
        balls = discover_balls(network=network, timeout=timeout, continuous=continuous)
    except KeyboardInterrupt:
        print("\nSearch cancelled by user")
        sys.exit(0)
    
    if not balls:
        print("No balls found")
        sys.exit(1)
    
    # Handle commands
    if command == "scan":
        print("\nFound balls:")
        for ip in balls:
            print(f"- {ip}")
    else:
        # Color commands
        if command == "color":
            if not custom_rgb:
                print("Error: 'color' command requires --rgb option")
                print("Example: --rgb=255,128,0")
                sys.exit(1)
            color = custom_rgb
        else:
            color = {
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "off": (0, 0, 0)
            }.get(command)
            
            if not color:
                print(f"Unknown command: {command}")
                print_help()
                sys.exit(1)
        
        # Let user select a ball if more than one found
        if len(balls) > 1:
            selected_ball = select_ball(balls)
            balls = {selected_ball}
        
        # Send commands to all selected balls
        for ball_ip in balls:
            # Set brightness if specified
            if brightness is not None:
                send_brightness_command(ball_ip, brightness)
            # Set color
            send_color_command(ball_ip, color)
