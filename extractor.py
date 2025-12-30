# extractor.py
from PIL import Image
import argparse
import sys

# Dictionary of file signatures to identify file types.
FILE_SIGNATURES = {
    b'\x89PNG\r\n\x1a\n': 'png',
    b'\xFF\xD8\xFF': 'jpg',
    b'%PDF-': 'pdf',
    b'PK\x03\x04': 'zip',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
    b'BM': 'bmp',
    b'RIFF': 'wav', # Could also be AVI
    b'ID3': 'mp3',
    b'7z\xBC\xAF\x27\x1C': '7z',
    b'Rar!\x1A\x07': 'rar'
}

def find_signature(data_chunk):
    """Searches for a file signature and returns the type and start index."""
    for signature, extension in FILE_SIGNATURES.items():
        index = data_chunk.find(signature)
        if index != -1:
            return extension, index
    return None, -1

def bits_to_bytes(bit_stream, lsb_first=False):
    """Converts a bit stream to a byte array, with an option to reverse bit order."""
    byte_array = bytearray()
    for i in range(0, len(bit_stream), 8):
        byte_segment = bit_stream[i:i+8]
        if len(byte_segment) == 8:
            if lsb_first:
                byte_segment = byte_segment[::-1]
            try:
                byte_array.append(int(byte_segment, 2))
            except ValueError:
                pass
    return byte_array

def extract_hidden_data_by_plane(image, num_lsb, channel_indices):
    """Flow: RRR...GGG...BBB..."""
    pixels = list(image.getdata())
    bit_stream = ""
    for channel_index in channel_indices:
        for pixel in pixels:
            if channel_index < len(pixel):
                color_value = pixel[channel_index]
                bit_stream += format(color_value, '08b')[-num_lsb:]
    return bit_stream

def extract_hidden_data_by_pixel(image, num_lsb, channel_indices):
    """Flow: RGB,RGB,RGB..."""
    pixels = list(image.getdata())
    bit_stream = ""
    for pixel in pixels:
        for channel_index in channel_indices:
            if channel_index < len(pixel):
                color_value = pixel[channel_index]
                bit_stream += format(color_value, '08b')[-num_lsb:]
    return bit_stream

def main():
    parser = argparse.ArgumentParser(description="Advanced search and precise extraction of hidden files in images.")
    parser.add_argument("image_file", help="Path to the input PNG image.")
    parser.add_argument("--max-bits", type=int, default=8, help="Maximum number of LSBs to test (1-8). Default: 8.")
    
    args = parser.parse_args()
    print(f"Analyzing image: {args.image_file}")
    
    try:
        image = Image.open(args.image_file).convert('RGBA')
    except FileNotFoundError:
        print(f"Error: File not found at '{args.image_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening image: {e}")
        sys.exit(1)

    channel_configs = [(0, 1, 2), (2, 1, 0), (0, 1, 2, 3), (0,), (1,), (2,), (3,)]
    extraction_methods = [('planes', extract_hidden_data_by_plane), ('pixel_by_pixel', extract_hidden_data_by_pixel)]
    
    found_something = False
    files_found_count = 0

    for n_bits in range(1, args.max_bits + 1):
        for config in channel_configs:
            for lsb_mode in [False, True]:
                for data_flow_name, extraction_function in extraction_methods:
                    config_name = "".join({0:'R', 1:'G', 2:'B', 3:'A'}[i] for i in config)
                    bit_order_name = "LSB-first" if lsb_mode else "MSB-first"
                    
                    print(f"\n--- Testing: {n_bits} LSB | Channels: {config_name} | Flow: {data_flow_name} | Bit Order: {bit_order_name} ---")

                    bit_stream = extraction_function(image, n_bits, config)
                    if not bit_stream: continue
                    hidden_data = bits_to_bytes(bit_stream, lsb_first=lsb_mode)
                    if not hidden_data: continue

                    file_type, start_index = find_signature(hidden_data)
                    
                    if file_type:
                        found_something = True
                        files_found_count += 1
                        
                        print(f"Signature found! Seems to be a '{file_type}' file at position {start_index}.")
                        
                        end_index = -1 
                        if file_type == 'jpg':
                            EOF_MARKER = b'\xFF\xD9'
                            end_index = hidden_data.find(EOF_MARKER, start_index)
                            if end_index != -1:
                                final_data = hidden_data[start_index : end_index + len(EOF_MARKER)]
                            else:
                                final_data = hidden_data[start_index:]
                        else:
                            final_data = hidden_data[start_index:]
                        
                        output_filename = f"found_{files_found_count}_{n_bits}LSB_{config_name}_{data_flow_name}_{bit_order_name}.{file_type}"
                        
                        try:
                            with open(output_filename, "wb") as output_file:
                                output_file.write(final_data)
                            
                            print("\n" + "="*60)
                            print(f"   DISCOVERY REPORT #{files_found_count}")
                            print("="*60)
                            print(f"\nA potential file has been located and extracted with the following configuration:")
                            
                            human_readable_channels = ", ".join([{0:'Red (R)', 1:'Green (G)', 2:'Blue (B)', 3:'Alpha (A)'}[i] for i in config])
                            human_readable_bit_order = "Normal (MSB-first)" if not lsb_mode else "Inversed (LSB-first)"
                            human_readable_data_flow = f"By planes (RR...GG...BB...)" if data_flow_name == 'planes' else f"Interleaved (RGB,RGB,RGB...)"

                            print(f"\n[+] HIDING TECHNIQUE")
                            print(f"    - Bit Depth:      {n_bits} LSB")
                            print(f"    - Carrier Channels: {human_readable_channels}")
                            print(f"    - Data Flow:      {human_readable_data_flow}")
                            print(f"    - Byte Assembly:  {human_readable_bit_order}")
                            
                            print(f"\n[+] EXTRACTED FILE DATA")
                            print(f"    - Resulting File: {output_filename}")
                            print(f"    - Identified Type: {file_type.upper()}")
                            print("="*60)
                            
                        except Exception as e:
                            print(f"Error saving file: {e}")

    print("\n" + "*"*70)
    if found_something:
        print(f"Exhaustive search finished. {files_found_count} potential file(s) found and saved.")
        print("Please review the generated files to find the correct one.")
    else:
        print("Exhaustive search finished. No known file signatures found.")
    print("*"*70)


if __name__ == "__main__":
    main()
