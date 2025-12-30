# Hidden Data Extractor

This tool allows you to search for and extract hidden files within PNG images using Steganography techniques. It performs an exhaustive search by testing multiple combinations of:

-   **Bit Depth**: Number of Least Significant Bits (LSB) used (1 to 8).
-   **Channels**: Which color channels carry the hidden data (R, G, B, A, and combinations).
-   **Data Flow**: Whether data is hidden by color planes (e.g., all Red bits first) or pixel-by-pixel.
-   **Bit Order**: Most Significant Bit first or Least Significant Bit first.

## Features

-   **Automatic Detection**: Identifies file signatures (Magic Numbers) for common formats like PNG, JPG, PDF, ZIP, etc.
-   **Exhaustive Search**: Tries hundreds of combinations to find hidden data without prior knowledge of the hiding method.
-   **Automatic Extraction**: Saves any potential found files with a descriptive filename.

## Installation

Ensure you have Python installed and the `Pillow` library:

```bash
pip install Pillow
```

## Usage

Run the script from the command line, providing the path to the image you want to analyze:

```bash
python extractor.py path/to/image.png
```

### Options

-   `--max-bits`: (Optional) Limit the number of LSBs to test. Default is 8.

Example:

```bash
python extractor.py my_image.png --max-bits 4
```

## Output

If the tool finds any potential files, it will save them in the current directory with filenames indicating the configuration used to find them, for example:
`found_1_2LSB_RGB_pixel_by_pixel_MSB-first.png`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
