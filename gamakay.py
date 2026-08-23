import usb.core
import usb.util
import sys

VENDOR_ID = 0x3151
PRODUCT_ID = 0x5030

device_set = int(sys.argv[1]) if len(sys.argv) > 1 else 0

code_effect_main = int(sys.argv[2]) if len(sys.argv) > 2 else 1

code_effect_set = code_effect_main - 1

speed_set = int(sys.argv[3]) if len(sys.argv) > 3 else 3

brightness_set = int(sys.argv[4]) if len(sys.argv) > 4 else 4

mode_set = int(sys.argv[5]) if len(sys.argv) > 5 else 0

rgb = [int(sys.argv[6]) if len(sys.argv) > 6 else 160, int(sys.argv[7]) if len(sys.argv) > 7 else 255, int(sys.argv[8]) if len(sys.argv) > 8 else 255]



device = [0x07, 0x08]

speed = {4: 0x00, 3: 0x01, 2: 0x02, 1: 0x03, 0: 0x04}

brightness = {4: 0x04, 3: 0x03, 2: 0x02, 1: 0x01, 0: 0x00}

mode = [0x7, 0x8]

code_effect = [0x10, 0x06, 0x0a, 0x05, 0x0c, 0x11, 0x09, 0x0e, 0x12, 0x08, 0x04, 0x0f, 0x01, 0x02, 0x07]


print("1. colorful", "2, starlight", "3. sinewave", "4. ripple", "5. flowerwave", "6. snowfall \n", 
"7. mounataion wave", "8. kill two birds", "9. meteor", "10.shadow \n",
 "12. wave", "13. circal wave", "14. always on \n", 
 "15. breathing", "16. stream")

effect = bytes([0x07, 0x10, 0x01, 0x04, 0x07])

effect = bytes([device[device_set], code_effect[code_effect_set], speed[speed_set], brightness[brightness_set], mode[mode_set]])

print(effect)
    

def create_color_payload(r: int, g: int, b: int) -> bytes:
    """
    Generates a 64-byte USB HID payload for the RGB controller.
    Expects r, g, b values between 0 and 255.
    """
    # 1. The static 5-byte header
    header = effect
    
    # 2. Append the target colors
    active_payload = header + bytes([r, g, b])
    
    # 3. Calculate the One's Complement checksum for the 8th byte
    checksum = (~sum(active_payload)) & 0xFF
    
    packet = active_payload + bytes([checksum])
    
    # 5. Pad the rest with zeros to hit the strict 64-byte wLength requirement
    padded_packet = packet.ljust(64, b'\x00')
    
    return padded_packet

colorResult = create_color_payload(rgb[0], rgb[1], rgb[2]).hex()

def send_raw_control_transfer(hex_string):
    raw_bytes = bytes.fromhex(hex_string)
    
    # Linux will look for natively installed libusb libraries automatically
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    
    if dev is None:
        print("[-] Keyboard not found. Make sure the cable is secure and mode is set to WIRED.")
        return

    print(f"[*] Actively targeting Wired Keyboard (Bus {dev.bus}, Address {dev.address})")

    try:
        # LINUX FIX: Safely detach the default operating system driver from Interface 2
        # so our script can inject the data without a resource conflict error.
        if dev.is_kernel_driver_active(2):
            dev.detach_kernel_driver(2)
            print("[*] Detached default kernel driver from configuration interface.")

        bytes_sent = dev.ctrl_transfer(
            bmRequestType=0x21,       # Host-to-Device Class Request
            bRequest=0x09,            # SET_REPORT Command opcode
            wValue=0x0300,            # Feature Report ID mapping
            wIndex=2,                 # Target Interface 2
            data_or_wLength=raw_bytes 
        )
        
        if bytes_sent == len(raw_bytes):
            print("[+] Successfully injected raw lighting packet directly to the keyboard hardware!")
        else:
            print(f"[-] Warning: Only transmitted {bytes_sent}/{len(raw_bytes)} bytes.")
            
    except Exception as e:
        print(f"[-] Native Control Transfer Failed: {e}")

def main():

    send_raw_control_transfer(colorResult)


if __name__ == "__main__":
    main()
