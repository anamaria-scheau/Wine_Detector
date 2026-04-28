# convert_config.py
import sys

def convert_bmeconfig_to_header(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    
    with open(output_file, 'w') as f:
        f.write("#ifndef BSEC_CONFIG_H\n")
        f.write("#define BSEC_CONFIG_H\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write("static const uint8_t bsec_config[] = {\n")
        
        # Write bytes in rows of 12
        for i in range(0, len(data), 12):
            chunk = data[i:i+12]
            line = ", ".join(f"0x{b:02x}" for b in chunk)
            f.write(f"    {line},\n")
        
        f.write("};\n\n")
        f.write(f"#define BSEC_CONFIG_SIZE {len(data)}\n\n")
        f.write("#endif\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_config.py input.bmeconfig output.h")
        sys.exit(1)
    convert_bmeconfig_to_header(sys.argv[1], sys.argv[2])